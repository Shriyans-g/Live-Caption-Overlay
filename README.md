# Live Caption Overlay with Whisper

This project captures system audio (e.g., Zoom calls) on macOS and transcribes it in real-time

### BlackHole Setup
1. Install BlackHole (https://github.com/ExistentialAudio/BlackHole)
2. In Audio MIDI Setup, create a Multi-Output Device with your speakers and BlackHole
3. Set your system output to the Multi-Output Device

## Installation
pip install -r requirements.txt

## Usage
python3 main.py

## Files
- `main.py`: Orchestrates everything
- `audio_capture.py`: Captures system audio
- `transcriber.py`: Whisper transcription
- `overlay.py`: Caption overlay
 