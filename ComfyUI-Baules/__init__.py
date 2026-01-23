"""
ComfyUI Custom Nodes Pack: Baúles (Chests)
Sistema modular de gestión de assets y prompts para workflows.

Estructura de archivos requerida:
- baules_image_chests_local.py
- baules_image_chests_cloud.py
- baules_prompt_chests.py
- baules_prompt_constructor.py
- baules_storage_manager.py
"""

# 1. Importar nodos de imágenes locales (Dropdown + Imagen)
from .baules_image_chests_local import (
    ImageChestLocal,
    OpenPoseChestLocal,
    DepthChestLocal,
    LineartChestLocal,
)

# 2. Importar nodos de referencias cloud (String)
from .baules_image_chests_cloud import (
    ImageChestCloudRef,
    OpenPoseChestCloudRef,
    DepthChestCloudRef,
    LineartChestCloudRef,
    Chest3DCloudRef,
)

# 3. Importar nodos de prompts (Presets)
from .baules_prompt_chests import (
    PromptChestBase,
    StyleChest,
    PoseChest,
    CameraChest,
    LightingChest,
    EnvironmentChest,
    QualityChest,
    NegativeChest,
)

# 4. Importar utilidades (Constructor + Negativo)
from .baules_prompt_constructor import (
    PromptConstructor,
    NegativeQuick,
)

# ============================================================================
# Registro de Nodos en ComfyUI
# ============================================================================

NODE_CLASS_MAPPINGS = {
    # --- Baúles Locales ---
    "ImageChestLocal": ImageChestLocal,
    "OpenPoseChestLocal": OpenPoseChestLocal,
    "DepthChestLocal": DepthChestLocal,
    "LineartChestLocal": LineartChestLocal,
    
    # --- Baúles Cloud ---
    "ImageChestCloudRef": ImageChestCloudRef,
    "OpenPoseChestCloudRef": OpenPoseChestCloudRef,
    "DepthChestCloudRef": DepthChestCloudRef,
    "LineartChestCloudRef": LineartChestCloudRef,
    "Chest3DCloudRef": Chest3DCloudRef,
    
    # --- Prompts ---
    "PromptChestBase": PromptChestBase,
    "StyleChest": StyleChest,
    "PoseChest": PoseChest,
    "CameraChest": CameraChest,
    "LightingChest": LightingChest,
    "EnvironmentChest": EnvironmentChest,
    "QualityChest": QualityChest,
    "NegativeChest": NegativeChest,
    
    # --- Herramientas ---
    "PromptConstructor": PromptConstructor,
    "NegativeQuick": NegativeQuick,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    # --- Locales ---
    "ImageChestLocal": "🧰 Baúl Imágenes (Local)",
    "OpenPoseChestLocal": "🧍 Baúl OpenPose (Local)",
    "DepthChestLocal": "🗺️ Baúl Depth (Local)",
    "LineartChestLocal": "✍️ Baúl Lineart (Local)",
    
    # --- Cloud ---
    "ImageChestCloudRef": "☁️🧰 Baúl Imágenes (Cloud)",
    "OpenPoseChestCloudRef": "☁️🧍 Baúl OpenPose (Cloud)",
    "DepthChestCloudRef": "☁️🗺️ Baúl Depth (Cloud)",
    "LineartChestCloudRef": "☁️✍️ Baúl Lineart (Cloud)",
    "Chest3DCloudRef": "☁️🧊 Baúl 3D / Referencias (Cloud)",
    
    # --- Prompts ---
    "PromptChestBase": "🧾 Baúl de Prompts (Base)",
    "StyleChest": "🎨 Baúl Estilos",
    "PoseChest": "🧍 Baúl Poses",
    "CameraChest": "📷 Baúl Cámara / Lente",
    "LightingChest": "💡 Baúl Iluminación",
    "EnvironmentChest": "🏞️ Baúl Fondo / Entorno",
    "QualityChest": "✨ Baúl Calidad",
    "NegativeChest": "⛔ Baúl Negativos",
    
    # --- Herramientas ---
    "PromptConstructor": "🧱 Prompt Constructor",
    "NegativeQuick": "⛔ Negativo Rápido",
}

# Exportar símbolos
__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]

print(f"✅ ComfyUI-Baules cargado: {len(NODE_CLASS_MAPPINGS)} nodos registrados.")