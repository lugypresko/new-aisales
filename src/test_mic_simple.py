"""
Microphone Test - Checks if your microphone is working.
Simple version without emoji characters for PowerShell compatibility.
"""

import sounddevice as sd
import numpy as np

def test_microphone():
    print("\n" + "="*80)
    print("MICROPHONE TEST")
    print("="*80 + "\n")
    
    # List available audio devices
    print("Available Audio Devices:\n")
    devices = sd.query_devices()
    
    for i, device in enumerate(devices):
        if device['max_input_channels'] > 0:  # Input device
            default = " (DEFAULT)" if i == sd.default.device[0] else ""
            print(f"   [{i}] {device['name']}{default}")
            print(f"       Channels: {device['max_input_channels']}, Sample Rate: {device['default_samplerate']}")
    
    print("\n" + "-"*80)
    print("Testing microphone input... (Speak now for 3 seconds)")
    print("-"*80 + "\n")
    
    # Record 3 seconds
    duration = 3
    sample_rate = 16000
    
    try:
        recording = sd.rec(int(duration * sample_rate), 
                          samplerate=sample_rate, 
                          channels=1, 
                          dtype='float32')
        sd.wait()
        
        # Analyze recording
        audio_data = recording.flatten()
        max_amplitude = np.max(np.abs(audio_data))
        rms = np.sqrt(np.mean(audio_data**2))
        
        print(f"Recording complete!\n")
        print(f"Audio Analysis:")
        print(f"   Max Amplitude: {max_amplitude:.4f}")
        print(f"   RMS Level: {rms:.4f}")
        
        if max_amplitude < 0.001:
            print("\nPROBLEM: No audio detected!")
            print("   Possible issues:")
            print("   - Microphone is muted")
            print("   - Wrong microphone selected")
            print("   - Microphone not plugged in")
            print("   - Microphone permissions not granted")
        elif max_amplitude < 0.01:
            print("\nWARNING: Audio level is very low")
            print("   Try speaking louder or check microphone volume")
        else:
            print("\nSUCCESS: Microphone is working!")
            print(f"   Audio detected successfully (level: {max_amplitude:.4f})")
        
        print("\n" + "="*80 + "\n")
        
    except Exception as e:
        print(f"\nError: {e}\n")
        print("This might be a microphone access issue.")

if __name__ == "__main__":
    test_microphone()
