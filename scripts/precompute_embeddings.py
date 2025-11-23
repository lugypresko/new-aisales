"""
Precompute embeddings for Week 0 data preparation.
This script generates:
1. Intent anchor embeddings (for Gate 1)
2. Knowledge base embeddings (for Gate 2 / FAISS)
"""

import json
import numpy as np
from pathlib import Path
from sentence_transformers import SentenceTransformer
import faiss
import time


def load_config():
    """Load configuration."""
    config_path = Path(__file__).parent.parent / "config.json"
    with open(config_path, 'r') as f:
        return json.load(f)


def load_intent_anchors(config):
    """Load intent anchor definitions."""
    anchors_path = Path(__file__).parent.parent / config['rag']['intent_anchors_path']
    with open(anchors_path, 'r') as f:
        return json.load(f)


def load_knowledge_base(config):
    """Load knowledge base Q&A pairs."""
    kb_path = Path(__file__).parent.parent / config['rag']['knowledge_base_path']
    with open(kb_path, 'r') as f:
        return json.load(f)


def compute_anchor_embeddings(model, anchors):
    """
    Compute average embeddings for each intent category.
    Each intent gets one representative embedding (average of anchor texts).
    """
    anchor_embeddings = {}
    
    for anchor in anchors:
        intent = anchor['intent']
        texts = anchor['anchor_texts']
        
        print(f"Computing embeddings for intent: {intent} ({len(texts)} anchor texts)")
        
        # Encode all anchor texts
        embeddings = model.encode(texts, show_progress_bar=False)
        
        # Average them to get single representative embedding
        avg_embedding = np.mean(embeddings, axis=0)
        
        anchor_embeddings[intent] = {
            'embedding': avg_embedding.tolist(),
            'dimension': len(avg_embedding),
            'num_anchors': len(texts)
        }
    
    return anchor_embeddings


def build_faiss_index(model, knowledge_base, config):
    """
    Build FAISS index for knowledge base.
    Each Q&A pair gets embedded based on trigger_text.
    """
    print(f"\nBuilding FAISS index for {len(knowledge_base)} knowledge items...")
    
    # Extract trigger texts
    trigger_texts = [item['trigger_text'] for item in knowledge_base]
    
    # Compute embeddings
    start_time = time.time()
    embeddings = model.encode(trigger_texts, show_progress_bar=True)
    embedding_time = time.time() - start_time
    
    print(f"✅ Embeddings computed in {embedding_time:.2f}s ({embedding_time/len(trigger_texts)*1000:.1f}ms per item)")
    
    # Create FAISS index
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatIP(dimension)  # Inner Product (cosine similarity with normalized vectors)
    
    # Normalize embeddings for cosine similarity
    faiss.normalize_L2(embeddings)
    
    # Add to index
    index.add(embeddings.astype('float32'))
    
    print(f"✅ FAISS index built with {index.ntotal} vectors (dimension={dimension})")
    
    return index, embeddings


def save_anchor_embeddings(anchor_embeddings, output_path):
    """Save precomputed anchor embeddings."""
    with open(output_path, 'w') as f:
        json.dump(anchor_embeddings, f, indent=2)
    print(f"✅ Anchor embeddings saved to: {output_path}")


def save_faiss_index(index, output_path):
    """Save FAISS index to disk."""
    faiss.write_index(index, str(output_path))
    print(f"✅ FAISS index saved to: {output_path}")


def validate_embeddings(model, anchor_embeddings, knowledge_base):
    """
    Validation: Test a few queries to ensure embeddings work correctly.
    """
    print("\n" + "="*60)
    print("VALIDATION: Testing embedding quality")
    print("="*60)
    
    test_queries = [
        ("What's the price?", "Pricing"),
        ("Is it secure?", "Technical"),
        ("How are you different?", "Competitors"),
        ("Send me a proposal", "NextSteps"),
    ]
    
    for query, expected_intent in test_queries:
        query_embedding = model.encode([query])[0]
        
        # Test Gate 1: Intent matching
        best_intent = None
        best_score = -1
        
        for intent, data in anchor_embeddings.items():
            anchor_vec = np.array(data['embedding'])
            # Cosine similarity
            score = np.dot(query_embedding, anchor_vec) / (
                np.linalg.norm(query_embedding) * np.linalg.norm(anchor_vec)
            )
            if score > best_score:
                best_score = score
                best_intent = intent
        
        status = "✅" if best_intent == expected_intent else "❌"
        print(f"{status} Query: '{query}'")
        print(f"   Expected: {expected_intent} | Got: {best_intent} (score: {best_score:.3f})")


def main():
    print("🚀 Week 0: Precomputing embeddings...\n")
    
    # Load config
    config = load_config()
    
    # Load model
    model_name = config['models']['embeddings']['model_name']
    print(f"Loading embedding model: {model_name}")
    model = SentenceTransformer(model_name)
    print(f"✅ Model loaded (dimension: {model.get_sentence_embedding_dimension()})\n")
    
    # Load data
    anchors = load_intent_anchors(config)
    knowledge_base = load_knowledge_base(config)
    
    # Compute anchor embeddings (Gate 1)
    print("="*60)
    print("STEP 1: Computing Intent Anchor Embeddings (Gate 1)")
    print("="*60)
    anchor_embeddings = compute_anchor_embeddings(model, anchors)
    
    # Save anchor embeddings
    output_dir = Path(__file__).parent.parent / "data"
    output_dir.mkdir(exist_ok=True)
    anchor_output = output_dir / "anchor_embeddings.json"
    save_anchor_embeddings(anchor_embeddings, anchor_output)
    
    # Build FAISS index (Gate 2)
    print("\n" + "="*60)
    print("STEP 2: Building FAISS Index (Gate 2)")
    print("="*60)
    index, embeddings = build_faiss_index(model, knowledge_base, config)
    
    # Save FAISS index
    faiss_output = output_dir / "faiss_index.bin"
    save_faiss_index(index, faiss_output)
    
    # Validation
    validate_embeddings(model, anchor_embeddings, knowledge_base)
    
    print("\n" + "="*60)
    print("✅ Week 0 embedding precomputation complete!")
    print("="*60)
    print(f"\nGenerated files:")
    print(f"  - {anchor_output}")
    print(f"  - {faiss_output}")
    print(f"\n📊 Stats:")
    print(f"  - Intent categories: {len(anchor_embeddings)}")
    print(f"  - Knowledge base items: {len(knowledge_base)}")
    print(f"  - Embedding dimension: {config['models']['embeddings']['dimension']}")


if __name__ == "__main__":
    main()
