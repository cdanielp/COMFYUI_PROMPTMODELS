"""
google_text_node.py - Nodos de Texto para ComfyUI (V2.5.0)
===========================================================
V2.5.0:
- Model strings corregidos (gemini-3-flash-preview, no gemini-3-flash)
- 5 pines de imagen (image_1..image_5) en TextNode
- ThinkingConfig: Off/Low/Medium/High (thinkingLevel para 3+, thinkingBudget para 2.5)
- gemini-3-pro-preview eliminado (deprecated 9 Mar 2026)
- TextVisionNode: 1 obligatoria + 4 opcionales

Autor: Prompt Models Studio | cdanielp
"""

import logging
from .google_core import GoogleAICore

logger = logging.getLogger("ComfyUI_GoogleAI")

# Strings exactos validos en la API - Mar 2026
TEXT_MODELS = [
    "gemini-3.1-pro-preview",    # Mas reciente - thinkingLevel
    "gemini-3-flash-preview",    # Gemini 3 Flash - thinkingLevel
    "gemini-2.5-pro",            # Gemini 2.5 Pro - thinkingBudget
    "gemini-2.5-flash",          # Gemini 2.5 Flash - thinkingBudget
]


class GoogleAI_TextNode:
    """
    Nodo de generacion de texto con Gemini.
    Soporta texto puro, hasta 5 imagenes multimodal, YouTube y thinking.
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
                "thinking_budget": (["Off", "Low", "Medium", "High"], {
                    "default": "Off",
                    "tooltip": (
                        "Gemini 3+: thinkingLevel (low/medium/high). "
                        "Gemini 2.5: thinkingBudget (1024/4096/8192 tokens)."
                    ),
                }),
            },
            "optional": {
                "api_key": ("STRING", {"default": ""}),
                "system_prompt": ("STRING", {"multiline": True, "default": ""}),
                "image_1": ("IMAGE", {"tooltip": "Imagen 1 para analisis multimodal."}),
                "image_2": ("IMAGE", {"tooltip": "Imagen 2 (opcional)."}),
                "image_3": ("IMAGE", {"tooltip": "Imagen 3 (opcional)."}),
                "image_4": ("IMAGE", {"tooltip": "Imagen 4 (opcional)."}),
                "image_5": ("IMAGE", {"tooltip": "Imagen 5 (opcional)."}),
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
                      system_prompt="",
                      image_1=None, image_2=None, image_3=None,
                      image_4=None, image_5=None,
                      youtube_url="",
                      max_tokens=4096, temperature=0.7):
        try:
            key = GoogleAICore.resolve_api_key(api_key)
            extra_parts = []

            # V2.5.0: Multiples imagenes
            for img in [image_1, image_2, image_3, image_4, image_5]:
                if img is not None:
                    img_b64 = GoogleAICore.tensor_to_base64(img, index=0)
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
    """
    Analisis de imagenes con Gemini Vision.
    1 imagen obligatoria + 4 opcionales para comparaciones/secuencias.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image_1": ("IMAGE", {"tooltip": "Imagen principal (obligatoria)."}),
                "prompt": ("STRING", {"multiline": True, "default": "Describe esta imagen en detalle."}),
                "model": (TEXT_MODELS, {"default": "gemini-3.1-pro-preview"}),
            },
            "optional": {
                "api_key": ("STRING", {"default": ""}),
                "system_prompt": ("STRING", {"multiline": True, "default": ""}),
                "image_2": ("IMAGE", {"tooltip": "Imagen adicional 2 (opcional)."}),
                "image_3": ("IMAGE", {"tooltip": "Imagen adicional 3 (opcional)."}),
                "image_4": ("IMAGE", {"tooltip": "Imagen adicional 4 (opcional)."}),
                "image_5": ("IMAGE", {"tooltip": "Imagen adicional 5 (opcional)."}),
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("analysis",)
    FUNCTION = "analyze_image"
    CATEGORY = "Google AI/Text"

    def analyze_image(self, image_1, prompt, model, api_key="", system_prompt="",
                      image_2=None, image_3=None, image_4=None, image_5=None):
        try:
            key = GoogleAICore.resolve_api_key(api_key)
            extra_parts = []

            for img in [image_1, image_2, image_3, image_4, image_5]:
                if img is not None:
                    img_b64 = GoogleAICore.tensor_to_base64(img, index=0)
                    extra_parts.append({"inlineData": {"mimeType": "image/png", "data": img_b64}})

            result = GoogleAICore.call_gemini_text(
                api_key=key, prompt=prompt, model=model,
                system_instruction=system_prompt if system_prompt else None,
                extra_parts=extra_parts,
            )
            return (result,)

        except Exception as e:
            logger.error(f"[GoogleAI_TextVisionNode] Error: {e}")
            return (f"❌ Error: {str(e)}",)
