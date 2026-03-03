"""
google_video_node.py - Nodos de Video para ComfyUI (V2.5.0)
=============================================================
Veo 3.1 | Duracion [4,6,8]s | Costo $0.40/s (Standard)
FPS de salida: 24. Configurar VHS Video Combine a 24 FPS.

V2.5.0:
- Audio check: model.startswith("veo-3") en vez de "veo-2.0" in model
  (futureproof para veo-2.1, veo-2.5, etc.)

Autor: Prompt Models Studio | cdanielp
"""

import logging
import torch
from .google_core import (
    GoogleAICore, VEO_RESOLUTION_PRESETS, VEO_DURATION_OPTIONS,
    DEFAULT_VIDEO_MODEL, _make_dummy_audio,
)

logger = logging.getLogger("ComfyUI_GoogleAI")

RESOLUTION_OPTIONS = list(VEO_RESOLUTION_PRESETS.keys())
DURATION_OPTIONS = [str(d) for d in VEO_DURATION_OPTIONS]

# Strings exactos validos en la API - Mar 2026
VIDEO_MODELS = [
    "veo-3.1-generate-preview",      # Standard - con audio nativo
    "veo-3.1-fast-generate-preview", # Fast - con audio nativo
    "veo-2.0-generate-001",          # Sin audio (silencio automatico)
]


def _model_has_native_audio(model: str) -> bool:
    """V2.5.0: Veo 3+ tiene audio nativo. Futureproof para veo-2.1, etc."""
    return model.startswith("veo-3")


class GoogleAI_VideoGenerator:
    """
    Genera video con Veo 3.1.
    1 frame -> Image-to-Video | >1 frame -> Video Extension (ultimo frame).
    Output AUDIO: pista nativa del MP4 (Veo 3.1) o silencio (Veo 2.0).
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "prompt": ("STRING", {"multiline": True, "default": "A cinematic drone shot flying over a mountain range at sunrise"}),
                "model": (VIDEO_MODELS, {"default": "veo-3.1-generate-preview"}),
                "video_preset": (RESOLUTION_OPTIONS, {"default": "1920x1080 (16:9)"}),
                "duration_seconds": (DURATION_OPTIONS, {"default": "6"}),
            },
            "optional": {
                "api_key": ("STRING", {"default": ""}),
                "init_image_or_video": ("IMAGE", {"tooltip": "1 frame=Img2Vid, >1=Extension (ultimo frame)."}),
                "negative_prompt": ("STRING", {"multiline": True, "default": ""}),
            },
        }

    RETURN_TYPES = ("IMAGE", "AUDIO", "STRING",)
    RETURN_NAMES = ("video_frames", "audio", "cost_estimate",)
    FUNCTION = "generate_video"
    CATEGORY = "Google AI/Video"

    def generate_video(self, prompt, model, video_preset, duration_seconds,
                       api_key="", init_image_or_video=None, negative_prompt=""):
        dummy_audio = _make_dummy_audio()
        duration = int(duration_seconds)
        cost_str = GoogleAICore.estimate_video_cost(duration)

        try:
            key = GoogleAICore.resolve_api_key(api_key)

            init_images_b64 = None
            if init_image_or_video is not None:
                num_frames = init_image_or_video.shape[0]
                if num_frames == 1:
                    logger.info("[VideoGenerator] Modo: Image-to-Video (1 frame)")
                    init_images_b64 = [GoogleAICore.tensor_to_base64(init_image_or_video, 0)]
                else:
                    logger.info(f"[VideoGenerator] Modo: Video Extension ({num_frames} frames -> ultimo)")
                    init_images_b64 = [GoogleAICore.tensor_to_base64(init_image_or_video, num_frames - 1)]

            full_prompt = prompt
            if negative_prompt:
                full_prompt += f"\n\nNegative: {negative_prompt}"

            video_bytes = GoogleAICore.run_async_in_thread(
                GoogleAICore.generate_video(
                    api_key=key, prompt=full_prompt, model=model,
                    resolution_preset=video_preset, duration_seconds=duration,
                    init_images_b64=init_images_b64,
                )
            )

            video_tensor = GoogleAICore.video_bytes_to_tensor(video_bytes)

            # V2.5.0: Check futureproof
            if _model_has_native_audio(model):
                audio_dict = GoogleAICore.video_bytes_to_audio(video_bytes)
            else:
                logger.info(f"[VideoGenerator] {model} no tiene audio nativo -> silencio.")
                audio_dict = dummy_audio

            logger.info(f"[VideoGenerator] {video_tensor.shape[0]} frames @ 24 FPS | {cost_str}")
            return (video_tensor, audio_dict, cost_str,)

        except Exception as e:
            logger.error(f"[VideoGenerator] Error: {e}")
            return (
                GoogleAICore.create_error_image(str(e)),
                dummy_audio,
                f"Error - {cost_str}",
            )


class GoogleAI_VideoInterpolation:
    """
    Interpola entre first_frame y last_frame.
    El last_frame se redimensiona automaticamente al tamano del first_frame.
    Output AUDIO: pista nativa del MP4 (Veo 3.1) o silencio (Veo 2.0).
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "first_frame": ("IMAGE",),
                "last_frame": ("IMAGE", {"tooltip": "Se redimensiona al tamano del first_frame."}),
                "prompt": ("STRING", {"multiline": True, "default": "A smooth cinematic transition between two scenes"}),
                "model": (VIDEO_MODELS, {"default": "veo-3.1-generate-preview"}),
                "video_preset": (RESOLUTION_OPTIONS, {"default": "1920x1080 (16:9)"}),
                "duration_seconds": (DURATION_OPTIONS, {"default": "6"}),
            },
            "optional": {"api_key": ("STRING", {"default": ""})},
        }

    RETURN_TYPES = ("IMAGE", "AUDIO", "STRING",)
    RETURN_NAMES = ("video_frames", "audio", "cost_estimate",)
    FUNCTION = "interpolate"
    CATEGORY = "Google AI/Video"

    def interpolate(self, first_frame, last_frame, prompt, model,
                    video_preset, duration_seconds, api_key=""):
        duration = int(duration_seconds)
        cost_str = GoogleAICore.estimate_video_cost(duration)
        dummy_audio = _make_dummy_audio()

        try:
            key = GoogleAICore.resolve_api_key(api_key)

            last_resized = GoogleAICore.resize_tensor_to_match(last_frame, first_frame)
            first_b64 = GoogleAICore.tensor_to_base64(first_frame, 0)
            last_b64  = GoogleAICore.tensor_to_base64(last_resized, 0)

            video_bytes = GoogleAICore.run_async_in_thread(
                GoogleAICore.generate_video(
                    api_key=key, prompt=prompt, model=model,
                    resolution_preset=video_preset, duration_seconds=duration,
                    init_images_b64=[first_b64], last_frame_b64=last_b64,
                )
            )

            video_tensor = GoogleAICore.video_bytes_to_tensor(video_bytes)

            if _model_has_native_audio(model):
                audio_dict = GoogleAICore.video_bytes_to_audio(video_bytes)
            else:
                logger.info(f"[VideoInterpolation] {model} no tiene audio nativo -> silencio.")
                audio_dict = dummy_audio

            logger.info(f"[VideoInterpolation] {video_tensor.shape[0]} frames @ 24 FPS | {cost_str}")
            return (video_tensor, audio_dict, cost_str,)

        except Exception as e:
            logger.error(f"[VideoInterpolation] Error: {e}")
            return (GoogleAICore.create_error_image(str(e)), dummy_audio, f"Error - {cost_str}",)


class GoogleAI_VideoStoryboard:
    """
    Video estilizado con hasta 3 imagenes de referencia.
    Con referencias, duracion forzada a 8s (restriccion API).
    Output AUDIO: pista nativa del MP4 (Veo 3.1) o silencio (Veo 2.0).
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "prompt": ("STRING", {"multiline": True, "default": "A stylized animated scene with vibrant colors"}),
                "model": (VIDEO_MODELS, {"default": "veo-3.1-generate-preview"}),
                "video_preset": (RESOLUTION_OPTIONS, {"default": "1920x1080 (16:9)"}),
                "duration_seconds": (DURATION_OPTIONS, {"default": "8", "tooltip": "Se forza a 8s con referencias."}),
            },
            "optional": {
                "api_key": ("STRING", {"default": ""}),
                "reference_image_1": ("IMAGE",),
                "reference_image_2": ("IMAGE",),
                "reference_image_3": ("IMAGE",),
            },
        }

    RETURN_TYPES = ("IMAGE", "AUDIO", "STRING",)
    RETURN_NAMES = ("video_frames", "audio", "cost_estimate",)
    FUNCTION = "generate_storyboard"
    CATEGORY = "Google AI/Video"

    def generate_storyboard(self, prompt, model, video_preset, duration_seconds,
                            api_key="", reference_image_1=None,
                            reference_image_2=None, reference_image_3=None):
        duration = int(duration_seconds)
        dummy_audio = _make_dummy_audio()

        try:
            key = GoogleAICore.resolve_api_key(api_key)

            ref_b64_list = []
            for ref_img in [reference_image_1, reference_image_2, reference_image_3]:
                if ref_img is not None:
                    ref_b64_list.append(GoogleAICore.tensor_to_base64(ref_img, 0))

            if ref_b64_list and duration != 8:
                logger.warning(f"[Storyboard] Duracion forzada {duration}s -> 8s (restriccion API)")
                duration = 8

            cost_str = GoogleAICore.estimate_video_cost(duration)

            video_bytes = GoogleAICore.run_async_in_thread(
                GoogleAICore.generate_video(
                    api_key=key, prompt=prompt, model=model,
                    resolution_preset=video_preset, duration_seconds=duration,
                    reference_images_b64=ref_b64_list if ref_b64_list else None,
                )
            )

            video_tensor = GoogleAICore.video_bytes_to_tensor(video_bytes)

            if _model_has_native_audio(model):
                audio_dict = GoogleAICore.video_bytes_to_audio(video_bytes)
            else:
                logger.info(f"[Storyboard] {model} no tiene audio nativo -> silencio.")
                audio_dict = dummy_audio

            logger.info(f"[Storyboard] {video_tensor.shape[0]} frames @ 24 FPS | {cost_str}")
            return (video_tensor, audio_dict, cost_str,)

        except Exception as e:
            logger.error(f"[Storyboard] Error: {e}")
            d = 8 if reference_image_1 else int(duration_seconds)
            return (
                GoogleAICore.create_error_image(str(e)),
                dummy_audio,
                f"Error - {GoogleAICore.estimate_video_cost(d)}",
            )
