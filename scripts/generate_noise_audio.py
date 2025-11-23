"""
Generate simple noise/silence audio for testing.
Bypasses TTS to avoid driver issues.
"""

import numpy as np
import soundfile as sf
from pathlib import Path

def generate_noise_wav(output_path):
    print(f"🔊 Generating noise audio to {output_path}...")
    
    sr = 16000
    
    # 1. Silence (0.5s)
    silence1 = np.zeros(int(0.5 * sr), dtype=np.float32)
    
    # 2. Speech-like Noise (2.0s)
    # Amplitude modulated white noise to simulate speech envelope
    t = np.linspace(0, 2.0, int(2.0 * sr))
    envelope = np.sin(2 * np.pi * 2 * t) * 0.5 + 0.5 # 2Hz modulation
    noise = np.random.uniform(-0.5, 0.5, len(t)) * envelope
    
    # 3. Silence (1.0s) - Should trigger VAD
    silence2 = np.zeros(int(1.0 * sr), dtype=np.float32)
    
    # 4. More Noise (1.5s)
    t2 = np.linspace(0, 1.5, int(1.5 * sr))
    envelope2 = np.sin(2 * np.pi * 3 * t2) * 0.5 + 0.5
    noise2 = np.random.uniform(-0.5, 0.5, len(t2)) * envelope2
    
    # Combine
    audio = np.concatenate([silence1, noise, silence2, noise2])
    
    # Save
    sf.write(output_path, audio, sr, subtype='PCM_16')
    print(f"✅ Generated {len(audio)/sr:.1f}s of audio.")

if __name__ == "__main__":
    output_dir = Path(__file__).parent.parent / "data"
    output_dir.mkdir(exist_ok=True)
    output_path = output_dir / "test_audio.wav"
    
    generate_noise_wav(str(output_path))
