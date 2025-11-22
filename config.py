import json
import os
from dataclasses import dataclass, asdict

CONFIG_FILE = "config.json"

@dataclass
class AppConfig:
    model_size: str = "distil-large-v3"
    device: str = "auto"  # 'auto', 'cuda', 'cpu'
    compute_type: str = "float16" # 'float16', 'int8_float16', 'int8'
    hotkey: str = "ctrl+shift+space"
    language: str = "en"
    input_device_index: int = -1 # -1 for default
    save_recordings: bool = False
    unload_model: bool = False
    gemini_api_key: str = ""
    gemini_model: str = "gemini-1.5-flash"
    translate_to_english: bool = False
    
    @classmethod
    def load(cls):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r") as f:
                    data = json.load(f)
                # Filter out keys that are not in the dataclass
                valid_keys = {k: v for k, v in data.items() if k in cls.__annotations__}
                cfg = cls(**valid_keys)
                
                # Sanity check for hotkey corruption
                if len(cfg.hotkey) > 30:
                    print(f"Detected corrupted hotkey '{cfg.hotkey}', resetting to default.")
                    cfg.hotkey = "ctrl+space"
                    
                return cfg
            except Exception as e:
                print(f"Error loading config: {e}")
                return cls()
        return cls()

    def save(self):
        try:
            with open(CONFIG_FILE, "w") as f:
                json.dump(asdict(self), f, indent=4)
        except Exception as e:
            print(f"Error saving config: {e}")

# Global config instance
config = AppConfig.load()
