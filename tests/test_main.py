"""
End-to-End Integration Tests for Aysh AI v2 backend endpoints & processing.
"""
import uuid
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.config import UPLOADS_DIR, OUTPUTS_DIR

client = TestClient(app)


def test_index_page():
    response = client.get("/")
    assert response.status_code == 200
    assert "Aysh AI v2" in response.text


def test_list_files_endpoint():
    response = client.get("/api/files")
    assert response.status_code == 200
    data = response.json()
    assert "files" in data
    assert isinstance(data["files"], list)


def test_chat_ai_interaction():
    response = client.post("/api/chat", json={"message": "Hi, what can you do?", "ai_mode": "Powerful Intelligent"})
    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    assert "POWERFUL INTELLIGENT" in data["response"]
    assert "action" in data


def test_generate_photo_via_chat():
    response = client.post("/api/chat", json={"message": "generate photo cosmic aura energy"})
    assert response.status_code == 200
    data = response.json()
    assert data["action"] == "photo_generated"
    assert "output_file" in data


def test_generate_video_via_chat():
    response = client.post("/api/chat", json={"message": "generate video pulsing neon lights"})
    assert response.status_code == 200
    data = response.json()
    assert data["action"] == "video_generated"
    assert "output_file" in data


def test_chunked_upload():
    upload_id = "test_upload_123"
    chunk_data = b"Hello World Chunk Content"
    unique_filename = f"test_upload_{uuid.uuid4().hex[:6]}.txt"
    response = client.post(
        "/api/upload_chunk",
        data={
            "upload_id": upload_id,
            "chunk_index": 0,
            "total_chunks": 1,
            "filename": unique_filename
        },
        files={"file": ("chunk0", chunk_data, "application/octet-stream")}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["completed"] is True
    assert data["filename"] == unique_filename


def test_sandbox_code_execution():
    code = "print(2 + 2)"
    response = client.post("/api/sandbox/execute", json={"code": code})
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "4" in data["stdout"]
