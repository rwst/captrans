#!/usr/bin/env python3
"""
German Speech-to-Command Bridge for LeRobot
A PyQt6 application for voice command recognition and translation.
"""
import sys
import io
import json
import os
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QPushButton, 
    QCheckBox, QLineEdit, QListWidget, QGroupBox,
    QHBoxLayout, QVBoxLayout, QLabel
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QByteArray, QBuffer, QIODevice
from PyQt6.QtMultimedia import QAudioInput, QMediaDevices, QAudioFormat
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
    command_sent = pyqtSignal()  # Signal when command is successfully sent
    
    def __init__(self, ngrok_url, is_sending_enabled, parent=None):
        super().__init__(parent)
        self.ngrok_url = ngrok_url
        self.is_sending_enabled = is_sending_enabled
        # TODO: Initialize speech recognition and translation services
        
    def run(self):
        """Main thread execution method."""
        # This method is intentionally left empty as we'll use process_audio directly
        # TODO: Implement any initialization needed for the thread
        pass
        
    def update_config(self, ngrok_url, is_sending_enabled):
        """Update worker configuration."""
        self.ngrok_url = ngrok_url
        self.is_sending_enabled = is_sending_enabled
        
    def process_audio(self, audio_data):
        """Process audio data through STT, translation, and HTTP sending."""
        try:
            # Step 1: Speech-to-Text (German)
            self.status_update.emit("Converting speech to text...")
            german_text = self.speech_to_text(audio_data)
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
                
        except Exception as e:
            self.error_occurred.emit(str(e))
        
    def speech_to_text(self, audio_data):
        """Convert German audio to text."""
        try:
            # Create a speech recognition recognizer
            recognizer = sr.Recognizer()
            
            # Convert QByteArray to BytesIO for speech recognition
            audio_bytes = io.BytesIO(audio_data.data())
            
            # TODO: Convert raw audio data to a format compatible with SpeechRecognition
            # For now, we'll create a placeholder AudioData object
            # In a complete implementation, we would convert the raw audio to WAV format
            
            # Create a placeholder AudioData object (this is incomplete)
            # For a working implementation, we would need to properly encode the raw audio
            audio_data_obj = sr.AudioData(audio_bytes.read(), 16000, 2)  # sample rate, sample width
            
            # Recognize speech using Google Speech Recognition
            german_text = recognizer.recognize_google(
                audio_data_obj, 
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
            # If translation fails, return the original text
            self.error_occurred.emit(f"Translation failed: {str(e)}")
            return german_text
        
    def send_command(self, english_text):
        """Send English command to the robot via HTTP POST."""
        try:
            # Prepare the payload
            payload = {
                "command": english_text
            }
            
            # Send POST request to the ngrok URL
            response = requests.post(
                self.ngrok_url,
                json=payload,
                timeout=10  # 10 second timeout
            )
            
            # Check if request was successful
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
        self.ngrok_url = "https://example.ngrok-free.app/command"  # Default URL
        
        # Audio recording variables
        self.audio_input = None
        self.audio_buffer = None
        
        # Load configuration
        self.load_config()
        
        self.init_ui()
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
        self.setGeometry(100, 100, 800, 500)
        
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        
        # Create left pane
        left_pane = QVBoxLayout()
        
        # Microphone button
        self.mic_button = QPushButton("Listen")
        self.mic_button.setCheckable(True)
        self.mic_button.clicked.connect(self.toggle_listening)
        left_pane.addWidget(self.mic_button)
        
        # Sending toggle
        self.send_toggle = QCheckBox("Send commands to robot")
        self.send_toggle.setChecked(self.is_sending_enabled)
        self.send_toggle.stateChanged.connect(self.toggle_sending)
        left_pane.addWidget(self.send_toggle)
        
        # ngrok URL group
        self.url_group = QGroupBox("Target URL")
        url_layout = QHBoxLayout()
        
        self.url_input = QLineEdit()
        self.url_input.setText(self.ngrok_url)
        self.url_input.setReadOnly(True)
        url_layout.addWidget(self.url_input)
        
        self.url_edit_button = QPushButton("Edit")
        self.url_edit_button.clicked.connect(self.toggle_url_edit)
        url_layout.addWidget(self.url_edit_button)
        
        self.url_group.setLayout(url_layout)
        left_pane.addWidget(self.url_group)
        
        # Add left pane to main layout
        main_layout.addLayout(left_pane)
        
        # Create right pane (log view)
        right_pane = QVBoxLayout()
        
        log_label = QLabel("Command Log:")
        right_pane.addWidget(log_label)
        
        self.log_view = QListWidget()
        right_pane.addWidget(self.log_view)
        
        # Add right pane to main layout
        main_layout.addLayout(right_pane)
        
        # Add initial log entry
        self.log_message("Application started")
        
    def init_worker(self):
        """Initialize the worker thread."""
        self.worker_thread = WorkerThread(self.ngrok_url, self.is_sending_enabled)
        
        # Connect worker signals to UI update slots
        self.worker_thread.german_recognized.connect(self.update_german_text)
        self.worker_thread.english_translated.connect(self.update_english_text)
        self.worker_thread.status_update.connect(self.log_message)
        self.worker_thread.error_occurred.connect(self.log_error)
        self.worker_thread.command_sent.connect(self.command_sent)
        
    def toggle_listening(self):
        """Toggle the listening state."""
        if self.mic_button.isChecked():
            self.mic_button.setText("Stop")
            self.mic_button.setStyleSheet("background-color: red")
            self.start_listening()
        else:
            self.mic_button.setText("Listen")
            self.mic_button.setStyleSheet("")
            self.stop_listening()
            
    def start_listening(self):
        """Start audio recording."""
        self.is_listening = True
        self.log_message("Listening for command...")
        
        # Set up audio format
        audio_format = QAudioFormat()
        audio_format.setSampleRate(16000)
        audio_format.setChannelCount(1)
        audio_format.setSampleFormat(QAudioFormat.SampleFormat.Int16)
        
        # Get default audio input device
        audio_device = QMediaDevices.defaultAudioInput()
        if not audio_device.isFormatSupported(audio_format):
            self.log_error("Audio format not supported")
            return
            
        # Create audio input
        self.audio_input = QAudioInput(audio_device, audio_format)
        
        # Create buffer to store audio data
        self.audio_buffer = QBuffer()
        self.audio_buffer.open(QIODevice.OpenModeFlag.WriteOnly)
        
        # Start recording
        self.audio_input.start(self.audio_buffer)
        
    def stop_listening(self):
        """Stop audio recording."""
        self.is_listening = False
        if self.audio_input:
            self.audio_input.stop()
            
        # Get recorded audio data
        if self.audio_buffer:
            self.audio_buffer.close()
            audio_data = self.audio_buffer.data()
            self.log_message("Processing audio...")
            
            # Send audio data to worker thread for processing
            if self.worker_thread:
                self.worker_thread.process_audio(audio_data)
                
        # Clean up
        self.audio_input = None
        self.audio_buffer = None
        
    def toggle_sending(self, state):
        """Toggle whether commands should be sent to the robot."""
        self.is_sending_enabled = (state == Qt.CheckState.Checked.value)
        self.worker_thread.update_config(self.ngrok_url, self.is_sending_enabled)
        self.save_config()
        self.log_message(f"Sending {'enabled' if self.is_sending_enabled else 'disabled'}")
        
    def toggle_url_edit(self):
        """Toggle the edit mode for the ngrok URL."""
        if self.url_input.isReadOnly():
            self.url_input.setReadOnly(False)
            self.url_edit_button.setText("Save")
        else:
            self.ngrok_url = self.url_input.text()
            self.url_input.setReadOnly(True)
            self.url_edit_button.setText("Edit")
            self.worker_thread.update_config(self.ngrok_url, self.is_sending_enabled)
            self.save_config()
            self.log_message(f"Target URL updated: {self.ngrok_url}")
            
    def log_message(self, message):
        """Add a message to the log view."""
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