# ==============================================================================
# __init__.py interno de ComfyUI_GrokAI - V2.0.0
# ==============================================================================
# Recolecta clases de todos los modulos y exporta NODE_CLASS_MAPPINGS.
# ==============================================================================

from .grok_text_node import GrokTextNode, Grok_Multimodal_Vision
from .grok_image_node import GrokImageNode, Grok_Image_Master
from .grok_video_node import Grok_Video_Forge, Grok_Video_Editor, Grok_Video_Extension
from .grok_prompt_node import Grok_Prompt_Architect
from .grok_diagnostic_node import Grok_Workflow_Debugger, Grok_Metadata_Reader

NODE_CLASS_MAPPINGS = {
    # V1 (Legado)
    "GrokTextNode": GrokTextNode,
    "GrokImageNode": GrokImageNode,
    # V2
    "Grok_Multimodal_Vision": Grok_Multimodal_Vision,
    "Grok_Image_Master": Grok_Image_Master,
    "Grok_Video_Forge": Grok_Video_Forge,
    "Grok_Prompt_Architect": Grok_Prompt_Architect,
    # Video Avanzado
    "Grok_Video_Editor": Grok_Video_Editor,
    "Grok_Video_Extension": Grok_Video_Extension,
    # Diagnostico
    "Grok_Workflow_Debugger": Grok_Workflow_Debugger,
    "Grok_Metadata_Reader": Grok_Metadata_Reader,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "GrokTextNode": "Grok Text [v1 Legacy]",
    "GrokImageNode": "Grok Image [v1 Legacy]",
    "Grok_Multimodal_Vision": "Grok Multimodal Vision",
    "Grok_Image_Master": "Grok Image Master",
    "Grok_Video_Forge": "Grok Video Forge",
    "Grok_Prompt_Architect": "Grok Prompt Architect",
    "Grok_Video_Editor": "Grok Video Editor",
    "Grok_Video_Extension": "Grok Video Extension",
    "Grok_Workflow_Debugger": "Grok Workflow Debugger",
    "Grok_Metadata_Reader": "Grok Metadata Reader",
}

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]
