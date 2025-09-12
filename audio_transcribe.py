#!/usr/bin/env python3

import speech_recognition as sr
import argparse
from os import path

# set up argument parser
parser = argparse.ArgumentParser(description="Transcribe an audio file.")
parser.add_argument(
    "--file",
    "-f",
    default=path.join(path.dirname(path.realpath(__file__)), "english.wav"),
    help="Path to the audio file to transcribe.",
)
args = parser.parse_args()
AUDIO_FILE = args.file
audio = sr.AudioData.from_file(AUDIO_FILE)

r = sr.Recognizer()

# recognize speech using Google Cloud Speech
# Before run, create local authentication credentials (``gcloud auth application-default login``)
try:
    print("Google Cloud Speech thinks you said " + r.recognize_google_cloud(audio, language_code="de-DE", model="command_and_search"))
except sr.UnknownValueError:
    print("Google Cloud Speech could not understand audio")
except sr.RequestError as e:
    print("Could not request results from Google Cloud Speech service; {0}".format(e))

