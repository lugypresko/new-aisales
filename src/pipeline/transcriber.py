"""
Transcriber module using Distil-Whisper.
Optimized for low-latency CPU inference with int8 quantization.
"""

import torch
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline
import time
import numpy as np
import json
from pathlib import Path

class Transcriber:
    def __init__(self, config_path: str = "config.json"):
        self.config = self._load_config(config_path)
        self.device = "cpu"  # Force CPU as per spec
        self.torch_dtype = torch.float32
        
        print("🚀 Loading Distil-Whisper model...")
        start_time = time.time()
        
        model_id = self.config.get('models', {}).get('whisper', {}).get('model_name', "distil-whisper/distil-medium.en")
        
        self.model = AutoModelForSpeechSeq2Seq.from_pretrained(
            model_id, 
            torch_dtype=self.torch_dtype, 
            low_cpu_mem_usage=True, 
            use_safetensors=True
        )
        self.model.to(self.device)
        
        self.processor = AutoProcessor.from_pretrained(model_id)
        
        self.pipe = pipeline(
            "automatic-speech-recognition",
            model=self.model,
            tokenizer=self.processor.tokenizer,
            feature_extractor=self.processor.feature_extractor,
            max_new_tokens=128,
            chunk_length_s=15,
            batch_size=1,
            torch_dtype=self.torch_dtype,
            device=self.device,
        )
        
        print(f"✅ Model loaded in {time.time() - start_time:.2f}s")

    def _load_config(self, config_path: str):
        try:
            path = Path(config_path)
            if not path.exists():
                path = Path(__file__).parent.parent.parent / config_path
            
            if path.exists():
                with open(path, 'r') as f:
                    return json.load(f)
        except Exception:
            pass
        return {}

    def transcribe(self, audio_data: np.ndarray, sample_rate: int = 16000) -> str:
        """
        Transcribe audio chunk.
        Args:
            audio_data: float32 numpy array
            sample_rate: sample rate (must be 16000 for Whisper)
        """
        if len(audio_data) < 100:  # Ignore tiny chunks
            return ""
            
        start_time = time.time()
        
        # Normalize if needed (Whisper expects float32 between -1 and 1)
        if audio_data.dtype != np.float32:
            audio_data = audio_data.astype(np.float32)
        
        # Run inference
        result = self.pipe(audio_data, generate_kwargs={"language": "english"})
        text = result["text"].strip()
        
        latency = time.time() - start_time
        if text:
            print(f"📝 Transcript ({latency:.3f}s): {text}")
            
        return text
