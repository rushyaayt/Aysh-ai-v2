"""
Conversational Engine for Aysh AI v2.
Parses user intent for media processing, generation, sandbox tasks, and chat with 4 AI modes.
"""
import re
import random
from typing import Dict, Any, List
from pathlib import Path
from backend.media_processor import media_processor
from backend.sandbox import sandbox_manager
from backend.config import UPLOADS_DIR, OUTPUTS_DIR


class AgentEngine:
    def __init__(self):
        self.ai_modes = ["Normal", "Pro", "Advance", "Powerful Intelligent"]

    def _get_mode_prefix(self, mode: str) -> str:
        if mode == "Powerful Intelligent":
            return "🔥 [POWERFUL INTELLIGENT MODE] "
        elif mode == "Advance":
            return "🚀 [ADVANCE MODE] "
        elif mode == "Pro":
            return "🌟 [PRO MODE] "
        return "⚡ "

    def process_message(self, message: str, file_context: str = None, ai_mode: str = "Normal") -> Dict[str, Any]:
        """Main entry point to process user prompts and perform agentic actions."""
        msg_lower = message.lower().strip()
        prefix = self._get_mode_prefix(ai_mode)

        # Check for media generation intent
        if "generate photo" in msg_lower or "create photo" in msg_lower or "generate image" in msg_lower:
            prompt = msg_lower.replace("generate photo", "").replace("create photo", "").replace("generate image", "").strip() or "cyberpunk cosmic aura"
            out_file = media_processor.generate_photo(prompt=prompt)
            filename = Path(out_file).name
            return {
                "reply": f"{prefix}I've generated a stunning photo for you based on '{prompt}'! You can preview and download it right now! 📸✨",
                "action": "photo_generated",
                "output_file": f"/outputs/{filename}"
            }

        if "generate video" in msg_lower or "create video" in msg_lower or "make video" in msg_lower:
            prompt = msg_lower.replace("generate video", "").replace("create video", "").replace("make video", "").strip() or "glowing energy waves"
            out_file = media_processor.generate_video(prompt=prompt)
            filename = Path(out_file).name
            return {
                "reply": f"{prefix}Here is your newly generated video clip for '{prompt}'! Check out the video player! 🎥🎆",
                "action": "video_generated",
                "output_file": f"/outputs/{filename}"
            }

        # Check for media editing intent
        if "aura edit" in msg_lower or "aura style" in msg_lower or "aura" in msg_lower:
            target_file = file_context
            if not target_file:
                # Find most recent file in uploads
                files = sandbox_manager.list_sandbox_files()
                if files:
                    target_file = files[0]["name"]

            if not target_file:
                return {
                    "reply": f"{prefix}I'd love to apply the signature Aura Edit style for you! Please upload a photo or video first using the uploader on the left panel! 🎨",
                    "action": "need_file"
                }

            input_path = UPLOADS_DIR / target_file
            if not input_path.exists():
                input_path = OUTPUTS_DIR / target_file

            if not input_path.exists():
                return {
                    "reply": f"{prefix}I couldn't locate file '{target_file}' in the sandbox. Please re-upload it!",
                    "action": "file_not_found"
                }

            ext = input_path.suffix.lower()
            if ext in ['.mp4', '.avi', '.mov', '.webm']:
                out_file = media_processor.apply_aura_video_effect(str(input_path))
            else:
                out_file = media_processor.apply_aura_photo_effect(str(input_path))

            filename = Path(out_file).name
            return {
                "reply": f"{prefix}Boom! I've applied the glowing Aura Edit style to '{target_file}'! Take a look at the preview! 🔥✨",
                "action": "aura_edit_complete",
                "output_file": f"/outputs/{filename}"
            }

        if "cyberpunk" in msg_lower:
            target_file = file_context
            if not target_file:
                files = sandbox_manager.list_sandbox_files()
                if files:
                    target_file = files[0]["name"]

            if target_file:
                input_path = UPLOADS_DIR / target_file
                if input_path.exists():
                    out_file = media_processor.apply_cyberpunk_effect(str(input_path))
                    filename = Path(out_file).name
                    return {
                        "reply": f"{prefix}Cyberpunk neon look applied to '{target_file}'! Enjoy the futuristic vibes! 🌆⚡",
                        "action": "cyberpunk_edit_complete",
                        "output_file": f"/outputs/{filename}"
                    }

        # Code execution intent
        if "run code" in msg_lower or "execute code" in msg_lower or msg_lower.startswith("python:"):
            code = message.replace("python:", "").replace("run code", "").strip()
            if not code:
                code = "print('Aysh AI Sandbox operational!')"
            exec_res = sandbox_manager.execute_code(code)
            output = exec_res.get("stdout") or exec_res.get("stderr") or "Done"
            return {
                "reply": f"{prefix}Executed code in sandbox! Result:\n```\n{output}\n```",
                "action": "code_executed"
            }

        # Friendly conversational responses
        friendly_greetings = [
            f"{prefix}Hey there! Super excited to hang out with you! What amazing photos, videos, or scripts are we cooking up today? 😊✨",
            f"{prefix}Yo! I'm Aysh AI v2, your friendly creative assistant. Tell me what you want to generate or edit!",
            f"{prefix}Hello friend! I'm running at 100% capacity in {ai_mode} mode. Let's create something epic together! 🎨🚀"
        ]

        return {
            "reply": random.choice(friendly_greetings),
            "action": "chat"
        }


agent_engine = AgentEngine()
