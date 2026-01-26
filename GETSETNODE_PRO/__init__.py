"""
GETSETNODE_PRO - Sistema de memoria de contexto para ComfyUI
"""

__version__ = "1.0.0"
__author__ = "TuNombre"

from .setget_nodes import (
    PRO_SetNode, 
    PRO_GetNode, 
    PRO_SetNodeNamed,
    PRO_ListCacheNode, 
    PRO_ClearCacheNode,
    ANY_TYPE
)
from .unet_loader_gguf import PRO_UnetLoaderGGUF, PRO_UnetLoaderGGUFAdvanced
from .qwen_cache import QwenCache, get_cache, COMFY_TYPES

# ============================================================================
# REGISTRO DE NODOS (Con prefijo PRO_ para evitar conflictos)
# ============================================================================
NODE_CLASS_MAPPINGS = {
    "PRO_SetNode": PRO_SetNode,
    "PRO_GetNode": PRO_GetNode,
    "PRO_UnetLoaderGGUF": PRO_UnetLoaderGGUF,
    "PRO_SetNodeNamed": PRO_SetNodeNamed,
    "PRO_UnetLoaderGGUFAdvanced": PRO_UnetLoaderGGUFAdvanced,
    "PRO_ListCacheNode": PRO_ListCacheNode,
    "PRO_ClearCacheNode": PRO_ClearCacheNode,
}

# Nombres que verá el usuario en el menú
NODE_DISPLAY_NAME_MAPPINGS = {
    "PRO_SetNode": "📦 PRO Set Node",
    "PRO_GetNode": "📤 PRO Get Node",
    "PRO_UnetLoaderGGUF": "🧠 PRO Unet Loader GGUF",
    "PRO_SetNodeNamed": "📦 PRO Set Node (Named)",
    "PRO_UnetLoaderGGUFAdvanced": "🧠 PRO Unet Loader GGUF+",
    "PRO_ListCacheNode": "📋 PRO List Cache",
    "PRO_ClearCacheNode": "🗑️ PRO Clear Cache",
}

WEB_DIRECTORY = None

__all__ = [
    "PRO_SetNode", "PRO_GetNode", "PRO_SetNodeNamed",
    "PRO_UnetLoaderGGUF", "PRO_UnetLoaderGGUFAdvanced",
    "PRO_ListCacheNode", "PRO_ClearCacheNode",
    "QwenCache", "get_cache", "ANY_TYPE", "COMFY_TYPES",
    "NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS",
]

print(f"✓ GETSETNODE_PRO v{__version__} loaded")