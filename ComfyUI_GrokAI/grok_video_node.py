# ==============================================================================
# grok_video_node.py — Generador de Video (Grok Video Forge)
# ==============================================================================
# Se conecta a los modelos de video de xAI.
# Convierte automáticamente el archivo MP4 de respuesta en un tensor de ComfyUI
# [Batch, H, W, C] para que pueda ser guardado o procesado por otros nodos.
# ==============================================================================

import os
import requests
import logging
import torch
import numpy as np
import cv2  # Librería estándar en el entorno de ComfyUI
import tempfile
from .grok_core import GrokCore, XAI_API_BASE

log = logging.getLogger("ComfyUI_GrokVideo")

GROK_VIDEO_MODELS = [
    "grok-video-preview",
    "grok-video"
]

class Grok_Video_Forge:
    """
    Nodo V2: Generador de Video (Text-to-Video e Image-to-Video).
    Si se conecta una imagen base, la utiliza como el primer frame (Image-to-Video).
    """
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "prompt": ("STRING", {"multiline": True, "default": "A cinematic shot of a futuristic neon city, camera panning forward."}),
                "model": (GROK_VIDEO_MODELS, {"default": "grok-video-preview"}),
                "fps": ("INT", {"default": 24, "min": 8, "max": 60}),
                "api_key": ("STRING", {"multiline": False, "default": ""}),
            },
            "optional": {
                "reference_image": ("IMAGE",),  # Imagen inicial para Image-to-Video
            }
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("video_frames",)
    FUNCTION = "generate_video"
    CATEGORY = "xAI/Grok"

    def generate_video(self, prompt, model, fps, api_key, reference_image=None):
        key = api_key.strip() or os.getenv("XAI_API_KEY", "")
        core = GrokCore(key) if key else None
        
        if not core:
            log.error("[Grok_Video_Forge] Error: API Key no configurada.")
            return (GrokCore.create_error_tensor(),)

        try:
            url = f"{XAI_API_BASE}/videos/generations"
            payload = {
                "prompt": prompt,
                "model": model,
            }

            # Si hay imagen conectada, la pasamos a base64 para Image-to-Video
            if reference_image is not None:
                log.info("[Grok_Video_Forge] Imagen de referencia detectada (Image-to-Video).")
                img_b64 = core.tensor_to_base64(reference_image, format="JPEG")
                payload["image"] = f"data:image/jpeg;base64,{img_b64}"

            log.info(f"[Grok_Video_Forge] Solicitando video a {model}... (Esto puede tardar varios minutos)")
            
            # Petición HTTP Pura. Timeout alto (10 minutos) porque el video tarda en renderizar
            response = requests.post(url, headers=core.headers, json=payload, timeout=600)
            
            if not response.ok:
                err_msg = response.json().get("error", {}).get("message", response.text)
                log.error(f"[Grok_Video_Forge] Error HTTP {response.status_code}: {err_msg}")
                return (core.create_error_tensor(),)

            res_json = response.json()
            
            # Asumimos que la API devuelve una URL para descargar el archivo .mp4
            # (Estándar en la mayoría de APIs REST de video para 2026)
            video_url = res_json["data"][0]["url"]
            
            log.info("[Grok_Video_Forge] Video generado en la nube. Descargando y decodificando frames...")
            return self._download_and_decode_video(video_url)

        except requests.exceptions.Timeout:
            log.error("[Grok_Video_Forge] Timeout: La generación de video tomó demasiado tiempo.")
            return (GrokCore.create_error_tensor(),)
        except Exception as e:
            log.error(f"[Grok_Video_Forge] Fallo crítico: {str(e)}")
            return (GrokCore.create_error_tensor(),)

    def _download_and_decode_video(self, video_url: str):
        """
        Descarga el MP4 temporalmente y usa OpenCV para extraer los frames
        y convertirlos en un tensor de ComfyUI.
        """
        try:
            # Descargar el video a un archivo temporal
            vid_response = requests.get(video_url, stream=True, timeout=120)
            vid_response.raise_for_status()

            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_vid:
                for chunk in vid_response.iter_content(chunk_size=8192):
                    temp_vid.write(chunk)
                temp_vid_path = temp_vid.name

            # Extraer frames con OpenCV
            cap = cv2.VideoCapture(temp_vid_path)
            frames = []
            
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                # OpenCV lee en BGR, convertimos a RGB
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                # Normalizamos a float32 entre 0.0 y 1.0
                frame_normalized = frame_rgb.astype(np.float32) / 255.0
                frames.append(frame_normalized)

            cap.release()
            os.remove(temp_vid_path) # Limpiar archivo temporal

            if not frames:
                log.error("[Grok_Video_Forge] No se pudieron extraer frames del video.")
                return (GrokCore.create_error_tensor(),)

            # Convertir lista de frames a un solo tensor de PyTorch [Batch, H, W, C]
            # Batch size = número de frames
            video_tensor = torch.from_numpy(np.array(frames))
            log.info(f"[Grok_Video_Forge] Éxito: Tensor de video creado con forma {video_tensor.shape}")
            
            return (video_tensor,)

        except Exception as e:
            log.error(f"[Grok_Video_Forge] Error procesando el archivo de video: {e}")
            return (GrokCore.create_error_tensor(),)
