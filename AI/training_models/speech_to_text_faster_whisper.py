# pip install faster-whisper
from faster_whisper import WhisperModel
import sounddevice as sd
import numpy as np

def record_audio(duration=5, sample_rate=16000):
    print(f"Recording for {duration} seconds...")
    recording = sd.rec(int(duration * sample_rate), 
                      samplerate=sample_rate, 
                      channels=1, 
                      dtype=np.float32)
    sd.wait()
    return recording.flatten()

# Use faster-whisper (up to 4x faster than regular whisper!)
model = WhisperModel("base", device="cpu", compute_type="int8")

audio_data = record_audio(duration=5)
segments, info = model.transcribe(audio_data, beam_size=1)  # beam_size=1 for speed

text = " ".join([segment.text for segment in segments])
print("You said:", text)