# 🧪 How to Test Sales AI

There are two ways to test the product: **Manual Live Testing** (for experience) and **Automated Testing** (for reliability).

## 1. Manual Live Testing (User Experience)

Use this to verify the UI and "feel" the latency.

### Prerequisites

- Microphone connected.
- Speakers/Headphones connected.
- `venv` activated.

### Steps

1. **Start the Application**:

   ```powershell
   python run_sales_ai.py
   ```

2. **Wait for Initialization**:
   - You will see "🚀 Pipeline Thread Started..." and "✅ Pipeline Components Ready."
   - A transparent overlay will appear in the top-right corner.
3. **Speak Test Phrases**:
   - *Pricing*: "How much does this cost?"
   - *Technical*: "Is your platform secure?"
   - *Silence*: "Hello?" (Should NOT trigger)
4. **Verify Output**:
   - The overlay should show a "Hint" card for valid questions.
   - It should remain invisible for small talk.

---

## 2. Automated Testing (Reliability)

Use this to verify the logic, thresholds, and performance metrics without speaking.

> **Note**: This suite is currently being built (Week 5).

### Running the Suite

```powershell
pytest tests/ -v
```

### What It Tests

1. **Unit Tests**: Checks if the Intent Classifier and RAG Engine return correct scores for specific text inputs.
2. **Integration Tests**: Checks if the Controller correctly blocks "low confidence" answers (Null Mode).
3. **End-to-End Tests**: Feeds a pre-recorded audio file (`data/test_audio.wav`) into the pipeline and asserts that:
    - Latency is < 2.2s.
    - False Trigger Rate is < 15%.
    - Correct hints are generated.

### Viewing Logs

- **Live Logs**: `logs/interactions.jsonl` (Production logs)
- **Test Logs**: `tests/logs/test_interactions.jsonl` (Test run logs)
