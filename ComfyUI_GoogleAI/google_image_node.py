"""
google_image_node.py - Nodos de Imagen para ComfyUI (V2.5.0)
==============================================================
V2.5.0: Arquitectura separada - un nodo por API endpoint.

GoogleAI_NanoBananaNode (NUEVO - nodo estrella):
  - Modelos: NB2, NB Pro, NB original (generateContent)
  - 14 aspect ratios oficiales + 5 imageSize separados
  - 5 pines de referencia + system_prompt
  - Output: IMAGE + STRING (descripcion del modelo)

GoogleAI_ImageNode (simplificado para Imagen 4/3):
  - Solo modelos Imagen 4/3 (generateImages)
  - negative_prompt (NB no lo soporta)
  - 5 aspect ratios de Imagen 4

ImageBatchNode ELIMINADO - usar multiples NanoBanana o Imagen nodes.

Autor: Prompt Models Studio | cdanielp
"""

import random
import logging
import torch
from .google_core import (
    GoogleAICore, GEMINI_IMAGE_MODELS, SAFETY_THRESHOLDS,
    NB_ASPECT_RATIOS, NB_IMAGE_SIZES, IMAGEN_ASPECT_RATIOS,
)

logger = logging.getLogger("ComfyUI_GoogleAI")


# ============================================================================
# NANO BANANA NODE - Nodo estrella (generateContent)
# ============================================================================
NB_MODELS = [
    "gemini-3.1-flash-image-preview",  # Nano Banana 2 (Feb 26 2026) - 4K, 0.5K
    "gemini-3-pro-image-preview",      # Nano Banana Pro - 4K, 14 refs
    "gemini-2.5-flash-image",          # Nano Banana original - 1K max
]


class GoogleAI_NanoBananaNode:
    """
    Generacion de imagen con Nano Banana (NB2 / Pro / original).
    API: generateContent con responseModalities: ["TEXT", "IMAGE"]

    NB2 (gemini-3.1-flash-image-preview):
      - Pro quality a Flash speed, free tier 500 imgs/dia
      - Soporta 0.5K (exclusivo), hasta 4K
      - 14 aspect ratios incluyendo 1:4, 4:1, 1:8, 8:1

    NB Pro (gemini-3-pro-image-preview):
      - Hasta 14 imagenes de referencia, hasta 4K
      - 14 aspect ratios (excepto 1:4, 4:1, 1:8, 8:1)

    NB Original (gemini-2.5-flash-image):
      - Velocidad maxima, solo hasta 1K
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "prompt": ("STRING", {
                    "multiline": True,
                    "default": "A beautiful cinematic portrait, photorealistic, 8K detail",
                }),
                "model": (NB_MODELS, {"default": "gemini-3.1-flash-image-preview"}),
                "aspect_ratio": (NB_ASPECT_RATIOS, {
                    "default": "1:1",
                    "tooltip": (
                        "14 ratios oficiales. Ultrawide: 21:9. "
                        "Extremos (1:4, 4:1, 1:8, 8:1) solo NB2."
                    ),
                }),
                "image_size": (NB_IMAGE_SIZES, {
                    "default": "2K",
                    "tooltip": (
                        "512px, 0.5K (solo NB2), 1K, 2K, 4K (NB2/Pro). "
                        "NB original: max 1K (downgrade automatico)."
                    ),
                }),
                "seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff}),
                "randomize_seed": ("BOOLEAN", {"default": True}),
            },
            "optional": {
                "api_key": ("STRING", {"default": ""}),
                "system_prompt": ("STRING", {
                    "multiline": True,
                    "default": (
                        "You are an expert image composition engine. "
                        "Use the reference images to understand the visual style, "
                        "character traits, and composition goals. "
                        "Generate a new image that matches the described scenario."
                    ),
                }),
                "image_1": ("IMAGE", {"tooltip": "Referencia 1 - estilo, personaje o composicion."}),
                "image_2": ("IMAGE", {"tooltip": "Referencia 2"}),
                "image_3": ("IMAGE", {"tooltip": "Referencia 3"}),
                "image_4": ("IMAGE", {"tooltip": "Referencia 4"}),
                "image_5": ("IMAGE", {"tooltip": "Referencia 5"}),
                "safety_threshold": (SAFETY_THRESHOLDS, {
                    "default": "BLOCK_ONLY_HIGH",
                    "tooltip": "Nivel de filtro de seguridad. BLOCK_ONLY_HIGH = menos restrictivo.",
                }),
            },
        }

    RETURN_TYPES = ("IMAGE", "STRING",)
    RETURN_NAMES = ("image", "description",)
    FUNCTION = "generate_image"
    CATEGORY = "Google AI/Image"

    def generate_image(
        self,
        prompt,
        model,
        aspect_ratio,
        image_size,
        seed,
        randomize_seed,
        api_key="",
        system_prompt="",
        image_1=None,
        image_2=None,
        image_3=None,
        image_4=None,
        image_5=None,
        safety_threshold="BLOCK_ONLY_HIGH",
    ):
        try:
            key = GoogleAICore.resolve_api_key(api_key)
            effective_seed = random.randint(0, 0xffffffffffffffff) if randomize_seed else seed

            ref_images_b64 = []
            for ref in [image_1, image_2, image_3, image_4, image_5]:
                if ref is not None:
                    ref_images_b64.append(GoogleAICore.compress_image_for_api(ref, 0))

            logger.info(
                f"[NanoBanana] '{model}' | "
                f"{len(ref_images_b64)} refs | {aspect_ratio} | {image_size} | "
                f"seed={effective_seed}"
            )

            safety_cfg = [
                {"category": cat, "threshold": safety_threshold}
                for cat in [
                    "HARM_CATEGORY_HARASSMENT", "HARM_CATEGORY_HATE_SPEECH",
                    "HARM_CATEGORY_SEXUALLY_EXPLICIT", "HARM_CATEGORY_DANGEROUS_CONTENT",
                ]
            ]

            img_bytes, description = GoogleAICore.generate_image_gemini(
                api_key=key,
                prompt=prompt,
                model=model,
                system_instruction=system_prompt if system_prompt else None,
                reference_images_b64=ref_images_b64 if ref_images_b64 else None,
                aspect_ratio=aspect_ratio,
                image_size=image_size,
                seed=effective_seed,
                safety_settings=safety_cfg,
            )

            return (GoogleAICore.bytes_to_image_tensor(img_bytes), description)

        except RuntimeError as e:
            error_msg = str(e)
            if "400" in error_msg or "safety" in error_msg.lower() or "block" in error_msg.lower():
                logger.warning(f"[NanoBanana] Violacion de seguridad: {error_msg}")
            else:
                logger.error(f"[NanoBanana] Error: {error_msg}")
            return (GoogleAICore.create_error_image(error_msg), f"Error: {error_msg}")
        except Exception as e:
            logger.error(f"[NanoBanana] Error inesperado: {e}")
            return (GoogleAICore.create_error_image(str(e)), f"Error: {str(e)}")


# ============================================================================
# IMAGEN 4 NODE - Simplificado (generateImages)
# ============================================================================
IMAGEN_MODELS = [
    "imagen-4.0-generate-001",       # Imagen 4 Standard
    "imagen-4.0-ultra-generate-001", # Imagen 4 Ultra
    "imagen-4.0-fast-generate-001",  # Imagen 4 Fast
    "imagen-3.0-generate-002",       # Imagen 3 (fallback)
    "imagen-3.0-fast-generate-001",  # Imagen 3 Fast (fallback)
]


class GoogleAI_ImageNode:
    """
    Generacion de imagen con Imagen 4/3 (generateImages).
    Soporta negative_prompt. Sin pines de referencia ni system_prompt.
    Para imagenes con referencias, usar GoogleAI_NanoBananaNode.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "prompt": ("STRING", {"multiline": True, "default": "A beautiful cinematic portrait"}),
                "model": (IMAGEN_MODELS, {"default": "imagen-4.0-generate-001"}),
                "aspect_ratio": (IMAGEN_ASPECT_RATIOS, {"default": "1:1"}),
                "seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff}),
                "randomize_seed": ("BOOLEAN", {"default": True}),
            },
            "optional": {
                "api_key": ("STRING", {"default": ""}),
                "negative_prompt": ("STRING", {"multiline": True, "default": ""}),
            },
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)
    FUNCTION = "generate_image"
    CATEGORY = "Google AI/Image"

    def generate_image(self, prompt, model, aspect_ratio, seed, randomize_seed,
                       api_key="", negative_prompt=""):
        try:
            key = GoogleAICore.resolve_api_key(api_key)
            effective_seed = random.randint(0, 0xffffffffffffffff) if randomize_seed else seed

            logger.info(
                f"[ImageNode] Imagen '{model}' | {aspect_ratio} | seed={effective_seed}"
            )

            img_bytes_list = GoogleAICore.generate_image(
                api_key=key,
                prompt=prompt,
                model=model,
                negative_prompt=negative_prompt,
                aspect_ratio=aspect_ratio,
                seed=effective_seed,
            )
            if not img_bytes_list:
                return (GoogleAICore.create_error_image("La API no retorno imagenes."),)

            return (GoogleAICore.bytes_to_image_tensor(img_bytes_list[0]),)

        except RuntimeError as e:
            error_msg = str(e)
            if "400" in error_msg or "safety" in error_msg.lower() or "block" in error_msg.lower():
                logger.warning(f"[ImageNode] Violacion de seguridad: {error_msg}")
            else:
                logger.error(f"[ImageNode] Error: {error_msg}")
            return (GoogleAICore.create_error_image(error_msg),)
        except Exception as e:
            logger.error(f"[ImageNode] Error inesperado: {e}")
            return (GoogleAICore.create_error_image(str(e)),)
