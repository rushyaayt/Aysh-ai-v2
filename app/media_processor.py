"""
Media processing library for photo and video editing.
Includes standard photo/video edits and signature Aura edit effects.
"""
import os
import math
import uuid
import numpy as np
import cv2
from PIL import Image, ImageEnhance, ImageFilter, ImageDraw
from pathlib import Path
from app.config import OUTPUTS_DIR


class MediaProcessor:
    def __init__(self):
        self.outputs_dir = OUTPUTS_DIR

    def _get_output_path(self, prefix: str, ext: str) -> Path:
        out_name = f"{prefix}_{uuid.uuid4().hex[:8]}.{ext}"
        return self.outputs_dir / out_name

    # ==================== PHOTO EDITING ====================

    def apply_photo_filter(
        self,
        image_path: str,
        style: str = "aura",
        brightness: float = 1.0,
        contrast: float = 1.0,
        saturation: float = 1.0
    ) -> str:
        """Applies filters and adjustments to photos, including signature Aura style."""
        img = Image.open(image_path).convert("RGB")

        # Color adjustments
        if brightness != 1.0:
            img = ImageEnhance.Brightness(img).enhance(brightness)
        if contrast != 1.0:
            img = ImageEnhance.Contrast(img).enhance(contrast)
        if saturation != 1.0:
            img = ImageEnhance.Color(img).enhance(saturation)

        cv_img = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

        if style == "aura":
            # Signature Glowing Aura Edit
            cv_img = self._apply_aura_to_image(cv_img)
        elif style == "cyberpunk":
            # Neon Cyberpunk Blue/Pink Tint
            b, g, r = cv2.split(cv_img)
            r = cv2.addWeighted(r, 0.7, cv2.equalizeHist(r), 0.5, 10)
            b = cv2.addWeighted(b, 0.9, cv2.equalizeHist(b), 0.5, 20)
            cv_img = cv2.merge([b, g, r])
        elif style == "vintage":
            # Vintage Warm Sepia
            sepia_kernel = np.array([
                [0.272, 0.534, 0.131],
                [0.349, 0.686, 0.168],
                [0.393, 0.769, 0.189]
            ])
            cv_img = cv2.transform(cv_img, sepia_kernel)
            cv_img = np.clip(cv_img, 0, 255).astype(np.uint8)
        elif style == "grayscale":
            gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)
            cv_img = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)

        out_path = self._get_output_path("photo", "jpg")
        cv2.imwrite(str(out_path), cv_img)
        return str(out_path)

    def _apply_aura_to_image(self, bgr_img: np.ndarray) -> np.ndarray:
        """Adds a glowing energy aura outline and radiant gradient overlay to an image."""
        h, w, _ = bgr_img.shape
        gray = cv2.cvtColor(bgr_img, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (7, 7), 0)
        edges = cv2.Canny(blurred, 50, 150)

        # Dilate edges to create aura glow mask
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15))
        glow_mask = cv2.dilate(edges, kernel, iterations=3)
        glow_mask_blur = cv2.GaussianBlur(glow_mask, (25, 25), 0)

        # Create neon aura color gradient (Cyan / Electric Purple / Pink)
        aura_color = np.zeros_like(bgr_img)
        for y in range(h):
            for x in range(w):
                # Radial energy pulse color distribution
                aura_color[y, x, 0] = int(255 * (0.5 + 0.5 * math.sin(x / 50))) # Blue
                aura_color[y, x, 1] = int(120 * (0.5 + 0.5 * math.cos(y / 50))) # Green
                aura_color[y, x, 2] = 255                                      # Red

        # Composite glow onto original photo
        glow_3ch = cv2.cvtColor(glow_mask_blur, cv2.COLOR_GRAY2BGR) / 255.0
        aura_layer = (aura_color * glow_3ch).astype(np.uint8)

        result = cv2.addWeighted(bgr_img, 0.85, aura_layer, 0.65, 0)
        return result

    def generate_photo(self, prompt: str) -> str:
        """Generates artistic abstract artwork based on text prompts completely free locally."""
        width, height = 800, 800
        img = Image.new("RGB", (width, height), color=(15, 15, 25))
        draw = ImageDraw.Draw(img)

        # Seed based on prompt text
        seed = sum(ord(c) for c in prompt)
        np.random.seed(seed % 99999)

        colors = [
            (255, 0, 128), (0, 230, 255), (150, 0, 255), (255, 215, 0), (0, 255, 150)
        ]

        # Draw dynamic artistic fluid shapes & aura rings
        for _ in range(30):
            color = colors[np.random.randint(0, len(colors))]
            cx, cy = np.random.randint(100, width - 100), np.random.randint(100, height - 100)
            radius = np.random.randint(40, 250)
            draw.ellipse([cx - radius, cy - radius, cx + radius, cy + radius], outline=color, width=np.random.randint(2, 8))

        # Add title text banner
        draw.text((20, height - 40), f"AI Artwork: '{prompt}'", fill=(255, 255, 255))

        out_path = self._get_output_path("gen_photo", "jpg")
        img.save(out_path)
        return str(out_path)

    # ==================== VIDEO EDITING ====================

    def edit_video(
        self,
        video_path: str,
        style: str = "aura",
        speed: float = 1.0,
        trim_start: float = 0.0,
        trim_end: float = None
    ) -> str:
        """Applies video transformations, speed adjustments, trimming, and Aura Edit style."""
        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        start_frame = int(trim_start * fps)
        end_frame = int(trim_end * fps) if trim_end and trim_end > 0 else total_frames

        out_path = self._get_output_path("edited_video", "mp4")

        # Use mp4v codec for web compatibility
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out_fps = fps * speed if speed > 0 else fps
        out = cv2.VideoWriter(str(out_path), fourcc, out_fps, (width, height))

        current_frame = 0
        frame_idx = 0

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            if current_frame >= start_frame and current_frame <= end_frame:
                processed_frame = self._process_video_frame(frame, style, frame_idx)
                out.write(processed_frame)
                frame_idx += 1

            current_frame += 1
            if current_frame > end_frame:
                break

        cap.release()
        out.release()
        return str(out_path)

    def _process_video_frame(self, frame: np.ndarray, style: str, frame_idx: int) -> np.ndarray:
        """Processes an individual video frame according to selected style."""
        if style == "aura":
            # Dynamic pulsating neon aura on video motion edges
            h, w, _ = frame.shape
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)
            edges = cv2.Canny(blurred, 60, 140)

            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9))
            glow_mask = cv2.dilate(edges, kernel, iterations=2)
            glow_mask_blur = cv2.GaussianBlur(glow_mask, (15, 15), 0)

            aura_color = np.zeros_like(frame)
            pulse = math.sin(frame_idx * 0.15)
            r_val = int(200 + 55 * pulse)
            b_val = int(200 - 55 * pulse)

            aura_color[:, :, 0] = b_val # Blue
            aura_color[:, :, 1] = 50   # Green
            aura_color[:, :, 2] = r_val # Red

            glow_3ch = cv2.cvtColor(glow_mask_blur, cv2.COLOR_GRAY2BGR) / 255.0
            aura_layer = (aura_color * glow_3ch).astype(np.uint8)

            result = cv2.addWeighted(frame, 0.85, aura_layer, 0.7, 0)
            return result

        elif style == "cyberpunk":
            b, g, r = cv2.split(frame)
            r = cv2.addWeighted(r, 0.8, cv2.equalizeHist(r), 0.4, 15)
            b = cv2.addWeighted(b, 1.0, cv2.equalizeHist(b), 0.4, 25)
            return cv2.merge([b, g, r])

        elif style == "vintage":
            sepia_kernel = np.array([
                [0.272, 0.534, 0.131],
                [0.349, 0.686, 0.168],
                [0.393, 0.769, 0.189]
            ])
            res = cv2.transform(frame, sepia_kernel)
            return np.clip(res, 0, 255).astype(np.uint8)

        elif style == "grayscale":
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            return cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)

        return frame

    def generate_video(self, prompt: str, duration_sec: int = 3) -> str:
        """Generates animated video based on text prompt completely free locally."""
        fps = 24
        total_frames = duration_sec * fps
        width, height = 640, 480

        out_path = self._get_output_path("gen_video", "mp4")
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(str(out_path), fourcc, fps, (width, height))

        seed = sum(ord(c) for c in prompt)
        np.random.seed(seed % 9999)

        for i in range(total_frames):
            frame = np.zeros((height, width, 3), dtype=np.uint8)
            t = i / fps

            # Draw glowing energetic wave / aura particles moving over time
            for p in range(15):
                cx = int(width / 2 + 150 * math.sin(t * 3 + p))
                cy = int(height / 2 + 100 * math.cos(t * 2 + p * 0.5))
                radius = int(25 + 15 * math.sin(t * 5 + p))
                color = (
                    int(127 + 127 * math.sin(t + p)),
                    int(127 + 127 * math.cos(t * 1.5 + p)),
                    255
                )
                cv2.circle(frame, (cx, cy), radius, color, -1)

            # Add prompt banner text
            cv2.putText(frame, f"AI Video: {prompt[:30]}", (20, height - 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

            out.write(frame)

        out.release()
        return str(out_path)


media_processor = MediaProcessor()
