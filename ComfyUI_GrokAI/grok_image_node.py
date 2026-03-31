# ==============================================================================
# grok_image_node.py - Generador y Editor de Imagenes de ComfyUI_Grok
# ==============================================================================
# V1 (Legado) para Text-to-Image puro.
# V2 (Grok_Image_Master) con soporte para Image-to-Image (edicion).
# Anti-Crash: imagen roja para errores de API.
#
# API xAI 2026: aspect_ratio + resolution (no size en pixeles).
# ==============================================================================

import os
import logging
import torch
from .grok_core import GrokCore, IMAGE_MODELS, IMAGE_ASPECT_RATIOS

log = logging.getLogger("ComfyUI_GrokImage")


# ======================================================================
# 1. NODO LEGADO (V1) - Text-to-Image Basico
# ======================================================================
class GrokImageNode:
    """Nodo V1: generacion pura desde texto. Retrocompatibilidad."""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "prompt": ("STRING", {"multiline": True, "default": "A futuristic city in cyberpunk style"}),
                "model": (IMAGE_MODELS, {"default": "grok-imagine-image"}),
                "aspect_ratio": (IMAGE_ASPECT_RATIOS, {"default": "1:1"}),
                "resolution": (["1k", "2k"], {"default": "1k"}),
                "batch_size": ("INT", {"default": 1, "min": 1, "max": 10}),
                "api_key": ("STRING", {"multiline": False, "default": ""}),
            },
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("images",)
    FUNCTION = "generate"
    CATEGORY = "Grok/Legado"

    def generate(self, prompt, model, aspect_ratio, resolution, batch_size, api_key):
        key = api_key.strip() or os.getenv("XAI_API_KEY", "")
        if not key:
            log.error("[GrokImageNode] No hay API Key.")
            return (GrokCore.create_error_tensor(),)

        try:
            core = GrokCore(key)
            res = core.generate_image(
                prompt=prompt, model=model,
                aspect_ratio=aspect_ratio, resolution=resolution, n=batch_size,
            )

            if res.get("error"):
                log.error(f"[GrokImageNode] API Error: {res.get('message')}")
                return (core.create_error_tensor(),)

            data_list = res.get("data", [])
            if not data_list:
                log.error("[GrokImageNode] Respuesta vacia de la API.")
                return (core.create_error_tensor(),)

            tensors = []
            for item in data_list:
                b64 = item.get("b64_json")
                if b64:
                    tensors.append(core.base64_to_tensor(b64))
                else:
                    url = item.get("url")
                    if url:
                        tensors.append(core.url_to_tensor(url))

            if not tensors:
                return (core.create_error_tensor(),)

            return (torch.cat(tensors, dim=0),)

        except Exception as e:
            log.error(f"[GrokImageNode] Crash evitado: {str(e)}")
            return (GrokCore.create_error_tensor(),)


# ======================================================================
# 2. NODO V2 MASTER - Text-to-Image & Image-to-Image (Edicion)
# ======================================================================
class Grok_Image_Master:
    """
    Nodo V2: Generador avanzado.
    Sin imagen conectada -> Text-to-Image (POST /v1/images/generations).
    Con imagen conectada -> Image-to-Image (POST /v1/images/edits).
    Anti-crash: imagen roja si la API falla o rechaza por NSFW.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "prompt": ("STRING", {"multiline": True, "default": "Transform the background into a snowy mountain"}),
                "model": (IMAGE_MODELS, {"default": "grok-imagine-image"}),
                "aspect_ratio": (IMAGE_ASPECT_RATIOS, {"default": "1:1"}),
                "resolution": (["1k", "2k"], {"default": "1k"}),
                "api_key": ("STRING", {"multiline": False, "default": ""}),
            },
            "optional": {
                "image": ("IMAGE",),
                "mask": ("MASK",),
                "n": ("INT", {
                    "default": 1, "min": 1, "max": 10, "step": 1,
                    "tooltip": "Numero de imagenes a generar (1-10).",
                }),
            },
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)
    FUNCTION = "generate_master"
    CATEGORY = "xAI/Grok"

    def generate_master(self, prompt, model, aspect_ratio, resolution, api_key,
                        image=None, mask=None, n=1):
        key = api_key.strip() or os.getenv("XAI_API_KEY", "")
        if not key:
            log.error("[Grok_Image_Master] API Key no configurada.")
            return (GrokCore.create_error_tensor(),)

        try:
            core = GrokCore(key)

            # --- MODO 1: TEXT-TO-IMAGE ---
            if image is None:
                log.info("[Grok_Image_Master] Modo: Text-to-Image")
                res = core.generate_image(
                    prompt=prompt, model=model,
                    aspect_ratio=aspect_ratio, resolution=resolution, n=n,
                )

                if res.get("error"):
                    log.error(f"API Error: {res.get('message')}")
                    return (core.create_error_tensor(),)

                return self._extract_images(core, res)

            # --- MODO 2: IMAGE-TO-IMAGE / EDIT ---
            log.info("[Grok_Image_Master] Modo: Image-to-Image / Edicion")
            img_b64 = core.tensor_to_base64(image, format="PNG")
            image_data_uri = f"data:image/png;base64,{img_b64}"

            res = core.edit_image(
                prompt=prompt, image_url=image_data_uri, model=model, n=n,
            )

            if res.get("error"):
                log.error(f"[Grok_Image_Master] Error: {res.get('message')}")
                return (core.create_error_tensor(),)

            return self._extract_images(core, res)

        except Exception as e:
            log.error(f"[Grok_Image_Master] Crash interceptado: {str(e)}")
            return (GrokCore.create_error_tensor(),)

    @staticmethod
    def _extract_images(core, res):
        """Extrae imagenes de la respuesta y las concatena en tensor batch."""
        data_list = res.get("data", [])
        if not data_list:
            return (core.create_error_tensor(),)

        tensors = []
        for item in data_list:
            b64 = item.get("b64_json")
            if b64:
                tensors.append(core.base64_to_tensor(b64))
            else:
                url = item.get("url")
                if url:
                    tensors.append(core.url_to_tensor(url))

        if not tensors:
            return (core.create_error_tensor(),)

        return (torch.cat(tensors, dim=0),)
