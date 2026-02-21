# ==============================================================================
# __init__.py interno de ComfyUI_GrokAI
# ==============================================================================
# Este archivo solo se encarga de recolectar las clases de los diferentes .py
# y exportar los diccionarios NODE_CLASS_MAPPINGS.
# ==============================================================================

from .grok_text_node import GrokTextNode, Grok_Multimodal_Vision
from .grok_image_node import GrokImageNode, Grok_Image_Master
from .grok_video_node import Grok_Video_Forge
from .grok_prompt_node import Grok_Prompt_Architect

NODE_CLASS_MAPPINGS = {
    # V1 (Legado)
    "GrokTextNode": GrokTextNode,
    "GrokImageNode": GrokImageNode,
    # V2 (Nuevos)
    "Grok_Multimodal_Vision": Grok_Multimodal_Vision,
    "Grok_Image_Master": Grok_Image_Master,
    "Grok_Video_Forge": Grok_Video_Forge,
    "Grok_Prompt_Architect": Grok_Prompt_Architect
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "GrokTextNode": "Grok Text [v1 Legacy]",
    "GrokImageNode": "Grok Image [v1 Legacy]",
    "Grok_Multimodal_Vision": "🔭 Grok Multimodal Vision",
    "Grok_Image_Master": "🎨 Grok Image Master",
    "Grok_Video_Forge": "🎬 Grok Video Forge",
    "Grok_Prompt_Architect": "✍️ Grok Prompt Architect"
}

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]
