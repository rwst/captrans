# Project Overview

This project is a PyQt6 application that provides a graphical user interface (GUI) for controlling a LeRobot with German voice commands. The application captures audio from a microphone, converts the German speech to text, translates the text to English, and then sends the English command to a LeRobot instance via an ngrok tunnel.

The application is structured with a main GUI thread and a worker thread for handling the long-running tasks of speech recognition, translation, and network requests. This prevents the GUI from freezing during these operations.

## Key Technologies

*   **GUI:** PyQt6
*   **Speech Recognition:** SpeechRecognition library (using Google Speech Recognition)
*   **Translation:** deep-translator library (using Google Translate)
*   **HTTP Requests:** requests library

# Building and Running

## 1. Create a virtual environment

```bash
python3 -m venv venv
source venv/bin/activate # On Windows: venv\Scripts\activate
```

## 2. Install dependencies

```bash
pip install -r requirements.txt
```

## 3. Run the application

```bash
python main.py
```

## 4. Test dependencies

To ensure all dependencies are installed and working correctly, you can run the following command:

```bash
python test_dependencies.py
```

# Development Conventions

*   **Configuration:** The application uses a `config.json` file to store the ngrok URL and a boolean flag for enabling or disabling sending commands to the robot.
*   **Error Handling:** The application has basic error handling for network failures and speech recognition issues. Errors are logged to the GUI.
*   **UI Design:** The UI is built with PyQt6 and is organized into a main window with a left pane for controls and a right pane for logging.
*   **Threading:** A `QThread` worker is used to handle blocking operations like speech recognition, translation, and HTTP requests, ensuring the UI remains responsive.
