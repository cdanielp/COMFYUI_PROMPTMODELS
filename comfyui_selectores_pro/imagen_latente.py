"""
Imagen latente Pro
==================
Genera un latent vacío usando presets de tamaño predefinidos.
"""

import torch
from typing import Dict, Any, Tuple

# Configuración
CATEGORY: str = "Selectores Pro"

# Presets de tamaño (width, height)
SIZE_PRESETS = {
    # --- TEST ---
    "256×256 (1:1) - Test": (256, 256),
    "208×256 (4:5) - Test": (208, 256),
    "192×256 (3:4) - Test": (192, 256),
    "168×256 (2:3) - Test": (168, 256),
    "144×256 (9:16) - Test": (144, 256),
    "256×144 (16:9) - Test": (256, 144),
    "256×168 (3:2) - Test": (256, 168),
    "256×128 (2:1) - Test": (256, 128),
    "256×112 (21:9) - Test": (256, 112),

    # --- MEDIO ---
    "512×512 (1:1) - Medio": (512, 512),
    "408×512 (4:5) - Medio": (408, 512),
    "384×512 (3:4) - Medio": (384, 512),
    "344×512 (2:3) - Medio": (344, 512),
    "288×512 (9:16) - Medio": (288, 512),
    "512×288 (16:9) - Medio": (512, 288),
    "512×344 (3:2) - Medio": (512, 344),
    "512×256 (2:1) - Medio": (512, 256),
    "512×216 (21:9) - Medio": (512, 216),

    # --- GRANDE ---
    "1024×1024 (1:1) - Grande": (1024, 1024),
    "816×1024 (4:5) - Grande": (816, 1024),
    "768×1024 (3:4) - Grande": (768, 1024),
    "680×1024 (2:3) - Grande": (680, 1024),
    "576×1024 (9:16) - Grande": (576, 1024),
    "1024×576 (16:9) - Grande": (1024, 576),
    "1024×680 (3:2) - Grande": (1024, 680),
    "1024×512 (2:1) - Grande": (1024, 512),
    "1024×440 (21:9) - Grande": (1024, 440),

    # --- SOCIALES ---
    "720×1280 (9:16) - Social": (720, 1280),
    "1280×720 (16:9) - Social": (1280, 720),
}

SIZE_PRESET_LIST = list(SIZE_PRESETS.keys())


class ImagenLatentePro:
    """
    Genera un latent vacío usando presets de tamaño predefinidos.
    Compatible con KSampler y cualquier nodo que acepte LATENT estándar.
    """
    
    @classmethod
    def INPUT_TYPES(cls) -> Dict[str, Any]:
        return {
            "required": {
                "size_preset": (SIZE_PRESET_LIST, {"default": "512×512 (1:1) - Medio"}),
                "batch_size": ("INT", {"default": 1, "min": 1, "max": 64}),
                "rounding": (["auto_round", "strict"], {"default": "auto_round"}),
            }
        }
    
    RETURN_TYPES = ("LATENT",)
    RETURN_NAMES = ("latent",)
    FUNCTION = "execute"
    CATEGORY = CATEGORY
    
    def execute(self, size_preset: str, batch_size: int, rounding: str) -> Tuple[Dict[str, torch.Tensor]]:
        # Obtener dimensiones del preset
        width, height = SIZE_PRESETS[size_preset]
        
        # Aplicar rounding
        if rounding == "auto_round":
            width = self._round_to_multiple(width, 8)
            height = self._round_to_multiple(height, 8)
        elif rounding == "strict":
            if width % 8 != 0 or height % 8 != 0:
                raise ValueError(
                    f"❌ Imagen latente Pro: resolución inválida en modo strict.\n"
                    f"   Preset: {size_preset}\n"
                    f"   Resolución: {width}x{height}\n"
                    f"   Ambos valores deben ser múltiplos de 8.\n"
                    f"   Activa auto_round o elige otro preset."
                )
        
        # Crear latent vacío
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
