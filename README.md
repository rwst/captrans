# LeRobot Voice Commander

A PyQt6 application for controlling LeRobot with German voice commands.

## Overview

This application provides a graphical interface for capturing German voice commands, translating them to English, and sending them to a LeRobot instance via an ngrok tunnel.

## Features

- Voice command capture via microphone
- German speech-to-text conversion
- German-to-English translation
- Sending commands to LeRobot via HTTP POST
- Command logging and history
- Persistent configuration

## Requirements

- Python 3.7+
- PyQt6
- SpeechRecognition
- deep-translator
- requests

## Installation

1. Create a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. Run the application:
   ```bash
   python main.py
   ```

2. Configure the ngrok URL:
   - Click "Edit" next to the Target URL
   - Enter your ngrok URL
   - Click "Save"

3. Use the microphone:
   - Click "Listen" to start recording
   - Speak a German command
   - Click "Stop" to process the command

4. Toggle command sending:
   - Check "Send commands to robot" to enable sending
   - Uncheck to disable sending (for testing)

## Configuration

The application stores configuration in `config.json`:
```json
{
    "ngrok_url": "https://example.ngrok-free.app/command",
    "send_commands": true
}
```

## Testing

You can test if all dependencies are working correctly:
```bash
python test_dependencies.py
```

## TODO

- Refine audio format conversion for speech recognition
- Implement automatic silence detection (optional)
- Add error handling for network failures
- Improve UI with better styling
- Add voice activity detection
- Add support for offline speech recognition with Vosk