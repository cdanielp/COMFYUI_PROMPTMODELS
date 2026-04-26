"""
grok_image_node.py - PMS_GrokImageGen v2.0.0
=============================================
Fusion de GrokImageNode + Grok_Image_Master en un solo nodo.
Sin imagen: POST /v1/images/generations (text-to-image).
Con imagen: POST /v1/images/edits (image-to-image, JSON no multipart).
Model ID: grok-imagine-image.
La API devuelve URL temporal -> descarga con requests y convierte a tensor.
Anti-crash: imagen roja 512x512 si la API falla.
"""

import os
import logging
import requests
import torch
from .grok_core import GrokCore

logger = logging.getLogger("ComfyUI_PromptModels")

_MODEL_ID      = "grok-imagine-image"
_ASPECT_RATIOS = ["1:1", "2:3", "3:2"]


class PMS_GrokImageGen:
    """
    Grok Image Gen. Genera o edita imagenes.
    Sin image_ref: text-to-image via /v1/images/generations.
    Con image_ref: image-to-image via /v1/images/edits (JSON).
    Output: tensor IMAGE + URL o mensaje de error.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "prompt": ("STRING", {
                    "multiline": True,
                    "default": "A futuristic city in cyberpunk style",
                }),
                "aspect_ratio": (_ASPECT_RATIOS, {"default": "1:1"}),
                "n": ("INT", {
                    "default": 1, "min": 1, "max": 4, "step": 1,
                    "tooltip": "Numero de imagenes a generar (1-4).",
                }),
            },
            "optional": {
                "image_ref": ("IMAGE", {
                    "tooltip": "Imagen de referencia para edicion (image-to-image).",
                }),
                "api_key": ("STRING", {"default": ""}),
            },
        }

    RETURN_TYPES = ("IMAGE", "STRING")
    RETURN_NAMES = ("imagen", "url_o_error")
    FUNCTION = "generar"
    CATEGORY = "PromptModels/Grok"

    @classmethod
    def IS_CHANGED(cls, **kwargs):
        return float("NaN")

    def generar(self, prompt, aspect_ratio, n, image_ref=None, api_key=""):
        key = (api_key or "").strip() or os.getenv("XAI_API_KEY", "")
        if not key:
            logger.error("[PMS_GrokImageGen] API Key no configurada.")
            return (GrokCore.create_error_tensor(), "Error: API Key de xAI requerida.")

        try:
            core = GrokCore(key)

            if image_ref is None:
                logger.info("[PMS_GrokImageGen] Modo: text-to-image")
                res = core.generate_image(
                    prompt=prompt,
                    model=_MODEL_ID,
                    aspect_ratio=aspect_ratio,
                    n=n,
                    response_format="url",
                )
            else:
                logger.info("[PMS_GrokImageGen] Modo: image-to-image (edits)")
                img_b64 = core.tensor_to_base64(image_ref, format="PNG")
                image_data_uri = f"data:image/png;base64,{img_b64}"
                res = core.edit_image(
                    prompt=prompt,
                    image_url=image_data_uri,
                    model=_MODEL_ID,
                    n=n,
                    response_format="url",
                )

            if res.get("error"):
                msg = res.get("message", "Error desconocido de la API.")
                logger.error(f"[PMS_GrokImageGen] API Error: {msg}")
                return (GrokCore.create_error_tensor(), f"Error: {msg}")

            data_list = res.get("data", [])
            if not data_list:
                logger.error("[PMS_GrokImageGen] Respuesta vacia de la API.")
                return (GrokCore.create_error_tensor(), "Error: respuesta vacia de la API.")

            tensors = []
            first_url = ""
            for item in data_list:
                url = item.get("url", "")
                b64 = item.get("b64_json", "")
                if url:
                    tensors.append(core.url_to_tensor(url))
                    if not first_url:
                        first_url = url
                elif b64:
                    tensors.append(core.base64_to_tensor(b64))

            if not tensors:
                return (GrokCore.create_error_tensor(), "Error: sin imagenes validas en respuesta.")

            return (torch.cat(tensors, dim=0), first_url)

        except Exception as e:
            logger.error(f"[PMS_GrokImageGen] Error: {e}")
            return (GrokCore.create_error_tensor(), f"Error: {str(e)}")
