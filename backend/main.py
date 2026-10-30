"""
FastAPI Main Application Web Server.
Exposes REST API endpoints for frontend connection.
"""
import os
from pathlib import Path
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from backend.config import SANDBOX_DIR, UPLOADS_DIR, OUTPUTS_DIR
from backend.sandbox import sandbox_manager
from backend.media_processor import media_processor
from backend.agent import agent_engine

app = FastAPI(title="Aysh AI v2 - Media Agent Sandbox Backend", version="2.0.0")

# Enable CORS for local dev servers
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static outputs and uploads for serving media files
app.mount("/outputs", StaticFiles(directory=str(OUTPUTS_DIR)), name="outputs")
app.mount("/uploads", StaticFiles(directory=str(UPLOADS_DIR)), name="uploads")


@app.get("/")
def index():
    """Backend status endpoint."""
    return {"status": "ok", "service": "Aysh AI v2 Backend API"}


@app.post("/api/chat")
def chat(payload: dict):
    """Processes conversational AI messages."""
    message = payload.get("message", "")
    file_context = payload.get("file_context")
    ai_mode = payload.get("ai_mode", "Normal")
    if not message:
        raise HTTPException(status_code=400, detail="Message cannot be empty.")

    res = agent_engine.process_message(message=message, file_context=file_context, ai_mode=ai_mode)
    return res


@app.post("/api/upload_chunk")
async def upload_chunk(
    file: UploadFile = File(...),
    upload_id: str = Form(...),
    chunk_index: int = Form(...),
    total_chunks: int = Form(...),
    filename: str = Form(...)
):
    """Chunked streaming file upload endpoint supporting >2GB files."""
    chunk_bytes = await file.read()
    res = sandbox_manager.handle_upload_chunk(
        upload_id=upload_id,
        chunk_index=chunk_index,
        total_chunks=total_chunks,
        filename=filename,
        chunk_bytes=chunk_bytes
    )
    return res


@app.get("/api/files")
def list_files():
    """Returns all files in the sandbox workspace."""
    return {"files": sandbox_manager.list_sandbox_files()}


@app.get("/api/download/{filename}")
def download_file(filename: str):
    """Downloads requested output file safely from sandbox outputs or uploads."""
    safe_filename = Path(filename).name
    out_path = OUTPUTS_DIR / safe_filename
    if not out_path.exists():
        out_path = UPLOADS_DIR / safe_filename

    if not out_path.exists():
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(
        path=out_path,
        filename=safe_filename,
        media_type="application/octet-stream",
        headers={"Content-Disposition": f"attachment; filename={safe_filename}"}
    )


@app.post("/api/sandbox/execute")
def execute_sandbox_code(payload: dict):
    """Executes code in isolated sandbox environment."""
    code = payload.get("code", "")
    if not code:
        raise HTTPException(status_code=400, detail="Code cannot be empty.")

    res = sandbox_manager.execute_code(code)
    return res
