"""
ComfyUI Selectores Pro
======================
Paquete de nodos para selección múltiple, generación de latents y construcción de prompts.

Nodos incluidos:
- Selector de imágenes
- Selector de Prompts
- Imagen latente Pro
- Prompt Pro

Versión: 1.2.0
"""

from .selector_imagenes import SelectorDeImagenes
from .selector_prompts import SelectorDePrompts
from .imagen_latente import ImagenLatentePro
from .prompt_pro import PromptPro

# =============================================================================
# REGISTRO DE NODOS
# =============================================================================

NODE_CLASS_MAPPINGS = {
    "SelectorDeImagenes": SelectorDeImagenes,
    "SelectorDePrompts": SelectorDePrompts,
    "ImagenLatentePro": ImagenLatentePro,
    "PromptPro": PromptPro,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "SelectorDeImagenes": "Selector de imágenes",
    "SelectorDePrompts": "Selector de Prompts",
    "ImagenLatentePro": "Imagen latente Pro",
    "PromptPro": "Prompt Pro",
}

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]

print("✅ ComfyUI Selectores Pro cargado (4 nodos)")
