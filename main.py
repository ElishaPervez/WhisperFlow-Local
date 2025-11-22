import os
import sys
import warnings
import webbrowser

# Suppress annoying pkg_resources deprecation warning
warnings.filterwarnings("ignore", category=UserWarning, module="ctranslate2")
warnings.filterwarnings("ignore", message=".*pkg_resources is deprecated.*")

# Pre-load torch
import torch
import time
import threading
import uvicorn
import asyncio

# Enable fast downloads
os.environ["HF_HUB_ENABLE_HF_TRANSFER"] = "1"

import keyboard
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QObject, pyqtSlot, pyqtSignal

from config import config
from core.audio_recorder import AudioRecorder
from core.transcriber import transcriber
from core.hotkey_manager import hotkey_manager
from core.gemini_formatter import gemini_formatter
from gui.system_tray import SystemTray
from gui.widgets import VisualizerOverlay
import shutil
from datetime import datetime

# Web Server Import
from web_ui import server

class ApplicationController(QObject):
    # Signals must be defined at class level
    paste_request = pyqtSignal(str)
    toggle_request = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.app = QApplication(sys.argv)
        self.app.setQuitOnLastWindowClosed(False)
        
        # Logic State
        self.is_recording = False
        self.status = "Ready"
        self.last_action = "Initialized"
        self.last_transcription = "-"
        
        # Initialize formatter
        gemini_formatter.configure()
        
        # GUI Elements (Tray + Overlay only)
        self.tray = SystemTray(None) # No main window parent
        self.tray.activated.connect(self.on_tray_click)
        
        self.overlay = VisualizerOverlay()
        
        self.recorder = AudioRecorder()
        self.recorder.level_updated.connect(self.overlay.set_level)
        
        # Connect signals for thread safety
        hotkey_manager.recording_toggled.connect(self.request_toggle_recording)
        self.toggle_request.connect(self.toggle_recording)
        self.paste_request.connect(self.handle_paste_request)
        
        # Start hotkey listener
        hotkey_manager.start()
        
        # Inject self into server
        server.controller = self

        # Start Web Server
        self.server_thread = threading.Thread(target=self.run_server, daemon=True)
        self.server_thread.start()
        
        print("Web Server started at http://127.0.0.1:8000")
        
        # Optional: Open browser on start
        # webbrowser.open("http://127.0.0.1:8000")

    def run_server(self):
        # Hardcore suppression handler
        def exception_handler(loop, context):
            exc = context.get("exception")
            if exc and (isinstance(exc, ConnectionResetError) or "WinError 10054" in str(exc)):
                return # Suppress
            loop.default_exception_handler(context)

        async def serve():
            loop = asyncio.get_running_loop()
            loop.set_exception_handler(exception_handler)
            
            config = uvicorn.Config(server.app, host="0.0.0.0", port=8000, log_level="critical", loop="asyncio")
            server_instance = uvicorn.Server(config)
            await server_instance.serve()

        # Run the async serve function in this thread's event loop
        if sys.platform == 'win32':
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        
        asyncio.run(serve())

    def on_tray_click(self, reason):
        # Open dashboard on click
        webbrowser.open("http://127.0.0.1:8000")

    # Thread-safe entry point for server/hotkey
    def request_toggle_recording(self):
        self.toggle_request.emit()

    @pyqtSlot()
    def toggle_recording(self):
        # This now runs on the Main Thread
        if self.recorder.recording:
            self.stop_recording()
        else:
            self.start_recording()

    def start_recording(self):
        self.is_recording = True
        self.status = "Recording..."
        self.last_action = "Started Recording"
        print(f"State: {self.status}")
        
        self.recorder.start()
        
        # Show overlay (Safe: Main Thread)
        screen_geo = self.app.primaryScreen().geometry()
        self.overlay.move(
            screen_geo.center().x() - self.overlay.width() // 2,
            screen_geo.bottom() - 150
        )
        self.overlay.show()

    def stop_recording(self):
        self.is_recording = False
        self.status = "Processing..."
        self.last_action = "Stopped Recording"
        print(f"State: {self.status}")
        self.overlay.hide()
        
        # Stop recorder and get audio path
        audio_path = self.recorder.stop()
        
        if audio_path:
            threading.Thread(target=self.process_audio, args=(audio_path,)).start()

    def process_audio(self, audio_path):
        start_time = time.time()
        try:
            self.status = "Transcribing..."
            
            text = transcriber.transcribe(audio_path)
            
            if text:
                self.status = "Formatting..."
                formatted_text = gemini_formatter.format_text(text)
                
                if formatted_text == text:
                    text = self.smart_format(text)
                else:
                    text = formatted_text

                duration = time.time() - start_time
                
                self.last_transcription = text
                self.last_action = f"Transcribed ({duration:.2f}s)"
                self.status = "Ready"
                
                # Emit signal to paste on main thread
                self.paste_request.emit(text)
            else:
                 self.status = "Ready"
                 self.last_action = "No speech detected"
            
        except Exception as e:
            self.status = "Error"
            self.last_action = f"Error: {str(e)[:50]}"
            print(f"Error: {e}")
        finally:
            if os.path.exists(audio_path):
                if config.save_recordings:
                    recordings_dir = os.path.join(os.getcwd(), "recordings")
                    os.makedirs(recordings_dir, exist_ok=True)
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    new_path = os.path.join(recordings_dir, f"recording_{timestamp}.wav")
                    shutil.move(audio_path, new_path)
                else:
                    os.remove(audio_path)

    def smart_format(self, text):
        text = text.strip()
        if text and text[0].islower():
            text = text[0].upper() + text[1:]
        return text

    @pyqtSlot(str)
    def handle_paste_request(self, text):
        # This runs on Main Thread - Safe for Clipboard/COM
        try:
            clipboard = self.app.clipboard()
            clipboard.setText(text)
            time.sleep(0.1)
            keyboard.send('ctrl+v')
        except Exception as e:
            print(f"Paste Error: {e}")
            try:
                keyboard.write(text)
            except:
                pass
    def run(self):
        sys.exit(self.app.exec())

if __name__ == "__main__":
    # Fix for Windows "WinError 10054" noise in asyncio logs
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    # HARDCORE SUPPRESSION of asyncio connection reset errors
    def exception_handler(loop, context):
        msg = context.get("message", "")
        exc = context.get("exception")
        
        # Filter out the specific noise
        if "WinError 10054" in str(exc) or "ConnectionResetError" in str(exc):
            return
        if "SSL handshake failed" in msg:
            return
            
        # Call default handler for everything else
        loop.default_exception_handler(context)

    # Apply the handler when the loop is created (which happens inside uvicorn mostly,
    # but we can try to set it on the global loop if one exists, or monkeypatch).
    # Since Uvicorn creates its own loop, we need to monkeypatch the policy or 
    # inject it. 
    
    # Better approach: Monkeypatch standard error printing if truly desperate,
    # but let's try setting it on the current loop if available.
    try:
        loop = asyncio.get_event_loop()
        loop.set_exception_handler(exception_handler)
    except:
        pass
        
    # We also need to patch the loop created by Uvicorn. 
    # We can do this by subclassing Uvicorn's server or just running it.
    # Actually, since we set the policy to Selector, we can trust that.
    
    # Let's inject the handler into the run_server method instead.

    controller = ApplicationController()
    controller.run()
