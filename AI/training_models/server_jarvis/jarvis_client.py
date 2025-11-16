import os
import pvporcupine
import pyaudio
import struct
import numpy as np
from faster_whisper import WhisperModel
import sounddevice as sd
import requests
import re

# Get free API key from: https://console.picovoice.ai/
ACCESS_KEY = os.getenv("JARVIS_ACCESS_KEY")

# Server configuration
SERVER_URL = "http://localhost:5000/command"  # Change if server is on different machine

# Initialize Whisper model once (reuse for efficiency)
print("Loading Whisper model...")
whisper_model = WhisperModel("base", device="cpu", compute_type="int8")

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
        language="en"
    )
    text = " ".join([segment.text for segment in segments])
    return text

def extract_plant_number(text):
    """Extract plant number (1-12) from text"""
    # Look for numbers written as digits or words
    number_words = {
        'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5, 'six': 6,
        'seven': 7, 'eight': 8, 'nine': 9, 'ten': 10, 'eleven': 11, 'twelve': 12
    }
    
    # Try to find digit (1-12)
    digit_match = re.search(r'\b([1-9]|1[0-2])\b', text)
    if digit_match:
        return int(digit_match.group(1))
    
    # Try to find word number
    text_lower = text.lower()
    for word, num in number_words.items():
        if word in text_lower:
            return num
    
    return None

def parse_command(command_text):
    """Parse command and return code and additional data"""
    text_lower = command_text.lower()
    
    # Check for "sensors greenhouse" (code 6)
    if "sensor" in text_lower and "greenhouse" in text_lower:
        return {
            "code": 6,
            "action": "GET GREENHOUSE SENSORS",
            "text": command_text
        }
    
    # Check for "water all plants" (code 3)
    if all(word in text_lower for word in ["water", "all", "plant"]):
        return {
            "code": 3,
            "action": "WATER ALL PLANTS",
            "text": command_text
        }
    
    # Check for "water plant [number]" (code 4)
    if "water" in text_lower and "plant" in text_lower:
        plant_num = extract_plant_number(text_lower)
        if plant_num:
            return {
                "code": 4,
                "action": f"WATER PLANT {plant_num}",
                "plant_number": plant_num,
                "text": command_text
            }
    
    # Check for "send picture/photo plant [number]" (code 5)
    if ("picture" in text_lower or "photo" in text_lower) and "plant" in text_lower and "send" in text_lower:
        plant_num = extract_plant_number(text_lower)
        if plant_num:
            return {
                "code": 5,
                "action": f"SEND PHOTO OF PLANT {plant_num}",
                "plant_number": plant_num,
                "text": command_text
            }
    
    # Check for "open" (code 1)
    if "open" in text_lower:
        return {
            "code": 1,
            "action": "OPEN ROOF",
            "text": command_text
        }
    
    # Check for "close" (code 2)
    if "close" in text_lower:
        return {
            "code": 2,
            "action": "CLOSE ROOF",
            "text": command_text
        }
    
    # No recognized command
    return None

def send_command(command_text):
    """Process command and send to server"""
    
    # Parse the command
    parsed = parse_command(command_text)
    
    if not parsed:
        print("❌ No recognized command")
        return
    
    # Send to server
    try:
        print(f"📤 Sending command: {parsed['action']} (code: {parsed['code']})")
        response = requests.post(
            SERVER_URL,
            json=parsed,
            timeout=5
        )
        
        if response.status_code == 200:
            print(f"✅ Command sent successfully!")
        else:
            print(f"⚠️ Server responded with status: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Is command_server.py running?")
    except Exception as e:
        print(f"❌ Error sending command: {e}")

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
            
            # Send command to server
            send_command(command)
            
            print("\n🎧 Listening for 'Jarvis' again...\n")
            
except KeyboardInterrupt:
    print("\n🛑 Stopping...")
finally:
    audio_stream.close()
    pa.terminate()
    porcupine.delete()