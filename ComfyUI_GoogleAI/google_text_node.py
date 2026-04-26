"""
google_text_node.py - PMS_GeminiChat v2.0.0
============================================
Nodo unificado de chat y vision con Gemini.
Sin imagen conectada -> texto puro.
Con imagen conectada -> vision multimodal.
ThinkingConfig auto: thinkingLevel (Gemini 3.x) / thinkingBudget (Gemini 2.5).
"""

import logging
from .google_core import GoogleAICore

logger = logging.getLogger("ComfyUI_PromptModels")

GEMINI_CHAT_MODELS = [
    "gemini-3.1-pro-preview",
    "gemini-3-flash-preview",
    "gemini-3.1-flash-lite-preview",
    "gemini-2.5-pro",
    "gemini-2.5-flash",
]

_THINKING_LEVEL_MAP = {
    "Off":    "none",
    "Low":    "low",
    "Medium": "medium",
    "High":   "high",
}

_THINKING_BUDGET_MAP = {
    "Off":    0,
    "Low":    1024,
    "Medium": 4096,
    "High":   8192,
}


def _build_thinking_config(model: str, level: str):
    """
    Gemini 3.x (contiene '3.' o '3-') -> thinkingLevel (string).
    Gemini 2.5 (contiene '2.5')        -> thinkingBudget (int).
    Nunca envia ambos simultaneamente.
    """
    if "3." in model or "3-" in model:
        return {"thinkingLevel": _THINKING_LEVEL_MAP.get(level, "none")}
    if "2.5" in model:
        return {"thinkingBudget": _THINKING_BUDGET_MAP.get(level, 0)}
    return None


class PMS_GeminiChat:
    """
    Chat con Gemini. Texto puro o vision si se conecta una imagen.
    ThinkingConfig se detecta automaticamente segun familia del modelo.
    Outputs: texto generado + nombre del modelo usado.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "prompt": ("STRING", {
                    "multiline": True,
                    "default": "Describe esta imagen en detalle.",
                }),
                "model": (GEMINI_CHAT_MODELS, {"default": "gemini-3.1-pro-preview"}),
                "thinking": (["Off", "Low", "Medium", "High"], {
                    "default": "Off",
                    "tooltip": (
                        "Gemini 3.x: thinkingLevel (none/low/medium/high). "
                        "Gemini 2.5: thinkingBudget (0/1024/4096/8192 tokens)."
                    ),
                }),
            },
            "optional": {
                "image": ("IMAGE", {
                    "tooltip": "Imagen para vision. Si no conectada: modo texto puro.",
                }),
                "system_prompt": ("STRING", {"multiline": True, "default": ""}),
                "max_tokens": ("INT", {
                    "default": 4096, "min": 64, "max": 65536, "step": 64,
                }),
                "temperature": ("FLOAT", {
                    "default": 0.7, "min": 0.0, "max": 2.0, "step": 0.05,
                }),
                "api_key": ("STRING", {"default": ""}),
            },
        }

    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("texto", "modelo_usado")
    FUNCTION = "chat"
    CATEGORY = "PromptModels/Google"

    def chat(self, prompt, model, thinking,
             image=None, system_prompt="",
             max_tokens=4096, temperature=0.7, api_key=""):
        try:
            key = GoogleAICore.resolve_api_key(api_key)
            extra_parts = []

            if image is not None:
                img_b64 = GoogleAICore.tensor_to_base64(image, index=0)
                extra_parts.append({"inlineData": {"mimeType": "image/png", "data": img_b64}})
                logger.info(f"[PMS_GeminiChat] Modo vision | model={model}")
            else:
                logger.info(f"[PMS_GeminiChat] Modo texto | model={model}")

            gen_config = {
                "maxOutputTokens": max_tokens,
                "temperature": temperature,
            }
            thinking_cfg = _build_thinking_config(model, thinking)
            if thinking_cfg is not None:
                gen_config["thinkingConfig"] = thinking_cfg

            result = GoogleAICore.call_gemini_text(
                api_key=key,
                prompt=prompt,
                model=model,
                system_instruction=system_prompt.strip() if system_prompt.strip() else None,
                thinking_budget=None,
                extra_parts=extra_parts if extra_parts else None,
                generation_config=gen_config,
            )
            return (result, model)

        except Exception as e:
            logger.error(f"[PMS_GeminiChat] Error: {e}")
            return (f"Error: {str(e)}", model)
