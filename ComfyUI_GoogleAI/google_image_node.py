# google_image_node.py
import torch
import numpy as np
from PIL import Image
from io import BytesIO
from .google_core import GoogleAICore

# Modelos de imagen - Actualizado Diciembre 2025
IMAGE_MODELS = [
    # Nano Banana Pro (Gemini 3 Pro Image) - Hasta 4K, 14 imgs referencia
    "gemini-3-pro-image-preview",
    
    # Nano Banana (Gemini 2.5 Flash Image) - Rápido, 1024px
    "gemini-2.5-flash-image",
    
    # Imagen 3 Series
    "imagen-3.0-generate-002",
    "imagen-3.0-generate-001",
]

# Mapeo de resoluciones actualizado para Nano Banana Pro
RESOLUTION_MAP = {
    "1K": 1024,
    "2K": 2048,
    "4K": 4096,  # Solo Nano Banana Pro
}

ASPECT_RATIOS = ["1:1", "3:4", "4:3", "9:16", "16:9", "3:2", "2:3", "21:9"]


def get_dimensions(resolution: str, aspect_ratio: str) -> tuple:
    """
    Calcula dimensiones basadas en resolución y aspect ratio
    Nano Banana Pro soporta hasta 4K
    """
    base = RESOLUTION_MAP.get(resolution, 1024)
    
    # Calcular dimensiones según aspect ratio
    aspect_map = {
        "1:1": (1, 1),
        "3:4": (3, 4),
        "4:3": (4, 3),
        "9:16": (9, 16),
        "16:9": (16, 9),
        "3:2": (3, 2),
        "2:3": (2, 3),
        "21:9": (21, 9),
    }
    
    w_ratio, h_ratio = aspect_map.get(aspect_ratio, (1, 1))
    
    # Calcular dimensiones manteniendo el área aproximada
    if w_ratio >= h_ratio:
        width = base
        height = int(base * h_ratio / w_ratio)
    else:
        height = base
        width = int(base * w_ratio / h_ratio)
    
    # Asegurar múltiplos de 64 para mejor compatibilidad
    width = (width // 64) * 64
    height = (height // 64) * 64
    
    return (width, height)


class GoogleAI_ImageNode:
    """
    Nodo multimodal: texto + imágenes → imagen generada (Gemini API)
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "api_key": ("STRING", {"default": "", "multiline": False}),
                "model": (IMAGE_MODELS, {"default": "gemini-3-pro-image-preview"}),
                "prompt": ("STRING", {"default": "", "multiline": True}),
                "system_prompt": ("STRING", {
                    "default": "You are an advanced image generator. Create high-quality, visually coherent compositions.",
                    "multiline": True
                }),
                "resolution": (["1K", "2K", "4K"], {"default": "1K"}),
                "aspect_ratio": (ASPECT_RATIOS, {"default": "1:1"}),
            },
            "optional": {
                "custom_model": ("STRING", {"default": "", "multiline": False}),
                "image_1": ("IMAGE",),
                "image_2": ("IMAGE",),
                "image_3": ("IMAGE",),
                "image_4": ("IMAGE",),
                "image_5": ("IMAGE",),
            },
        }

    RETURN_TYPES = ("IMAGE", "STRING",)
    RETURN_NAMES = ("image", "status",)
    FUNCTION = "generate_image"
    CATEGORY = "GoogleAI"

    def generate_image(self, api_key, model, prompt, system_prompt,
                       resolution, aspect_ratio,
                       custom_model="",
                       image_1=None, image_2=None, image_3=None, 
                       image_4=None, image_5=None):

        # Usar modelo personalizado si se proporciona
        active_model = custom_model.strip() if custom_model.strip() else model
        
        if not api_key.strip():
            return self._error_image("Error: API key is required")
        
        if not prompt.strip():
            return self._error_image("Error: Prompt is required")

        # Calcular dimensiones
        width, height = get_dimensions(resolution, aspect_ratio)

        # Convertir imágenes de entrada a base64
        image_data = []
        for img in [image_1, image_2, image_3, image_4, image_5]:
            if img is not None:
                try:
                    b64 = GoogleAICore.tensor_to_base64(img)
                    image_data.append(b64)
                except Exception as e:
                    print(f"[GoogleAI] Error converting image: {e}")

        # Llamar a la API
        client = GoogleAICore(api_key.strip(), active_model)
        result = client.generate_image(
            prompt=prompt,
            system_prompt=system_prompt,
            images=image_data if image_data else None,
            width=width,
            height=height
        )

        # Procesar respuesta
        try:
            candidates = result.get("candidates", [])
            if not candidates:
                error = result.get("error", {}).get("message", "No candidates returned")
                return self._error_image(f"API Error: {error}")
            
            parts = candidates[0].get("content", {}).get("parts", [])
            
            # Buscar parte con imagen
            for part in parts:
                if "inlineData" in part:
                    b64_data = part["inlineData"]["data"]
                    tensor = GoogleAICore.base64_to_tensor(b64_data)
                    return (tensor, "Success")
            
            # Si no hay imagen, puede haber solo texto
            for part in parts:
                if "text" in part:
                    return self._error_image(f"Model returned text only: {part['text'][:200]}")
            
            return self._error_image("No image in response")
            
        except Exception as e:
            return self._error_image(f"Error: {str(e)}")

    def _error_image(self, message: str):
        """
        Genera imagen de error roja con mensaje
        """
        print(f"[GoogleAI] {message}")
        # Crear tensor de imagen roja [1, 512, 512, 3]
        error_tensor = torch.zeros(1, 512, 512, 3)
        error_tensor[:, :, :, 0] = 0.8  # Rojo
        return (error_tensor, message)


class GoogleAI_ImageNode_Simple:
    """
    Versión simplificada del nodo de imagen (sin imágenes de referencia)
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "api_key": ("STRING", {"default": "", "multiline": False}),
                "model": (IMAGE_MODELS, {"default": "gemini-2.5-flash-image"}),
                "prompt": ("STRING", {"default": "", "multiline": True}),
            },
            "optional": {
                "aspect_ratio": (ASPECT_RATIOS, {"default": "1:1"}),
            },
        }

    RETURN_TYPES = ("IMAGE", "STRING",)
    RETURN_NAMES = ("image", "status",)
    FUNCTION = "generate_image"
    CATEGORY = "GoogleAI"

    def generate_image(self, api_key, model, prompt, aspect_ratio="1:1"):
        if not api_key.strip():
            return self._error_image("Error: API key is required")
        
        if not prompt.strip():
            return self._error_image("Error: Prompt is required")

        width, height = get_dimensions("1K", aspect_ratio)

        client = GoogleAICore(api_key.strip(), model)
        result = client.generate_image(prompt=prompt, width=width, height=height)

        try:
            candidates = result.get("candidates", [])
            if not candidates:
                error = result.get("error", {}).get("message", "No candidates returned")
                return self._error_image(f"API Error: {error}")
            
            parts = candidates[0].get("content", {}).get("parts", [])
            
            for part in parts:
                if "inlineData" in part:
                    b64_data = part["inlineData"]["data"]
                    tensor = GoogleAICore.base64_to_tensor(b64_data)
                    return (tensor, "Success")
            
            for part in parts:
                if "text" in part:
                    return self._error_image(f"Text only: {part['text'][:200]}")
            
            return self._error_image("No image in response")
            
        except Exception as e:
            return self._error_image(f"Error: {str(e)}")

    def _error_image(self, message: str):
        print(f"[GoogleAI] {message}")
        error_tensor = torch.zeros(1, 512, 512, 3)
        error_tensor[:, :, :, 0] = 0.8
        return (error_tensor, message)


NODE_CLASS_MAPPINGS = {
    "GoogleAI_ImageNode": GoogleAI_ImageNode,
    "GoogleAI_ImageNode_Simple": GoogleAI_ImageNode_Simple,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "GoogleAI_ImageNode": "🎨 Google AI Image Generator",
    "GoogleAI_ImageNode_Simple": "🎨 Google AI Image (Simple)",
}
