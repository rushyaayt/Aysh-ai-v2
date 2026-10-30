"""
Sandbox File and Code Execution Management.
Handles isolated code running and streaming chunk file assembly for large files (>2GB).
"""
import os
import shutil
import subprocess
import uuid
from typing import List, Dict, Any, Optional
from pathlib import Path
from backend.config import SANDBOX_DIR, UPLOADS_DIR, OUTPUTS_DIR, CHUNKS_DIR


class SandboxManager:
    def __init__(self):
        self.sandbox_dir = SANDBOX_DIR
        self.uploads_dir = UPLOADS_DIR
        self.outputs_dir = OUTPUTS_DIR
        self.chunks_dir = CHUNKS_DIR

    def handle_upload_chunk(
        self,
        upload_id: str,
        chunk_index: int,
        total_chunks: int,
        filename: str,
        chunk_bytes: bytes
    ) -> Dict[str, Any]:
        """Saves file chunk to disk and reassembles complete file once all chunks arrive."""
        chunk_dir = self.chunks_dir / upload_id
        chunk_dir.mkdir(parents=True, exist_ok=True)

        chunk_path = chunk_dir / f"chunk_{chunk_index}"
        with open(chunk_path, "wb") as f:
            f.write(chunk_bytes)

        # Check if all chunks have been received
        existing_chunks = list(chunk_dir.glob("chunk_*"))
        if len(existing_chunks) == total_chunks:
            final_path = self.uploads_dir / filename
            with open(final_path, "wb") as final_file:
                for idx in range(total_chunks):
                    c_path = chunk_dir / f"chunk_{idx}"
                    with open(c_path, "rb") as c_file:
                        shutil.copyfileobj(c_file, final_file)

            # Cleanup chunk directory
            shutil.rmtree(chunk_dir, ignore_errors=True)
            return {
                "completed": True,
                "filename": filename,
                "file_path": str(final_path),
                "message": f"File '{filename}' assembled successfully in sandbox!"
            }

        return {
            "completed": False,
            "chunks_received": len(existing_chunks),
            "total_chunks": total_chunks
        }

    def execute_code(self, code: str, timeout: int = 15) -> Dict[str, Any]:
        """Executes Python code inside sandbox_workspace directory."""
        script_filename = f"script_{uuid.uuid4().hex[:8]}.py"
        script_path = self.sandbox_dir / script_filename

        with open(script_path, "w", encoding="utf-8") as f:
            f.write(code)

        try:
            res = subprocess.run(
                ["python3", str(script_path)],
                cwd=str(self.sandbox_dir),
                capture_output=True,
                text=True,
                timeout=timeout
            )
            return {
                "success": res.returncode == 0,
                "stdout": res.stdout,
                "stderr": res.stderr,
                "returncode": res.returncode
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "stdout": "",
                "stderr": f"Execution timed out after {timeout} seconds.",
                "returncode": -1
            }
        finally:
            if script_path.exists():
                script_path.unlink(missing_ok=True)

    def list_sandbox_files(self) -> List[Dict[str, Any]]:
        """Lists files in uploads and outputs."""
        file_list = []
        for folder, category in [(self.uploads_dir, "upload"), (self.outputs_dir, "output")]:
            for p in folder.glob("*"):
                if p.is_file():
                    file_list.append({
                        "name": p.name,
                        "category": category,
                        "size": p.stat().st_size,
                        "path": str(p)
                    })
        return file_list


sandbox_manager = SandboxManager()
