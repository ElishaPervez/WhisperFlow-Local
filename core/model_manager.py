import os
from faster_whisper import download_model
from config import config

class ModelManager:
    def __init__(self):
        self.models_dir = os.path.join(os.getcwd(), "models")
        os.makedirs(self.models_dir, exist_ok=True)

    def get_model_path(self, model_size=None):
        size = model_size or config.model_size
        # Check if model is already downloaded (basic check)
        # faster_whisper's download_model handles caching automatically, 
        # so we can just call it. It returns the path to the model.
        print(f"Checking/Downloading model: {size}...")
        try:
            model_path = download_model(size, cache_dir=self.models_dir)
            print(f"Model available at: {model_path}")
            return model_path
        except Exception as e:
            print(f"Error downloading model {size}: {e}")
            raise

model_manager = ModelManager()
