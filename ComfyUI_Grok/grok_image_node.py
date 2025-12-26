# grok_image_node.py
"""
Nodo de generación de imagen usando xAI Grok API
"""
import torch
import numpy as np
from PIL import Image
from io import BytesIO
from .grok_core import call_grok_image, image_bytes_to_tensor

# Modelos de imagen disponibles - Diciembre 2025
IMAGE_MODELS = [
    "grok-2-image",       # Principal
    "grok-2-image-lite",  # Rápido/económico
]

# Resoluciones soportadas
RESOLUTIONS = [
    "512x512",
    "1024x1024",
    "1024x1536",   # Portrait
    "1536x1024",   # Landscape
    "2048x2048",
]

# Aspect ratios
ASPECT_RATIOS = ["1:1", "3:4", "4:3", "9:16", "16:9", "3:2", "2:3"]

# Estilos predefinidos
STYLES = [
    "None",
    "Realistic",
    "Artistic",
    "Cinematic",
    "Cartoon",
    "Concept Art",
    "Anime",
    "Oil Painting",
    "Watercolor",
    "Digital Art",
    "Photography",
    "3D Render",
]


def get_size_from_aspect(aspect_ratio: str, base_res: str) -> str:
    """
    Calcula el tamaño basado en aspect ratio y resolución base
    """
    base = int(base_res.split("x")[0])
    
    aspect_map = {
        "1:1": (1, 1),
        "3:4": (3, 4),
        "4:3": (4, 3),
        "9:16": (9, 16),
        "16:9": (16, 9),
        "3:2": (3, 2),
        "2:3": (2, 3),
    }
    
    w_ratio, h_ratio = aspect_map.get(aspect_ratio, (1, 1))
    
    if w_ratio >= h_ratio:
        width = base
        height = int(base * h_ratio / w_ratio)
    else:
        height = base
        width = int(base * w_ratio / h_ratio)
    
    # Asegurar múltiplos de 64
    width = (width // 64) * 64
    height = (height // 64) * 64
    
    return f"{width}x{height}"


class GrokImageNode:
    """
    Nodo completo de generación de imagen con Grok
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "api_key": ("STRING", {"default": "", "multiline": False}),
                "model": (IMAGE_MODELS, {"default": "grok-2-image"}),
                "prompt": ("STRING", {"default": "", "multiline": True}),
                "system_prompt": ("STRING", {
                    "default": "Generate a high-quality, detailed image.",
                    "multiline": True
                }),
                "resolution": (RESOLUTIONS, {"default": "1024x1024"}),
                "aspect_ratio": (ASPECT_RATIOS, {"default": "1:1"}),
            },
            "optional": {
                "style": (STYLES, {"default": "None"}),
                "n_images": ("INT", {
                    "default": 1,
                    "min": 1,
                    "max": 4,
                    "step": 1
                }),
                "custom_model": ("STRING", {"default": "", "multiline": False}),
            }
        }
    
    RETURN_TYPES = ("IMAGE", "STRING",)
    RETURN_NAMES = ("image", "status",)
    FUNCTION = "generate"
    CATEGORY = "xAI/Grok"
    
    def generate(self, api_key, model, prompt, system_prompt,
                 resolution, aspect_ratio,
                 style="None", n_images=1, custom_model=""):
        
        # Usar modelo personalizado si se proporciona
        active_model = custom_model.strip() if custom_model.strip() else model
        
        if not api_key.strip():
            return self._error_image("❌ Error: API key is required")
        
        if not prompt.strip():
            return self._error_image("❌ Error: Prompt is required")
        
        # Construir prompt final
        final_prompt = prompt.strip()
        
        if system_prompt and system_prompt.strip():
            final_prompt = f"{system_prompt.strip()} {final_prompt}"
        
        if style and style != "None":
            final_prompt = f"{final_prompt}. Style: {style}"
        
        # Calcular tamaño
        size = get_size_from_aspect(aspect_ratio, resolution)
        
        try:
            img_bytes = call_grok_image(
                model=active_model,
                prompt=final_prompt,
                size=size,
                n=n_images,
                api_key=api_key
            )
            
            tensor = image_bytes_to_tensor(img_bytes)
            return (tensor, f"✅ Generated with {active_model} ({size})")
            
        except Exception as e:
            return self._error_image(f"❌ Error: {str(e)}")
    
    def _error_image(self, message: str):
        """
        Genera imagen de error roja
        """
        print(f"[Grok] {message}")
        error_tensor = torch.zeros(1, 512, 512, 3)
        error_tensor[:, :, :, 0] = 0.8  # Rojo
        return (error_tensor, message)


class GrokImageNodeSimple:
    """
    Versión simplificada del nodo de imagen
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "api_key": ("STRING", {"default": "", "multiline": False}),
                "model": (IMAGE_MODELS, {"default": "grok-2-image"}),
                "prompt": ("STRING", {"default": "", "multiline": True}),
            },
            "optional": {
                "aspect_ratio": (ASPECT_RATIOS, {"default": "1:1"}),
            }
        }
    
    RETURN_TYPES = ("IMAGE", "STRING",)
    RETURN_NAMES = ("image", "status",)
    FUNCTION = "generate"
    CATEGORY = "xAI/Grok"
    
    def generate(self, api_key, model, prompt, aspect_ratio="1:1"):
        if not api_key.strip():
            return self._error_image("❌ Error: API key is required")
        
        if not prompt.strip():
            return self._error_image("❌ Error: Prompt is required")
        
        size = get_size_from_aspect(aspect_ratio, "1024x1024")
        
        try:
            img_bytes = call_grok_image(
                model=model,
                prompt=prompt,
                size=size,
                api_key=api_key
            )
            
            tensor = image_bytes_to_tensor(img_bytes)
            return (tensor, f"✅ Generated ({size})")
            
        except Exception as e:
            return self._error_image(f"❌ Error: {str(e)}")
    
    def _error_image(self, message: str):
        print(f"[Grok] {message}")
        error_tensor = torch.zeros(1, 512, 512, 3)
        error_tensor[:, :, :, 0] = 0.8
        return (error_tensor, message)


NODE_CLASS_MAPPINGS = {
    "Grok_Image": GrokImageNode,
    "Grok_Image_Simple": GrokImageNodeSimple,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "Grok_Image": "🎨 Grok Image Generator",
    "Grok_Image_Simple": "🎨 Grok Image (Simple)",
}
