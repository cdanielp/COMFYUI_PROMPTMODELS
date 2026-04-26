"""
grok_text_node.py - GrokTextNode v2.0.0
=========================================
Nodo de chat con Grok. Solo texto.
Fix critico: parsing seguro de content (puede ser string o lista).
Modelos: grok-4.20, grok-4.1, grok-4.1-fast.
Eliminado: Grok_Multimodal_Vision (diagnostico), Grok_Prompt_Architect.
"""

import os
import logging
from .grok_core import GrokCore, TEXT_MODELS

logger = logging.getLogger("ComfyUI_PromptModels")


class GrokTextNode:
    """
    Chat con Grok. Texto con razonamiento avanzado.
    Fix v2.0.0: parsing robusto de content (string o lista de partes).
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "prompt": ("STRING", {
                    "multiline": True,
                    "default": "Escribe tu mensaje aqui...",
                }),
                "model": (TEXT_MODELS, {"default": "grok-4.1"}),
            },
            "optional": {
                "system_prompt": ("STRING", {
                    "multiline": True,
                    "default": "You are a helpful assistant.",
                }),
                "temperature": ("FLOAT", {
                    "default": 0.7, "min": 0.0, "max": 2.0, "step": 0.1,
                }),
                "api_key": ("STRING", {"default": ""}),
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("texto",)
    FUNCTION = "generate"
    CATEGORY = "PromptModels/Grok"

    def generate(self, prompt, model, system_prompt="", temperature=0.7, api_key=""):
        key = (api_key or "").strip() or os.getenv("XAI_API_KEY", "")
        if not key:
            logger.error("[GrokTextNode] API Key no configurada.")
            return ("Error: API Key de xAI no encontrada en el nodo ni en XAI_API_KEY.",)

        try:
            core = GrokCore(key)
            res = core.chat_completion(
                model=model,
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=temperature,
            )
            if res.get("error"):
                return (f"API Error: {res.get('message')}",)

            # Fix critico: content puede ser string o lista de partes (xAI reasoning models)
            content = res.get("choices", [{}])[0].get("message", {}).get("content", "")
            if isinstance(content, list):
                content = content[0].get("text", "") if content else ""

            return (content,)

        except Exception as e:
            logger.error(f"[GrokTextNode] Error: {e}")
            return (f"Error: {str(e)}",)
