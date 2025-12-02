import pytest
import time
from unittest.mock import MagicMock

def test_controller_null_mode_intent(controller):
    """Test that Controller returns None if Intent is None."""
    # Mock Intent Classifier to return None
    controller.intent_classifier.classify = MagicMock(return_value=(None, 0.0))
    
    decision = controller.process("Hello?", time.time())
    assert decision is None

def test_controller_null_mode_rag(controller):
    """Test that Controller returns None if RAG score is low."""
    # Mock Intent OK, but RAG Low
    controller.intent_classifier.classify = MagicMock(return_value=("Pricing", 0.9))
    controller.rag_engine.search = MagicMock(return_value=({"response_text": "foo", "category": "Pricing"}, 0.4))
    
    decision = controller.process("How much?", time.time())
    assert decision is None

def test_controller_success(controller):
    """Test full success path."""
    # Mock everything OK
    controller.intent_classifier.classify = MagicMock(return_value=("Pricing", 0.9))
    controller.rag_engine.search = MagicMock(return_value=({"response_text": "It costs $50", "category": "Pricing"}, 0.9))
    
    decision = controller.process("How much?", time.time())
    
    assert decision is not None
    assert decision['intent'] == "Pricing"
    assert decision['response'] == "It costs $50"
    assert decision['latency'] < 2.2

def test_controller_latency_timeout(controller):
    """Test that Controller aborts if latency budget exceeded."""
    # Simulate start time 3 seconds ago
    start_time = time.time() - 3.0
    
    decision = controller.process("How much?", start_time)
    assert decision is None
