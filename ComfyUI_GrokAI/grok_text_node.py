# ==============================================================================
# grok_text_node.py - Nodos de Texto y Vision de ComfyUI_Grok
# ==============================================================================
# Contiene el nodo original V1 (Legado) y el nuevo nodo V2 Multimodal.
# Integra fallback automatico a la variable de entorno XAI_API_KEY.
# ==============================================================================

import os
import logging
from .grok_core import GrokCore, TEXT_MODELS

log = logging.getLogger("ComfyUI_GrokText")


# ======================================================================
# 1. NODO LEGADO (V1)
# ======================================================================
class GrokTextNode:
    """Nodo original V1. Solo acepta texto. Retrocompatibilidad."""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "prompt": ("STRING", {"multiline": True, "default": "Escribe tu prompt aqui..."}),
                "model": (TEXT_MODELS, {"default": "grok-4-1-fast-non-reasoning"}),
                "api_key": ("STRING", {"multiline": False, "default": ""}),
            },
            "optional": {
                "system_prompt": ("STRING", {"multiline": True, "default": "You are a helpful assistant."}),
                "temperature": ("FLOAT", {"default": 0.7, "min": 0.0, "max": 2.0, "step": 0.1}),
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("text",)
    FUNCTION = "generate"
    CATEGORY = "Grok/Legado"

    def generate(self, prompt, model, api_key, system_prompt="", temperature=0.7):
        key = api_key.strip() or os.getenv("XAI_API_KEY", "")
        if not key:
            return ("Error: API Key de xAI no encontrada en el nodo ni en entorno.",)

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
            text = res["choices"][0]["message"]["content"]
            return (text,)
        except Exception as e:
            log.error(f"[GrokTextNode] Fallo: {str(e)}")
            return (f"Error interno: {str(e)}",)


# ======================================================================
# 2. NODO MULTIMODAL (V2.0) - ANALISTA VISUAL
# ======================================================================
class Grok_Multimodal_Vision:
    """
    Nodo V2: Soporta hasta 5 imagenes de entrada.
    Convierte tensores a Base64 y enruta la peticion multimodal via grok_core.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "prompt": ("STRING", {"multiline": True, "default": "Describe detalladamente que hay en esta imagen."}),
                "model": (TEXT_MODELS, {"default": "grok-4-1-fast-reasoning"}),
                "api_key": ("STRING", {"multiline": False, "default": ""}),
            },
            "optional": {
                "system_prompt": ("STRING", {"multiline": True, "default": "Eres un experto analista visual de IA."}),
                "temperature": ("FLOAT", {"default": 0.7, "min": 0.0, "max": 2.0, "step": 0.1}),
                "reasoning_effort": (["Off", "low", "medium", "high"], {"default": "Off"}),
                "image_1": ("IMAGE",),
                "image_2": ("IMAGE",),
                "image_3": ("IMAGE",),
                "image_4": ("IMAGE",),
                "image_5": ("IMAGE",),
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("analysis",)
    FUNCTION = "analyze"
    CATEGORY = "xAI/Grok"

    def analyze(self, prompt, model, api_key, system_prompt="", temperature=0.7,
                reasoning_effort="Off", image_1=None, image_2=None, image_3=None,
                image_4=None, image_5=None):

        key = api_key.strip() or os.getenv("XAI_API_KEY", "")
        if not key:
            return ("Error: API Key de xAI requerida.",)

        try:
            core = GrokCore(key)

            images_b64 = []
            for idx, img_tensor in enumerate([image_1, image_2, image_3, image_4, image_5], 1):
                if img_tensor is not None:
                    b64_str = core.tensor_to_base64(img_tensor)
                    if b64_str:
                        images_b64.append(b64_str)
                        log.info(f"[Grok_Multimodal] Imagen {idx} convertida.")

            kwargs = {"temperature": temperature}
            if reasoning_effort != "Off":
                kwargs["reasoning_effort"] = reasoning_effort

            log.info(f"[Grok_Multimodal] Peticion con {len(images_b64)} imagenes.")
            res = core.chat_completion(
                model=model,
                prompt=prompt,
                system_prompt=system_prompt,
                images_b64=images_b64,
                **kwargs,
            )

            if res.get("error"):
                return (f"API Error: {res.get('message')}",)

            return (res["choices"][0]["message"]["content"],)

        except Exception as e:
            err_msg = f"Error en nodo de vision: {str(e)}"
            log.error(err_msg)
            return (err_msg,)
