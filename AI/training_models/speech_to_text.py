import whisper
import sounddevice as sd
import soundfile as sf
import numpy as np

# First install: pip install sounddevice soundfile

def record_audio(duration=5, sample_rate=16000):
    print(f"Recording for {duration} seconds...")
    recording = sd.rec(int(duration * sample_rate), 
                      samplerate=sample_rate, 
                      channels=1, 
                      dtype=np.float32)
    sd.wait()
    print("Recording finished!")
    return recording, sample_rate

# Record audio
audio_data, sr = record_audio(duration=5)

# Save temporarily
sf.write("temp_recording.wav", audio_data, sr)

# Transcribe
model = whisper.load_model("base")
result = model.transcribe("./temp_recording.wav")
print("You said:", result["text"])