import subprocess
import json
import requests
from googletrans import Translator

# --- CONFIGURATION ---
# IMPORTANT: Replace this URL with the public ngrok URL printed by your Colab notebook.
COLAB_URL = "https://<your-ngrok-subdomain>.ngrok.io/command"

def capture_speech_german():
    """
    Uses Termux:API to capture speech and returns the transcribed text.
    Returns None if speech recognition fails or is empty.
    """
    print("\n🎤 Listening for German command...")
    try:
        # Execute the termux-speech-to-text command
        result = subprocess.run(
            ['termux-speech-to-text'],
            capture_output=True,
            text=True,
            check=True  # This will raise an exception if the command fails
        )
        # The transcribed text is in stdout
        transcribed_text = result.stdout.strip()
        if transcribed_text:
            print(f"   Recognized (German): '{transcribed_text}'")
            return transcribed_text
        else:
            print("   -> No speech detected or recognition was empty.")
            return None
    except subprocess.CalledProcessError as e:
        # This can happen if the user cancels the speech recognition dialog
        print(f"   -> Speech recognition cancelled or failed. Error: {e}")
        return None
    except FileNotFoundError:
        print("   -> ERROR: 'termux-speech-to-text' not found. Is Termux:API installed?")
        return None

def translate_to_english(text):
    """
    Translates the given text from German to English.
    Returns None if translation fails.
    """
    if not text:
        return None
    print("   Translating to English...")
    try:
        translator = Translator()
        translation = translator.translate(text, src='de', dest='en')
        translated_text = translation.text
        print(f"   Translated (English): '{translated_text}'")
        return translated_text
    except Exception as e:
        print(f"   -> Translation failed. Error: {e}")
        return None

def send_command_to_colab(command):
    """
    Sends the command to the Google Colab server via an HTTP POST request.
    Returns True on success, False on failure.
    """
    if not command:
        return False
    print(f"   Sending command to Colab at {COLAB_URL}...")
    try:
        payload = {"command": command}
        headers = {"Content-Type": "application/json"}
        response = requests.post(COLAB_URL, json=payload, headers=headers, timeout=10)

        # Check for a successful response from the server
        if response.status_code == 200:
            print("✅ Command sent successfully!")
            return True
        else:
            print(f"   -> Error: Server responded with status code {response.status_code}")
            print(f"   -> Response: {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"   -> Network error: Could not send command. Is the Colab server running and the URL correct?")
        print(f"   -> Details: {e}")
        return False

def main():
    """Main loop to continuously listen, translate, and send commands."""
    print("--- Android Voice Control for LeRobot ---")
    if "your-ngrok-subdomain" in COLAB_URL:
        print("\n⚠️ WARNING: Please edit this script and replace the placeholder COLAB_URL.")
        return

    while True:
        german_text = capture_speech_german()
        if german_text:
            english_command = translate_to_english(german_text)
            if english_command:
                send_command_to_colab(english_command)

if __name__ == "__main__":
    main()
