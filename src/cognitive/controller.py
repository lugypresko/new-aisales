import time
from typing import Optional, Dict
from src.cognitive.intent_classifier import IntentClassifier
from src.cognitive.rag_engine import RAGEngine
from src.utils.logger import SalesLogger

class Controller:
    def __init__(self, config_path: str = "config.json"):
        # Initialize Gates
        self.intent_classifier = IntentClassifier(config_path)
        self.rag_engine = RAGEngine(config_path)
        self.logger = SalesLogger(config_path)
        
        # Shared model optimization (if possible)
        # In this MVP, we let them load separately, but in prod we'd share the instance
        
        # Latency Budget
        self.max_latency = 2.2  # Seconds

    def process(self, transcript: str, start_time: float) -> Optional[Dict]:
        """
        Main Control Logic.
        Returns response dict or None (Silence).
        """
        if not transcript:
            return None
            
        print(f"\n🧠 Processing: '{transcript}'")
        
        # 1. Latency Check (Pre-computation)
        current_latency = time.time() - start_time
        if current_latency > self.max_latency:
            print(f"⏱️  Timeout (Pre-check): {current_latency:.2f}s > {self.max_latency}s")
            return None

        # 2. Gate 1: Intent Recognition
        intent, intent_score = self.intent_classifier.classify(transcript)
        
        if not intent:
            print(f"⛔ Gate 1 Blocked: No Intent (Score: {intent_score:.2f})")
            self.logger.log_interaction(transcript, None, time.time() - start_time, intent_score, 0.0)
            return None
            
        print(f"✅ Gate 1 Passed: {intent} (Score: {intent_score:.2f})")
        
        # 3. Gate 2: Knowledge Retrieval
        response_item, rag_score = self.rag_engine.search(transcript)
        
        if not response_item:
            print(f"⛔ Gate 2 Blocked: Low Confidence (Score: {rag_score:.2f})")
            self.logger.log_interaction(transcript, None, time.time() - start_time, intent_score, rag_score)
            return None
            
        print(f"✅ Gate 2 Passed: Match Found (Score: {rag_score:.2f})")
        
        # 4. Final Latency Check
        total_latency = time.time() - start_time
        if total_latency > self.max_latency:
            print(f"⏱️  Timeout (Final): {total_latency:.2f}s > {self.max_latency}s")
            self.logger.log_interaction(transcript, None, total_latency, intent_score, rag_score)
            return None
            
        # Success!
        decision = {
            "response": response_item['response_text'],
            "intent": intent,
            "category": response_item['category'],
            "latency": total_latency,
            "scores": {
                "intent": intent_score,
                "rag": rag_score
            }
        }
        
        self.logger.log_interaction(transcript, decision, total_latency, intent_score, rag_score)
        return decision
