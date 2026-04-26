"""
grok_video_gen.py - PMS_GrokVideoGen v2.0.0
=============================================
Generacion de video con Grok via API asincrona de xAI.
Endpoint submit:  POST https://api.x.ai/v1/videos/generations
Endpoint polling: GET  https://api.x.ai/v1/videos/{request_id}
Modelo: grok-imagine-video
Polling cada 5s. Timeout 300s.

Output: URL del MP4 generado (STRING).
Conectar la URL a VHS Load Video From URL para usar en el pipeline.

Nota source_image: si el input esta conectado, se codifica como data URI
y se envia en el campo image.url. Si xAI no acepta data URIs en ese campo,
el nodo continua en modo text-to-video ignorando la imagen.
TODO: xAI video image-to-video requiere URL publica. Implementar upload temporal.
"""

import os
import base64
import time
import io
import logging
import requests
import torch
import numpy as np

logger = logging.getLogger("ComfyUI_PromptModels")

_XAI_BASE       = "https://api.x.ai/v1"
_VIDEO_MODEL    = "grok-imagine-video"
_POLL_INTERVAL  = 5
_POLL_TIMEOUT   = 300


class PMS_GrokVideoGen:
    """
    Grok Video Gen. Genera video con xAI.
    Output: URL del MP4. Conectar a VHS Load Video From URL para usar en el pipeline.
    source_image: activa image-to-video si esta conectada.
    Anti-crash: devuelve string vacio y log de error si falla.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "prompt": ("STRING", {
                    "multiline": True,
                    "default": "A cinematic shot of a futuristic neon city.",
                }),
                "duration": ("INT", {
                    "default": 8, "min": 1, "max": 15, "step": 1,
                    "tooltip": "Duracion del video en segundos (1-15).",
                }),
                "aspect_ratio": (["16:9", "9:16", "1:1", "4:3"], {"default": "16:9"}),
                "resolution": (["720p", "1080p"], {"default": "720p"}),
            },
            "optional": {
                "source_image": ("IMAGE", {
                    "tooltip": "Imagen de inicio para image-to-video (opcional).",
                }),
                "api_key": ("STRING", {"default": ""}),
            },
        }

    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("video_url", "status")
    FUNCTION = "generar"
    CATEGORY = "PromptModels/Grok"

    def generar(self, prompt, duration, aspect_ratio, resolution,
                source_image=None, api_key=""):
        key = (api_key or "").strip() or os.getenv("XAI_API_KEY", "")
        if not key:
            logger.error("[PMS_GrokVideoGen] API Key no configurada.")
            return ("", "Error: API Key de xAI requerida.")

        headers = {
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model":        _VIDEO_MODEL,
            "prompt":       prompt,
            "duration":     duration,
            "aspect_ratio": aspect_ratio,
            "resolution":   resolution,
        }

        if source_image is not None:
            try:
                img_tensor = source_image
                if img_tensor.dim() == 4:
                    img_tensor = img_tensor[0]
                img_np  = (img_tensor.cpu().numpy() * 255).clip(0, 255).astype(np.uint8)
                from PIL import Image
                buf = io.BytesIO()
                Image.fromarray(img_np, "RGB").save(buf, format="JPEG", quality=90)
                data_uri = "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()
                # TODO: xAI video image-to-video requiere URL publica. Implementar upload temporal.
                payload["image"] = {"url": data_uri}
                logger.info("[PMS_GrokVideoGen] source_image adjuntada como data URI.")
            except Exception as img_err:
                logger.warning(
                    f"[PMS_GrokVideoGen] No se pudo preparar source_image: {img_err}. "
                    "Continuando en modo text-to-video."
                )

        try:
            logger.info(
                f"[PMS_GrokVideoGen] Submit: {duration}s | {resolution} | {aspect_ratio}"
            )
            submit_resp = requests.post(
                f"{_XAI_BASE}/videos/generations",
                headers=headers,
                json=payload,
                timeout=60,
            )
            if not submit_resp.ok:
                msg = _extract_error(submit_resp)
                logger.error(f"[PMS_GrokVideoGen] Error en submit: {msg}")
                return ("", f"Error submit: {msg}")

            submit_data = submit_resp.json()
            request_id = submit_data.get("request_id") or submit_data.get("id")
            if not request_id:
                return ("", f"Error: no se recibio request_id. Respuesta: {submit_data}")

            logger.info(f"[PMS_GrokVideoGen] request_id={request_id}. Polling cada {_POLL_INTERVAL}s...")

            elapsed = 0
            while elapsed < _POLL_TIMEOUT:
                time.sleep(_POLL_INTERVAL)
                elapsed += _POLL_INTERVAL

                poll_resp = requests.get(
                    f"{_XAI_BASE}/videos/{request_id}",
                    headers=headers,
                    timeout=30,
                )
                if not poll_resp.ok:
                    msg = _extract_error(poll_resp)
                    logger.error(f"[PMS_GrokVideoGen] Polling error: {msg}")
                    return ("", f"Error polling: {msg}")

                poll_data = poll_resp.json()
                status = poll_data.get("status", "")

                if status == "done":
                    video_url = poll_data.get("video", {}).get("url", "")
                    if not video_url:
                        return ("", "Error: video done pero sin URL en la respuesta.")
                    logger.info(f"[PMS_GrokVideoGen] Video listo tras {elapsed}s: {video_url}")
                    return (video_url, "done")

                if status in ("failed", "expired"):
                    return ("", f"Error: video status={status}")

                logger.info(f"[PMS_GrokVideoGen] status={status} | {elapsed}s/{_POLL_TIMEOUT}s")

            return ("", f"Error: timeout {_POLL_TIMEOUT}s alcanzado sin respuesta.")

        except Exception as e:
            logger.error(f"[PMS_GrokVideoGen] Error: {e}")
            return ("", f"Error: {str(e)}")


def _extract_error(response) -> str:
    try:
        data = response.json()
        err = data.get("error", "")
        if isinstance(err, dict):
            return err.get("message", str(err))
        return str(err) or response.text[:200]
    except Exception:
        return response.text[:200]
