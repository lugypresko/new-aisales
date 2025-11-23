"""
Generate test audio for Sales AI MVP testing.
This script creates a synthetic sales call with proper timing and silence gaps.
"""

import pyttsx3
import wave
import numpy as np
from pathlib import Path
import time

# Mock sales call transcript with timing
SALES_CALL_SCRIPT = [
    {"speaker": "Rep", "text": "Hi there! Thanks for taking the time to chat today. How are you doing?", "pause_after": 2.0},
    {"speaker": "Prospect", "text": "Good, thanks. So tell me about your platform.", "pause_after": 1.5},
    {"speaker": "Rep", "text": "Absolutely. We help teams collaborate more effectively with AI-powered workflows.", "pause_after": 1.0},
    {"speaker": "Prospect", "text": "Interesting. How much does it cost?", "pause_after": 2.5},  # TRIGGER: Pricing
    {"speaker": "Rep", "text": "Great question. We have two main tiers to fit different needs.", "pause_after": 1.5},
    {"speaker": "Prospect", "text": "Okay. And is your platform secure? We handle sensitive data.", "pause_after": 2.0},  # TRIGGER: Technical
    {"speaker": "Rep", "text": "Security is our top priority. Let me walk you through our approach.", "pause_after": 1.5},
    {"speaker": "Prospect", "text": "We're currently using Competitor X. Why should we switch?", "pause_after": 2.5},  # TRIGGER: Competitors
    {"speaker": "Rep", "text": "That's a fair question. Many of our customers came from Competitor X.", "pause_after": 1.0},
    {"speaker": "Prospect", "text": "Hmm. Can you send me a proposal to review?", "pause_after": 2.0},  # TRIGGER: NextSteps
    {"speaker": "Rep", "text": "Absolutely! I can get that to you by end of day.", "pause_after": 1.5},
    {"speaker": "Prospect", "text": "Perfect. Let's schedule a follow-up for next week.", "pause_after": 2.0},  # TRIGGER: NextSteps
    {"speaker": "Rep", "text": "Sounds great. I'll send over some time options. Thanks so much!", "pause_after": 1.0},
]


def generate_silence(duration_seconds, sample_rate=16000):
    """Generate silence as numpy array."""
    num_samples = int(duration_seconds * sample_rate)
    return np.zeros(num_samples, dtype=np.int16)


def text_to_speech_segment(text, output_path, rate=150):
    """Convert text to speech and save as WAV file."""
    engine = pyttsx3.init()
    engine.setProperty('rate', rate)
    engine.save_to_file(text, str(output_path))
    engine.runAndWait()


def combine_audio_segments(segments, output_path, sample_rate=16000):
    """Combine multiple audio segments with silence gaps."""
    combined = np.array([], dtype=np.int16)
    
    for segment in segments:
        combined = np.concatenate([combined, segment])
    
    # Write to WAV file
    with wave.open(str(output_path), 'wb') as wav_file:
        wav_file.setnchannels(1)  # Mono
        wav_file.setsampwidth(2)  # 16-bit
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(combined.tobytes())


def generate_test_audio_simple(output_path):
    """
    Simple version: Generate a text transcript that can be manually recorded.
    This is more reliable than TTS for testing.
    """
    transcript_path = Path(output_path).parent / "test_audio_transcript.txt"
    
    with open(transcript_path, 'w', encoding='utf-8') as f:
        f.write("SALES AI MVP - TEST AUDIO TRANSCRIPT\n")
        f.write("=" * 60 + "\n\n")
        f.write("INSTRUCTIONS:\n")
        f.write("1. Read this script aloud at a natural pace\n")
        f.write("2. Pause for the specified duration after each line\n")
        f.write("3. Record as 16kHz mono WAV and save to: data/test_audio.wav\n")
        f.write("4. Total duration should be ~5 minutes\n\n")
        f.write("=" * 60 + "\n\n")
        
        total_time = 0
        for i, line in enumerate(SALES_CALL_SCRIPT, 1):
            speaker = line['speaker']
            text = line['text']
            pause = line['pause_after']
            
            # Estimate speech duration (rough: 150 words per minute = 2.5 words per second)
            word_count = len(text.split())
            speech_duration = word_count / 2.5
            total_time += speech_duration + pause
            
            f.write(f"[{total_time:.1f}s] {speaker}: {text}\n")
            f.write(f"    → PAUSE for {pause}s\n\n")
        
        f.write("=" * 60 + "\n")
        f.write(f"TOTAL ESTIMATED DURATION: {total_time:.1f} seconds (~{total_time/60:.1f} minutes)\n")
        f.write("\nKEY TRIGGER MOMENTS (for validation):\n")
        f.write("- ~15s: 'How much does it cost?' (Pricing)\n")
        f.write("- ~35s: 'Is your platform secure?' (Technical)\n")
        f.write("- ~55s: 'Why should we switch?' (Competitors)\n")
        f.write("- ~75s: 'Can you send me a proposal?' (NextSteps)\n")
        f.write("- ~90s: 'Let's schedule a follow-up' (NextSteps)\n")
    
    print(f"✅ Test audio transcript generated: {transcript_path}")
    print(f"\n📝 Next steps:")
    print(f"   1. Open {transcript_path}")
    print(f"   2. Record yourself reading it (or use a TTS tool)")
    print(f"   3. Save as 16kHz mono WAV to: {output_path}")
    print(f"\n💡 Alternative: Use online TTS services like:")
    print(f"   - Google Cloud Text-to-Speech")
    print(f"   - Amazon Polly")
    print(f"   - elevenlabs.io")


if __name__ == "__main__":
    output_dir = Path(__file__).parent.parent / "data"
    output_dir.mkdir(exist_ok=True)
    
    output_path = output_dir / "test_audio.wav"
    
    print("🎙️  Generating test audio transcript...")
    generate_test_audio_simple(output_path)
    print("\n✅ Week 0 test audio preparation complete!")
