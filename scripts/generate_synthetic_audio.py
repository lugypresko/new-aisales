"""
Generate synthetic test audio using pyttsx3.
This allows automated verification of the pipeline.
"""

import pyttsx3
import numpy as np
import wave
import os
from pathlib import Path
import time

def generate_synthetic_wav(output_path):
    print(f"🔊 Generating synthetic audio to {output_path}...")
    
    engine = pyttsx3.init()
    engine.setProperty('rate', 150)
    
    # Temporary file for speech segments
    temp_file = "temp_speech.wav"
    
    # Script with pauses
    script = [
        ("Hello, I am interested in your product.", 1.0),
        ("How much does it cost?", 2.0),
        ("Is it secure?", 1.0),
        ("Thank you, goodbye.", 1.0)
    ]
    
    final_audio = []
    sample_rate = 16000
    
    for text, pause_duration in script:
        print(f"  - Synthesizing: '{text}'")
        
        # 1. Generate Speech
        engine.save_to_file(text, temp_file)
        engine.runAndWait()
        
        # 2. Read Speech WAV
        # pyttsx3 saves as default system format, usually 22050Hz or 44100Hz
        # We need to resample to 16000Hz for our pipeline
        import librosa
        speech, _ = librosa.load(temp_file, sr=sample_rate)
        
        # 3. Generate Silence
        silence_samples = int(pause_duration * sample_rate)
        silence = np.zeros(silence_samples, dtype=np.float32)
        
        # 4. Append
        final_audio.append(speech)
        final_audio.append(silence)
        
    # Concatenate
    full_audio = np.concatenate(final_audio)
    
    # Save as 16-bit PCM WAV
    import soundfile as sf
    sf.write(output_path, full_audio, sample_rate, subtype='PCM_16')
    
    # Cleanup
    if os.path.exists(temp_file):
        os.remove(temp_file)
        
    print(f"✅ Generated {len(full_audio)/sample_rate:.1f}s of audio.")

if __name__ == "__main__":
    output_dir = Path(__file__).parent.parent / "data"
    output_dir.mkdir(exist_ok=True)
    output_path = output_dir / "test_audio.wav"
    
    try:
        generate_synthetic_wav(str(output_path))
    except Exception as e:
        print(f"❌ Error: {e}")
        # Fallback if pyttsx3 fails (e.g. no audio driver in env)
        print("⚠️  TTS failed, generating white noise with silence gaps...")
        sr = 16000
        # Speech = noise, Silence = zeros
        speech = np.random.uniform(-0.1, 0.1, sr*2) # 2s noise
        silence = np.zeros(sr*1) # 1s silence
        audio = np.concatenate([speech, silence, speech, silence])
        import soundfile as sf
        sf.write(output_path, audio, sr, subtype='PCM_16')
