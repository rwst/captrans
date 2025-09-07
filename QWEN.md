# LeRobot Voice Commander - Project Context

## Project Overview

This is a PyQt6 application called "LeRobot Voice Commander" that enables controlling a LeRobot instance using German voice commands. The application captures audio from the microphone, converts German speech to text, translates it to English, and sends the command to a LeRobot instance via an HTTP POST request through an ngrok tunnel.

### Key Features
- Voice command capture via microphone
- German speech-to-text conversion
- German-to-English translation
- Sending commands to LeRobot via HTTP POST
- Command logging and history
- Persistent configuration

### Technologies Used
- Python 3.7+
- PyQt6 (GUI framework)
- SpeechRecognition library (for speech-to-text)
- deep-translator library (for translation)
- requests library (for HTTP communication)

## Project Structure

```
.
├── main.py                 # Main application entry point
├── requirements.txt        # Python dependencies
├── config.json             # Application configuration
├── test_dependencies.py    # Dependency testing script
├── README.md               # Project documentation
├── pyqt-plan.md            # Development plan and implementation details
└── LICENSE                 # CC0 1.0 Universal license
```

## Core Components

### Main Application (main.py)
- `MainWindow`: Main application window with UI elements and controller logic
- `WorkerThread`: Worker thread for handling audio processing, speech-to-text, translation, and HTTP requests
- Audio recording using `QAudioInput` and `QMediaDevices`
- UI with microphone button, sending toggle, URL configuration, and command log

### Configuration (config.json)
```json
{
    "ngrok_url": "https://example.ngrok-free.app/command",
    "send_commands": true
}
```

## Development and Usage

### Installation
1. Create a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\\Scripts\\activate
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Running the Application
```bash
python main.py
```

### Testing Dependencies
```bash
python test_dependencies.py
```

## Development Notes

### UI Design
- Left pane contains controls:
  - Microphone button ("Listen"/"Stop")
  - Sending toggle ("Send commands to robot")
  - Target URL group with editable URL field
- Right pane contains command log showing:
  - Informational messages
  - Recognized German text
  - Translated English text
  - Command sending status

### Implementation Details
- Uses PyQt6.QtMultimedia for audio recording
- Offloads processing to a worker thread to prevent UI freezing
- Implements custom signals for thread communication
- Supports configuration persistence via JSON file
- Uses Google Speech Recognition for STT and Google Translate for translation

### Planned Improvements
- Refine audio format conversion for speech recognition
- Implement automatic silence detection
- Add error handling for network failures
- Improve UI with better styling
- Add voice activity detection
- Add support for offline speech recognition with Vosk

## Dependencies

- PyQt6>=6.0.0
- SpeechRecognition>=3.8.1
- deep-translator>=1.4.0
- requests>=2.25.0

## License

This project is licensed under the Creative Commons CC0 1.0 Universal license, effectively placing it in the public domain.