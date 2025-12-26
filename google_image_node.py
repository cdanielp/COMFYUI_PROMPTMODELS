# google_image_node.py
import torch
import numpy as np
from PIL import Image
from io import BytesIO
from .google_core import GoogleAICore

# Modelos con capacidad de generación de imagen
IMAGE_MODELS = [
    "gemini-2.0-flash-preview-image-generation",
    "imagen-3.0-generate-002",
    "imagen-3.0-generate-001",
]

# Mapeo de resoluciones
RESOLUTION_MAP = {
    "1024x1024": (1024, 1024),
    "1536x1536": (1536, 1536),
    "768x1024": (768, 1024),
    "1024x768": (1024, 768),
    "768x1280": (768, 1280),
    "1280x768": (1280, 768),
}

ASPECT_RATIOS = ["1:1", "3:4", "4:3", "9:16", "16:9"]


def get_dimensions(resolution: str, aspect_ratio: str) -> tuple:
    """
    Calcula dimensiones basadas en resolución y aspect ratio
    """
    # Resoluciones base por aspect ratio
    aspect_map = {
        "1:1": {"1K": (1024, 1024), "2K": (2048, 2048)},
        "3:4": {"1K": (768, 1024), "2K": (1536, 2048)},
        "4:3": {"1K": (1024, 768), "2K": (2048, 1536)},
        "9:16": {"1K": (576, 1024), "2K": (1152, 2048)},
        "16:9": {"1K": (1024, 576), "2K": (2048, 1152)},
    }
    
    return aspect_map.get(aspect_ratio, {}).get(resolution, (1024, 1024))


class GoogleAI_ImageNode:
    """
    Nodo multimodal: texto + imágenes → imagen generada (Gemini API)
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "api_key": ("STRING", {"default": "", "multiline": False}),
                "model": (IMAGE_MODELS, {"default": "gemini-2.0-flash-preview-image-generation"}),
                "prompt": ("STRING", {"default": "", "multiline": True}),
            },
            "optional": {
                "system_prompt": ("STRING", {"default": "", "multiline": True, "forceInput": True}),
                "resolution": (["1K", "2K"], {"default": "1K"}),
                "aspect_ratio": (ASPECT_RATIOS, {"default": "1:1"}),
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

    def generate_image(self, api_key, model, prompt, 
                       system_prompt="", resolution="1K", aspect_ratio="1:1",
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
                "model": (IMAGE_MODELS, {"default": "gemini-2.0-flash-preview-image-generation"}),
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
