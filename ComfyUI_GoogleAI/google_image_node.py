"""
google_image_node.py - Nodos de Imagen para ComfyUI (V2.1)
===========================================================
Imagen 3 | seed 64→32 sanitizado | batch_size 1-4 | 5 imágenes de referencia
HTTP 400 (violación de seguridad) → imagen roja 512×512, no crashea.

V2.1 Cambios:
  - seed (INT, 0-0xffffffffffffffff) sanitizado a 32 bits via safe_seed()
  - batch_size (INT, 1-4) integrado en nodo principal
  - 5 puertos image_1..image_5 de referencia opcionales
  - negative_prompt restaurado como optional
  - ImageBatchNode mantenido por retrocompatibilidad

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
    """
    Genera imágenes con Imagen 3.
    - seed de 64 bits sanitizado internamente a 32 bits
    - batch_size para generar 1-4 imágenes
    - Hasta 5 imágenes de referencia opcionales
    - Error HTTP 400 → imagen roja, no crashea
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "prompt": ("STRING", {
                    "multiline": True,
                    "default": "A beautiful landscape painting",
                }),
                "model": (IMAGE_MODELS, {"default": "imagen-3.0-generate-002"}),
                "aspect_ratio": (ASPECT_RATIOS, {"default": "1:1"}),
                "seed": ("INT", {
                    "default": 0,
                    "min": 0,
                    "max": 0xFFFFFFFFFFFFFFFF,
                    "tooltip": "Seed de 64 bits. Se sanitiza a 32 bits internamente.",
                }),
                "batch_size": ("INT", {
                    "default": 1,
                    "min": 1,
                    "max": 4,
                    "tooltip": "Número de imágenes a generar (1-4).",
                }),
            },
            "optional": {
                "api_key": ("STRING", {"default": ""}),
                "negative_prompt": ("STRING", {
                    "multiline": True,
                    "default": "",
                    "tooltip": "Elementos a evitar en la generación.",
                }),
                "image_1": ("IMAGE", {"tooltip": "Imagen de referencia 1."}),
                "image_2": ("IMAGE", {"tooltip": "Imagen de referencia 2."}),
                "image_3": ("IMAGE", {"tooltip": "Imagen de referencia 3."}),
                "image_4": ("IMAGE", {"tooltip": "Imagen de referencia 4."}),
                "image_5": ("IMAGE", {"tooltip": "Imagen de referencia 5."}),
            },
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)
    FUNCTION = "generate_image"
    CATEGORY = "Google AI/Image"

    def generate_image(self, prompt, model, aspect_ratio, seed, batch_size,
                       api_key="", negative_prompt="",
                       image_1=None, image_2=None, image_3=None,
                       image_4=None, image_5=None):
        try:
            key = GoogleAICore.resolve_api_key(api_key)

            # Sanitizar seed 64→32 bits
            safe_seed = GoogleAICore.safe_seed(seed)
            logger.info(f"[ImageNode] Seed: {seed} → sanitizado: {safe_seed}")

            # Recolectar imágenes de referencia
            ref_b64_list = []
            for ref_img in [image_1, image_2, image_3, image_4, image_5]:
                if ref_img is not None:
                    ref_b64_list.append(GoogleAICore.tensor_to_base64(ref_img, 0))

            if ref_b64_list:
                logger.info(f"[ImageNode] {len(ref_b64_list)} imágenes de referencia adjuntas")

            image_bytes_list = GoogleAICore.generate_image(
                api_key=key,
                prompt=prompt,
                model=model,
                negative_prompt=negative_prompt,
                aspect_ratio=aspect_ratio,
                num_images=batch_size,
                seed=safe_seed,
                reference_images_b64=ref_b64_list if ref_b64_list else None,
            )

            if not image_bytes_list:
                return (GoogleAICore.create_error_image("La API no retornó imágenes."),)

            # Si batch_size > 1, concatenar en batch [B, H, W, C]
            if len(image_bytes_list) > 1:
                tensors = [GoogleAICore.bytes_to_image_tensor(b) for b in image_bytes_list]
                return (torch.cat(tensors, dim=0),)
            else:
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
    """
    Genera múltiples imágenes en batch [B, H, W, C].
    ⚠️ Retrocompatibilidad: Usa GoogleAI_ImageNode con batch_size para la misma función.
    """

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
