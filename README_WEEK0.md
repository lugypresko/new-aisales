# Week 0: Data & Assets Foundation

## Overview
This directory contains all foundational data assets required for the Sales AI MVP. Week 0 must be completed before any code development begins.

## 📁 Directory Structure

```
AIsales/
├── data/
│   ├── knowledge_base.json          # 20 Q&A pairs for RAG
│   ├── intent_anchors.json          # 4 intent category definitions
│   ├── anchor_embeddings.json       # Precomputed intent embeddings (generated)
│   ├── faiss_index.bin              # FAISS index for RAG (generated)
│   ├── test_audio.wav               # 5-min mock sales call (to be created)
│   └── test_audio_transcript.txt    # Script for recording test audio (generated)
├── scripts/
│   ├── generate_test_audio.py       # Creates test audio transcript
│   └── precompute_embeddings.py     # Generates embeddings and FAISS index
├── logs/                             # Created automatically
└── config.json                       # Centralized configuration
```

## 🚀 Week 0 Setup Instructions

### Step 1: Install Dependencies

```powershell
# Create virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install required packages
pip install sentence-transformers faiss-cpu pyttsx3 numpy
```

### Step 2: Generate Embeddings

This creates the anchor embeddings and FAISS index:

```powershell
python scripts\precompute_embeddings.py
```

**Expected output:**
- `data/anchor_embeddings.json` - 4 intent category embeddings
- `data/faiss_index.bin` - FAISS index with 20 knowledge items
- Validation results showing intent matching accuracy

### Step 3: Create Test Audio

```powershell
python scripts\generate_test_audio.py
```

This generates `data/test_audio_transcript.txt`. You have three options:

**Option A: Manual Recording (Recommended)**
1. Open `data/test_audio_transcript.txt`
2. Record yourself reading the script at a natural pace
3. Save as 16kHz mono WAV to `data/test_audio.wav`

**Option B: Online TTS**
- Use Google Cloud Text-to-Speech, Amazon Polly, or ElevenLabs
- Paste the transcript and download as 16kHz mono WAV

**Option C: Local TTS (Lower quality)**
- Use `pyttsx3` or similar (quality may vary)

### Step 4: Validate Setup

Run this validation check:

```powershell
python -c "import json; from pathlib import Path; print('✅ All files present!' if all([(Path('data') / f).exists() for f in ['knowledge_base.json', 'intent_anchors.json', 'anchor_embeddings.json', 'faiss_index.bin']]) else '❌ Missing files')"
```

## 📊 Data Specifications

### Knowledge Base (`knowledge_base.json`)

**Structure:**
```json
{
  "id": 1,
  "trigger_text": "User question/statement",
  "response_text": "Sales rep response",
  "category": "Pricing|Technical|Competitors|NextSteps"
}
```

**Distribution:**
- Pricing: 5 items (IDs 1-5)
- Technical: 5 items (IDs 6-10)
- Competitors: 5 items (IDs 11-15)
- NextSteps: 5 items (IDs 16-20)

### Intent Anchors (`intent_anchors.json`)

Each intent category has 5 anchor texts used to compute the representative embedding for Gate 1 filtering.

**Categories:**
1. **Pricing** - Cost, budget, discounts
2. **Technical** - Security, integrations, implementation
3. **Competitors** - Differentiation, comparisons
4. **NextSteps** - Proposals, scheduling, closing

### Configuration (`config.json`)

**Key Parameters:**

| Parameter | Value | Purpose |
|-----------|-------|---------|
| `sample_rate` | 16000 Hz | Required by Distil-Whisper |
| `gate1_intent_threshold` | 0.60 | Intent recognition filter |
| `gate2_knowledge_threshold` | 0.75 | Knowledge match quality |
| `max_processing_latency_seconds` | 2.2 | Null Mode timeout |
| `context_window_seconds` | 30 | Rolling text buffer |

## 🧪 Testing the Data

### Test Intent Recognition

```python
from sentence_transformers import SentenceTransformer
import json
import numpy as np

model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

# Load anchor embeddings
with open('data/anchor_embeddings.json', 'r') as f:
    anchors = json.load(f)

# Test query
query = "How much does this cost?"
query_embedding = model.encode([query])[0]

# Find best matching intent
for intent, data in anchors.items():
    anchor_vec = np.array(data['embedding'])
    score = np.dot(query_embedding, anchor_vec) / (
        np.linalg.norm(query_embedding) * np.linalg.norm(anchor_vec)
    )
    print(f"{intent}: {score:.3f}")
```

### Test FAISS Retrieval

```python
import faiss
import json
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
index = faiss.read_index('data/faiss_index.bin')

# Load knowledge base
with open('data/knowledge_base.json', 'r') as f:
    kb = json.load(f)

# Test query
query = "What's the pricing?"
query_embedding = model.encode([query]).astype('float32')
faiss.normalize_L2(query_embedding)

# Search
distances, indices = index.search(query_embedding, k=1)
best_match = kb[indices[0][0]]

print(f"Query: {query}")
print(f"Match: {best_match['trigger_text']} (score: {distances[0][0]:.3f})")
print(f"Response: {best_match['response_text']}")
```

## ✅ Week 0 Completion Checklist

- [ ] Virtual environment created and activated
- [ ] Dependencies installed (`sentence-transformers`, `faiss-cpu`, etc.)
- [ ] `anchor_embeddings.json` generated successfully
- [ ] `faiss_index.bin` created (should be ~30KB)
- [ ] Test audio transcript generated
- [ ] `test_audio.wav` created (16kHz mono, ~5 minutes)
- [ ] Validation tests pass (intent matching works correctly)
- [ ] All 4 intent categories have embeddings
- [ ] FAISS index contains 20 items

## 🎯 Success Criteria

**Embedding Quality:**
- Intent matching accuracy > 90% on test queries
- Average embedding computation time < 25ms

**FAISS Index:**
- All 20 knowledge items indexed
- Search latency < 5ms

**Test Audio:**
- Duration: 4-6 minutes
- Format: 16kHz mono WAV
- Contains at least 5 trigger moments (one per category minimum)

## 🔄 Next Steps

Once Week 0 is complete, proceed to **Week 1: Audio Pipeline Implementation**.

Week 1 will use:
- `config.json` for audio parameters
- `test_audio.wav` for pipeline testing
- `anchor_embeddings.json` and `faiss_index.bin` for cognitive layer integration

## 📝 Notes

- The knowledge base uses **generic B2B SaaS** examples - customize for your specific product
- Anchor embeddings are **averaged** from 5 example texts per intent
- FAISS uses **Inner Product** similarity (equivalent to cosine with normalized vectors)
- Test audio should include natural pauses and silence gaps (0.7s+) to trigger VAD

## 🐛 Troubleshooting

**Issue: `sentence-transformers` installation fails**
- Solution: Install PyTorch first: `pip install torch --index-url https://download.pytorch.org/whl/cpu`

**Issue: FAISS index size is 0 bytes**
- Solution: Ensure embeddings are float32 and normalized before adding to index

**Issue: Test audio has no silence gaps**
- Solution: Manually edit the WAV file to add 0.7s+ silence between phrases

---

**Week 0 Status:** Ready for execution
**Estimated Time:** 1-2 hours
**Blocking:** None - all dependencies are open source and available
