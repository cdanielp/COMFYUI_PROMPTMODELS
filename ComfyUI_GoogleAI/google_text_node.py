"""
google_text_node.py - Nodos de Texto para ComfyUI (V2.0)
=========================================================
Modelos actualizados a strings estables (Feb 2026).
Soporta: thinking_budget, youtube_url, imagen multimodal.

Autor: Prompt Models Studio | cdanielp
"""

import logging
from .google_core import GoogleAICore

logger = logging.getLogger("ComfyUI_GoogleAI")

# Strings exactos válidos en la API — Feb 2026
TEXT_MODELS = [
    "gemini-3.1-pro-preview",   # Más reciente
    "gemini-3-pro",              # Gemini 3 Pro
    "gemini-3-flash",            # Gemini 3 Flash
    "gemini-2.5-pro",            # Antes: gemini-2.5-pro-preview-06-05
    "gemini-2.5-flash",          # Antes: gemini-2.5-flash-preview-05-20
    "gemini-2.5-flash-lite",     # Antes: gemini-2.5-flash-lite-preview-06-17
]


class GoogleAI_TextNode:
    """
    Nodo de generación de texto con Gemini.
    Soporta texto puro, imagen multimodal, YouTube y thinking budget.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "prompt": ("STRING", {
                    "multiline": True,
                    "default": "Describe esta imagen en detalle.",
                }),
                "model": (TEXT_MODELS, {"default": "gemini-3.1-pro-preview"}),
                "thinking_budget": (["Off", "Low", "High"], {
                    "default": "Off",
                    "tooltip": "Low=1024 tokens, High=8192 tokens de razonamiento."
                }),
            },
            "optional": {
                "api_key": ("STRING", {"default": ""}),
                "system_prompt": ("STRING", {"multiline": True, "default": ""}),
                "image": ("IMAGE",),
                "youtube_url": ("STRING", {"default": ""}),
                "max_tokens": ("INT", {"default": 4096, "min": 64, "max": 65536, "step": 64}),
                "temperature": ("FLOAT", {"default": 0.7, "min": 0.0, "max": 2.0, "step": 0.05}),
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("text",)
    FUNCTION = "generate_text"
    CATEGORY = "Google AI/Text"

    def generate_text(self, prompt, model, thinking_budget, api_key="",
                      system_prompt="", image=None, youtube_url="",
                      max_tokens=4096, temperature=0.7):
        try:
            key = GoogleAICore.resolve_api_key(api_key)
            extra_parts = []

            if image is not None:
                img_b64 = GoogleAICore.tensor_to_base64(image, index=0)
                extra_parts.append({"inlineData": {"mimeType": "image/png", "data": img_b64}})

            if youtube_url and youtube_url.strip():
                extra_parts.append({"fileData": {"mimeType": "video/*", "fileUri": youtube_url.strip()}})

            gen_config = {"maxOutputTokens": max_tokens, "temperature": temperature}
            tb = thinking_budget if thinking_budget != "Off" else None

            result = GoogleAICore.call_gemini_text(
                api_key=key, prompt=prompt, model=model,
                system_instruction=system_prompt if system_prompt else None,
                thinking_budget=tb,
                extra_parts=extra_parts if extra_parts else None,
                generation_config=gen_config,
            )
            return (result,)

        except Exception as e:
            logger.error(f"[GoogleAI_TextNode] Error: {e}")
            return (f"❌ Error: {str(e)}",)


class GoogleAI_TextVisionNode:
    """Análisis de imágenes con Gemini Vision. Requiere imagen obligatoria."""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "prompt": ("STRING", {"multiline": True, "default": "Describe esta imagen en detalle."}),
                "model": (TEXT_MODELS, {"default": "gemini-3.1-pro-preview"}),
            },
            "optional": {
                "api_key": ("STRING", {"default": ""}),
                "system_prompt": ("STRING", {"multiline": True, "default": ""}),
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("analysis",)
    FUNCTION = "analyze_image"
    CATEGORY = "Google AI/Text"

    def analyze_image(self, image, prompt, model, api_key="", system_prompt=""):
        try:
            key = GoogleAICore.resolve_api_key(api_key)
            img_b64 = GoogleAICore.tensor_to_base64(image, index=0)
            extra_parts = [{"inlineData": {"mimeType": "image/png", "data": img_b64}}]

            result = GoogleAICore.call_gemini_text(
                api_key=key, prompt=prompt, model=model,
                system_instruction=system_prompt if system_prompt else None,
                extra_parts=extra_parts,
            )
            return (result,)

        except Exception as e:
            logger.error(f"[GoogleAI_TextVisionNode] Error: {e}")
            return (f"❌ Error: {str(e)}",)
