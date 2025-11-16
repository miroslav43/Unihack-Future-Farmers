import sounddevice as sd
import soundfile as sf
import numpy as np
import whisper
import speech_recognition as sr

# Installation instructions:
# pip install openai-whisper sounddevice soundfile SpeechRecognition

def wait_for_wake_word(wake_word="hey john"):
    """Listen for the wake word using Google Speech Recognition (free)"""
    recognizer = sr.Recognizer()
    mic = sr.Microphone()
    
    print(f"🎤 Listening... say '{wake_word}' to start recording.")
    
    with mic as source:
        recognizer.adjust_for_ambient_noise(source, duration=1)
        
        while True:
            try:
                print(".", end="", flush=True)  # Progress indicator
                audio = recognizer.listen(source, timeout=1, phrase_time_limit=3)
                
                # Try to recognize speech
                text = recognizer.recognize_google(audio).lower()
                
                # Check if wake word is in the recognized text
                if wake_word.lower() in text:
                    print("\n✅ Wake-word detected!")
                    return True
                    
            except sr.WaitTimeoutError:
                # No speech detected, continue listening
                continue
            except sr.UnknownValueError:
                # Speech was unintelligible, continue listening
                continue
            except sr.RequestError as e:
                print(f"\n❌ Could not request results from Google Speech Recognition; {e}")
                return False
            except KeyboardInterrupt:
                print("\n\n🛑 Stopped by user")
                return False

def record_audio(duration=5, sample_rate=16000):
    """Record audio for specified duration"""
    print(f"🎙️  Recording for {duration} seconds... Speak now!")
    recording = sd.rec(int(duration * sample_rate), 
                      samplerate=sample_rate, 
                      channels=1, 
                      dtype=np.float32)
    sd.wait()
    print("✅ Recording finished!")
    return recording, sample_rate

def transcribe_audio(audio_file):
    """Transcribe audio using Whisper"""
    print("🤖 Transcribing audio...")
    model = whisper.load_model("tiny")
    result = model.transcribe(audio_file)
    return result["text"]

# Main flow
if __name__ == "__main__":
    print("=" * 50)
    print("Voice Assistant with Wake Word (Free Version)")
    print("=" * 50)
    print("Using Google Speech Recognition for wake word")
    print("Press Ctrl+C to exit\n")
    
    # Wait for wake word
    if wait_for_wake_word(wake_word="hey john"):
        # Record audio after wake word is detected
        audio_data, sr_rate = record_audio(duration=5)
        
        # Save temporarily
        temp_file = "temp_recording.wav"
        sf.write(temp_file, audio_data, sr_rate)
        
        # Transcribe
        text = transcribe_audio(temp_file)
        print("\n" + "=" * 50)
        print(f"📝 You said: {text}")
        print("=" * 50)
    else:
        print("❌ Failed to initialize wake word detection")
