import os
import pvporcupine
import pyaudio
import struct
import numpy as np
from faster_whisper import WhisperModel
import sounddevice as sd

# Get free API key from: https://console.picovoice.ai/
ACCESS_KEY = os.getenv("JARVIS_ACCESS_KEY")

# Initialize Whisper model once (reuse for efficiency)
print("Loading Whisper model...")
whisper_model = WhisperModel("small", device="cpu", compute_type="int8")

def record_command(duration=5, sample_rate=16000):
    """Record audio command after wake word"""
    print(f"🎤 Recording for {duration} seconds...")
    recording = sd.rec(int(duration * sample_rate), 
                      samplerate=sample_rate, 
                      channels=1, 
                      dtype=np.float32)
    sd.wait()
    print("Recording finished!")
    return recording.flatten()

def transcribe_command(audio_data):
    """Transcribe audio using Faster Whisper - English only"""
    segments, info = whisper_model.transcribe(
        audio_data, 
        beam_size=1,
        language="en"  # Force English transcription
    )
    text = " ".join([segment.text for segment in segments])
    return text

# Initialize Porcupine with built-in wake word
porcupine = pvporcupine.create(
    access_key=ACCESS_KEY,
    keywords=["jarvis"]
)

# Audio stream for wake word detection
pa = pyaudio.PyAudio()
audio_stream = pa.open(
    rate=porcupine.sample_rate,
    channels=1,
    format=pyaudio.paInt16,
    input=True,
    frames_per_buffer=porcupine.frame_length
)

print("🎧 Listening for 'Jarvis'...\n")

try:
    while True:
        # Listen for wake word
        pcm = audio_stream.read(porcupine.frame_length)
        pcm = struct.unpack_from("h" * porcupine.frame_length, pcm)
        
        keyword_index = porcupine.process(pcm)
        
        if keyword_index >= 0:
            print("✅ Wake word detected! Listening for command...\n")
            
            # Record command
            audio_data = record_command(duration=5)
            
            # Transcribe
            command = transcribe_command(audio_data)
            print(f"💬 You said: {command}\n")
            
            # TODO: Process the command here
            # if "weather" in command.lower():
            #     print("Getting weather...")
            # elif "time" in command.lower():
            #     print("Getting time...")
            
            print("🎧 Listening for 'Jarvis' again...\n")
            
except KeyboardInterrupt:
    print("\n🛑 Stopping...")
finally:
    audio_stream.close()
    pa.terminate()
    porcupine.delete()