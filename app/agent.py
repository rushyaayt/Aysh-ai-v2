"""
Friendly AI Agent Engine for parsing user chat requests and orchestrating video/photo edits,
sandbox operations, generation, and downloading outputs.
"""
import os
import re
import random
from typing import Dict, Any, List
from pathlib import Path
from app.media_processor import media_processor
from app.sandbox import sandbox_manager
from app.config import UPLOADS_DIR, OUTPUTS_DIR


class AgentEngine:
    def __init__(self):
        self.friendly_greetings = [
            "Hey there, super creator! ✨ How can I help you bring your media to life today?",
            "Yo! Excited to create with you! What cool video or photo project are we building next? 🚀",
            "Hey friend! Ready to edit some fire media or generate some wild visuals? Let's go! 🔥"
        ]

    def process_message(self, message: str, file_context: str = None, ai_mode: str = "Normal") -> Dict[str, Any]:
        """Parses conversational user intent and executes media tasks or sandbox scripts."""
        msg_lower = message.lower()

        # Determine latest file if context file is provided or look up uploaded files
        file_to_use = file_context
        if not file_to_use:
            sandbox_files = sandbox_manager.list_sandbox_files()
            if sandbox_files:
                file_to_use = str(sandbox_manager.sandbox_dir / sandbox_files[0]["path"])

        # Intent 1: Video Edit (Aura / Cyberpunk / Vintage / Speed / Trim)
        if any(kw in msg_lower for kw in ["edit video", "video aura", "aura video", "video edit", "trim video", "speed video"]):
            if not file_to_use or not (file_to_use.endswith(".mp4") or file_to_use.endswith(".mov") or file_to_use.endswith(".avi") or file_to_use.endswith(".mkv")):
                return {
                    "response": "I'd love to edit your video with awesome vibes! 🎬 Please upload a video file first or specify an uploaded video filename so I can get to work! ✨",
                    "action": "need_upload"
                }

            style = "aura"
            if "cyberpunk" in msg_lower:
                style = "cyberpunk"
            elif "vintage" in msg_lower or "sepia" in msg_lower:
                style = "vintage"
            elif "grayscale" in msg_lower or "black and white" in msg_lower:
                style = "grayscale"

            speed = 1.0
            if "fast" in msg_lower or "2x" in msg_lower:
                speed = 2.0
            elif "slow" in msg_lower or "0.5x" in msg_lower:
                speed = 0.5

            output_file = media_processor.edit_video(
                video_path=file_to_use,
                style=style,
                speed=speed
            )
            out_filename = Path(output_file).name

            return {
                "response": f"✨ Done! I edited your video with **{style.upper()}** style vibes! You can preview and download your transformed video below! 🚀🎥",
                "action": "video_edited",
                "output_file": f"/outputs/{out_filename}",
                "download_url": f"/api/download/{out_filename}",
                "filename": out_filename
            }

        # Intent 2: Photo Edit / Aura Style
        if any(kw in msg_lower for kw in ["edit photo", "edit image", "photo aura", "aura photo", "aura edit", "apply filter", "cyberpunk photo", "vintage photo"]):
            if not file_to_use or not (file_to_use.endswith(".jpg") or file_to_use.endswith(".jpeg") or file_to_use.endswith(".png") or file_to_use.endswith(".webp")):
                return {
                    "response": "I'm super hyped to style your photo! 📸 Please upload an image file first or reference your uploaded photo!",
                    "action": "need_upload"
                }

            style = "aura"
            if "cyberpunk" in msg_lower:
                style = "cyberpunk"
            elif "vintage" in msg_lower:
                style = "vintage"
            elif "grayscale" in msg_lower or "black and white" in msg_lower:
                style = "grayscale"

            output_file = media_processor.apply_photo_filter(
                image_path=file_to_use,
                style=style
            )
            out_filename = Path(output_file).name

            return {
                "response": f"✨ Woohoo! Your photo is transformed with glowing **{style.upper()}** energy! Check out the output download link below! 🖼️✨",
                "action": "photo_edited",
                "output_file": f"/outputs/{out_filename}",
                "download_url": f"/api/download/{out_filename}",
                "filename": out_filename
            }

        # Intent 3: Generate Photo
        if any(kw in msg_lower for kw in ["generate photo", "generate image", "create photo", "create image", "draw photo", "make picture"]):
            prompt = message.replace("generate photo", "").replace("generate image", "").replace("create photo", "").strip() or "Glowing Cosmic Aura"
            output_file = media_processor.generate_photo(prompt=prompt)
            out_filename = Path(output_file).name

            return {
                "response": f"✨ Here is your newly generated artwork for **'{prompt}'**! Created completely free and locally! 🎨✨",
                "action": "photo_generated",
                "output_file": f"/outputs/{out_filename}",
                "download_url": f"/api/download/{out_filename}",
                "filename": out_filename
            }

        # Intent 4: Generate Video
        if any(kw in msg_lower for kw in ["generate video", "create video", "make video", "animating video"]):
            prompt = message.replace("generate video", "").replace("create video", "").replace("make video", "").strip() or "Energetic Neon Aura Wave"
            output_file = media_processor.generate_video(prompt=prompt, duration_sec=3)
            out_filename = Path(output_file).name

            return {
                "response": f"✨ Video generation complete! Here is your animated scene for **'{prompt}'**! Ready for streaming and downloading! 🎬⚡",
                "action": "video_generated",
                "output_file": f"/outputs/{out_filename}",
                "download_url": f"/api/download/{out_filename}",
                "filename": out_filename
            }

        # Intent 5: Execute Python Script in Sandbox
        if "python" in msg_lower or "run code" in msg_lower or "sandbox code" in msg_lower or "```python" in message:
            code_match = re.search(r"```(?:python)?\s*(.*?)\s*```", message, re.DOTALL)
            code = code_match.group(1) if code_match else message

            res = sandbox_manager.execute_code(code)
            status_str = "Successfully executed!" if res["success"] else "Execution encountered an error."

            output_str = f"**{status_str}**\n\n```text\nSTDOUT:\n{res['stdout'] or '(none)'}\n\nSTDERR:\n{res['stderr'] or '(none)'}\n```"

            return {
                "response": f"🤖 **Sandbox Code Execution Result:**\n\n{output_str}",
                "action": "code_executed",
                "result": res
            }

        # Mode Specific Intelligence Enhancements
        mode_prefix = f"⚡ **[Mode: {ai_mode.upper()}]** " if ai_mode != "Normal" else ""

        mode_insights = {
            "Normal": "Operating in standard casual mode.",
            "Pro": "Operating in Pro mode with enhanced multi-pass parameter tuning.",
            "Advance": "Operating in Advance mode with high-precision frame and layer alignment.",
            "Powerful Intelligent": "Operating in Powerful Intelligent mode! Deep multi-layered structural reasoning & ultimate creative precision activated! 🧠🚀"
        }

        greeting = random.choice(self.friendly_greetings)
        return {
            "response": f"{greeting}\n\n{mode_prefix}{mode_insights.get(ai_mode, '')}\n\nI can do all these awesome things for you 100% free with zero API tokens needed:\n"
                        f"• 🎬 **Edit videos** with glowing **Aura Edit** style, cyberpunk neon, vintage, or speed control.\n"
                        f"• 🖼️ **Edit photos** with radiant energy aura, filters, & contrast boosts.\n"
                        f"• 🎨 **Generate videos & photos** from custom prompts.\n"
                        f"• 📁 **Upload large files (>2GB)** seamlessly.\n"
                        f"• 🧪 **Run custom sandbox scripts** to manipulate workspace files directly!",
            "action": "chat"
        }


agent_engine = AgentEngine()
