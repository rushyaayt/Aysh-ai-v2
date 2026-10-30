"""
Media Processing Module using OpenCV and Pillow.
Supports Photo/Video Aura edits, Cyberpunk, Sepia, Speed, Trim, and Local Visual Generation.
"""
import os
import math
import time
import cv2
from PIL import Image, ImageEnhance, ImageFilter, ImageDraw
from pathlib import Path
from backend.config import OUTPUTS_DIR


class MediaProcessor:
    def __init__(self):
        self.outputs_dir = OUTPUTS_DIR

    def apply_aura_photo_effect(self, input_path: str, output_name: str = None) -> str:
        """Applies dynamic glowing energy aura outlines to an image."""
        if not output_name:
            output_name = f"aura_{Path(input_path).name}"
        output_path = self.outputs_dir / output_name

        img = cv2.imread(str(input_path))
        if img is None:
            raise ValueError("Could not read image file.")

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 100, 200)

        # Create glowing aura mask
        aura_glow = cv2.GaussianBlur(edges, (21, 21), 0)
        aura_colored = cv2.applyColorMap(aura_glow, cv2.COLORMAP_JET)

        # Blend original with glowing edge aura
        blended = cv2.addWeighted(img, 0.8, aura_colored, 0.6, 0)
        cv2.imwrite(str(output_path), blended)
        return str(output_path)

    def apply_cyberpunk_effect(self, input_path: str, output_name: str = None) -> str:
        """Applies neon cyberpunk color scheme."""
        if not output_name:
            output_name = f"cyberpunk_{Path(input_path).name}"
        output_path = self.outputs_dir / output_name

        img = Image.open(input_path).convert("RGB")
        r, g, b = img.split()

        # Boost cyan and magenta
        r = r.point(lambda i: i * 1.2)
        b = b.point(lambda i: i * 1.4)
        g = g.point(lambda i: i * 0.7)

        enhanced = Image.merge("RGB", (r, g, b))
        enhancer = ImageEnhance.Contrast(enhanced)
        enhanced = enhancer.enhance(1.3)

        enhanced.save(str(output_path))
        return str(output_path)

    def generate_photo(self, prompt: str, output_name: str = None) -> str:
        """Generates visual artwork locally using PIL canvas rendering."""
        if not output_name:
            output_name = f"gen_photo_{int(time.time())}.png"
        output_path = self.outputs_dir / output_name

        width, height = 800, 800
        img = Image.new("RGB", (width, height), color=(10, 12, 18))
        draw = ImageDraw.Draw(img)

        # Render vibrant cosmic gradient & shapes
        for radius in range(350, 0, -5):
            color = (
                int(120 + 135 * math.sin(radius / 20.0)),
                int(50 + 100 * math.cos(radius / 30.0)),
                int(200 + 55 * math.sin(radius / 10.0))
            )
            draw.ellipse(
                [width//2 - radius, height//2 - radius, width//2 + radius, height//2 + radius],
                outline=color,
                width=2
            )

        draw.text((width//2 - 140, height//2 - 10), f"Aysh AI Generated:\n{prompt[:30]}", fill=(255, 255, 255))
        img.save(str(output_path))
        return str(output_path)

    def generate_video(self, prompt: str, output_name: str = None) -> str:
        """Generates dynamic animated video clip locally using OpenCV video writer."""
        if not output_name:
            output_name = f"gen_video_{int(time.time())}.mp4"
        output_path = self.outputs_dir / output_name

        width, height = 640, 480
        fps = 24
        duration_sec = 3
        total_frames = fps * duration_sec

        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(str(output_path), fourcc, fps, (width, height))

        for frame_idx in range(total_frames):
            frame = cv2.fillPoly(
                cv2.cvtColor(
                    (cv2.UMat(height, width, cv2.CV_8UC3)).get(), cv2.COLOR_BGR2RGB
                ),
                [],
                (10, 10, 20)
            )
            # Pulsing energetic visual effect
            center_x = int(width / 2 + 100 * math.sin(frame_idx / 5.0))
            center_y = int(height / 2 + 50 * math.cos(frame_idx / 5.0))
            radius = int(40 + 20 * math.sin(frame_idx / 3.0))

            cv2.circle(frame, (center_x, center_y), radius, (255, 0, 240), -1)
            cv2.circle(frame, (center_x, center_y), radius + 15, (0, 240, 255), 3)

            cv2.putText(
                frame,
                f"Aysh AI Video: {prompt[:20]}",
                (30, 50),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (255, 255, 255),
                2
            )
            out.write(frame)

        out.release()
        return str(output_path)

    def apply_aura_video_effect(self, input_path: str, output_name: str = None) -> str:
        """Applies dynamic glowing aura video filter frame by frame."""
        if not output_name:
            output_name = f"aura_video_{Path(input_path).name}"
        output_path = self.outputs_dir / output_name

        cap = cv2.VideoCapture(str(input_path))
        if not cap.isOpened():
            raise ValueError("Could not open video file.")

        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)) or 640
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)) or 480
        fps = cap.get(cv2.CAP_PROP_FPS) or 24

        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(str(output_path), fourcc, fps, (width, height))

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            edges = cv2.Canny(gray, 80, 180)
            glow = cv2.GaussianBlur(edges, (15, 15), 0)
            colored_glow = cv2.applyColorMap(glow, cv2.COLORMAP_MAGMA)

            aura_frame = cv2.addWeighted(frame, 0.85, colored_glow, 0.5, 0)
            out.write(aura_frame)

        cap.release()
        out.release()
        return str(output_path)


media_processor = MediaProcessor()
