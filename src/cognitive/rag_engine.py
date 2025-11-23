"""
RAG Engine (Gate 2).
Retrieves specific knowledge using FAISS index.
"""

import json
import numpy as np
import faiss
from pathlib import Path
from typing import Optional, Tuple, Dict
from sentence_transformers import SentenceTransformer
from functools import lru_cache

class RAGEngine:
    def __init__(self, config_path: str = "config.json"):
        self.config = self._load_config(config_path)
        self.threshold = self.config.get('cognitive_layer', {}).get('gate2_knowledge_threshold', 0.75)
        
        # Load Model (Shared with Intent Classifier in production, but loaded here for independence)
        # In a real optimized app, we'd pass the model instance to avoid double loading
        print("📚 Loading Embedding Model (Gate 2)...")
        model_name = self.config.get('models', {}).get('embeddings', {}).get('model_name', 'sentence-transformers/all-MiniLM-L6-v2')
        self.model = SentenceTransformer(model_name)
        
        # Load Knowledge Base & Index
        self.kb = self._load_knowledge_base()
        self.index = self._load_faiss_index()
        print(f"✅ RAG Engine Ready ({len(self.kb)} items loaded)")

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

    def _load_knowledge_base(self):
        try:
            path = Path(__file__).parent.parent.parent / "data" / "knowledge_base.json"
            with open(path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ Error loading KB: {e}")
            return []

    def _load_faiss_index(self):
        try:
            path = Path(__file__).parent.parent.parent / "data" / "faiss_index.bin"
            if path.exists():
                return faiss.read_index(str(path))
            else:
                print(f"❌ FAISS index not found at {path}")
                return None
        except Exception as e:
            print(f"❌ Error loading FAISS index: {e}")
            return None

    def search(self, text: str) -> Tuple[Optional[Dict], float]:
        """
        Search for the best matching knowledge item.
        Returns (ResponseItem, Score) or (None, Score) if below threshold.
        """
        if not text or not self.index:
            return None, 0.0
            
        # Encode (Cached)
        embedding = self._get_embedding(text)
        faiss.normalize_L2(embedding)
        
        # Search
        distances, indices = self.index.search(embedding, k=1)
        
        score = float(distances[0][0])
        idx = int(indices[0][0])
        
        if idx < 0 or idx >= len(self.kb):
            return None, score
            
        result = self.kb[idx]
        
        if score >= self.threshold:
            return result, score
        else:
            return None, score

    @lru_cache(maxsize=128)
    def _get_embedding(self, text: str) -> np.ndarray:
        """Cached embedding generation."""
        # FAISS requires float32
        return self.model.encode([text]).astype('float32')
