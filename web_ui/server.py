import os
import asyncio
import subprocess
from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional

from config import config
from core.model_manager import model_manager
from core.hotkey_manager import hotkey_manager
from core.gemini_formatter import gemini_formatter
import sounddevice as sd
import torch

# Global reference to the main application controller
# This will be set by main.py
controller = None

app = FastAPI()

# Mount static files
app.mount("/static", StaticFiles(directory="web_ui/static"), name="static")
templates = Jinja2Templates(directory="web_ui/templates")

class Settings(BaseModel):
    model_size: str
    language: str
    translate_to_english: bool
    input_device_index: int
    save_recordings: bool
    unload_model: bool
    hotkey: str
    gemini_api_key: str
    gemini_model: str
    device: Optional[str] = "auto"

def get_cpu_name():
    try:
        if os.name == 'nt':
            command = "wmic cpu get name"
            output = subprocess.check_output(command, shell=True).decode().strip()
            lines = output.split('\n')
            if len(lines) > 1:
                return lines[1].strip()
    except:
        pass
    return "Generic CPU"

# Websocket for real-time status updates
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                pass

manager = ConnectionManager()

@app.get("/")
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/api/status")
async def get_status():
    if controller:
        return {
            "is_recording": controller.is_recording,
            "status_text": controller.status,
            "last_action": controller.last_action,
            "last_transcription": controller.last_transcription
        }
    return {}

@app.post("/api/record/toggle")
async def toggle_recording():
    if controller:
        # We need to run this on the main thread logic or ensure thread safety
        # Since controller uses PyQt signals or direct calls, direct call is fine 
        # if we are careful. Ideally, we trigger the hotkey action.
        controller.toggle_recording()
        return {"status": "toggled"}
    return {"error": "Controller not ready"}

@app.get("/api/config")
async def get_config():
    return {
        "model_size": config.model_size,
        "language": config.language,
        "translate_to_english": config.translate_to_english,
        "input_device_index": config.input_device_index,
        "save_recordings": config.save_recordings,
        "unload_model": config.unload_model,
        "hotkey": config.hotkey,
        "gemini_api_key": config.gemini_api_key,
        "gemini_model": config.gemini_model,
        "device": config.device
    }

@app.post("/api/config")
async def save_config(settings: Settings):
    config.model_size = settings.model_size
    config.language = settings.language
    config.translate_to_english = settings.translate_to_english
    config.input_device_index = settings.input_device_index
    config.save_recordings = settings.save_recordings
    config.unload_model = settings.unload_model
    config.hotkey = settings.hotkey
    config.gemini_api_key = settings.gemini_api_key
    config.gemini_model = settings.gemini_model
    config.device = settings.device
    
    config.save()
    
    # Reload components
    gemini_formatter.configure()
    hotkey_manager.stop()
    hotkey_manager.start()
    
    return {"status": "saved"}

@app.get("/api/devices")
async def get_devices():
    devices = []
    try:
        all_devices = sd.query_devices()
        for i, d in enumerate(all_devices):
            if d['max_input_channels'] > 0:
                devices.append({"index": i, "name": d['name']})
    except:
        pass
    return devices

@app.get("/api/system-info")
async def get_system_info():
    gpu_name = torch.cuda.get_device_name(0) if torch.cuda.is_available() else None
    cpu_name = get_cpu_name()
    
    vram_total = 0
    vram_free = 0
    
    if torch.cuda.is_available():
        vram_total = torch.cuda.get_device_properties(0).total_memory / 1024**3
        # Rough estimate of free memory
        r = torch.cuda.memory_reserved(0)
        a = torch.cuda.memory_allocated(0)
        vram_free = (vram_total * 1024**3 - r) / 1024**3 # Very rough

    return {
        "gpu": gpu_name,
        "cpu": cpu_name,
        "cuda_available": torch.cuda.is_available(),
        "vram_total_gb": round(vram_total, 2),
        "models_available": [
            "tiny", "base", "small", "medium", "large-v3", 
            "large-v3-turbo", "distil-large-v3", "distil-large-v2", 
            "distil-medium.en", "distil-small.en"
        ]
    }

@app.post("/api/action/free-vram")
async def free_vram():
    from core.transcriber import transcriber
    transcriber.unload_model()
    return {"status": "freed"}

@app.post("/api/action/setup-dns")
async def setup_dns():
    import sys
    if sys.platform != 'win32':
        return {"status": "error", "message": "Only supported on Windows"}
    
    hosts_path = r"C:\Windows\System32\drivers\etc\hosts"
    entry = "\n127.0.0.1 whisper.local"
    
    try:
        # Check if exists
        with open(hosts_path, 'r') as f:
            content = f.read()
            if "whisper.local" in content:
                return {"status": "success", "message": "URL already configured!"}
        
        # Append
        with open(hosts_path, 'a') as f:
            f.write(entry)
            
        return {"status": "success", "message": "URL configured! Access at http://whisper.local:8000"}
        
    except PermissionError:
        return {"status": "error", "message": "Permission Denied. Run app as Administrator."}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# Helper to push updates from Controller to Web
def broadcast_update(data):
    # asyncio.run is blocking, we need to schedule it on the existing loop
    # But this function is called from a different thread (Main/Qt thread).
    # We will use run_coroutine_threadsafe if we have access to the loop.
    # For now, let's rely on the frontend polling every 500ms for status 
    # which is simpler and robust enough for this use case.
    pass
