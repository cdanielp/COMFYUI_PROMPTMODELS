# ==============================================================================
# grok_video_node.py - Generador de Video (Grok Video Forge)
# ==============================================================================
# Conecta con la API asincrona de video de xAI (grok-imagine-video).
#
# Flujo:
#   1. POST /v1/videos/generations -> recibe request_id
#   2. GET  /v1/videos/{request_id} cada N segundos (polling)
#   3. Cuando status == "done" -> descarga video.url -> extrae frames -> tensor
#
# Soporta: Text-to-Video, Image-to-Video, Video Editing, Video Extension.
# ==============================================================================

import os
import requests
import logging
import torch
import numpy as np
import cv2
import tempfile
from .grok_core import GrokCore, VIDEO_MODELS, VIDEO_ASPECT_RATIOS

log = logging.getLogger("ComfyUI_GrokVideo")


class Grok_Video_Forge:
    """
    Nodo V2: Generador de Video con API asincrona de xAI.

    POST /v1/videos/generations -> request_id
    GET  /v1/videos/{request_id} -> polling hasta status='done'
    Descarga MP4 -> OpenCV -> tensor [B, H, W, C]
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "prompt": ("STRING", {
                    "multiline": True,
                    "default": "A cinematic shot of a futuristic neon city, camera panning forward.",
                }),
                "model": (VIDEO_MODELS, {"default": "grok-imagine-video"}),
                "duration": ("INT", {
                    "default": 5, "min": 1, "max": 15, "step": 1,
                    "tooltip": "Duracion del video en segundos (1-15).",
                }),
                "aspect_ratio": (VIDEO_ASPECT_RATIOS, {"default": "16:9"}),
                "resolution": (["480p", "720p"], {"default": "720p"}),
                "api_key": ("STRING", {"multiline": False, "default": ""}),
            },
            "optional": {
                "reference_image": ("IMAGE",),
                "timeout": ("INT", {
                    "default": 300, "min": 60, "max": 600, "step": 30,
                    "tooltip": "Timeout maximo en segundos para el polling.",
                }),
                "poll_interval": ("INT", {
                    "default": 5, "min": 2, "max": 30, "step": 1,
                    "tooltip": "Intervalo entre cada check de status (segundos).",
                }),
            },
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("video_frames",)
    FUNCTION = "generate_video"
    CATEGORY = "xAI/Grok"

    def generate_video(self, prompt, model, duration, aspect_ratio, resolution,
                       api_key, reference_image=None, timeout=300, poll_interval=5):
        key = api_key.strip() or os.getenv("XAI_API_KEY", "")
        if not key:
            log.error("[Grok_Video_Forge] API Key no configurada.")
            return (GrokCore.create_error_tensor(),)

        try:
            core = GrokCore(key)

            # -- Construir payload --
            payload = {
                "prompt": prompt,
                "model": model,
                "duration": duration,
                "aspect_ratio": aspect_ratio,
                "resolution": resolution,
            }

            # Image-to-Video: imagen como primer frame
            if reference_image is not None:
                log.info("[Grok_Video_Forge] Imagen de referencia detectada (Image-to-Video).")
                img_b64 = core.tensor_to_base64(reference_image, format="JPEG")
                payload["image"] = f"data:image/jpeg;base64,{img_b64}"

            # -- Paso 1: Submit (obtener request_id) --
            log.info(f"[Grok_Video_Forge] Solicitando video ({duration}s, {resolution})...")
            submit_res = core.submit_video("/videos/generations", payload)

            if submit_res.get("error"):
                log.error(f"[Grok_Video_Forge] Error en submit: {submit_res.get('message')}")
                return (GrokCore.create_error_tensor(),)

            request_id = submit_res.get("request_id") or submit_res.get("id")
            if not request_id:
                log.error(f"[Grok_Video_Forge] No se recibio request_id: {submit_res}")
                return (GrokCore.create_error_tensor(),)

            log.info(f"[Grok_Video_Forge] request_id: {request_id}. Polling...")

            # -- Paso 2: Polling hasta status='done' --
            poll_res = core.poll_video(request_id, timeout=timeout, interval=poll_interval)

            if poll_res.get("error"):
                log.error(f"[Grok_Video_Forge] Polling error: {poll_res.get('message')}")
                return (GrokCore.create_error_tensor(),)

            # -- Paso 3: Extraer URL y descargar --
            video_data = poll_res.get("video", {})
            video_url = video_data.get("url", "")

            if not video_url:
                log.error(f"[Grok_Video_Forge] No video.url en respuesta: {poll_res}")
                return (GrokCore.create_error_tensor(),)

            log.info("[Grok_Video_Forge] Video generado. Descargando frames...")
            return self._download_and_decode_video(video_url)

        except Exception as e:
            log.error(f"[Grok_Video_Forge] Fallo critico: {str(e)}")
            return (GrokCore.create_error_tensor(),)

    def _download_and_decode_video(self, video_url: str):
        """Descarga MP4 y extrae frames como tensor [B, H, W, C]."""
        try:
            vid_response = requests.get(video_url, stream=True, timeout=120)
            vid_response.raise_for_status()

            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_vid:
                for chunk in vid_response.iter_content(chunk_size=8192):
                    temp_vid.write(chunk)
                temp_vid_path = temp_vid.name

            cap = cv2.VideoCapture(temp_vid_path)
            frames = []

            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frames.append(frame_rgb.astype(np.float32) / 255.0)

            cap.release()
            os.remove(temp_vid_path)

            if not frames:
                log.error("[Grok_Video_Forge] No se extrajeron frames.")
                return (GrokCore.create_error_tensor(),)

            video_tensor = torch.from_numpy(np.array(frames))
            log.info(f"[Grok_Video_Forge] Tensor: {video_tensor.shape}")
            return (video_tensor,)

        except Exception as e:
            log.error(f"[Grok_Video_Forge] Error procesando video: {e}")
            return (GrokCore.create_error_tensor(),)


# ======================================================================
# NODO: Video Editor - POST /v1/videos/edits
# ======================================================================
class Grok_Video_Editor:
    """
    Edita un video existente con lenguaje natural.
    POST /v1/videos/edits con video_url + prompt.
    Preserva contenido no mencionado; modifica solo lo pedido.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "video_url": ("STRING", {
                    "default": "",
                    "tooltip": "URL del video a editar (temporal de xAI u otra URL publica).",
                }),
                "prompt": ("STRING", {
                    "multiline": True,
                    "default": "Change the sky to a dramatic sunset.",
                }),
                "model": (VIDEO_MODELS, {"default": "grok-imagine-video"}),
                "api_key": ("STRING", {"multiline": False, "default": ""}),
            },
            "optional": {
                "timeout": ("INT", {"default": 300, "min": 60, "max": 600, "step": 30}),
                "poll_interval": ("INT", {"default": 5, "min": 2, "max": 30, "step": 1}),
            },
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("video_frames",)
    FUNCTION = "edit_video"
    CATEGORY = "xAI/Grok"

    def edit_video(self, video_url, prompt, model, api_key,
                   timeout=300, poll_interval=5):
        key = api_key.strip() or os.getenv("XAI_API_KEY", "")
        if not key:
            return (GrokCore.create_error_tensor(),)

        try:
            core = GrokCore(key)
            payload = {
                "video_url": video_url,
                "prompt": prompt,
                "model": model,
            }

            log.info("[Grok_Video_Editor] Enviando edicion de video...")
            submit_res = core.submit_video("/videos/edits", payload)

            if submit_res.get("error"):
                log.error(f"[Grok_Video_Editor] Error: {submit_res.get('message')}")
                return (GrokCore.create_error_tensor(),)

            request_id = submit_res.get("request_id") or submit_res.get("id")
            if not request_id:
                return (GrokCore.create_error_tensor(),)

            poll_res = core.poll_video(request_id, timeout=timeout, interval=poll_interval)
            if poll_res.get("error"):
                return (GrokCore.create_error_tensor(),)

            video_data = poll_res.get("video", {})
            url = video_data.get("url", "")
            if not url:
                return (GrokCore.create_error_tensor(),)

            return Grok_Video_Forge._download_and_decode_video(None, url)

        except Exception as e:
            log.error(f"[Grok_Video_Editor] Fallo: {str(e)}")
            return (GrokCore.create_error_tensor(),)


# ======================================================================
# NODO: Video Extension - POST /v1/videos/extensions
# ======================================================================
class Grok_Video_Extension:
    """
    Extiende un video existente con contenido nuevo.
    POST /v1/videos/extensions con video_url + prompt + duration.
    Duration controla solo la extension (ej: 10s original + 5s ext = 15s total).
    Maximo total: 15 segundos.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "video_url": ("STRING", {
                    "default": "",
                    "tooltip": "URL del video a extender.",
                }),
                "prompt": ("STRING", {
                    "multiline": True,
                    "default": "Continue the scene with an explosion in the background.",
                }),
                "model": (VIDEO_MODELS, {"default": "grok-imagine-video"}),
                "duration": ("INT", {
                    "default": 5, "min": 2, "max": 10, "step": 1,
                    "tooltip": "Duracion de la extension en segundos (2-10). Se suma al video original.",
                }),
                "api_key": ("STRING", {"multiline": False, "default": ""}),
            },
            "optional": {
                "timeout": ("INT", {"default": 300, "min": 60, "max": 600, "step": 30}),
                "poll_interval": ("INT", {"default": 5, "min": 2, "max": 30, "step": 1}),
            },
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("video_frames",)
    FUNCTION = "extend_video"
    CATEGORY = "xAI/Grok"

    def extend_video(self, video_url, prompt, model, duration, api_key,
                     timeout=300, poll_interval=5):
        key = api_key.strip() or os.getenv("XAI_API_KEY", "")
        if not key:
            return (GrokCore.create_error_tensor(),)

        try:
            core = GrokCore(key)
            payload = {
                "video_url": video_url,
                "prompt": prompt,
                "model": model,
                "duration": duration,
            }

            log.info(f"[Grok_Video_Extension] Extendiendo video +{duration}s...")
            submit_res = core.submit_video("/videos/extensions", payload)

            if submit_res.get("error"):
                log.error(f"[Grok_Video_Extension] Error: {submit_res.get('message')}")
                return (GrokCore.create_error_tensor(),)

            request_id = submit_res.get("request_id") or submit_res.get("id")
            if not request_id:
                return (GrokCore.create_error_tensor(),)

            poll_res = core.poll_video(request_id, timeout=timeout, interval=poll_interval)
            if poll_res.get("error"):
                return (GrokCore.create_error_tensor(),)

            video_data = poll_res.get("video", {})
            url = video_data.get("url", "")
            if not url:
                return (GrokCore.create_error_tensor(),)

            return Grok_Video_Forge._download_and_decode_video(None, url)

        except Exception as e:
            log.error(f"[Grok_Video_Extension] Fallo: {str(e)}")
            return (GrokCore.create_error_tensor(),)
