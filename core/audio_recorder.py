import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav
import tempfile
import os
import threading
import time
from config import config

from PyQt6.QtCore import QObject, pyqtSignal

class AudioRecorder(QObject):
    level_updated = pyqtSignal(float)

    def __init__(self):
        super().__init__()
        self.recording = False
        self.frames = []
        self.fs = 16000  # Sample rate for Whisper
        self.thread = None
        self.temp_file = None

    def start(self):
        if self.recording:
            return
        self.recording = True
        self.frames = []
        self.thread = threading.Thread(target=self._record)
        self.thread.start()
        print("Recording started...")

    def _record(self):
        device = config.input_device_index if config.input_device_index != -1 else None
        
        # Validate and get device info
        try:
            if device is not None:
                # Check if the specified device is actually an input device
                device_info = sd.query_devices(device)
                if device_info['max_input_channels'] == 0:
                    print(f"Warning: Device '{device_info['name']}' is not an input device. Using default input instead.")
                    device = None  # Fall back to default
                else:
                    max_channels = device_info['max_input_channels']
                    print(f"Using device: {device_info['name']} ({max_channels} channels)")
            
            # Get final device info (either specified or default)
            if device is None:
                device_info = sd.query_devices(kind='input')
                print(f"Using default input device: {device_info['name']}")
            else:
                device_info = sd.query_devices(device, 'input')
            
            max_channels = device_info['max_input_channels']
            # Use mono if supported, otherwise use device's max channels
            channels = 1 if max_channels >= 1 else max_channels
            print(f"Recording with {channels} channel(s) (device supports {max_channels})")
            
        except Exception as e:
            print(f"Warning: Could not query device info: {e}. Using system default with 1 channel.")
            device = None
            channels = 1
        
        try:
            with sd.InputStream(samplerate=self.fs, device=device, channels=channels, dtype='float32', callback=self._callback):
                while self.recording:
                    sd.sleep(50) # Faster updates for visualizer
        except Exception as e:
            print(f"Error during recording: {e}")
            self.recording = False

    def _callback(self, indata, frames, time, status):
        if status:
            print(status)
        
        # Convert stereo to mono if needed (Whisper expects mono)
        if indata.shape[1] > 1:
            # Average all channels to get mono
            mono_data = np.mean(indata, axis=1, keepdims=True)
        else:
            mono_data = indata
        
        self.frames.append(mono_data.copy())
        
        # Calculate RMS for visualizer
        rms = np.sqrt(np.mean(mono_data**2))
        self.level_updated.emit(float(rms))

    def stop(self):
        if not self.recording:
            return None
        
        print("Stopping recording...")
        self.recording = False
        if self.thread:
            self.thread.join()
        
        if not self.frames:
            print("No audio recorded.")
            return None

        # Concatenate all frames
        recording = np.concatenate(self.frames, axis=0)
        
        # Save to temp file
        # We use a named temp file but close it so other processes can read it if needed, 
        # though here we just pass the path.
        fd, path = tempfile.mkstemp(suffix=".wav")
        os.close(fd)
        
        # Convert to 16-bit PCM for compatibility
        data_int16 = (recording * 32767).astype(np.int16)
        wav.write(path, self.fs, data_int16)
        
        self.temp_file = path
        print(f"Audio saved to {path}")
        return path

    def cleanup(self):
        if self.temp_file and os.path.exists(self.temp_file):
            try:
                os.remove(self.temp_file)
            except:
                pass
