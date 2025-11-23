"""
Audio Stream Handler.
Captures real-time audio and performs VAD (Voice Activity Detection).
"""

import sounddevice as sd
import numpy as np
import torch
import time
import queue
from typing import Generator, Optional
import json
from pathlib import Path

class AudioStream:
    def __init__(self, config_path: str = "config.json"):
        self.config = self._load_config(config_path)
        self.sample_rate = 16000
        self.chunk_size = 512
        
        # VAD Parameters
        self.vad_threshold = 0.5
        self.silence_trigger_duration = 0.7  # Seconds of silence to trigger processing
        
        # State
        self.audio_queue = queue.Queue()
        self.is_speaking = False
        self.speech_buffer = []
        self.silence_counter = 0
        self.running = False
        
        # Load VAD Model
        print("🎤 Loading Silero VAD...")
        self.model, utils = torch.hub.load(repo_or_dir='snakers4/silero-vad',
                                         model='silero_vad',
                                         force_reload=False,
                                         trust_repo=True)
        (self.get_speech_timestamps, _, self.read_audio, _, _) = utils
        print("✅ VAD Loaded")

    def _load_config(self, config_path: str):
        try:
            path = Path(config_path)
            if not path.exists():
                path = Path(__file__).parent.parent.parent / config_path
            
            if path.exists():
                with open(path, 'r') as f:
                    cfg = json.load(f)
                    audio_cfg = cfg.get('audio', {})
                    self.sample_rate = audio_cfg.get('sample_rate', 16000)
                    self.chunk_size = audio_cfg.get('chunk_size', 512)
                    self.vad_threshold = audio_cfg.get('vad_threshold', 0.5)
                    self.silence_trigger_duration = audio_cfg.get('silence_duration_trigger', 0.7)
                    return cfg
        except Exception as e:
            print(f"⚠️ Config error: {e}")
        return {}

    def _callback(self, indata, frames, time, status):
        """SoundDevice callback."""
        if status:
            print(status)
        self.audio_queue.put(indata.copy())

    def stream(self) -> Generator[np.ndarray, None, None]:
        """
        Yields speech segments when silence is detected.
        """
        self.running = True
        
        # Calculate silence chunks threshold
        # chunk_duration = 512 / 16000 = 0.032s
        # 0.7s / 0.032s = ~22 chunks
        chunks_per_second = self.sample_rate / self.chunk_size
        silence_chunk_threshold = int(self.silence_trigger_duration * chunks_per_second)
        
        print("👂 Listening... (Press Ctrl+C to stop)")
        
        with sd.InputStream(samplerate=self.sample_rate,
                          channels=1,
                          callback=self._callback,
                          blocksize=self.chunk_size):
            
            while self.running:
                try:
                    chunk = self.audio_queue.get(timeout=0.1)
                    
                    # Convert to float32 for VAD
                    audio_float32 = chunk.flatten().astype(np.float32)
                    
                    # Run VAD
                    speech_prob = self.model(torch.from_numpy(audio_float32), self.sample_rate).item()
                    
                    if speech_prob > self.vad_threshold:
                        # Speech detected
                        if not self.is_speaking:
                            print("🗣️  Speech Started")
                            self.is_speaking = True
                        
                        self.speech_buffer.append(audio_float32)
                        self.silence_counter = 0
                        
                    else:
                        # Silence
                        if self.is_speaking:
                            self.speech_buffer.append(audio_float32) # Keep trailing silence
                            self.silence_counter += 1
                            
                            if self.silence_counter > silence_chunk_threshold:
                                # Trigger Event!
                                print("🤫 Silence Trigger - Processing...")
                                full_audio = np.concatenate(self.speech_buffer)
                                yield full_audio
                                
                                # Reset
                                self.speech_buffer = []
                                self.is_speaking = False
                                self.silence_counter = 0
                                
                except queue.Empty:
                    continue
                except KeyboardInterrupt:
                    break

    def stream_from_file(self, file_path: str) -> Generator[np.ndarray, None, None]:
        """
        Simulate real-time stream from a WAV file.
        """
        import librosa
        
        self.running = True
        print(f"🎧 Streaming from file: {file_path}")
        
        # Load audio
        audio, _ = librosa.load(file_path, sr=self.sample_rate)
        
        # Calculate chunk size in samples
        # chunk_size is 512
        
        # Calculate silence threshold
        chunks_per_second = self.sample_rate / self.chunk_size
        silence_chunk_threshold = int(self.silence_trigger_duration * chunks_per_second)
        
        cursor = 0
        total_samples = len(audio)
        
        while self.running and cursor < total_samples:
            # Get chunk
            end = min(cursor + self.chunk_size, total_samples)
            chunk = audio[cursor:end]
            
            # Pad last chunk if needed
            if len(chunk) < self.chunk_size:
                chunk = np.pad(chunk, (0, self.chunk_size - len(chunk)))
            
            cursor += self.chunk_size
            
            # Simulate real-time delay (optional, but good for testing UI)
            # time.sleep(self.chunk_size / self.sample_rate) 
            
            # VAD Logic (Same as live)
            audio_float32 = chunk.astype(np.float32)
            
            # Run VAD
            speech_prob = self.model(torch.from_numpy(audio_float32), self.sample_rate).item()
            
            if speech_prob > self.vad_threshold:
                if not self.is_speaking:
                    print("🗣️  Speech Started")
                    self.is_speaking = True
                
                self.speech_buffer.append(audio_float32)
                self.silence_counter = 0
                
            else:
                if self.is_speaking:
                    self.speech_buffer.append(audio_float32)
                    self.silence_counter += 1
                    
                    if self.silence_counter > silence_chunk_threshold:
                        print("🤫 Silence Trigger - Processing...")
                        full_audio = np.concatenate(self.speech_buffer)
                        yield full_audio
                        
                        self.speech_buffer = []
                        self.is_speaking = False
                        self.silence_counter = 0

    def stop(self):
        self.running = False
