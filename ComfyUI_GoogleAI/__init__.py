"""
ComfyUI_GoogleAI - Suite Google AI v2.0.0
==========================================
3 nodos activos: PMS_GeminiChat, PMS_NanaBanana, PMS_GeminiTTS.

Eliminados en v2.0.0:
- GoogleAI_VideoGenerator / Interpolation / Storyboard (Veo)
- GoogleAI_ImageNode (Imagen 4/3)
- GoogleAI_TextVisionNode (fusionado en PMS_GeminiChat)
- Suite de diagnostico (5 nodos)

Autor: Prompt Models Studio | cdanielp
"""

import logging

logger = logging.getLogger("ComfyUI_PromptModels")

from .google_text_node import PMS_GeminiChat
from .google_image_node import PMS_NanaBanana
from .google_tts_node   import PMS_GeminiTTS

NODE_CLASS_MAPPINGS = {
    "PMS_GeminiChat": PMS_GeminiChat,
    "PMS_NanaBanana": PMS_NanaBanana,
    "PMS_GeminiTTS":  PMS_GeminiTTS,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "PMS_GeminiChat": "Gemini Chat (PMS)",
    "PMS_NanaBanana": "Nano Banana - Imagen IA (PMS)",
    "PMS_GeminiTTS":  "Gemini Text to Speech (PMS)",
}

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]
