You are absolutely right. I tried to "future-proof" the MVP, but in doing so, I violated the core principle of this spec: **Latency and Cognitive Accuracy above all else.**

The 3-minute window and Electron are bloat. The 60+ triggers create noise. We are cutting them.

Here is the **Rectified MVP V2 Plan**—leaner, faster, and strictly aligned with the "Cognitive Layer" and "Control Layer" specifications.

---

### ✂️ The Cuts (Explicit)
1.  **Context Window:** Reduced from 3 mins to **30 seconds** (Rolling Buffer).
2.  **Intent Detector:** Reduced to **4 Core Classes** (Pricing, Objection, Pain Point, Next Steps). No wide-net similarity.
3.  **UI Framework:** **PyQt6** (Native, lightweight) replaces Electron.
4.  **Trigger List:** Gone. We rely on the 4 Core Classes + Embedding Score.

---

### ⚙️ The Pipeline: Event-Driven Architecture
This is the strict logic flow for V2.

`Audio Stream` -> `VAD (Silence > 0.7s)` -> `Distil-Whisper` -> **COGNITIVE LAYER** -> **CONTROL LAYER** -> `PyQt HUD`

---

### 📅 The Corrected 4-Week Execution Plan

#### **Week 1: The Audio Core & Short-Term Memory**
*Goal: Get text into the system fast and maintain a 30s buffer.*

1.  **Audio Ingestion:** `SoundDevice` + `Silero VAD`.
2.  **Distil-Whisper Integration:**
    *   Implement `int8` quantization.
    *   **Success Check:** Transcription must finish <0.6s after user stops speaking.
3.  **The 30s Buffer:**
    *   Implement a simple `deque` (text buffer).
    *   New text pushes old text out. This is our only context source for the MVP.

#### **Week 2: The Cognitive & Control Layers (The "Brain")**
*Goal: The "Null Mode" and Intent Detection.*

1.  **Intent Detector (Mini-Classifier):**
    *   Create 4 "Anchor Embeddings" (Pricing, Objection, Pain, Closing).
    *   Compare incoming transcript to these 4 anchors.
    *   If distance is too far -> **Intent = None**.
2.  **The "Null Mode" Logic Gate (Crucial):**
    *   Write the master control function:
        ```python
        def control_logic(transcript, latency_start):
            if detect_intent(transcript) == None: return NULL
            if (current_time - latency_start) > 2.2s: return NULL
            response = rag_search(transcript)
            if response.score < 0.75: return NULL
            return response
        ```
    *   **Result:** The system learns to "shut up" unless it is sure.

#### **Week 3: RAG, Caching & The KPI Check**
*Goal: Retrieve answers instantly and validate the "Silence" strategy.*

1.  **In-Memory LRU Cache:**
    *   `@lru_cache(maxsize=128)` on the embedding function.
    *   If the user repeats "How much?", we fetch the embedding from RAM.
2.  **FAISS Setup:** Index the 20 Prompt Items.
3.  **False Trigger Enforcement (Manual Review):**
    *   **Task:** Run 20 mock interactions.
    *   **Metric:** If the system pops up when you didn't ask for help > 3 times (15%), **raise the Intent Threshold** from 0.75 to 0.80.
    *   *This connects directly to the "Cognitive Reliability" goal.*

#### **Week 4: The "Heads-Up" UI & UX Safety**
*Goal: Visualizing the result without annoyance.*

1.  **PyQt6 Overlay:**
    *   Frameless window, transparent background, positioned top-right.
    *   **Thumbs Up/Down:** Simple buttons that log the `UUID` of the interaction to a CSV.
2.  **Interruption Logic (Fade-Out):**
    *   Connect VAD signal to UI.
    *   **Event:** `VAD_Speech_Start` -> **Action:** `UI.hide()` (Immediate Fade Out).
    *   *Why:* Even if the answer is good, if the client interrupts, the HUD must vanish.
3.  **Time-to-First-Value Test:**
    *   Full system run. verify the first helpful hint appears within 5 minutes of a mock call.

---

### 📊 Final Architecture Validation Checklist

| Component | Spec Requirement | MVP Implementation |
| :--- | :--- | :--- |
| **STT** | Low Latency | Distil-Whisper (Quantized) |
| **Context** | Relevant Scope | **30s** Rolling Window (Text Deque) |
| **Cognition** | Event Detection | **4-Class Intent Detector** (Pricing, Objection, etc.) |
| **Control** | Graceful Degradation | **Null Mode** (Latency/Score/Intent Checks) |
| **UI** | Native/Fast | **PyQt6** Floating Window + Fade-out on VAD |
| **Cache** | Performance | **LRU In-Memory Cache** |

This plan strips the fat. It builds the Control Layer in Week 2 (early) to ensure we don't build a "spammy" bot. Shall we proceed with this roadmap?