#!/usr/bin/env python3
"""
Test script to verify that all required dependencies are installed and working.
"""

def test_pyqt6():
    """Test PyQt6 installation."""
    try:
        from PyQt6.QtWidgets import QApplication
        from PyQt6.QtCore import Qt
        print("✓ PyQt6: OK")
        return True
    except ImportError as e:
        print(f"✗ PyQt6: {e}")
        return False

def test_speech_recognition():
    """Test SpeechRecognition library."""
    try:
        import speech_recognition as sr
        print("✓ SpeechRecognition: OK")
        return True
    except ImportError as e:
        print(f"✗ SpeechRecognition: {e}")
        return False

def test_deep_translator():
    """Test deep-translator library."""
    try:
        from deep_translator import GoogleTranslator
        # Test translation
        translator = GoogleTranslator(source='de', target='en')
        result = translator.translate("Hallo")
        print("✓ deep-translator: OK")
        return True
    except Exception as e:
        print(f"✗ deep-translator: {e}")
        return False

def test_requests():
    """Test requests library."""
    try:
        import requests
        print("✓ requests: OK")
        return True
    except ImportError as e:
        print(f"✗ requests: {e}")
        return False

def main():
    """Run all tests."""
    print("Testing dependencies...")
    print()
    
    all_passed = True
    all_passed &= test_pyqt6()
    all_passed &= test_speech_recognition()
    all_passed &= test_deep_translator()
    all_passed &= test_requests()
    
    print()
    if all_passed:
        print("All dependencies are installed and working correctly!")
        return 0
    else:
        print("Some dependencies are missing or not working properly.")
        return 1

if __name__ == "__main__":
    exit(main())