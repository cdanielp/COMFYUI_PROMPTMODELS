"""
ComfyUI_GrokAI - Suite Grok v2.0.0
=====================================
5 nodos activos: GrokTextNode, PMS_GrokImageGen, PMS_GrokVideoGen,
                 PMS_GrokTTS, PMS_GrokSTT.

Eliminados en v2.0.0:
- Grok_Multimodal_Vision
- Grok_Image_Master / GrokImageNode (fusionados en PMS_GrokImageGen)
- Grok_Video_Forge / Grok_Video_Editor / Grok_Video_Extension (reemplazados por PMS_GrokVideoGen)
- Grok_Workflow_Debugger / Grok_Metadata_Reader (diagnostico)
- Grok_Prompt_Architect

Autor: Prompt Models Studio | cdanielp
"""

import logging

logger = logging.getLogger("ComfyUI_PromptModels")

from .grok_text_node  import GrokTextNode
from .grok_image_node import PMS_GrokImageGen
from .grok_video_gen  import PMS_GrokVideoGen
from .grok_tts_node   import PMS_GrokTTS
from .grok_stt_node   import PMS_GrokSTT

NODE_CLASS_MAPPINGS = {
    "GrokTextNode":     GrokTextNode,
    "PMS_GrokImageGen": PMS_GrokImageGen,
    "PMS_GrokVideoGen": PMS_GrokVideoGen,
    "PMS_GrokTTS":      PMS_GrokTTS,
    "PMS_GrokSTT":      PMS_GrokSTT,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "GrokTextNode":     "Grok Chat (PMS)",
    "PMS_GrokImageGen": "Grok Image Gen (PMS)",
    "PMS_GrokVideoGen": "Grok Video Gen (PMS)",
    "PMS_GrokTTS":      "Grok Text to Speech (PMS)",
    "PMS_GrokSTT":      "Grok Speech to Text (PMS)",
}

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]
