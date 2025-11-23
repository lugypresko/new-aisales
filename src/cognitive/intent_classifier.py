"""
Intent Classifier (Gate 1).
Filters input based on broad intent categories using precomputed anchor embeddings.
"""

import json
import numpy as np
from pathlib import Path
from typing import Optional, Tuple, Dict
from sentence_transformers import SentenceTransformer
import time
from functools import lru_cache

class IntentClassifier:
    def __init__(self, config_path: str = "config.json"):
        self.config = self._load_config(config_path)
        self.threshold = self.config.get('cognitive_layer', {}).get('gate1_intent_threshold', 0.60)
        
        # Load Model
        print("🧠 Loading Embedding Model (Gate 1)...")
        model_name = self.config.get('models', {}).get('embeddings', {}).get('model_name', 'sentence-transformers/all-MiniLM-L6-v2')
        self.model = SentenceTransformer(model_name)
        
        # Load Anchors
        self.anchors = self._load_anchors()
        print(f"✅ Intent Classifier Ready ({len(self.anchors)} intents loaded)")

    def _load_config(self, config_path: str) -> Dict:
        try:
            path = Path(config_path)
            if not path.exists():
                path = Path(__file__).parent.parent.parent / config_path
            
            if path.exists():
                with open(path, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"⚠️ Config error: {e}")
        return {}

    def _load_anchors(self) -> Dict:
        """Load precomputed anchor embeddings."""
        try:
            path = Path(__file__).parent.parent.parent / "data" / "anchor_embeddings.json"
            if path.exists():
                with open(path, 'r') as f:
                    return json.load(f)
            else:
                print(f"❌ Anchor embeddings not found at {path}")
                return {}
        except Exception as e:
            print(f"❌ Error loading anchors: {e}")
            return {}

    def classify(self, text: str) -> Tuple[Optional[str], float]:
        """
        Classify text into an intent.
        Returns (Intent, Score) or (None, Score) if below threshold.
        """
        if not text or not self.anchors:
            return None, 0.0
            
        # Get embedding (cached)
        embedding = self._get_embedding(text)
        
        best_intent = None
        best_score = -1.0
        
        # Compare with anchors
        for intent, data in self.anchors.items():
            anchor_vec = np.array(data['embedding'])
            
            # Cosine Similarity
            score = np.dot(embedding, anchor_vec) / (
                np.linalg.norm(embedding) * np.linalg.norm(anchor_vec)
            )
            
            if score > best_score:
                best_score = score
                best_intent = intent
                
        if best_score >= self.threshold:
            return best_intent, float(best_score)
        else:
            return None, float(best_score)

    @lru_cache(maxsize=128)
    def _get_embedding(self, text: str) -> np.ndarray:
        """Cached embedding generation."""
        return self.model.encode([text])[0]
