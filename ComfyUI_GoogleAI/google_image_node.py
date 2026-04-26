"""
google_image_node.py - PMS_NanaBanana v2.0.0
=============================================
Generacion de imagen con Gemini (generateContent + responseModalities TEXT+IMAGE).
Modelos: gemini-3-pro-image-preview, gemini-3.1-flash-image-preview.
Sin Imagen 4, imagen-3.0 ni imagen-4.0.
Hasta 3 imagenes de referencia opcionales.
"""

import logging
from .google_core import GoogleAICore

logger = logging.getLogger("ComfyUI_PromptModels")

NB_MODELS = [
    "gemini-3-pro-image-preview",
    "gemini-3.1-flash-image-preview",
]

NB_ASPECT_RATIOS = ["1:1", "9:16", "16:9", "3:4", "4:3", "2:3", "3:2"]
NB_RESOLUTIONS   = ["1K", "2K", "4K"]


class PMS_NanaBanana:
    """
    Nano Banana - Imagen IA.
    Genera imagenes con Gemini via generateContent + responseModalities TEXT+IMAGE.
    negative_prompt se adjunta al prompt como restriccion de estilo.
    Hasta 3 imagenes de referencia para guiar composicion o estilo.
    Anti-crash: devuelve imagen roja 512x512 si la API falla.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "prompt": ("STRING", {
                    "multiline": True,
                    "default": "A beautiful cinematic portrait, photorealistic, 8K detail",
                }),
                "model": (NB_MODELS, {"default": "gemini-3-pro-image-preview"}),
                "aspect_ratio": (NB_ASPECT_RATIOS, {"default": "1:1"}),
                "resolution": (NB_RESOLUTIONS, {
                    "default": "2K",
                    "tooltip": "1K, 2K o 4K. El modelo puede ajustar si no soporta la resolucion.",
                }),
                "seed": ("INT", {"default": 0, "min": 0, "max": 0xFFFFFFFF}),
            },
            "optional": {
                "negative_prompt": ("STRING", {
                    "multiline": True,
                    "default": "",
                    "tooltip": "Elementos a evitar en la imagen.",
                }),
                "image_1": ("IMAGE", {"tooltip": "Referencia 1: estilo, personaje o composicion."}),
                "image_2": ("IMAGE", {"tooltip": "Referencia 2 (opcional)."}),
                "image_3": ("IMAGE", {"tooltip": "Referencia 3 (opcional)."}),
                "api_key": ("STRING", {"default": ""}),
            },
        }

    RETURN_TYPES = ("IMAGE", "STRING")
    RETURN_NAMES = ("imagen", "descripcion")
    FUNCTION = "generar"
    CATEGORY = "PromptModels/Google"

    def generar(self, prompt, model, aspect_ratio, resolution, seed,
                negative_prompt="", image_1=None, image_2=None, image_3=None,
                api_key=""):
        try:
            key = GoogleAICore.resolve_api_key(api_key)

            full_prompt = prompt
            if negative_prompt and negative_prompt.strip():
                full_prompt += f"\n\nEvitar en la imagen: {negative_prompt.strip()}"

            ref_images_b64 = []
            for ref in [image_1, image_2, image_3]:
                if ref is not None:
                    ref_images_b64.append(GoogleAICore.compress_image_for_api(ref, 0))

            logger.info(
                f"[PMS_NanaBanana] model={model} | {aspect_ratio} | {resolution} | "
                f"refs={len(ref_images_b64)} | seed={seed}"
            )

            img_bytes, description = GoogleAICore.generate_image_gemini(
                api_key=key,
                prompt=full_prompt,
                model=model,
                reference_images_b64=ref_images_b64 if ref_images_b64 else None,
                aspect_ratio=aspect_ratio,
                image_size=resolution,
                seed=seed,
            )
            return (GoogleAICore.bytes_to_image_tensor(img_bytes), description)

        except Exception as e:
            logger.error(f"[PMS_NanaBanana] Error: {e}")
            return (GoogleAICore.create_error_image(str(e)), f"Error: {str(e)}")
