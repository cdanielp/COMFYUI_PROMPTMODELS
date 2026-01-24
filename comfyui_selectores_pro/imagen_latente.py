"""
Imagen latente Pro
==================
Genera un latent vacío usando presets de ratio y tamaño.
"""

import torch
from typing import Dict, Any, Tuple

# Configuración
CATEGORY: str = "Selectores Pro"


class ImagenLatentePro:
    """
    Genera un latent vacío usando presets de ratio y tamaño.
    Compatible con KSampler y cualquier nodo que acepte LATENT estándar.
    """
    
    SIZES = ["256", "320", "384", "448", "512", "640", "768", "896", "1024"]
    RATIOS = ["1:1", "9:16", "16:9"]
    
    @classmethod
    def INPUT_TYPES(cls) -> Dict[str, Any]:
        return {
            "required": {
                "ratio": (cls.RATIOS, {"default": "1:1"}),
                "size": (cls.SIZES, {"default": "512"}),
                "batch_size": ("INT", {"default": 1, "min": 1, "max": 64}),
                "rounding": (["auto_round", "strict"], {"default": "auto_round"}),
            }
        }
    
    RETURN_TYPES = ("LATENT",)
    RETURN_NAMES = ("latent",)
    FUNCTION = "execute"
    CATEGORY = CATEGORY
    
    def execute(self, ratio: str, size: str, batch_size: int, rounding: str) -> Tuple[Dict[str, torch.Tensor]]:
        size_int = int(size)
        
        if ratio == "1:1":
            width = size_int
            height = size_int
        elif ratio == "9:16":
            height = size_int
            width = round(size_int * 9 / 16)
        elif ratio == "16:9":
            width = size_int
            height = round(size_int * 9 / 16)
        else:
            raise ValueError(f"❌ Ratio desconocido: {ratio}")
        
        if rounding == "auto_round":
            width = self._round_to_multiple(width, 8)
            height = self._round_to_multiple(height, 8)
        elif rounding == "strict":
            if width % 8 != 0 or height % 8 != 0:
                raise ValueError(
                    f"❌ Imagen latente Pro: resolución inválida en modo strict.\n"
                    f"   Calculado: {width}x{height}\n"
                    f"   Ambos valores deben ser múltiplos de 8.\n"
                    f"   Activa auto_round o elige otro size."
                )
        
        latent_height = height // 8
        latent_width = width // 8
        
        latent = torch.zeros(
            [batch_size, 4, latent_height, latent_width],
            dtype=torch.float32
        )
        
        return ({"samples": latent},)
    
    @staticmethod
    def _round_to_multiple(value: int, multiple: int) -> int:
        return ((value + multiple // 2) // multiple) * multiple
