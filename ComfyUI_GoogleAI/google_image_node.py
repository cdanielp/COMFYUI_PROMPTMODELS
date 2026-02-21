"""
google_image_node.py - Nodos de Imagen para ComfyUI (V2.4.2 Ultra)
===================================================================
Routing automático: Nano Banana → generateContent | Imagen 4 → generateImages
5 pines de imagen de referencia para Nano Banana Pro/Flash.
Mapeo inteligente size_preset → aspectRatio + resolution_hint.
Validación 4K: solo Nano Banana Pro, downgrade automático a 2K en otros modelos.

Modelos disponibles (Feb 2026):
  Nano Banana Pro  → gemini-3-pro-image-preview  (hasta 14 refs, hasta 4K)
  Nano Banana      → gemini-2.5-flash-image       (velocidad, hasta 1K)
  Imagen 4 Standard→ imagen-4.0-generate-001
  Imagen 4 Ultra   → imagen-4.0-ultra-generate-001
  Imagen 4 Fast    → imagen-4.0-fast-generate-001
  Imagen 3         → imagen-3.0-generate-002

Autor: Prompt Models Studio | cdanielp
"""

import random
import logging
import torch
from .google_core import GoogleAICore, GEMINI_IMAGE_MODELS

logger = logging.getLogger("ComfyUI_GoogleAI")

# Orden: Nano Banana primero (modelos estrella), luego Imagen 4
IMAGE_MODELS = [
    "gemini-3-pro-image-preview",    # Nano Banana Pro  — hasta 4K, 14 refs
    "gemini-2.5-flash-image",        # Nano Banana       — velocidad, 1K
    "imagen-4.0-generate-001",       # Imagen 4 Standard
    "imagen-4.0-ultra-generate-001", # Imagen 4 Ultra
    "imagen-4.0-fast-generate-001",  # Imagen 4 Fast
    "imagen-3.0-generate-002",       # Imagen 3 (fallback)
    "imagen-3.0-fast-generate-001",  # Imagen 3 Fast (fallback)
]

# size_preset → (aspect_ratio_api, resolution_hint)
# ⚠️ Convención INVERSA a VEO_RESOLUTION_PRESETS que usa (resolution_api, aspect_ratio_api)
#    Imagen: (aspect_ratio, resolution_hint)    — ej. ("16:9", "2K")
#    Video:  (resolution_api, aspect_ratio_api) — ej. ("1080p", "16:9")
# aspect_ratio_api  → usado por AMBOS (Gemini generateContent + Imagen generateImages)
# resolution_hint   → solo Nano Banana (se incluye como hint en el prompt)
SIZE_PRESETS = {
    "1024×1024 (1:1) - 1K":  ("1:1",  "1K"),
    "1280×720 (16:9) - 1K":  ("16:9", "1K"),
    "720×1280 (9:16) - 1K":  ("9:16", "1K"),
    "2048×2048 (1:1) - 2K":  ("1:1",  "2K"),
    "2048×1152 (16:9) - 2K": ("16:9", "2K"),
    "1152×2048 (9:16) - 2K": ("9:16", "2K"),
    "4096×4096 (1:1) - 4K":  ("1:1",  "4K"),
    "4096×2304 (16:9) - 4K": ("16:9", "4K"),
    "2304×4096 (9:16) - 4K": ("9:16", "4K"),
}

# Modelos que NO soportan 4K → downgrade automático a 2K
_4K_ONLY_MODELS = {"gemini-3-pro-image-preview"}

# Opciones de aspect_ratio independiente para ImageBatchNode (Imagen 4 solo)
ASPECT_RATIOS = ["1:1", "16:9", "9:16", "4:3", "3:4"]


def _resolve_size(model: str, size_preset: str):
    """
    Retorna (aspect_ratio, resolution_hint) para el modelo y preset dados.
    Aplica downgrade 4K→2K si el modelo no es Nano Banana Pro.
    """
    aspect_ratio, resolution_hint = SIZE_PRESETS.get(size_preset, ("1:1", "2K"))

    if resolution_hint == "4K" and model not in _4K_ONLY_MODELS:
        logger.warning(
            f"[ImageNode] 4K no soportado por '{model}' → downgrade a 2K. "
            f"Solo 'gemini-3-pro-image-preview' soporta 4K."
        )
        resolution_hint = "2K"
        # También ajustamos el label del aspect_ratio para no confundir
        # (el aspect_ratio en sí no cambia, solo el hint)

    return aspect_ratio, resolution_hint


def _is_gemini_image_model(model: str) -> bool:
    """True si el modelo es Nano Banana (usa generateContent). False = Imagen 4 (generateImages)."""
    return any(model.startswith(m) for m in GEMINI_IMAGE_MODELS)


class GoogleAI_ImageNode:
    """
    Nodo maestro de imagen.
    Nano Banana: routing a generateContent, 5 pines de referencia.
    Imagen 4/3: routing a generateImages, sin pines de referencia.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "prompt": ("STRING", {"multiline": True, "default": "A beautiful cinematic portrait"}),
                "model": (IMAGE_MODELS, {"default": "gemini-3-pro-image-preview"}),
                "size_preset": (list(SIZE_PRESETS.keys()), {"default": "2048×2048 (1:1) - 2K"}),
                "seed": ("INT", {"default": 0, "min": 0, "max": 2147483647}),
                "randomize_seed": ("BOOLEAN", {"default": True}),
            },
            "optional": {
                "api_key": ("STRING", {"default": ""}),
                "system_prompt": (
                    "STRING",
                    {
                        "multiline": True,
                        "default": (
                            "You are an expert image composition engine. "
                            "Use the reference images to understand the visual style, "
                            "character traits, and composition goals. "
                            "Generate a new image that matches the described scenario."
                        ),
                    },
                ),
                "negative_prompt": ("STRING", {"multiline": True, "default": ""}),
                # 5 pines de referencia para Nano Banana
                "image_1": ("IMAGE", {"tooltip": "Referencia 1 — estilo, personaje o composición."}),
                "image_2": ("IMAGE", {"tooltip": "Referencia 2"}),
                "image_3": ("IMAGE", {"tooltip": "Referencia 3"}),
                "image_4": ("IMAGE", {"tooltip": "Referencia 4"}),
                "image_5": ("IMAGE", {"tooltip": "Referencia 5"}),
            },
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)
    FUNCTION = "generate_image"
    CATEGORY = "Google AI/Image"

    def generate_image(
        self,
        prompt,
        model,
        size_preset,
        seed,
        randomize_seed,
        api_key="",
        system_prompt="",
        negative_prompt="",
        image_1=None,
        image_2=None,
        image_3=None,
        image_4=None,
        image_5=None,
    ):
        try:
            key = GoogleAICore.resolve_api_key(api_key)
            effective_seed = random.randint(0, 2147483647) if randomize_seed else seed
            aspect_ratio, resolution_hint = _resolve_size(model, size_preset)

            if _is_gemini_image_model(model):
                # ── Nano Banana: generateContent + responseModalities:IMAGE ──
                ref_images_b64 = []
                for ref in [image_1, image_2, image_3, image_4, image_5]:
                    if ref is not None:
                        ref_images_b64.append(GoogleAICore.tensor_to_base64(ref, 0))

                if ref_images_b64:
                    logger.info(
                        f"[ImageNode] Nano Banana '{model}' | "
                        f"{len(ref_images_b64)} referencias | {aspect_ratio} | {resolution_hint}"
                    )
                else:
                    logger.info(
                        f"[ImageNode] Nano Banana '{model}' | sin referencias | "
                        f"{aspect_ratio} | {resolution_hint}"
                    )

                img_bytes = GoogleAICore.generate_image_gemini(
                    api_key=key,
                    prompt=prompt,
                    model=model,
                    system_instruction=system_prompt if system_prompt else None,
                    reference_images_b64=ref_images_b64 if ref_images_b64 else None,
                    aspect_ratio=aspect_ratio,
                    resolution_hint=resolution_hint,
                    seed=effective_seed,
                )
                return (GoogleAICore.bytes_to_image_tensor(img_bytes),)

            else:
                # ── Imagen 4/3: generateImages ──
                if image_1 is not None or image_2 is not None:
                    logger.warning(
                        f"[ImageNode] '{model}' es Imagen 4/3 y no soporta pines de referencia. "
                        f"Conecta pines solo cuando uses Nano Banana."
                    )

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
                    return (GoogleAICore.create_error_image("La API no retornó imágenes."),)

                return (GoogleAICore.bytes_to_image_tensor(img_bytes_list[0]),)

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
    Solo Imagen 4/3 (generateImages soporta batch nativo).
    Para batch con Nano Banana: usar múltiples GoogleAI_ImageNode en paralelo.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "prompt": ("STRING", {"multiline": True, "default": "A beautiful landscape painting"}),
                "model": (IMAGE_MODELS, {"default": "imagen-4.0-generate-001"}),
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

            if _is_gemini_image_model(model):
                # Nano Banana no soporta batch nativo → generar una imagen
                logger.warning(
                    f"[ImageBatchNode] '{model}' (Nano Banana) no soporta batch nativo. "
                    f"Generando 1 imagen. Usa múltiples GoogleAI_ImageNode para batch."
                )
                img_bytes = GoogleAICore.generate_image_gemini(
                    api_key=key, prompt=prompt, model=model,
                    aspect_ratio=aspect_ratio,
                )
                return (GoogleAICore.bytes_to_image_tensor(img_bytes),)

            img_bytes_list = GoogleAICore.generate_image(
                api_key=key, prompt=prompt, model=model,
                negative_prompt=negative_prompt,
                aspect_ratio=aspect_ratio,
                num_images=batch_size,
            )
            if not img_bytes_list:
                return (GoogleAICore.create_error_image("No se generaron imágenes."),)

            tensors = [GoogleAICore.bytes_to_image_tensor(b) for b in img_bytes_list]
            return (torch.cat(tensors, dim=0),)

        except Exception as e:
            logger.error(f"[ImageBatchNode] Error: {e}")
            return (GoogleAICore.create_error_image(str(e)),)
