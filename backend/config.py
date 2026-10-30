"""
Core application settings and directory configurations.
"""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
SANDBOX_DIR = BASE_DIR / "sandbox_workspace"
UPLOADS_DIR = SANDBOX_DIR / "uploads"
OUTPUTS_DIR = SANDBOX_DIR / "outputs"
CHUNKS_DIR = SANDBOX_DIR / "chunks"
STATIC_DIR = BASE_DIR / "app" / "static"

# Ensure required directories exist
for directory in [SANDBOX_DIR, UPLOADS_DIR, OUTPUTS_DIR, CHUNKS_DIR, STATIC_DIR]:
    directory.mkdir(parents=True, exist_ok=True)
