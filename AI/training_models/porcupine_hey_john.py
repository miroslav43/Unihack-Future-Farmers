import os
import pvporcupine
import pyaudio
import struct
import numpy as np
from faster_whisper import WhisperModel

# Get free API key from: https://console.picovoice.ai/
ACCESS_KEY = os.getenv("JARVIS_ACCESS_KEY")

# Initialize Porcupine with built-in wake word
porcupine = pvporcupine.create(
    access_key=ACCESS_KEY,
    keywords=["jarvis"]  # Use built-in, then customize later
)

# Audio stream
pa = pyaudio.PyAudio()
audio_stream = pa.open(
    rate=porcupine.sample_rate,
    channels=1,
    format=pyaudio.paInt16,
    input=True,
    frames_per_buffer=porcupine.frame_length
)

print("Listening for 'Jarvis'...")

try:
    while True:
        pcm = audio_stream.read(porcupine.frame_length)
        pcm = struct.unpack_from("h" * porcupine.frame_length, pcm)
        
        keyword_index = porcupine.process(pcm)
        
        if keyword_index >= 0:
            print("Wake word detected! Listening...")
            
            # Now record and transcribe command
            # (use your faster-whisper code here)
            
except KeyboardInterrupt:
    print("Stopping...")
finally:
    audio_stream.close()
    pa.terminate()
    porcupine.delete()