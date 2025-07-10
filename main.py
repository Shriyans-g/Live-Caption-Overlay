import sys
import threading
import signal
from audio_capture import SystemAudioStream
from transcriber import WhisperTranscriber
from overlay import CaptionOverlay
from PyQt5 import QtWidgets
import PyQt5.QtCore as QtCore

class CaptionApp:
    def __init__(self):
        self.app = QtWidgets.QApplication(sys.argv)
        self.overlay = CaptionOverlay()
        self.audio_stream = SystemAudioStream()
        self.transcriber = WhisperTranscriber(self.on_new_caption)
        self.running = True
        self.audio_thread = threading.Thread(target=self.audio_loop, daemon=True)
        self.paused = False
        self.overlay.set_pause_callback(self.toggle_pause)

    def toggle_pause(self, paused):
        self.paused = paused

    def on_new_caption(self, text):
        if not self.paused:
            self.overlay.set_caption(text)

    def audio_loop(self):
        self.audio_stream.start()
        while self.running:
            audio_chunk = self.audio_stream.read_chunk()
            self.transcriber.add_audio(audio_chunk)
        self.audio_stream.close()

    def run(self):
        self.transcriber.start()
        self.audio_thread.start()
        signal.signal(signal.SIGINT, self.stop)
        self.app.exec_()
        self.stop()

    def stop(self, *args):
        self.running = False
        self.transcriber.stop()
        self.audio_stream.close()
        sys.exit(0)

if __name__ == '__main__':
    app = CaptionApp()
    app.run() 