import os
import sys
import warnings

# Suppress annoying pkg_resources deprecation warning from ctranslate2/faster-whisper
warnings.filterwarnings("ignore", category=UserWarning, module="ctranslate2")
# Also suppress specific message if module filtering isn't enough
warnings.filterwarnings("ignore", message=".*pkg_resources is deprecated.*")

# Pre-load torch to prevent DLL errors
import torch
import time
import threading

# Enable fast downloads
os.environ["HF_HUB_ENABLE_HF_TRANSFER"] = "1"

import keyboard
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot

from config import config
from core.audio_recorder import AudioRecorder
from core.transcriber import transcriber
from core.hotkey_manager import hotkey_manager
from core.gemini_formatter import gemini_formatter
from gui.main_window import MainWindow
from gui.system_tray import SystemTray
from gui.widgets import VisualizerOverlay
import shutil
from datetime import datetime

class ApplicationController(QObject):
    stats_updated = pyqtSignal(str, float)
    paste_request = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.app = QApplication(sys.argv)
        self.app.setQuitOnLastWindowClosed(False)
        
        # Status State
        self.status = "Ready"
        self.last_action = "Initialized"
        
        # Initialize formatter
        gemini_formatter.configure()
        
        self.main_window = MainWindow()
        self.tray = SystemTray(self.main_window)
        self.overlay = VisualizerOverlay()
        
        self.recorder = AudioRecorder()
        self.recorder.level_updated.connect(self.overlay.set_level)
        
        # Connect signals
        hotkey_manager.recording_toggled.connect(self.toggle_recording)
        self.stats_updated.connect(self.main_window.update_stats)
        self.paste_request.connect(self.inject_text)
        
        # Start hotkey listener
        hotkey_manager.start()
        
        # Show main window initially
        self.main_window.show()
        self.print_status()

    def print_status(self):
        # Clear line and print status
        # \033[K clears to end of line, \r returns to start
        sys.stdout.write(f"\r\033[K[{datetime.now().strftime('%H:%M:%S')}] Status: {self.status} | Last Action: {self.last_action}")
        sys.stdout.flush()

    @pyqtSlot()
    def toggle_recording(self):
        if self.recorder.recording:
            self.stop_recording()
        else:
            self.start_recording()

    def start_recording(self):
        self.status = "Recording..."
        self.last_action = "Started Recording"
        self.print_status()
        
        self.recorder.start()
        
        # Show overlay at bottom center
        screen_geo = self.app.primaryScreen().geometry()
        self.overlay.move(
            screen_geo.center().x() - self.overlay.width() // 2,
            screen_geo.bottom() - 150 # 150px from bottom
        )
        self.overlay.show()

    def stop_recording(self):
        self.status = "Processing..."
        self.last_action = "Stopped Recording"
        self.print_status()
        self.overlay.hide()
        
        # Stop recorder and get audio path
        audio_path = self.recorder.stop()
        
        if audio_path:
            # Run transcription in a separate thread
            threading.Thread(target=self.process_audio, args=(audio_path,)).start()

    def process_audio(self, audio_path):
        start_time = time.time()
        try:
            self.status = "Transcribing..."
            self.print_status()
            
            text = transcriber.transcribe(audio_path)
            
            if text:
                self.status = "Formatting..."
                self.print_status()
                
                # Advanced formatting with Gemini
                formatted_text = gemini_formatter.format_text(text)
                
                # Fallback
                if formatted_text == text:
                    text = self.smart_format(text)
                else:
                    text = formatted_text

                duration = time.time() - start_time
                
                self.last_action = f"Transcribed ({duration:.2f}s)"
                self.status = "Ready"
                self.print_status()
                
                self.paste_request.emit(text)
                self.stats_updated.emit(text, duration)
            else:
                 self.status = "Ready"
                 self.last_action = "No speech detected"
                 self.print_status()
            
        except Exception as e:
            self.status = "Error"
            self.last_action = f"Error: {str(e)[:50]}"
            self.print_status()
        finally:
            # Handle file cleanup or saving
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
        # Basic cleanup
        text = text.strip()
        # Capitalize first letter
        if text and text[0].islower():
            text = text[0].upper() + text[1:]
        return text

    @pyqtSlot(str)
    def inject_text(self, text):
        # ... existing logic ...
        try:
            clipboard = self.app.clipboard()
            clipboard.setText(text)
            time.sleep(0.1)
            keyboard.send('ctrl+v')
        except Exception as e:
            # Fallback to typing if paste fails
            try:
                keyboard.write(text)
            except:
                pass

    def run(self):
        print("Wispr Flow Clone Started. Press Ctrl+C to quit.")
        print(f"Global Hotkey: {config.hotkey}")
        self.print_status()
        sys.exit(self.app.exec())

if __name__ == "__main__":
    controller = ApplicationController()
    controller.run()
