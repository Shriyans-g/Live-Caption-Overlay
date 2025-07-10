import threading
import queue
import numpy as np
import whisper

class WhisperTranscriber:
    def __init__(self, callback, model_name='base', rate=16000, chunk_duration=2.0):
        self.callback = callback
        self.model = whisper.load_model(model_name)
        self.rate = rate
        self.chunk_samples = int(rate * chunk_duration)
        self.audio_buffer = np.zeros(0, dtype=np.int16)
        self.audio_queue = queue.Queue()
        self.running = False
        self.thread = threading.Thread(target=self._run, daemon=True)

    def add_audio(self, audio_chunk):
        self.audio_queue.put(audio_chunk)

    def start(self):
        self.running = True
        self.thread.start()

    def stop(self):
        self.running = False
        self.thread.join()

    def _run(self):
        while self.running:
            try:
                audio_chunk = self.audio_queue.get(timeout=0.1)
                self.audio_buffer = np.concatenate([self.audio_buffer, audio_chunk])
                while len(self.audio_buffer) >= self.chunk_samples:
                    chunk = self.audio_buffer[:self.chunk_samples]
                    self.audio_buffer = self.audio_buffer[self.chunk_samples:]
                    # Whisper expects float32 in range [-1, 1]
                    audio_float = chunk.astype(np.float32) / 32768.0
                    result = self.model.transcribe(audio_float, language='en', fp16=False, verbose=False)
                    text = result.get('text', '').strip()
                    if text:
                        self.callback(text)
            except queue.Empty:
                continue 