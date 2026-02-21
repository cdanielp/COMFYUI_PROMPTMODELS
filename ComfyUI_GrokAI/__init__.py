"""
ComfyUI_GrokAI - Suite de xAI (Grok) para ComfyUI (V1.0)
===========================================================
Texto + Razonamiento | Visión Multimodal | JSON Estructurado
Generación de Imagen | Edición de Imagen | Diagnóstico

CERO SDKs — Solo requests HTTP puras.

Autor: Prompt Models Studio | cdanielp
"""

from .grok_text_node import (
    Grok_Text_Advanced,
    Grok_Vision_Analyzer,
    Grok_JSON_Formatter,
)
from .grok_image_node import (
    Grok_Image_Generator,
    Grok_Image_Editor,
)
from .grok_diagnostic_node import (
    Grok_Workflow_Debugger,
    Grok_Metadata_Reader,
)

# ============================================================================
# NODE_CLASS_MAPPINGS
# ============================================================================
NODE_CLASS_MAPPINGS = {
    # Suite 1: Texto / Visión / JSON
    "Grok_Text_Advanced": Grok_Text_Advanced,
    "Grok_Vision_Analyzer": Grok_Vision_Analyzer,
    "Grok_JSON_Formatter": Grok_JSON_Formatter,
    # Suite 2: Imagen
    "Grok_Image_Generator": Grok_Image_Generator,
    "Grok_Image_Editor": Grok_Image_Editor,
    # Suite 3: Diagnóstico
    "Grok_Workflow_Debugger": Grok_Workflow_Debugger,
    "Grok_Metadata_Reader": Grok_Metadata_Reader,
}

# ============================================================================
# NODE_DISPLAY_NAME_MAPPINGS (con emojis)
# ============================================================================
NODE_DISPLAY_NAME_MAPPINGS = {
    "Grok_Text_Advanced": "🧠 Grok - Text Advanced",
    "Grok_Vision_Analyzer": "👁️ Grok - Vision Analyzer",
    "Grok_JSON_Formatter": "📋 Grok - JSON Formatter",
    "Grok_Image_Generator": "🎨 Grok - Image Generator",
    "Grok_Image_Editor": "✏️ Grok - Image Editor",
    "Grok_Workflow_Debugger": "🔧 Grok - Workflow Debugger",
    "Grok_Metadata_Reader": "🔍 Grok - Metadata Reader",
}

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]

print(
    f"\n{'='*55}\n"
    f"  ✅ ComfyUI_GrokAI V1.0 — {len(NODE_CLASS_MAPPINGS)} nodos\n"
    f"  🧠 Text | 👁️ Vision | 📋 JSON | 🎨 Image\n"
    f"  ✏️ Editor | 🔧 Debugger | 🔍 Metadata\n"
    f"{'='*55}\n"
)
