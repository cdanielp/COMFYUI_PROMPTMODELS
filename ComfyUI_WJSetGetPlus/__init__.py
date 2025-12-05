"""
ComfyUI_WJSetGetPlus - Sistema de memoria de contexto para ComfyUI

Nodos compatibles con rgthree-comfy:
- SetNode: Almacena variables con nombre
- GetNode: Recupera variables almacenadas  
- UnetLoaderGGUF: Carga modelos cuantizados GGUF

Compatible con workflows JSON existentes (nombres idénticos).
"""

__version__ = "1.1.0"
__author__ = "WJNode"

# Importar nodos
from .setget_nodes import (
    SetNode, 
    GetNode, 
    SetNodeNamed,
    ListCacheNode, 
    ClearCacheNode,
    ANY_TYPE
)
from .unet_loader_gguf import UnetLoaderGGUF, UnetLoaderGGUFAdvanced
from .qwen_cache import QwenCache, get_cache, COMFY_TYPES

# ============================================================================
# REGISTRO DE NODOS
# ============================================================================
# IMPORTANTE: Los nombres de clase deben coincidir con el JSON original
# para mantener compatibilidad con workflows existentes

NODE_CLASS_MAPPINGS = {
    # Nodos principales (compatibilidad con rgthree/JSON existente)
    "SetNode": SetNode,
    "GetNode": GetNode,
    "UnetLoaderGGUF": UnetLoaderGGUF,
    
    # Nodos adicionales
    "SetNodeNamed": SetNodeNamed,
    "UnetLoaderGGUFAdvanced": UnetLoaderGGUFAdvanced,
    "ListCacheNode": ListCacheNode,
    "ClearCacheNode": ClearCacheNode,
}

# Nombres para mostrar en la UI de ComfyUI
NODE_DISPLAY_NAME_MAPPINGS = {
    "SetNode": "📦 Set Node",
    "GetNode": "📤 Get Node",
    "UnetLoaderGGUF": "🧠 Unet Loader GGUF",
    "SetNodeNamed": "📦 Set Node (Named)",
    "UnetLoaderGGUFAdvanced": "🧠 Unet Loader GGUF+",
    "ListCacheNode": "📋 List Cache",
    "ClearCacheNode": "🗑️ Clear Cache",
}

# Sin archivos web adicionales
WEB_DIRECTORY = None

# ============================================================================
# MENSAJE DE CARGA
# ============================================================================
print("=" * 60)
print(f"✓ ComfyUI_WJSetGetPlus v{__version__} loaded")
print(f"  Main: SetNode, GetNode, UnetLoaderGGUF")
print(f"  Extra: SetNodeNamed, UnetLoaderGGUFAdvanced, ListCacheNode, ClearCacheNode")
print("=" * 60)

# ============================================================================
# EXPORTS
# ============================================================================
__all__ = [
    # Nodos
    "SetNode",
    "GetNode", 
    "SetNodeNamed",
    "UnetLoaderGGUF",
    "UnetLoaderGGUFAdvanced",
    "ListCacheNode",
    "ClearCacheNode",
    # Caché
    "QwenCache",
    "get_cache",
    # Tipos
    "ANY_TYPE",
    "COMFY_TYPES",
    # Mappings
    "NODE_CLASS_MAPPINGS",
    "NODE_DISPLAY_NAME_MAPPINGS",
]
