"""
Buffer Manager for Sales AI.
Maintains a rolling 30-second context window of the conversation.
"""

import time
from collections import deque
from dataclasses import dataclass
from typing import List, Dict
import json
from pathlib import Path

@dataclass
class TranscriptSegment:
    text: str
    timestamp: float
    speaker: str = "User"  # Future proofing for speaker diarization

class BufferManager:
    def __init__(self, config_path: str = "config.json"):
        self.buffer: deque[TranscriptSegment] = deque()
        self.load_config(config_path)
        
    def load_config(self, config_path: str):
        """Load configuration to get context window size."""
        try:
            # Look for config in parent directories if not found
            path = Path(config_path)
            if not path.exists():
                path = Path(__file__).parent.parent.parent / config_path
                
            if path.exists():
                with open(path, 'r') as f:
                    config = json.load(f)
                    self.window_seconds = config.get('cognitive_layer', {}).get('context_window_seconds', 30)
            else:
                print(f"⚠️ Config not found at {config_path}, using default 30s window")
                self.window_seconds = 30
        except Exception as e:
            print(f"⚠️ Error loading config: {e}, using default 30s window")
            self.window_seconds = 30

    def add_segment(self, text: str):
        """Add a new text segment to the buffer."""
        if not text or not text.strip():
            return
            
        segment = TranscriptSegment(
            text=text.strip(),
            timestamp=time.time()
        )
        self.buffer.append(segment)
        self._prune()

    def _prune(self):
        """Remove segments older than the window size."""
        current_time = time.time()
        while self.buffer and (current_time - self.buffer[0].timestamp > self.window_seconds):
            self.buffer.popleft()

    def get_context(self) -> str:
        """Return the current context as a single string."""
        self._prune()  # Ensure fresh
        return " ".join([seg.text for seg in self.buffer])

    def get_full_history(self) -> List[Dict]:
        """Return full history for logging/debugging."""
        return [
            {
                "text": seg.text,
                "timestamp": seg.timestamp,
                "age": time.time() - seg.timestamp
            }
            for seg in self.buffer
        ]

    def clear(self):
        """Clear the buffer."""
        self.buffer.clear()
