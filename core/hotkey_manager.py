import keyboard
import threading
import time
from PyQt6.QtCore import QObject, pyqtSignal
from config import config

class HotkeyManager(QObject):
    # Signals to communicate with the GUI/Main thread
    recording_toggled = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.running = False
        self.thread = None

    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self._listen)
        self.thread.daemon = True
        self.thread.start()

    def _listen(self):
        print(f"Listening for hotkey: {config.hotkey}")
        # We use add_hotkey which is non-blocking, but we need to keep the thread alive
        # or just use the main thread if we weren't using PyQt.
        # Since we are using PyQt, we can't block the main thread with keyboard.wait()
        # But keyboard.add_hotkey runs in a separate thread managed by the library usually,
        # or hooks into the OS.
        
        # However, to be safe and clean with PyQt, let's just use a simple loop or the library's feature.
        # keyboard.add_hotkey is the best way.
        
        try:
            keyboard.add_hotkey(config.hotkey, self._on_hotkey)
            
            # Keep the thread alive
            while self.running:
                time.sleep(0.1)
        except Exception as e:
            print(f"Error in hotkey listener: {e}")
        finally:
            try:
                keyboard.remove_hotkey(config.hotkey)
            except Exception:
                pass

    def _on_hotkey(self):
        print("Hotkey pressed!")
        self.recording_toggled.emit()

    def stop(self):
        self.running = False
        try:
            keyboard.remove_hotkey(config.hotkey)
        except:
            pass
        if self.thread:
            self.thread.join(timeout=1)

hotkey_manager = HotkeyManager()
