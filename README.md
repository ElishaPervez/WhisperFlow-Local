# 🎙️ Whisper Flow Dictation

A powerful, local speech-to-text application inspired by Wispr Flow. This tool allows you to dictate text anywhere on your computer using a global hotkey, with high-accuracy local transcription and intelligent AI post-processing.

## ✨ Features

*   **🚀 Local Transcription:** Uses `faster-whisper` for fast, private, and accurate speech-to-text on your own hardware (GPU recommended).
*   **🧠 AI Post-Processing:** Integrates with **Google Gemini** to fix punctuation, capitalization, and grammar, making your dictation read naturally.
*   **⌨️ Global Hotkey:** Toggle recording from any application (Default: `Ctrl+Shift+Space`).
*   **🌐 Auto-Translation:** Option to translate spoken foreign languages directly into English.
*   **🎨 Modern GUI:** Clean PyQt6 interface with a system tray icon and a floating visualizer overlay while recording.
*   **💾 Save Recordings:** Optional setting to archive your raw audio files.
*   **⚡ VRAM Management:** Options to unload models after use to free up GPU memory.

## 🛠️ Installation

### Prerequisites
*   **OS:** Windows 10/11
*   **Python:** 3.10 or higher (3.12 recommended)
*   **Hardware:** NVIDIA GPU with CUDA is highly recommended for speed, though CPU execution is supported.

### Steps

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/yourusername/whisper-dictation.git
    cd whisper-dictation
    ```

2.  **Install Dependencies:**
    Run the provided batch script to install all required Python packages globally:
    ```cmd
    install_global.bat
    ```
    *Alternatively, you can install manually:*
    ```bash
    pip install -r requirements.txt
    ```

3.  **Install FFmpeg:**
    Ensure `ffmpeg` is installed and added to your system PATH (Required for audio processing).

## 🚀 Usage

1.  **Start the Application:**
    Run the startup script:
    ```cmd
    run.bat
    ```
    *Note: The script may request Administrator privileges to enable global hotkey detection.*

2.  **Configuration:**
    *   **Model:** Select a Whisper model size (e.g., `distil-large-v3` for speed/accuracy balance).
    *   **Microphone:** Select your input device.
    *   **AI Post-Processing:** Enter your [Google Gemini API Key](https://aistudio.google.com/app/apikey) to enable smart formatting (highly recommended).

3.  **Dictate:**
    *   Place your cursor in any text field.
    *   Press `Ctrl+Shift+Space` (or your custom hotkey).
    *   Speak clearly.
    *   Press the hotkey again to stop.
    *   The transcribed and formatted text will be pasted automatically.

## 📂 Project Structure

*   `main.py`: Entry point and controller logic.
*   `core/`: Backend logic (Audio recording, Transcriber, Gemini Formatter).
*   `gui/`: PyQt6 interface elements (Main Window, Tray, Visualizer).
*   `models/`: Directory where Whisper models are downloaded (ignored by git).
*   `config.json`: Stores user settings (ignored by git).

## 🛡️ Privacy & Security

*   **Audio:** Your voice is processed locally on your machine by Whisper. Audio is never sent to the cloud for transcription.
*   **Text:** If AI Post-Processing is enabled, the *transcribed text* is sent to Google Gemini for formatting. If disabled, everything remains 100% local.
*   **Keys:** Your API keys are stored locally in `config.json`.

## 📄 License

MIT License. Feel free to modify and distribute.
