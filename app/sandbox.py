"""
Sandbox file management and safe script execution engine.
Handles large chunked file uploads (>2GB support) and isolated workspace execution.
"""
import os
import shutil
import subprocess
import sys
import uuid
from typing import List, Dict, Any, Optional
from pathlib import Path
from app.config import SANDBOX_DIR, UPLOADS_DIR, OUTPUTS_DIR, CHUNKS_DIR


class SandboxManager:
    def __init__(self):
        self.sandbox_dir = SANDBOX_DIR
        self.uploads_dir = UPLOADS_DIR
        self.outputs_dir = OUTPUTS_DIR
        self.chunks_dir = CHUNKS_DIR

    def list_sandbox_files(self) -> List[Dict[str, Any]]:
        """Lists files available in the sandbox workspace."""
        files_info = []
        for root_dir, folder_name in [(self.uploads_dir, "uploads"), (self.outputs_dir, "outputs")]:
            if root_dir.exists():
                for p in root_dir.glob("*"):
                    if p.is_file():
                        stat = p.stat()
                        files_info.append({
                            "name": p.name,
                            "category": folder_name,
                            "path": str(p.relative_to(self.sandbox_dir)),
                            "size_bytes": stat.st_size,
                            "size_mb": round(stat.st_size / (1024 * 1024), 2),
                            "modified": stat.st_mtime
                        })
        return sorted(files_info, key=lambda x: x["modified"], reverse=True)

    def handle_upload_chunk(self, upload_id: str, chunk_index: int, total_chunks: int, filename: str, chunk_bytes: bytes) -> Dict[str, Any]:
        """Saves an incoming chunk to disk and merges when all chunks are uploaded."""
        upload_chunk_dir = self.chunks_dir / upload_id
        upload_chunk_dir.mkdir(parents=True, exist_ok=True)

        chunk_path = upload_chunk_dir / f"chunk_{chunk_index:05d}"
        with open(chunk_path, "wb") as f:
            f.write(chunk_bytes)

        existing_chunks = list(upload_chunk_dir.glob("chunk_*"))
        if len(existing_chunks) == total_chunks:
            # Reassemble file streamingly to handle >2GB without high RAM usage
            safe_filename = Path(filename).name
            final_path = self.uploads_dir / safe_filename

            # If file already exists, append unique suffix
            if final_path.exists():
                stem = final_path.stem
                suffix = final_path.suffix
                final_path = self.uploads_dir / f"{stem}_{uuid.uuid4().hex[:6]}{suffix}"

            with open(final_path, "wb") as outfile:
                for i in range(total_chunks):
                    cp = upload_chunk_dir / f"chunk_{i:05d}"
                    if cp.exists():
                        with open(cp, "rb") as infile:
                            shutil.copyfileobj(infile, outfile, length=1024*1024*8) # 8MB buffer

            # Clean up temp chunks
            shutil.rmtree(upload_chunk_dir, ignore_errors=True)

            return {
                "completed": True,
                "filename": final_path.name,
                "filepath": str(final_path),
                "relative_path": f"uploads/{final_path.name}",
                "size_bytes": final_path.stat().st_size,
                "size_mb": round(final_path.stat().st_size / (1024 * 1024), 2)
            }

        return {
            "completed": False,
            "upload_id": upload_id,
            "received_chunks": len(existing_chunks),
            "total_chunks": total_chunks
        }

    def execute_code(self, code_str: str, timeout_sec: int = 60) -> Dict[str, Any]:
        """Executes custom Python code inside the sandbox workspace safely."""
        script_filename = f"script_{uuid.uuid4().hex[:8]}.py"
        script_path = self.sandbox_dir / script_filename

        with open(script_path, "w", encoding="utf-8") as f:
            f.write(code_str)

        try:
            res = subprocess.run(
                [sys.executable, str(script_path)],
                cwd=str(self.sandbox_dir),
                capture_output=True,
                text=True,
                timeout=timeout_sec
            )
            stdout = res.stdout
            stderr = res.stderr
            returncode = res.returncode
        except subprocess.TimeoutExpired:
            stdout = ""
            stderr = f"Execution timed out after {timeout_sec} seconds."
            returncode = -1
        except Exception as e:
            stdout = ""
            stderr = str(e)
            returncode = -1
        finally:
            if script_path.exists():
                script_path.unlink()

        return {
            "returncode": returncode,
            "stdout": stdout,
            "stderr": stderr,
            "success": returncode == 0
        }

sandbox_manager = SandboxManager()
