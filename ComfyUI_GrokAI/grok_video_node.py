"""
grok_video_node.py — Grok Video Forge
======================================
Nodo para generación y edición de video con xAI Grok Video Forge.

Modos soportados:
  - Texto → Video  : Solo prompt + parámetros
  - Imagen → Video : Imagen inicial como primer frame
  - Video  → Video : Edición de estilo con video de referencia

Nota: La generación de video es inherentemente lenta (30–120 segundos).
El nodo implementa un timeout extendido y no bloqueará ComfyUI gracias
al manejo robusto de excepciones.

Autor: Prompt Models Studio — xAI Integration Layer v2.0
"""

import logging
import torch
from typing import Optional

from .grok_core import (
    PayloadRouter,
    tensor_to_base64,
    sample_video_frames,
    pil_to_tensor,
    DEFAULT_VIDEO_MODEL,
    VIDEO_TIMEOUT,
)

log = logging.getLogger("ComfyUI_Grok")

# Modelos de video disponibles
VIDEO_MODELS = [
    "grok-video-forge",
    "grok-video-forge-turbo",
]

VIDEO_SIZES = [
    "1280x720",
    "720x1280",
    "1920x1080",
    "1080x1920",
    "1024x576",
    "576x1024",
]

VIDEO_DURATIONS = [3, 4, 5, 6, 8, 10]


class Grok_Video_Forge:
    """
    [v2.0] Nodo de generación y edición de video con Grok Video Forge.

    MODO 1 — Texto a Video:
      Solo `prompt` + parámetros de video.

    MODO 2 — Imagen a Video:
      Conectar `start_image` como primer frame del video generado.

    MODO 3 — Video a Video (Edición de estilo):
      Conectar `reference_video` (tensor [B, H, W, C]).
      Grok analizará su composición y generará uno nuevo siguiendo el prompt.

    Salidas:
      - IMAGE  : Tensor [B, H, W, C] con todos los frames del video
      - INT    : Total de frames en el tensor resultante
      - STRING : Información del proceso y modo utilizado
    """

    CATEGORY     = "Grok/Video"
    FUNCTION     = "forge_video"
    RETURN_TYPES = ("IMAGE", "INT", "STRING")
    RETURN_NAMES = ("video_frames", "frame_count", "info")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "api_key":       ("STRING",       {"default": "", "multiline": False}),
                "prompt":        ("STRING",       {
                    "default": "A cinematic timelapse of a cyberpunk city at night, neon lights reflecting on wet streets, camera slowly pulling back.",
                    "multiline": True
                }),
                "model":         (VIDEO_MODELS,   {"default": "grok-video-forge"}),
                "size":          (VIDEO_SIZES,    {"default": "1280x720"}),
                "duration_sec":  ([str(d) for d in VIDEO_DURATIONS], {"default": "5"}),
                "fps":           ("INT",          {"default": 24, "min": 12, "max": 60, "step": 1}),
                "style_strength":("FLOAT",        {
                    "default": 0.7,
                    "min": 0.1,
                    "max": 1.0,
                    "step": 0.05,
                    "display": "slider"
                }),
                "negative_prompt": ("STRING",     {
                    "default": "blurry, watermark, text overlay, low quality",
                    "multiline": True
                }),
            },
            "optional": {
                # Imagen inicial (convierte imagen → video)
                "start_image":          ("IMAGE",),
                # Video de referencia para edición de estilo
                "reference_video":      ("IMAGE",),
                # Cuántos frames del video de referencia enviar a la API
                "ref_video_max_frames": ("INT", {"default": 6, "min": 1, "max": 16, "step": 1}),
            }
        }

    def forge_video(
        self,
        api_key: str,
        prompt: str,
        model: str,
        size: str,
        duration_sec: str,
        fps: int,
        style_strength: float,
        negative_prompt: str,
        start_image=None,
        reference_video=None,
        ref_video_max_frames: int = 6,
    ):
        # ── Tensor de fallback (1 frame negro) ──────────────────────
        black_frame = torch.zeros(1, 720, 1280, 3)

        try:
            router = PayloadRouter(api_key)
            duration = int(duration_sec)

            # ── Determinar modo ──────────────────────────────────────
            has_start_img = start_image is not None
            has_ref_video = reference_video is not None and reference_video.shape[0] > 1

            if has_ref_video:
                mode = "video-to-video"
            elif has_start_img:
                mode = "imagen-a-video"
            else:
                mode = "texto-a-video"

            log.info(f"[Grok Video Forge] Modo: {mode.upper()}")
            log.info(f"[Grok Video Forge] Duración: {duration}s @ {fps}fps → ~{duration * fps} frames esperados")

            # ── Enriquecer prompt ────────────────────────────────────
            full_prompt = prompt
            if negative_prompt.strip():
                full_prompt += f"\n\nNegative prompt: {negative_prompt}"

            # ── Convertir imagen inicial a Base64 ────────────────────
            start_img_b64 = None
            if has_start_img:
                log.info("[Grok Video Forge] Procesando imagen inicial como primer frame...")
                start_img_b64 = tensor_to_base64(
                    start_image,
                    batch_index=0,
                    format="JPEG",
                    quality=90
                )

            # ── Procesar video de referencia con muestreo ────────────
            ref_video_b64 = None
            if has_ref_video:
                total_ref_frames = reference_video.shape[0]
                log.info(
                    f"[Grok Video Forge] Video referencia: {total_ref_frames} frames. "
                    f"Muestreando {ref_video_max_frames} frames representativos..."
                )

                sampled_frames = sample_video_frames(
                    reference_video,
                    max_frames=ref_video_max_frames,
                    strategy="uniform"
                )

                # Para video-to-video: usar el primer frame muestreado
                # como imagen de referencia (la API acepta imagen, no video completo)
                # En una implementación futura, si la API acepta video, enviar todos
                ref_video_b64 = tensor_to_base64(
                    sampled_frames[0],
                    batch_index=0,
                    format="JPEG",
                    quality=90
                )

                # Añadir contexto del video al prompt
                full_prompt += (
                    f"\n\n[REFERENCIA DE ESTILO: Analiza y replica el estilo visual, "
                    f"composición y paleta de colores del video de referencia. "
                    f"El video tiene {total_ref_frames} frames totales.]"
                )

            # ── Llamada a la API con timeout extendido ───────────────
            log.info(f"[Grok Video Forge] Enviando a API... (timeout: {VIDEO_TIMEOUT}s)")
            video_tensor = router.generate_video(
                prompt=full_prompt,
                model=model,
                duration_seconds=duration,
                fps=fps,
                size=size,
                reference_video_b64=ref_video_b64,
                reference_image_b64=start_img_b64 if not has_ref_video else None,
                style_strength=style_strength
            )

            frame_count = video_tensor.shape[0]
            log.info(f"[Grok Video Forge] Video recibido: {frame_count} frames. Shape: {video_tensor.shape}")

            info = (
                f"✅ Video generado exitosamente\n"
                f"Modo: {mode}\n"
                f"Modelo: {model}\n"
                f"Resolución: {size} | Duración: {duration}s @ {fps}fps\n"
                f"Frames totales: {frame_count}\n"
                f"Style Strength: {style_strength if has_ref_video else 'N/A'}"
            )

            return (video_tensor, frame_count, info)

        except Exception as e:
            error_msg = f"[Grok_Video_Forge ERROR] {e}"
            log.error(error_msg)
            return (black_frame, 0, error_msg)
