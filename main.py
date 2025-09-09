#!/usr/bin/env python3
"""
German Speech-to-Command Bridge for LeRobot
A PyQt6 application for voice command recognition and translation.
"""
import sys
import io
import json
import os
import wave
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QPushButton,
    QCheckBox, QLineEdit, QListWidget, QGroupBox,
    QHBoxLayout, QVBoxLayout, QLabel, QMessageBox
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QBuffer, QIODevice
from PyQt6.QtMultimedia import QMediaDevices, QAudioFormat, QAudioSource
import speech_recognition as sr
from deep_translator import GoogleTranslator
import requests


class WorkerThread(QThread):
    """Worker thread for handling audio processing, STT, translation, and HTTP requests."""

    # Signals for communicating with the main thread
    german_recognized = pyqtSignal(str)
    english_translated = pyqtSignal(str)
    status_update = pyqtSignal(str)
    error_occurred = pyqtSignal(str)
    command_sent = pyqtSignal()

    def __init__(self, ngrok_url, is_sending_enabled, parent=None):
        super().__init__(parent)
        self.ngrok_url = ngrok_url
        self.is_sending_enabled = is_sending_enabled
        self.recognizer = sr.Recognizer()

    def update_config(self, ngrok_url, is_sending_enabled):
        """Update worker configuration."""
        self.ngrok_url = ngrok_url
        self.is_sending_enabled = is_sending_enabled

    def process_audio(self, audio_data, sample_rate, sample_width):
        """Process audio data through STT, translation, and HTTP sending."""
        try:
            # Step 1: Speech-to-Text (German)
            self.status_update.emit("Converting speech to text...")
            german_text = self.speech_to_text(audio_data, sample_rate, sample_width)
            if german_text:
                self.german_recognized.emit(german_text)

                # Step 2: Translation (German to English)
                self.status_update.emit("Translating text...")
                english_text = self.translate_text(german_text)
                self.english_translated.emit(english_text)

                # Step 3: Send command via HTTP if enabled
                if self.is_sending_enabled:
                    self.status_update.emit("Sending command to robot...")
                    self.send_command(english_text)
                    self.command_sent.emit()
                else:
                    self.status_update.emit("Command processing complete (not sent)")
            else:
                self.error_occurred.emit("Speech recognition returned empty text.")

        except Exception as e:
            self.error_occurred.emit(str(e))

    def speech_to_text(self, audio_data, sample_rate, sample_width):
        """Convert German audio to text."""
        try:
            # The audio_data from PyQt is raw. We need to convert it to a WAV format in-memory
            # for the SpeechRecognition library to process it correctly.
            audio_bytes = io.BytesIO()
            with wave.open(audio_bytes, 'wb') as wf:
                wf.setnchannels(1)  # Mono
                wf.setsampwidth(sample_width)
                wf.setframerate(sample_rate)
                wf.writeframes(audio_data.data())

            audio_bytes.seek(0)

            with sr.AudioFile(audio_bytes) as source:
                audio = self.recognizer.record(source)

            # Recognize speech using Google Speech Recognition
            german_text = self.recognizer.recognize_google(
                audio,
                language="de-DE"
            )
            return german_text
        except sr.UnknownValueError:
            raise Exception("Speech could not be understood")
        except sr.RequestError as e:
            raise Exception(f"Could not request results from Google Speech Recognition service; {e}")
        except Exception as e:
            raise Exception(f"Speech recognition failed: {str(e)}")

    def translate_text(self, german_text):
        """Translate German text to English."""
        try:
            translator = GoogleTranslator(source='de', target='en')
            english_text = translator.translate(german_text)
            return english_text
        except Exception as e:
            self.error_occurred.emit(f"Translation failed: {str(e)}")
            return german_text

    def send_command(self, english_text):
        """Send English command to the robot via HTTP POST."""
        try:
            payload = {"command": english_text}
            response = requests.post(self.ngrok_url, json=payload, timeout=10)
            if response.status_code != 200:
                raise Exception(f"HTTP {response.status_code}: {response.text}")
        except requests.exceptions.RequestException as e:
            raise Exception(f"Network error: {str(e)}")
        except Exception as e:
            raise Exception(f"Failed to send command: {str(e)}")


class MainWindow(QMainWindow):
    """Main application window with UI elements and controller logic."""

    def __init__(self):
        super().__init__()
        self.worker_thread = None
        self.is_listening = False
        self.is_sending_enabled = True
        self.ngrok_url = "https://example.ngrok-free.app/command"

        self.audio_source = None
        self.audio_buffer = None
        self.audio_devices = []
        self.audio_format = None

        self.load_config()
        self.init_ui()
        self.check_audio_devices() # Check for devices on startup
        self.init_worker()

    def load_config(self):
        """Load configuration from config.json file."""
        try:
            if os.path.exists("config.json"):
                with open("config.json", "r") as f:
                    config = json.load(f)
                    self.ngrok_url = config.get("ngrok_url", self.ngrok_url)
                    self.is_sending_enabled = config.get("send_commands", self.is_sending_enabled)
        except Exception as e:
            self.log_error(f"Failed to load config: {str(e)}")

    def save_config(self):
        """Save configuration to config.json file."""
        try:
            config = {
                "ngrok_url": self.ngrok_url,
                "send_commands": self.is_sending_enabled
            }
            with open("config.json", "w") as f:
                json.dump(config, f, indent=4)
        except Exception as e:
            self.log_error(f"Failed to save config: {str(e)}")

    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("LeRobot Voice Commander")
        self.setGeometry(100, 100, 1200, 500)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        left_pane = QVBoxLayout()

        self.send_toggle = QCheckBox("Send commands to robot")
        self.send_toggle.setChecked(self.is_sending_enabled)
        self.send_toggle.stateChanged.connect(self.toggle_sending)
        left_pane.addWidget(self.send_toggle)

        self.url_group = QGroupBox("Target URL")
        self.url_group.setAlignment(Qt.AlignmentFlag.AlignTop)
        url_layout = QHBoxLayout()

        self.url_input = QLineEdit(self.ngrok_url)
        self.url_input.setReadOnly(True)
        url_layout.addWidget(self.url_input)

        self.url_edit_button = QPushButton("Edit")
        self.url_edit_button.clicked.connect(self.toggle_url_edit)
        url_layout.addWidget(self.url_edit_button)

        self.url_group.setLayout(url_layout)
        left_pane.addWidget(self.url_group)
        self.url_group.setEnabled(self.is_sending_enabled)

        left_pane.addStretch()

        self.mic_button = QPushButton("Listen")
        self.mic_button.setCheckable(True)
        self.mic_button.clicked.connect(self.toggle_listening)
        self.mic_button.setFixedSize(100, 100)

        button_container = QWidget()
        button_layout = QHBoxLayout(button_container)
        button_layout.addWidget(self.mic_button)
        button_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        left_pane.addWidget(button_container)

        left_pane.addStretch()
        main_layout.addLayout(left_pane)

        right_pane = QVBoxLayout()
        right_pane.addWidget(QLabel("Command Log:"))
        self.log_view = QListWidget()
        right_pane.addWidget(self.log_view)
        main_layout.addLayout(right_pane)

        self.log_message("Application started")

    def check_audio_devices(self):
        """Check for available audio input devices and log them."""
        self.audio_devices = QMediaDevices.audioInputs()
        if not self.audio_devices:
            self.log_error("No audio input devices found.")
            QMessageBox.critical(self, "Microphone Error", "No microphone was detected on this system. The application cannot record audio.")
            self.mic_button.setEnabled(False)
        else:
            self.log_message("Available audio input devices:")
            for device in self.audio_devices:
                self.log_message(f"- {device.description()}")

    def init_worker(self):
        """Initialize the worker thread."""
        self.worker_thread = WorkerThread(self.ngrok_url, self.is_sending_enabled)
        self.worker_thread.german_recognized.connect(self.update_german_text)
        self.worker_thread.english_translated.connect(self.update_english_text)
        self.worker_thread.status_update.connect(self.log_message)
        self.worker_thread.error_occurred.connect(self.log_error)
        self.worker_thread.command_sent.connect(self.command_sent)

    def toggle_listening(self):
        """Toggle the listening state."""
        if self.mic_button.isChecked():
            self.start_listening()
        else:
            self.stop_listening()

    def start_listening(self):
        """Start audio recording."""
        if not self.audio_devices:
            self.log_error("Cannot start listening, no audio device found.")
            self.mic_button.setChecked(False)
            return

        self.mic_button.setText("Stop")
        self.mic_button.setStyleSheet("background-color: red; border-radius: 5px;")
        self.is_listening = True
        self.log_message("Listening for command...")

        self.audio_format = QAudioFormat()
        self.audio_format.setSampleRate(16000)
        self.audio_format.setChannelCount(1)
        self.audio_format.setSampleFormat(QAudioFormat.SampleFormat.Int16)

        audio_device = QMediaDevices.defaultAudioInput()
        if audio_device.isNull() or not audio_device.isFormatSupported(self.audio_format):
            self.log_message("Default audio device not suitable, searching for another...")
            found_device = False
            for device in self.audio_devices:
                if device.isFormatSupported(self.audio_format):
                    audio_device = device
                    self.log_message(f"Using device: {device.description()}")
                    found_device = True
                    break
            if not found_device:
                self.log_error("No audio device supports the required format (16kHz, 16-bit, Mono).")
                self.stop_listening()
                return

        try:
            # FIX: Use QAudioSource instead of QAudioInput
            self.audio_source = QAudioSource(audio_device, self.audio_format, self)

            self.audio_buffer = QBuffer()
            self.audio_buffer.open(QIODevice.OpenModeFlag.WriteOnly)

            # FIX: Start the audio source with the buffer
            self.audio_source.start(self.audio_buffer)

        except Exception as e:
            self.log_error(f"Failed to start audio recording: {e}")
            self.stop_listening()

    def stop_listening(self):
        """Stop audio recording and process the data."""
        self.mic_button.setText("Listen")
        self.mic_button.setStyleSheet("")
        self.mic_button.setChecked(False)
        self.is_listening = False

        # FIX: Use self.audio_source.stop()
        if self.audio_source:
            self.audio_source.stop()

        if self.audio_buffer and self.audio_buffer.isOpen():
            self.audio_buffer.close()
            audio_data = self.audio_buffer.data()
            if audio_data:
                self.log_message("Processing audio...")
                sample_rate = self.audio_format.sampleRate()
                sample_width = self.audio_format.bytesPerSample()
                if self.worker_thread:
                    self.worker_thread.process_audio(audio_data, sample_rate, sample_width)
            else:
                self.log_error("No audio data was recorded.")

        self.audio_source = None
        self.audio_buffer = None

    def toggle_sending(self, state):
        """Toggle whether commands should be sent."""
        self.is_sending_enabled = (state == Qt.CheckState.Checked.value)
        self.worker_thread.update_config(self.ngrok_url, self.is_sending_enabled)
        self.save_config()
        self.log_message(f"Sending {'enabled' if self.is_sending_enabled else 'disabled'}")
        self.url_group.setEnabled(self.is_sending_enabled)

    def toggle_url_edit(self):
        """Toggle the edit mode for the ngrok URL."""
        if self.url_input.isReadOnly():
            self.url_input.setReadOnly(False)
            self.url_edit_button.setText("Save")
            self.url_input.setFocus()
        else:
            self.ngrok_url = self.url_input.text()
            self.url_input.setReadOnly(True)
            self.url_edit_button.setText("Edit")
            self.worker_thread.update_config(self.ngrok_url, self.is_sending_enabled)
            self.save_config()
            self.log_message(f"Target URL updated: {self.ngrok_url}")

    def log_message(self, message):
        """Add an info message to the log view."""
        self.log_view.addItem(f"[INFO] {message}")
        self.log_view.scrollToBottom()

    def log_error(self, error_message):
        """Add an error message to the log view."""
        self.log_view.addItem(f"[ERROR] {error_message}")
        self.log_view.scrollToBottom()

    def update_german_text(self, text):
        """Update UI with recognized German text."""
        self.log_view.addItem(f'[DE] "{text}"')
        self.log_view.scrollToBottom()

    def update_english_text(self, text):
        """Update UI with translated English text."""
        self.log_view.addItem(f'[EN] "{text}"')
        self.log_view.scrollToBottom()

    def command_sent(self):
        """Update UI when command is successfully sent."""
        self.log_view.addItem("[SEND] Command sent successfully.")
        self.log_view.scrollToBottom()

def main():
    """Main application entry point."""
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
