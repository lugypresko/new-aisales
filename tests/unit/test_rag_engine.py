import pytest

def test_rag_known_query(rag_engine):
    """Test retrieval for a known query."""
    # "What is the pricing?" -> Should match Pricing ID 1-5
    item, score = rag_engine.search("What is the pricing?")
    assert item is not None
    assert item['category'] == "Pricing"
    assert score > 0.75

def test_rag_near_miss(rag_engine):
    """Test query that is relevant but might be low confidence."""
    # "Do you have a discount?" -> Should match Pricing
    item, score = rag_engine.search("Do you offer any discounts for startups?")
    assert item is not None
    assert item['category'] == "Pricing"

def test_rag_irrelevant_query(rag_engine):
    """Test query that should return None or low score."""
    # "What is the capital of France?"
    # Note: RAG always returns *something* (nearest neighbor), 
    # but the score should be low.
    item, score = rag_engine.search("What is the capital of France?")
    
    # If the score is below threshold, RAG engine might return None 
    # depending on implementation. Let's check the score.
    if item:
        assert score < 0.7
    else:
        assert True  # None is also acceptable for bad queries
