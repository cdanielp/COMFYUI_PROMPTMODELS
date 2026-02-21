# ==============================================================================
# grok_image_node.py — Generador y Editor de Imágenes de ComfyUI_Grok
# ==============================================================================
# Contiene el nodo V1 (Legado) para Text-to-Image puro.
# Introduce el nodo V2 (Grok_Image_Master) con soporte para Image-to-Image.
# Incluye sistema Anti-Crash (Imagen Roja) para errores de API.
# ==============================================================================

import os
import requests
import logging
import torch
from .grok_core import GrokCore, XAI_API_BASE

log = logging.getLogger("ComfyUI_GrokImage")

GROK_IMAGE_MODELS = [
    "grok-2-image-1212",
    "grok-2-image"
]

ASPECT_RATIOS = ["1:1", "16:9", "9:16", "4:3", "3:4"]

# ══════════════════════════════════════════════════════════════════════════════
# 1. NODO LEGADO (V1) - Text-to-Image Básico
# ══════════════════════════════════════════════════════════════════════════════
class GrokImageNode:
    """
    Nodo original V1. Generación pura desde texto.
    Se mantiene intacto para no romper los JSON de workflows antiguos.
    """
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "prompt": ("STRING", {"multiline": True, "default": "A futuristic city in cyberpunk style"}),
                "model": (GROK_IMAGE_MODELS, {"default": "grok-2-image-1212"}),
                "aspect_ratio": (ASPECT_RATIOS, {"default": "1:1"}),
                "batch_size": ("INT", {"default": 1, "min": 1, "max": 4}),
                "api_key": ("STRING", {"multiline": False, "default": ""}),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("images",)
    FUNCTION = "generate"
    CATEGORY = "Grok/Legado"

    def generate(self, prompt, model, aspect_ratio, batch_size, api_key):
        key = api_key.strip() or os.getenv("XAI_API_KEY", "")
        if not key:
            log.error("[GrokImageNode] Falla: No hay API Key.")
            return (GrokCore.create_error_tensor(),)

        try:
            core = GrokCore(key)
            # Adaptamos el aspect ratio al formato que espera xAI/OpenAI
            size = "1024x1024"
            if aspect_ratio == "16:9": size = "1280x720"
            elif aspect_ratio == "9:16": size = "720x1280"
            
            res = core.generate_image(
                prompt=prompt, 
                model=model, 
                size=size,
                n=batch_size
            )

            if res.get("error"):
                log.error(f"[GrokImageNode] Error de API: {res.get('message')}")
                return (core.create_error_tensor(),)

            # Extraemos la imagen en base64 y la convertimos a Tensor [1, H, W, C]
            b64_img = res["data"][0]["b64_json"]
            out_tensor = core.base64_to_tensor(b64_img)
            
            # Si se pidieron múltiples imágenes, habría que concatenarlas (simplificado aquí)
            return (out_tensor,)

        except Exception as e:
            log.error(f"[GrokImageNode] Crash evitado. Retornando imagen roja. Error: {str(e)}")
            return (GrokCore.create_error_tensor(),)


# ══════════════════════════════════════════════════════════════════════════════
# 2. NODO V2 MASTER - Text-to-Image & Image-to-Image (Edición)
# ══════════════════════════════════════════════════════════════════════════════
class Grok_Image_Master:
    """
    Nodo V2: Generador avanzado.
    Si se conecta una imagen base, cambia automáticamente al endpoint de edición.
    Si la API rechaza el prompt por NSFW, devuelve una imagen roja en vez de crashear.
    """
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "prompt": ("STRING", {"multiline": True, "default": "Transform the background into a snowy mountain"}),
                "model": (GROK_IMAGE_MODELS, {"default": "grok-2-image-1212"}),
                "aspect_ratio": (ASPECT_RATIOS, {"default": "1:1"}),
                "api_key": ("STRING", {"multiline": False, "default": ""}),
            },
            "optional": {
                "image": ("IMAGE",),       # Imagen base a editar
                "mask": ("MASK",),         # (Opcional) Máscara para inpainting
                "strength": ("FLOAT", {"default": 0.8, "min": 0.1, "max": 1.0, "step": 0.05}),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)
    FUNCTION = "generate_master"
    CATEGORY = "xAI/Grok"

    def generate_master(self, prompt, model, aspect_ratio, api_key, image=None, mask=None, strength=0.8):
        key = api_key.strip() or os.getenv("XAI_API_KEY", "")
        core = GrokCore(key) if key else None
        
        if not core:
            log.error("[Grok_Image_Master] Error: API Key no configurada.")
            # Sistema Anti-crash: devolvemos tensor rojo si no hay llave
            # Es necesario instanciar GrokCore al menos para el método estático si no usamos la clase directamente
            return (GrokCore.create_error_tensor(),)

        try:
            # --- MODO 1: TEXT-TO-IMAGE (Sin imagen conectada) ---
            if image is None:
                log.info("[Grok_Image_Master] Modo: Text-to-Image")
                size = "1024x1024"
                if aspect_ratio == "16:9": size = "1280x720"
                elif aspect_ratio == "9:16": size = "720x1280"
                
                res = core.generate_image(prompt=prompt, model=model, size=size)
                
                if res.get("error"):
                    log.error(f"API Error: {res.get('message')}")
                    return (core.create_error_tensor(),)
                    
                b64_img = res["data"][0]["b64_json"]
                return (core.base64_to_tensor(b64_img),)

            # --- MODO 2: IMAGE-TO-IMAGE / EDIT (Con imagen conectada) ---
            log.info("[Grok_Image_Master] Modo: Image-to-Image / Edición")
            
            # Convertimos la imagen de ComfyUI (Tensor) a Base64
            img_b64 = core.tensor_to_base64(image, format="PNG")
            
            # Endpoint estándar REST para edición de imágenes
            url = f"{XAI_API_BASE}/images/edits"
            
            # Construimos el payload
            payload = {
                "image": f"data:image/png;base64,{img_b64}",
                "prompt": prompt,
                "model": model,
                "response_format": "b64_json"
            }
            
            # Realizamos la petición HTTP Pura
            response = requests.post(url, headers=core.headers, json=payload, timeout=180)
            
            if not response.ok:
                err_msg = response.json().get("error", {}).get("message", response.text)
                log.error(f"[Grok_Image_Master] Error de Edición HTTP {response.status_code}: {err_msg}")
                return (core.create_error_tensor(),)
                
            res_json = response.json()
            b64_result = res_json["data"][0]["b64_json"]
            
            # Retornamos el tensor convertido
            return (core.base64_to_tensor(b64_result),)

        except Exception as e:
            log.error(f"[Grok_Image_Master] Crash fatal interceptado: {str(e)}")
            return (GrokCore.create_error_tensor(),)
