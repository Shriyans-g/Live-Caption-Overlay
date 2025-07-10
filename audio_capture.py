import pyaudio
import numpy as np

class SystemAudioStream:
    def __init__(self, device_name='BlackHole 2ch', rate=16000, chunk=1024):
        self.p = pyaudio.PyAudio()
        self.rate = rate
        self.chunk = chunk
        self.device_index = self._find_device_index(device_name)
        if self.device_index is None:
            raise RuntimeError(f'Audio device "{device_name}" not found.')
        self.stream = None

    def _find_device_index(self, device_name):
        for i in range(self.p.get_device_count()):
            info = self.p.get_device_info_by_index(i)
            if device_name.lower() in info['name'].lower():
                return i
        return None

    def start(self):
        self.stream = self.p.open(
            format=pyaudio.paInt16,
            channels=2,
            rate=self.rate,
            input=True,
            input_device_index=self.device_index,
            frames_per_buffer=self.chunk
        )

    def read_chunk(self):
        data = self.stream.read(self.chunk, exception_on_overflow=False)
        audio = np.frombuffer(data, dtype=np.int16)
        # Convert to mono by averaging channels if stereo
        if len(audio) == self.chunk * 2:
            audio = audio.reshape(-1, 2).mean(axis=1).astype(np.int16)
        return audio

    def close(self):
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
        self.p.terminate() 