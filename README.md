# AI Sales Copilot — Python Pipeline

A Python prototype that processes audio input into text and passes transcribed segments through a cognitive controller for a contextual response.

> **Status:** Engineering prototype. This README describes code present in the repository; it does not claim production deployment or measured business impact.

## What the code does

```text
AudioStream (microphone or test file)
  → Transcriber
  → BufferManager
  → Controller.process(text, start_time)
  → response / no-response
```

The entry point is [`src/main_pipeline.py`](src/main_pipeline.py). It supports a `--test-file` input, making the pipeline inspectable without a live microphone. Components are separated under [`src/pipeline/`](src/pipeline/) and [`src/cognitive/`](src/cognitive/).

## Engineering evidence

- **Python integration:** streaming input, transcription, buffering and controller orchestration in the main pipeline.
- **Retrieval and decisions:** inspect [`src/cognitive/`](src/cognitive/) for the RAG engine, intent classifier and controller.
- **Test organization:** [`tests/unit/`](tests/unit/) holds 11 implemented unit tests (controller, intent classifier, RAG engine). `tests/integration/`, `tests/regression/` and `tests/e2e/` are empty placeholders for now — no tests exist there yet.
- **Test fixtures:** [`tests/conftest.py`](tests/conftest.py) defines pytest fixtures for the controller, RAG engine, classifier and logger.

## Inspect / verify

1. Clone the repository and create an isolated Python environment.
2. Review dependencies and configuration under `src/` before installing or providing credentials.
3. Run `python -m pytest tests/` after installing the project's required dependencies.
4. To inspect the entry point, run `python -m src.main_pipeline --help`.
5. A real audio test may require local audio libraries, model assets and external credentials.

**Verification status:** `python -m pytest tests/` was run on 2026-11-10 (Python 3.10, CPU, `sentence-transformers/all-MiniLM-L6-v2`, faiss-cpu): **11 passed, 0 failed**. Live microphone, audio transcription and end-to-end execution were not run; accuracy and latency in production are not claimed.

## Design discussion

The separation between audio acquisition, transcription, context buffering and decision logic enables component-level testing and future replacement of individual model providers. The main loop records a start timestamp before transcription and reports controller latency when a decision is returned; this is **not** an end-to-end latency benchmark.

## Ownership and limitations

This repository is presented as a portfolio artifact, not proof of who authored every line. Review commit history for contribution details. Some development artifacts may need cleanup before this is suitable as a reusable open-source package.

## Next engineering steps

- Document and pin dependencies; provide a safe `.env.example`.
- Add a deterministic, credential-free smoke test and publish its CI result.
- Add evaluation cases for correct intent, false interventions, response latency and failure handling.
- Document threat model and handling of potentially sensitive audio/transcript data.
