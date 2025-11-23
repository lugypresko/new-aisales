"""
Structured Logger for Sales AI.
Records interaction metrics (latency, intent, outcome) to JSONL for analysis.
"""

import json
import time
import logging
from pathlib import Path
from typing import Dict, Any, Optional

class SalesLogger:
    def __init__(self, config_path: str = "config.json"):
        self.config = self._load_config(config_path)
        self.log_path = self._get_log_path()
        
        # Ensure log directory exists
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        
        print(f"📝 Logging interactions to {self.log_path}")

    def _load_config(self, config_path: str) -> Dict:
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

    def _get_log_path(self) -> Path:
        """Get absolute path to interaction log."""
        rel_path = self.config.get('logging', {}).get('interaction_log_path', 'logs/interactions.jsonl')
        return Path(__file__).parent.parent.parent / rel_path

    def log_interaction(self, 
                        transcript: str, 
                        decision: Optional[Dict], 
                        latency: float,
                        gate1_score: float,
                        gate2_score: float):
        """
        Log a single interaction event.
        """
        event = {
            "timestamp": time.time(),
            "iso_time": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
            "input_text": transcript,
            "latency_seconds": round(latency, 3),
            "outcome": "SPOKEN" if decision else "SILENT",
            "intent": decision['intent'] if decision else None,
            "scores": {
                "gate1_intent": round(gate1_score, 3),
                "gate2_rag": round(gate2_score, 3)
            },
            "response_category": decision['category'] if decision else None
        }
        
        try:
            with open(self.log_path, 'a', encoding='utf-8') as f:
                f.write(json.dumps(event) + "\n")
        except Exception as e:
            print(f"❌ Logging failed: {e}")
