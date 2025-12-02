import pytest
import time

def test_intent_exact_match(intent_classifier):
    """Test exact matches for known anchors."""
    # Pricing Anchor
    intent, score = intent_classifier.classify("How much does it cost?")
    assert intent == "Pricing"
    assert score > 0.8

def test_intent_paraphrase(intent_classifier):
    """Test semantic paraphrases."""
    # "Is it safe?" -> Technical
    intent, score = intent_classifier.classify("Is your platform secure against hackers?")
    assert intent == "Technical"
    assert score > 0.6

def test_intent_negative_case(intent_classifier):
    """Test non-business speech (should be None)."""
    intent, score = intent_classifier.classify("Hello, can you hear me?")
    assert intent is None
    assert score < 0.6

def test_intent_caching(intent_classifier):
    """Verify that repeated queries are faster (LRU Cache)."""
    query = "What is the pricing model?"
    
    # First call
    start = time.time()
    intent_classifier.classify(query)
    first_duration = time.time() - start
    
    # Second call (Cached)
    start = time.time()
    intent_classifier.classify(query)
    second_duration = time.time() - start
    
    # Cache should be significantly faster (or at least not slower)
    # Note: On fast CPUs, both might be near 0, so we check logic mostly
    assert second_duration <= first_duration
