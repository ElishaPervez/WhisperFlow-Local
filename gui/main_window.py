from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QComboBox, QPushButton, QLineEdit, QSystemTrayIcon, QMessageBox)
from PyQt6.QtCore import Qt, pyqtSlot
from gui.styles import DARK_THEME
from gui.widgets import Card, ParticleBackground
from config import config
from core.model_manager import model_manager
from core.hotkey_manager import hotkey_manager
import sounddevice as sd
from PyQt6.QtWidgets import QCheckBox

from PyQt6.QtWidgets import QGraphicsBlurEffect

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Wispr Flow Clone")
        self.setMinimumSize(500, 600)
        self.setStyleSheet(DARK_THEME)
        
        # Stacked layout for background
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # Main layout is a stack: [Background, Content]
        self.particles = ParticleBackground(self.central_widget)
        self.particles.lower() # Send to back
        
        self.layout = QVBoxLayout(self.central_widget)
        self.layout.setSpacing(25)  # Increased spacing
        self.layout.setContentsMargins(40, 40, 40, 40) # Increased margins
        
        self.cards = [] # Track cards for focus mode
        self.force_quit = False

        self.setup_ui()

    def resizeEvent(self, event):
        self.particles.resize(self.size())
        super().resizeEvent(event)

    def setup_ui(self):
        # Header
        header = QLabel("Wispr Flow Clone")
        header.setObjectName("Title")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter) # Center title
        self.layout.addWidget(header)
        self.layout.addSpacing(10) # Space below title

        # Settings Container (Scrollable if needed, but simple VBox for now)
        # Group Model and Audio into a "Core Settings" section visually?
        # For now, just better spacing is enough.

        # Model Selection Card
        model_card = Card()
        self.cards.append(model_card)
        model_card.hovered.connect(lambda h: self.on_card_hover(h, model_card))
        model_layout = QVBoxLayout(model_card)
        model_layout.setSpacing(15) # Space inside card
        
        # ... (rest of model card setup) ...
        model_label = QLabel("Whisper Model Size")
        self.model_combo = QComboBox()
        self.model_combo.addItems(["tiny", "base", "small", "medium", "large-v3", "distil-large-v3"])
        self.model_combo.setCurrentText(config.model_size)
        self.model_combo.currentTextChanged.connect(self.save_model_setting)
        
        model_layout.addWidget(model_label)
        model_layout.addWidget(self.model_combo)
        
        # Language & Translation
        lang_layout = QHBoxLayout()
        lang_v = QVBoxLayout()
        lang_v.addWidget(QLabel("Language"))
        self.lang_combo = QComboBox()
        languages = ["auto", "en", "es", "fr", "de", "it", "pt", "nl", "ja", "zh", "ru", "ko"]
        self.lang_combo.addItems(languages)
        self.lang_combo.setEditable(True)
        self.lang_combo.setCurrentText(config.language)
        self.lang_combo.currentTextChanged.connect(self.save_lang_setting)
        lang_v.addWidget(self.lang_combo)
        lang_layout.addLayout(lang_v)
        
        # Translation Toggle
        self.translate_check = QCheckBox("Translate to English")
        self.translate_check.setChecked(config.translate_to_english)
        self.translate_check.toggled.connect(self.save_translate_setting)
        lang_layout.addWidget(self.translate_check)
        
        model_layout.addLayout(lang_layout)

        
        # VRAM Controls
        vram_layout = QHBoxLayout()
        self.unload_check = QCheckBox("Unload Model after use")
        self.unload_check.setChecked(config.unload_model)
        self.unload_check.toggled.connect(self.save_unload_setting)
        vram_layout.addWidget(self.unload_check)
        
        self.free_vram_btn = QPushButton("Free VRAM Now")
        self.free_vram_btn.setObjectName("SecondaryButton")
        self.free_vram_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.free_vram_btn.clicked.connect(self.manual_free_vram)
        vram_layout.addWidget(self.free_vram_btn)
        
        model_layout.addLayout(vram_layout)
        
        self.layout.addWidget(model_card)

        # Audio & Hotkey Group (Side by Side?)
        # Vertical is safer for resizing.
        
        audio_card = Card()
        self.cards.append(audio_card)
        audio_card.hovered.connect(lambda h: self.on_card_hover(h, audio_card))
        audio_layout = QVBoxLayout(audio_card)
        audio_layout.setSpacing(10)
        
        audio_layout.addWidget(QLabel("Microphone Device"))
        self.device_combo = QComboBox()
        self.populate_devices()
        self.device_combo.currentIndexChanged.connect(self.save_device_setting)
        audio_layout.addWidget(self.device_combo)
        
        self.save_audio_check = QCheckBox("Save Audio Recordings")
        self.save_audio_check.setChecked(config.save_recordings)
        self.save_audio_check.toggled.connect(self.save_recording_setting)
        audio_layout.addWidget(self.save_audio_check)
        
        self.layout.addWidget(audio_card)

        # Hotkey Card
        hotkey_card = Card()
        self.cards.append(hotkey_card)
        hotkey_card.hovered.connect(lambda h: self.on_card_hover(h, hotkey_card))
        hotkey_layout = QVBoxLayout(hotkey_card)
        hotkey_layout.setSpacing(10)
        
        hotkey_layout.addWidget(QLabel("Global Hotkey"))
        self.hotkey_input = QLineEdit()
        self.hotkey_input.setText(config.hotkey)
        self.hotkey_input.setPlaceholderText("e.g. ctrl+space")
        self.hotkey_input.editingFinished.connect(self.save_hotkey_setting)
        hotkey_layout.addWidget(self.hotkey_input)
        self.layout.addWidget(hotkey_card)

        # AI Post-Processing Card
        ai_card = Card()
        self.cards.append(ai_card)
        ai_card.hovered.connect(lambda h: self.on_card_hover(h, ai_card))
        ai_layout = QVBoxLayout(ai_card)
        ai_layout.setSpacing(10)
        
        ai_label = QLabel("AI Post-Processing (Gemini)")
        ai_label.setStyleSheet("font-weight: bold;")
        ai_layout.addWidget(ai_label)
        
        # Grid for API and Model
        ai_grid = QVBoxLayout()
        
        key_layout = QHBoxLayout()
        key_layout.addWidget(QLabel("API Key:"))
        self.api_key_input = QLineEdit()
        self.api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.api_key_input.setText(config.gemini_api_key)
        self.api_key_input.setPlaceholderText("Paste Gemini API Key here")
        self.api_key_input.editingFinished.connect(self.save_ai_settings)
        key_layout.addWidget(self.api_key_input)
        ai_grid.addLayout(key_layout)
        
        model_ai_layout = QHBoxLayout()
        model_ai_layout.addWidget(QLabel("Model:"))
        self.ai_model_combo = QComboBox()
        self.ai_model_combo.addItems(["gemini-1.5-flash", "gemini-1.5-pro", "gemini-2.0-flash-exp"])
        self.ai_model_combo.setEditable(True)
        self.ai_model_combo.setCurrentText(config.gemini_model)
        self.ai_model_combo.currentTextChanged.connect(self.save_ai_settings)
        model_ai_layout.addWidget(self.ai_model_combo)
        ai_grid.addLayout(model_ai_layout)
        
        ai_layout.addLayout(ai_grid)
        
        self.layout.addWidget(ai_card)

        # Stats Card
        stats_card = Card()
        self.cards.append(stats_card)
        # stats_card.hovered.connect(lambda h: self.on_card_hover(h, stats_card)) # Removed to fix shaking
        stats_layout = QVBoxLayout(stats_card)
        stats_layout.setSpacing(5)
        
        stats_layout.addWidget(QLabel("Statistics"))
        self.last_transcribed_label = QLabel("Last: -")
        self.last_transcribed_label.setWordWrap(True)
        self.last_transcribed_label.setStyleSheet("color: #aaaaaa; font-style: italic;")
        self.time_label = QLabel("Time: -")
        self.time_label.setStyleSheet("color: #aaaaaa;")
        
        stats_layout.addWidget(self.last_transcribed_label)
        stats_layout.addWidget(self.time_label)
        self.layout.addWidget(stats_card)

        # Buttons
        btn_layout = QHBoxLayout()
        self.hide_btn = QPushButton("Hide to Tray")
        self.hide_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.hide_btn.clicked.connect(self.hide)
        
        self.quit_btn = QPushButton("Quit")
        self.quit_btn.setObjectName("SecondaryButton")
        self.quit_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.quit_btn.clicked.connect(self.close_app)
        
        btn_layout.addStretch()
        btn_layout.addWidget(self.hide_btn)
        btn_layout.addWidget(self.quit_btn)
        self.layout.addLayout(btn_layout)
        
        self.layout.addStretch()

    # Hover effect removed to prevent layout instability (shaking)
    # def on_card_hover(self, hovered, target_card):
    #     ...

    def manual_free_vram(self):
        from core.transcriber import transcriber
        transcriber.unload_model()
        self.update_stats("VRAM Freed Manually", 0.0)



    def populate_devices(self):
        devices = sd.query_devices()
        default_input = sd.default.device[0]
        
        self.device_combo.addItem("Default", -1)
        
        for i, device in enumerate(devices):
            if device['max_input_channels'] > 0:
                self.device_combo.addItem(f"{device['name']}", i)
                if config.input_device_index == i:
                    self.device_combo.setCurrentIndex(self.device_combo.count() - 1)

    def save_model_setting(self, text):
        config.model_size = text
        config.save()

    def save_lang_setting(self, text):
        config.language = text
        config.save()

    def save_translate_setting(self, checked):
        config.translate_to_english = checked
        config.save()

    def save_unload_setting(self, checked):
        config.unload_model = checked
        config.save()
    
    def save_recording_setting(self, checked):
        config.save_recordings = checked
        config.save()

    def save_ai_settings(self):
        config.gemini_api_key = self.api_key_input.text().strip()
        config.gemini_model = self.ai_model_combo.currentText().strip()
        config.save()
        # Re-configure formatter
        from core.gemini_formatter import gemini_formatter
        gemini_formatter.configure()



    def save_device_setting(self, index):
        data = self.device_combo.currentData()
        config.input_device_index = data
        config.save()

    def save_hotkey_setting(self):
        new_hotkey = self.hotkey_input.text().strip()
        # Basic validation: Hotkeys shouldn't be super long or contain newlines
        if new_hotkey and len(new_hotkey) < 30 and "\n" not in new_hotkey:
            config.hotkey = new_hotkey
            config.save()
            # Restart hotkey listener
            hotkey_manager.stop()
            hotkey_manager.start()
        else:
            # Revert to previous valid hotkey if invalid
            self.hotkey_input.setText(config.hotkey)

    def update_stats(self, text, duration):
        # Truncate text if too long
        display_text = text[:100] + "..." if len(text) > 100 else text
        self.last_transcribed_label.setText(f"Last: {display_text}")
        self.time_label.setText(f"Time: {duration:.2f}s")

    def close_app(self):
        self.force_quit = True
        self.close()

    def closeEvent(self, event):
        if self.force_quit:
            event.accept()
        else:
            # Minimize to tray instead of closing
            event.ignore()
            self.hide()
            
            # Optional: Show a notification the first time?
            # For now, just hiding is standard behavior for this type of app.
