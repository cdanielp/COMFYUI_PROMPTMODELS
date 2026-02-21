"""
google_video_node.py - Nodos de Video para ComfyUI (V2.1)
==========================================================
Veo 3.1 | Cascada Async (todas las FUNCTION son async def)
⚡ FPS de salida: 24. Configurar VHS Video Combine a 24 FPS.

V2.1 Cambios:
  - Todas las funciones FUNCTION → async def + await (cascada async)
  - NO hay seed manual (Veo 3.1 no lo soporta → HTTP 400)
  - VideoStoryboard mantiene 3 puertos reference_image opcionales
  - Error HTTP 400/safety → create_error_image() sin crash

Autor: Prompt Models Studio | cdanielp
"""

import logging
import torch
from .google_core import (
    GoogleAICore, VEO_RESOLUTION_PRESETS, VEO_DURATION_OPTIONS, DEFAULT_VIDEO_MODEL,
)

logger = logging.getLogger("ComfyUI_GoogleAI")

RESOLUTION_OPTIONS = list(VEO_RESOLUTION_PRESETS.keys())
DURATION_OPTIONS = [str(d) for d in VEO_DURATION_OPTIONS]
VIDEO_MODELS = ["veo-3.1", "veo-3.0-generate-preview", "veo-2.0-generate-001"]


class GoogleAI_VideoGenerator:
    """
    Genera video con Veo 3.1 (async).
    1 frame → Image-to-Video | >1 frame → Video Extension (último frame).
    ⚠️ Sin seed manual — la API de Veo no lo soporta.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "prompt": ("STRING", {
                    "multiline": True,
                    "default": "A cinematic drone shot flying over a mountain range at sunrise",
                }),
                "model": (VIDEO_MODELS, {"default": "veo-3.1"}),
                "video_preset": (RESOLUTION_OPTIONS, {"default": "1920x1080 (16:9)"}),
                "duration_seconds": (DURATION_OPTIONS, {"default": "6"}),
            },
            "optional": {
                "api_key": ("STRING", {"default": ""}),
                "init_image_or_video": ("IMAGE", {
                    "tooltip": "1 frame=Img2Vid, >1 frames=Extension (usa último frame).",
                }),
                "negative_prompt": ("STRING", {"multiline": True, "default": ""}),
            },
        }

    RETURN_TYPES = ("IMAGE", "STRING",)
    RETURN_NAMES = ("video_frames", "cost_estimate",)
    FUNCTION = "generate_video"
    CATEGORY = "Google AI/Video"

    async def generate_video(self, prompt, model, video_preset, duration_seconds,
                             api_key="", init_image_or_video=None, negative_prompt=""):
        try:
            key = GoogleAICore.resolve_api_key(api_key)
            duration = int(duration_seconds)
            cost_str = GoogleAICore.estimate_video_cost(duration)

            init_images_b64 = None
            if init_image_or_video is not None:
                num_frames = init_image_or_video.shape[0]
                if num_frames == 1:
                    logger.info("[VideoGenerator] Modo: Image-to-Video (1 frame)")
                    init_images_b64 = [GoogleAICore.tensor_to_base64(init_image_or_video, 0)]
                else:
                    logger.info(f"[VideoGenerator] Modo: Video Extension ({num_frames} frames → último)")
                    init_images_b64 = [GoogleAICore.tensor_to_base64(init_image_or_video, num_frames - 1)]

            full_prompt = prompt
            if negative_prompt:
                full_prompt += f"\n\nNegative: {negative_prompt}"

            # await al core asíncrono
            video_bytes = await GoogleAICore.generate_video(
                api_key=key,
                prompt=full_prompt,
                model=model,
                resolution_preset=video_preset,
                duration_seconds=duration,
                init_images_b64=init_images_b64,
            )

            video_tensor = GoogleAICore.video_bytes_to_tensor(video_bytes)
            logger.info(
                f"[VideoGenerator] ✅ {video_tensor.shape[0]} frames @ 24 FPS | {cost_str}"
            )
            logger.info(
                "[Veo 3.1] ⚠️ IMPORTANTE: El video tiene un estándar de 24 FPS. "
                "Configura tu VHS Video Combine a 24 FPS."
            )
            return (video_tensor, cost_str,)

        except RuntimeError as e:
            error_msg = str(e)
            if "400" in error_msg or "safety" in error_msg.lower() or "block" in error_msg.lower():
                logger.warning(f"[VideoGenerator] Violación de seguridad: {error_msg}")
            else:
                logger.error(f"[VideoGenerator] Error: {error_msg}")
            return (
                GoogleAICore.create_error_image(error_msg),
                f"❌ Error - {GoogleAICore.estimate_video_cost(int(duration_seconds))}",
            )

        except Exception as e:
            logger.error(f"[VideoGenerator] Error inesperado: {e}")
            return (
                GoogleAICore.create_error_image(str(e)),
                f"❌ Error - {GoogleAICore.estimate_video_cost(int(duration_seconds))}",
            )


class GoogleAI_VideoInterpolation:
    """
    Interpola entre first_frame y last_frame (async).
    El last_frame se redimensiona automáticamente al tamaño del first_frame.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "first_frame": ("IMAGE",),
                "last_frame": ("IMAGE", {
                    "tooltip": "Se redimensiona automáticamente al tamaño del first_frame.",
                }),
                "prompt": ("STRING", {
                    "multiline": True,
                    "default": "A smooth cinematic transition between two scenes",
                }),
                "model": (VIDEO_MODELS, {"default": "veo-3.1"}),
                "video_preset": (RESOLUTION_OPTIONS, {"default": "1920x1080 (16:9)"}),
                "duration_seconds": (DURATION_OPTIONS, {"default": "6"}),
            },
            "optional": {
                "api_key": ("STRING", {"default": ""}),
            },
        }

    RETURN_TYPES = ("IMAGE", "STRING",)
    RETURN_NAMES = ("video_frames", "cost_estimate",)
    FUNCTION = "interpolate"
    CATEGORY = "Google AI/Video"

    async def interpolate(self, first_frame, last_frame, prompt, model,
                          video_preset, duration_seconds, api_key=""):
        try:
            key = GoogleAICore.resolve_api_key(api_key)
            duration = int(duration_seconds)
            cost_str = GoogleAICore.estimate_video_cost(duration)

            last_resized = GoogleAICore.resize_tensor_to_match(last_frame, first_frame)
            first_b64 = GoogleAICore.tensor_to_base64(first_frame, 0)
            last_b64 = GoogleAICore.tensor_to_base64(last_resized, 0)

            # await al core asíncrono
            video_bytes = await GoogleAICore.generate_video(
                api_key=key,
                prompt=prompt,
                model=model,
                resolution_preset=video_preset,
                duration_seconds=duration,
                init_images_b64=[first_b64],
                last_frame_b64=last_b64,
            )

            video_tensor = GoogleAICore.video_bytes_to_tensor(video_bytes)
            logger.info(
                f"[VideoInterpolation] ✅ {video_tensor.shape[0]} frames @ 24 FPS | {cost_str}"
            )
            logger.info(
                "[Veo 3.1] ⚠️ IMPORTANTE: El video tiene un estándar de 24 FPS. "
                "Configura tu VHS Video Combine a 24 FPS."
            )
            return (video_tensor, cost_str,)

        except RuntimeError as e:
            error_msg = str(e)
            if "400" in error_msg or "safety" in error_msg.lower() or "block" in error_msg.lower():
                logger.warning(f"[VideoInterpolation] Violación de seguridad: {error_msg}")
            else:
                logger.error(f"[VideoInterpolation] Error: {error_msg}")
            return (
                GoogleAICore.create_error_image(error_msg),
                f"❌ Error - {GoogleAICore.estimate_video_cost(int(duration_seconds))}",
            )

        except Exception as e:
            logger.error(f"[VideoInterpolation] Error inesperado: {e}")
            return (
                GoogleAICore.create_error_image(str(e)),
                f"❌ Error - {GoogleAICore.estimate_video_cost(int(duration_seconds))}",
            )


class GoogleAI_VideoStoryboard:
    """
    Video estilizado con hasta 3 imágenes de referencia (async).
    ⚠️ Con referencias, duración forzada a 8s (restricción API).
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "prompt": ("STRING", {
                    "multiline": True,
                    "default": "A stylized animated scene with vibrant colors",
                }),
                "model": (VIDEO_MODELS, {"default": "veo-3.1"}),
                "video_preset": (RESOLUTION_OPTIONS, {"default": "1920x1080 (16:9)"}),
                "duration_seconds": (DURATION_OPTIONS, {
                    "default": "8",
                    "tooltip": "⚠️ Se forza a 8s cuando hay imágenes de referencia.",
                }),
            },
            "optional": {
                "api_key": ("STRING", {"default": ""}),
                "reference_image_1": ("IMAGE", {"tooltip": "Imagen de referencia 1."}),
                "reference_image_2": ("IMAGE", {"tooltip": "Imagen de referencia 2."}),
                "reference_image_3": ("IMAGE", {"tooltip": "Imagen de referencia 3."}),
            },
        }

    RETURN_TYPES = ("IMAGE", "STRING",)
    RETURN_NAMES = ("video_frames", "cost_estimate",)
    FUNCTION = "generate_storyboard"
    CATEGORY = "Google AI/Video"

    async def generate_storyboard(self, prompt, model, video_preset, duration_seconds,
                                  api_key="", reference_image_1=None,
                                  reference_image_2=None, reference_image_3=None):
        try:
            key = GoogleAICore.resolve_api_key(api_key)
            duration = int(duration_seconds)

            ref_b64_list = []
            for idx, ref_img in enumerate([reference_image_1, reference_image_2, reference_image_3], 1):
                if ref_img is not None:
                    ref_b64_list.append(GoogleAICore.tensor_to_base64(ref_img, 0))
                    logger.info(f"[Storyboard] Referencia {idx} adjunta")

            # Regla: con referencias → forzar 8s
            if ref_b64_list and duration != 8:
                logger.warning(f"[Storyboard] Duración forzada {duration}s → 8s (restricción API con referencias)")
                duration = 8

            cost_str = GoogleAICore.estimate_video_cost(duration)

            # await al core asíncrono
            video_bytes = await GoogleAICore.generate_video(
                api_key=key,
                prompt=prompt,
                model=model,
                resolution_preset=video_preset,
                duration_seconds=duration,
                reference_images_b64=ref_b64_list if ref_b64_list else None,
            )

            video_tensor = GoogleAICore.video_bytes_to_tensor(video_bytes)
            logger.info(
                f"[Storyboard] ✅ {video_tensor.shape[0]} frames @ 24 FPS | {cost_str}"
            )
            logger.info(
                "[Veo 3.1] ⚠️ IMPORTANTE: El video tiene un estándar de 24 FPS. "
                "Configura tu VHS Video Combine a 24 FPS."
            )
            return (video_tensor, cost_str,)

        except RuntimeError as e:
            error_msg = str(e)
            if "400" in error_msg or "safety" in error_msg.lower() or "block" in error_msg.lower():
                logger.warning(f"[Storyboard] Violación de seguridad: {error_msg}")
            else:
                logger.error(f"[Storyboard] Error: {error_msg}")
            d = 8 if reference_image_1 else int(duration_seconds)
            return (
                GoogleAICore.create_error_image(error_msg),
                f"❌ Error - {GoogleAICore.estimate_video_cost(d)}",
            )

        except Exception as e:
            logger.error(f"[Storyboard] Error inesperado: {e}")
            d = 8 if reference_image_1 else int(duration_seconds)
            return (
                GoogleAICore.create_error_image(str(e)),
                f"❌ Error - {GoogleAICore.estimate_video_cost(d)}",
            )
