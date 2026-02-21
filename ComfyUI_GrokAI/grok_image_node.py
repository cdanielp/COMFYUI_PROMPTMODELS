"""
grok_image_node.py - Nodos de Imagen para ComfyUI
===================================================
Suite 2: Grok_Image_Generator, Grok_Image_Editor
Anti-Crash: HTTP 400/429 → imagen roja 512x512, no crashea.

Autor: Prompt Models Studio | cdanielp
"""

import logging
import torch
from .grok_core import GrokCore, IMAGE_MODELS

logger = logging.getLogger("ComfyUI_GrokAI")

ASPECT_RATIOS = ["1:1", "16:9", "9:16", "4:3", "3:4"]


class Grok_Image_Generator:
    """
    Generación Text-to-Image con Grok.
    Soporta batch (1-4 imágenes) y múltiples aspect ratios.
    Anti-Crash: errores HTTP retornan imagen roja en vez de crash.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "prompt": ("STRING", {
                    "multiline": True,
                    "default": "A hyper-realistic photograph of a cyberpunk city at night",
                }),
                "model": (IMAGE_MODELS, {"default": "grok-2-image-1212"}),
                "aspect_ratio": (ASPECT_RATIOS, {
                    "default": "1:1",
                    "tooltip": "Relación de aspecto de la imagen.",
                }),
                "batch_size": ("INT", {
                    "default": 1, "min": 1, "max": 4,
                    "tooltip": "Cantidad de imágenes a generar (1-4).",
                }),
            },
            "optional": {
                "api_key": ("STRING", {"default": ""}),
            },
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("images",)
    FUNCTION = "generate"
    CATEGORY = "Grok AI/Image"
    DESCRIPTION = "Genera imágenes con Grok. Anti-crash: errores → imagen roja."

    def generate(self, prompt, model, aspect_ratio, batch_size, api_key=""):
        try:
            key = GrokCore.resolve_api_key(api_key)
            size = GrokCore.aspect_ratio_to_size(aspect_ratio)

            images_b64 = GrokCore.generate_image(
                api_key=key,
                prompt=prompt,
                model=model,
                n=batch_size,
                size=size,
            )

            if not images_b64:
                logger.warning("[Image_Generator] API no retornó imágenes.")
                return (GrokCore.create_error_image("La API no retornó imágenes."),)

            # Convertir a tensores y apilar en batch
            tensors = [GrokCore.base64_to_tensor(b64) for b64 in images_b64]
            batch = torch.cat(tensors, dim=0)  # [B, H, W, C]

            logger.info(
                f"[Image_Generator] {batch.shape[0]} imagen(es) generada(s): "
                f"{batch.shape[2]}x{batch.shape[1]}"
            )
            return (batch,)

        except RuntimeError as e:
            error_msg = str(e)
            if any(code in error_msg for code in ["400", "429", "safety", "block", "nsfw"]):
                logger.warning(f"[Image_Generator] Safety/Rate limit: {error_msg}")
            else:
                logger.error(f"[Image_Generator] Error: {error_msg}")
            return (GrokCore.create_error_image(error_msg),)

        except Exception as e:
            logger.error(f"[Image_Generator] Error inesperado: {e}")
            return (GrokCore.create_error_image(str(e)),)


class Grok_Image_Editor:
    """
    Edición de imágenes usando lenguaje natural con Grok.
    Recibe una imagen ComfyUI y un prompt de edición.
    Anti-Crash: errores → imagen roja.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE", {"tooltip": "Imagen base a editar."}),
                "prompt": ("STRING", {
                    "multiline": True,
                    "default": "Make the sky a dramatic sunset with purple and orange colors",
                    "tooltip": "Instrucción de edición en lenguaje natural.",
                }),
            },
            "optional": {
                "api_key": ("STRING", {"default": ""}),
                "model": (IMAGE_MODELS, {"default": "grok-2-image-1212"}),
            },
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("edited_image",)
    FUNCTION = "edit"
    CATEGORY = "Grok AI/Image"
    DESCRIPTION = "Edita imágenes con lenguaje natural usando Grok."

    def edit(self, image, prompt, api_key="", model="grok-2-image-1212"):
        try:
            key = GrokCore.resolve_api_key(api_key)

            # Convertir tensor de entrada a base64
            img_b64 = GrokCore.tensor_to_base64(image, index=0)

            # Enviar a la API de edición
            results_b64 = GrokCore.edit_image(
                api_key=key,
                image_b64=img_b64,
                prompt=prompt,
                model=model,
            )

            if not results_b64:
                logger.warning("[Image_Editor] API no retornó imágenes editadas.")
                return (GrokCore.create_error_image("La API no retornó resultado."),)

            # Convertir el primer resultado a tensor
            edited_tensor = GrokCore.base64_to_tensor(results_b64[0])
            logger.info(
                f"[Image_Editor] Imagen editada: "
                f"{edited_tensor.shape[2]}x{edited_tensor.shape[1]}"
            )
            return (edited_tensor,)

        except RuntimeError as e:
            error_msg = str(e)
            logger.error(f"[Image_Editor] Error: {error_msg}")
            return (GrokCore.create_error_image(error_msg),)

        except Exception as e:
            logger.error(f"[Image_Editor] Error inesperado: {e}")
            return (GrokCore.create_error_image(str(e)),)
