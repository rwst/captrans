# CapTrans Project Overview

## Project Description
This is a voice control interface for a robot (likely LeRobot) that runs on Android/Termux. The system captures German speech commands, translates them to English, and sends them to a Google Colab notebook via HTTP requests. This allows voice control of a robot through a cloud-based computing environment.

## Key Components
1. **control.py** - Main application script that:
   - Captures German speech using Termux:API
   - Translates German to English using Google Translate
   - Sends commands to a Google Colab notebook via HTTP POST requests

2. **Dependencies** (requirements.txt):
   - `googletrans==4.0.0-rc1` - For German to English translation
   - `requests` - For HTTP communication with the Colab notebook

## Configuration
The script requires configuration of the `COLAB_URL` variable in `control.py`:
- This should be set to the public ngrok URL provided by your Google Colab notebook
- The placeholder value is: `https://<your-ngrok-subdomain>.ngrok.io/command`

## Usage Workflow
1. User speaks a command in German
2. Termux:API captures and transcribes the speech
3. The German text is translated to English
4. The English command is sent via HTTP POST to the Colab notebook
5. The Colab notebook processes the command to control the robot

## Development Environment
- Designed to run on Android with Termux
- Requires Termux:API plugin for speech-to-text functionality
- Python 3.x with the dependencies listed in requirements.txt

## License
This project is licensed under Creative Commons CC0 1.0 Universal, which means it's effectively in the public domain with no copyright restrictions.

## Important Notes
- The script includes error handling for speech recognition failures, translation issues, and network problems
- There's a continuous loop in the main function for ongoing command processing
- Security considerations: The communication with the Colab notebook should be secured as it controls physical hardware