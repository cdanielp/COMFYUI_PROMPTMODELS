# ==============================================================================
# grok_text_node.py — Nodos de Texto y Visión de ComfyUI_Grok
# ==============================================================================
# Contiene el nodo original V1 (Legado) y el nuevo nodo V2 Multimodal.
# Integra fallback automático a la variable de entorno XAI_API_KEY.
# ==============================================================================

import os
import logging
from .grok_core import GrokCore

log = logging.getLogger("ComfyUI_GrokText")

# Modelos disponibles basados en la API de xAI (2026)
GROK_TEXT_MODELS = [
    "grok-4.1-fast-reasoning", # Último modelo (de tu README)
    "grok-2-vision-1212",      # Modelo estable con visión
    "grok-2-1212",             # Modelo estable de texto
    "grok-vision-beta",
]

# ══════════════════════════════════════════════════════════════════════════════
# 1. NODO LEGADO (V1) - NO MODIFICAR ESTRUCTURA PARA NO ROMPER WORKFLOWS
# ══════════════════════════════════════════════════════════════════════════════
class GrokTextNode:
    """
    Nodo original V1. Solo acepta texto.
    Se mantiene por estricta retrocompatibilidad.
    """
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "prompt": ("STRING", {"multiline": True, "default": "Escribe tu prompt aquí..."}),
                "model": (GROK_TEXT_MODELS, {"default": "grok-2-1212"}),
                "api_key": ("STRING", {"multiline": False, "default": ""}),
            },
            "optional": {
                "system_prompt": ("STRING", {"multiline": True, "default": "You are a helpful assistant."}),
                "temperature": ("FLOAT", {"default": 0.7, "min": 0.0, "max": 2.0, "step": 0.1}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("text",)
    FUNCTION = "generate"
    CATEGORY = "Grok/Legado"

    def generate(self, prompt, model, api_key, system_prompt="", temperature=0.7):
        # Fallback a variable de entorno si el usuario deja el campo vacío
        key = api_key.strip() or os.getenv("XAI_API_KEY", "")
        if not key:
            return ("⚠️ Error: API Key de xAI no encontrada en el nodo ni en entorno.",)

        try:
            core = GrokCore(key)
            res = core.chat_completion(
                model=model,
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=temperature
            )

            if res.get("error"):
                return (f"❌ API Error: {res.get('message')}",)

            # Extraer respuesta
            text = res["choices"][0]["message"]["content"]
            return (text,)
            
        except Exception as e:
            log.error(f"[GrokTextNode] Fallo: {str(e)}")
            return (f"❌ Error interno: {str(e)}",)


# ══════════════════════════════════════════════════════════════════════════════
# 2. NODO MULTIMODAL (V2.0) - EL NUEVO ANALISTA VISUAL
# ══════════════════════════════════════════════════════════════════════════════
class Grok_Multimodal_Vision:
    """
    Nodo V2: Soporta hasta 5 imágenes de entrada.
    Convierte tensores a Base64 y enruta automáticamente la petición
    multimodal en `grok_core.py`.
    """
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "prompt": ("STRING", {"multiline": True, "default": "Describe detalladamente qué hay en esta imagen."}),
                "model": (GROK_TEXT_MODELS, {"default": "grok-2-vision-1212"}),
                "api_key": ("STRING", {"multiline": False, "default": ""}),
            },
            "optional": {
                "system_prompt": ("STRING", {"multiline": True, "default": "Eres un experto analista visual de IA."}),
                "temperature": ("FLOAT", {"default": 0.7, "min": 0.0, "max": 2.0, "step": 0.1}),
                "reasoning_effort": (["Off", "low", "medium", "high"], {"default": "Off"}),
                # PINES DE IMAGEN (Se mostrarán en ComfyUI para conectar)
                "image_1": ("IMAGE",),
                "image_2": ("IMAGE",),
                "image_3": ("IMAGE",),
                "image_4": ("IMAGE",),
                "image_5": ("IMAGE",),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("analysis",)
    FUNCTION = "analyze"
    CATEGORY = "xAI/Grok"

    def analyze(self, prompt, model, api_key, system_prompt="", temperature=0.7, reasoning_effort="Off",
                image_1=None, image_2=None, image_3=None, image_4=None, image_5=None):
        
        # 1. Resolución de API Key
        key = api_key.strip() or os.getenv("XAI_API_KEY", "")
        if not key:
            return ("⚠️ Error: API Key de xAI requerida.",)

        try:
            core = GrokCore(key)
            
            # 2. Recolección y conversión de imágenes conectadas
            images_b64 = []
            connected_images = [image_1, image_2, image_3, image_4, image_5]
            
            for idx, img_tensor in enumerate(connected_images, 1):
                if img_tensor is not None:
                    b64_str = core.tensor_to_base64(img_tensor)
                    if b64_str:
                        images_b64.append(b64_str)
                        log.info(f"[Grok_Multimodal] Imagen {idx} convertida con éxito.")

            # 3. Preparar parámetros extra (como el nuevo reasoning_effort)
            kwargs = {"temperature": temperature}
            if reasoning_effort != "Off":
                kwargs["reasoning_effort"] = reasoning_effort

            # 4. Enviar al motor core
            log.info(f"[Grok_Multimodal] Ejecutando petición. Imágenes adjuntas: {len(images_b64)}")
            res = core.chat_completion(
                model=model,
                prompt=prompt,
                system_prompt=system_prompt,
                images_b64=images_b64,
                **kwargs
            )

            # 5. Manejo de respuesta
            if res.get("error"):
                return (f"❌ API Error: {res.get('message')}",)

            analysis_text = res["choices"][0]["message"]["content"]
            return (analysis_text,)
            
        except Exception as e:
            err_msg = f"❌ Error en nodo de visión: {str(e)}"
            log.error(err_msg)
            return (err_msg,)
