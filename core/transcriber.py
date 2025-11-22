import os
from faster_whisper import WhisperModel
from config import config
from core.model_manager import model_manager
import torch

class Transcriber:
    def __init__(self):
        self.model = None
        self.current_model_size = None

    def load_model(self):
        if self.model and self.current_model_size == config.model_size:
            return

        model_path = model_manager.get_model_path(config.model_size)
        
        device = config.device
        if device == "auto":
            device = "cuda" if torch.cuda.is_available() else "cpu"
        
        compute_type = config.compute_type
        if device == "cpu":
            compute_type = "int8" # Force int8 on CPU for speed
        
        print(f"Loading model {config.model_size} on {device} with {compute_type}...")
        
        try:
            self.model = WhisperModel(
                model_path, 
                device=device, 
                compute_type=compute_type
            )
            self.current_model_size = config.model_size
            print("Model loaded successfully.")
        except Exception as e:
            print(f"Error loading model: {e}")
            raise

    def unload_model(self):
        if self.model:
            print("Unloading model to free VRAM...")
            del self.model
            self.model = None
            import gc
            gc.collect()
            if torch.cuda.is_available():
                torch.cuda.empty_cache()

    def transcribe(self, audio_path):
        if not self.model:
            self.load_model()
        
        if not os.path.exists(audio_path):
            return ""

        print(f"Transcribing {audio_path}...")
        try:
            # Determine task based on config
            task = "transcribe"
            if config.translate_to_english:
                task = "translate"
            
            segments, info = self.model.transcribe(
                audio_path, 
                beam_size=5,
                language=config.language if config.language != "auto" else None,
                task=task
            )
            
            text = ""
            for segment in segments:
                text += segment.text
            
            return text.strip()
        finally:
            if config.unload_model:
                self.unload_model()

transcriber = Transcriber()
