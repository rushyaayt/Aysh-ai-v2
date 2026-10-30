# Aysh AI v2 - Agentic Media Studio & Sandbox 🚀✨

**Aysh AI v2** is a 100% free, local-first agentic AI application designed for editing videos, transforming photos, generating media visuals, executing sandbox code scripts, and handling large file uploads (>2GB) — all with friendly conversational AI vibes and **zero paid API tokens required**!

---

## 🌟 Key Features

- 🎬 **Video & Photo Editing Engine**:
  - **Aura Edit Style**: Signature glowing pulsating energy aura and neon outline effects.
  - **Styles & Filters**: Cyberpunk neon tints, vintage sepia, grayscale, speed adjustments (2x fast, 0.5x slow), and custom trimming.
- 🧠 **4 AI Intelligence Modes**:
  - **Normal**: Casual friendly interactions and quick edits.
  - **Pro**: Multi-pass parameter tuning and enhanced visual polishing.
  - **Advance**: High-precision frame and layer alignment.
  - **Powerful Intelligent**: Ultimate creative reasoning and multi-layered processing depth.
- 🎨 **Local AI Media Generation**:
  - Generates custom abstract photos and dynamic animated videos from text prompts completely free and locally!
- 📁 **Chunked Large File Streaming (>2GB Support)**:
  - High-performance chunked file upload system that streams large video/photo files in chunks to prevent memory spikes or browser timeouts.
- 🧪 **Code Execution Sandbox**:
  - Safe, isolated workspace environment where the AI or user can dynamically run custom Python scripts to manipulate media and files.
- 📥 **Instant Download & Preview Studio**:
  - Live preview studio for images and videos with direct downloadable output format links.

---

## 📂 Project Architecture

```text
├── app/
│   ├── config.py           # Core directory & path configurations
│   ├── main.py             # FastAPI web server & REST endpoints
│   ├── agent.py            # Friendly AI Agent conversational engine & mode logic
│   ├── media_processor.py  # Computer vision, photo filters, & Aura video editor
│   ├── sandbox.py          # Chunked streaming upload engine & sandbox execution
│   └── static/
│       └── index.html      # Interactive 3-panel Web Studio UI
├── tests/
│   └── test_main.py        # End-to-end integration test suite
├── .gitignore              # Ignores pycache, outputs, logs, and temp sandbox files
├── README.md               # Application documentation
└── requirements.txt        # Dependencies
```

---

## 🚀 Quick Start Guide

### 1. Requirements & Dependencies
Ensure Python 3.10+ is installed on your machine.

Install required dependencies:
```bash
pip install fastapi uvicorn opencv-python-headless Pillow imageio imageio-ffmpeg numpy moviepy python-multipart requests pytest
```

### 2. Run the Application Server
Start the Uvicorn web server:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Open your browser and navigate to:
```text
http://localhost:8000
```

---

## 🧪 Running Tests

Run the unit and integration test suite:
```bash
python -m pytest tests/
```

---

## 🔒 Privacy & Safety
- Runs 100% locally and free.
- No personal data or API keys are required or leaked.
- Files are safely stored in the isolated `sandbox_workspace` directory.

---

*Built for creators with friendly vibes!* ✨
