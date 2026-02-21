"""
google_image_node.py - Nodos de Imagen para ComfyUI (V2.0)
===========================================================
HTTP 400 (violación de seguridad) → imagen roja 512x512 en vez de crash.

Autor: Prompt Models Studio | cdanielp
"""

import logging
import torch
from .google_core import GoogleAICore

logger = logging.getLogger("ComfyUI_GoogleAI")

IMAGE_MODELS = [
    "imagen-3.0-generate-002",
    "imagen-3.0-generate-001",
    "imagen-3.0-fast-generate-001",
]

ASPECT_RATIOS = ["1:1", "16:9", "9:16", "4:3", "3:4"]


class GoogleAI_ImageNode:
    """Genera imágenes con Imagen 3. Error 400 → imagen roja, no crashea."""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "prompt": ("STRING", {"multiline": True, "default": "A beautiful landscape painting"}),
                "model": (IMAGE_MODELS, {"default": "imagen-3.0-generate-002"}),
                "aspect_ratio": (ASPECT_RATIOS, {"default": "1:1"}),
            },
            "optional": {
                "api_key": ("STRING", {"default": ""}),
                "negative_prompt": ("STRING", {"multiline": True, "default": ""}),
                "seed": ("INT", {"default": 0, "min": 0, "max": 2147483647}),
            },
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)
    FUNCTION = "generate_image"
    CATEGORY = "Google AI/Image"

    def generate_image(self, prompt, model, aspect_ratio,
                       api_key="", negative_prompt="", seed=0):
        try:
            key = GoogleAICore.resolve_api_key(api_key)
            image_bytes_list = GoogleAICore.generate_image(
                api_key=key, prompt=prompt, model=model,
                negative_prompt=negative_prompt, aspect_ratio=aspect_ratio,
            )
            if not image_bytes_list:
                return (GoogleAICore.create_error_image("La API no retornó imágenes."),)

            return (GoogleAICore.bytes_to_image_tensor(image_bytes_list[0]),)

        except RuntimeError as e:
            error_msg = str(e)
            if "400" in error_msg or "safety" in error_msg.lower() or "block" in error_msg.lower():
                logger.warning(f"[ImageNode] Violación de seguridad: {error_msg}")
            else:
                logger.error(f"[ImageNode] Error: {error_msg}")
            return (GoogleAICore.create_error_image(error_msg),)

        except Exception as e:
            logger.error(f"[ImageNode] Error inesperado: {e}")
            return (GoogleAICore.create_error_image(str(e)),)


class GoogleAI_ImageBatchNode:
    """Genera múltiples imágenes en batch [B, H, W, C]."""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "prompt": ("STRING", {"multiline": True, "default": "A beautiful landscape painting"}),
                "model": (IMAGE_MODELS, {"default": "imagen-3.0-generate-002"}),
                "aspect_ratio": (ASPECT_RATIOS, {"default": "1:1"}),
                "batch_size": ("INT", {"default": 2, "min": 1, "max": 4}),
            },
            "optional": {
                "api_key": ("STRING", {"default": ""}),
                "negative_prompt": ("STRING", {"multiline": True, "default": ""}),
            },
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("images",)
    FUNCTION = "generate_batch"
    CATEGORY = "Google AI/Image"

    def generate_batch(self, prompt, model, aspect_ratio, batch_size,
                       api_key="", negative_prompt=""):
        try:
            key = GoogleAICore.resolve_api_key(api_key)
            image_bytes_list = GoogleAICore.generate_image(
                api_key=key, prompt=prompt, model=model,
                negative_prompt=negative_prompt, aspect_ratio=aspect_ratio,
                num_images=batch_size,
            )
            if not image_bytes_list:
                return (GoogleAICore.create_error_image("No se generaron imágenes."),)

            tensors = [GoogleAICore.bytes_to_image_tensor(b) for b in image_bytes_list]
            return (torch.cat(tensors, dim=0),)

        except Exception as e:
            logger.error(f"[ImageBatchNode] Error: {e}")
            return (GoogleAICore.create_error_image(str(e)),)
