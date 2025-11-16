"""
EASIEST Text-to-Speech Option - Google TTS (gTTS)
Save as: easiest_tts.py

This is the absolute SIMPLEST way to do TTS!
Just 3 lines of code!

Installation: pip install gtts

Usage: python easiest_tts.py
"""

from gtts import gTTS
import os

def text_to_speech_easy(text, output_file="output.mp3", language='en'):
    """
    Convert text to speech using Google TTS (simplest method)
    
    Args:
        text: Text to convert to speech
        output_file: Output audio file name
        language: Language code (en, es, fr, de, etc.)
    """
    
    print(f"Generating speech in {language}...")
    
    try:
        # This is literally all you need!
        tts = gTTS(text=text, lang=language, slow=False)
        tts.save(output_file)
        
        print(f"✓ Audio saved to: {output_file}")
        print(f"File size: {os.path.getsize(output_file) / 1024:.1f} KB")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nMake sure you have internet connection (gTTS needs online access)")
        return False


def main():
    print("=" * 60)
    print("EASIEST Text-to-Speech with Google TTS")
    print("=" * 60)
    print("Note: Requires internet connection")
    
    # Get text from user
    print("\nEnter the text you want to convert to speech:")
    print("(or press Enter for default demo text)")
    text = input("> ").strip()
    
    if not text:
        text = "Hello! This is the easiest way to do text to speech in Python. Just three lines of code!"
    
    # Get output filename
    output = input("\nOutput filename (default: output.mp3): ").strip()
    if not output:
        output = "output.mp3"
    
    if not output.endswith('.mp3'):
        output += '.mp3'
    
    # Language selection
    print("\n--- Language Options ---")
    languages = {
        "1": ("en", "English"),
        "2": ("es", "Spanish"),
        "3": ("fr", "French"),
        "4": ("de", "German"),
        "5": ("it", "Italian"),
        "6": ("pt", "Portuguese"),
        "7": ("zh", "Chinese"),
        "8": ("ja", "Japanese"),
        "9": ("ko", "Korean"),
        "10": ("ro", "Romanian")
    }
    
    for key, (code, name) in languages.items():
        print(f"{key}. {name} ({code})")
    
    choice = input("\nSelect language (1-10, default: 1): ").strip()
    lang = languages.get(choice, languages["1"])[0]
    
    # Generate speech
    print("\n" + "=" * 60)
    success = text_to_speech_easy(text, output, lang)
    print("=" * 60)
    
    if success:
        print("\nTo play the audio:")
        print(f"  - Windows: start {output}")
        print(f"  - Mac: afplay {output}")
        print(f"  - Linux: mpg123 {output}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nCancelled by user.")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        print("\nMake sure you have installed:")
        print("  pip install gtts")