"""
ComfyUI_GoogleAI - Suite Google AI v2.0.1
==========================================
RESTAURACION: nodos legacy v2.5.0 reactivados + nodos PMS_* mantenidos.

Legacy (12):  GoogleAI_TextNode, GoogleAI_TextVisionNode,
              GoogleAI_NanoBananaNode, GoogleAI_ImageNode,
              GoogleAI_VideoGenerator/Interpolation/Storyboard,
              GoogleAI_ModelArchitectureDetector, GoogleAI_TriggerWordExtractor,
              GoogleAI_WorkflowAnalyzer, GoogleAI_CompatibilityChecker,
              GoogleAI_LoRATrainingAnalyzer
PMS_* (3):    PMS_GeminiChat (alias de GoogleAI_TextNode),
              PMS_NanaBanana (alias de GoogleAI_NanoBananaNode),
              PMS_GeminiTTS (nodo nuevo independiente)

Autor: Prompt Models Studio | cdanielp
"""

import logging
from aiohttp import web

logger = logging.getLogger("ComfyUI_GoogleAI")

# ============================================================================
# IMPORTAR NODOS LEGACY (restaurados desde v2.5.0)
# ============================================================================
from .google_text_node import GoogleAI_TextNode, GoogleAI_TextVisionNode
from .google_image_node import GoogleAI_NanoBananaNode, GoogleAI_ImageNode
from .google_video_node import (
    GoogleAI_VideoGenerator,
    GoogleAI_VideoInterpolation,
    GoogleAI_VideoStoryboard,
)
from .google_diagnostic_node import (
    GoogleAI_ModelArchitectureDetector,
    GoogleAI_TriggerWordExtractor,
    GoogleAI_WorkflowAnalyzer,
    GoogleAI_CompatibilityChecker,
    GoogleAI_LoRATrainingAnalyzer,
)

# ============================================================================
# IMPORTAR NODO NUEVO TTS
# ============================================================================
from .google_tts_node import PMS_GeminiTTS

# ============================================================================
# ALIASES PMS_* (misma clase, distinto class ID para retrocompatibilidad)
# ============================================================================
PMS_GeminiChat = GoogleAI_TextNode
PMS_NanaBanana = GoogleAI_NanoBananaNode

# ============================================================================
# NODE_CLASS_MAPPINGS
# ============================================================================
NODE_CLASS_MAPPINGS = {
    # Texto
    "GoogleAI_TextNode":           GoogleAI_TextNode,
    "GoogleAI_TextVisionNode":     GoogleAI_TextVisionNode,
    # Imagen
    "GoogleAI_NanoBananaNode":     GoogleAI_NanoBananaNode,
    "GoogleAI_ImageNode":          GoogleAI_ImageNode,
    # Video
    "GoogleAI_VideoGenerator":     GoogleAI_VideoGenerator,
    "GoogleAI_VideoInterpolation": GoogleAI_VideoInterpolation,
    "GoogleAI_VideoStoryboard":    GoogleAI_VideoStoryboard,
    # Diagnostico
    "GoogleAI_ModelArchitectureDetector": GoogleAI_ModelArchitectureDetector,
    "GoogleAI_TriggerWordExtractor":      GoogleAI_TriggerWordExtractor,
    "GoogleAI_WorkflowAnalyzer":          GoogleAI_WorkflowAnalyzer,
    "GoogleAI_CompatibilityChecker":      GoogleAI_CompatibilityChecker,
    "GoogleAI_LoRATrainingAnalyzer":      GoogleAI_LoRATrainingAnalyzer,
    # PMS_* (aliases + TTS nuevo)
    "PMS_GeminiChat":              PMS_GeminiChat,
    "PMS_NanaBanana":              PMS_NanaBanana,
    "PMS_GeminiTTS":               PMS_GeminiTTS,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    # Legacy
    "GoogleAI_TextNode":           "Google AI - Text Generator",
    "GoogleAI_TextVisionNode":     "Google AI - Vision Analyzer",
    "GoogleAI_NanoBananaNode":     "Google AI - Nano Banana (NB2/Pro)",
    "GoogleAI_ImageNode":          "Google AI - Image Generator (Imagen 4)",
    "GoogleAI_VideoGenerator":     "Google AI - Video Generator (Veo 3.1)",
    "GoogleAI_VideoInterpolation": "Google AI - Video Interpolation",
    "GoogleAI_VideoStoryboard":    "Google AI - Video Storyboard",
    "GoogleAI_ModelArchitectureDetector": "Google AI - Architecture Detector",
    "GoogleAI_TriggerWordExtractor":      "Google AI - Trigger Word Extractor",
    "GoogleAI_WorkflowAnalyzer":          "Google AI - Workflow Analyzer",
    "GoogleAI_CompatibilityChecker":      "Google AI - Compatibility Checker",
    "GoogleAI_LoRATrainingAnalyzer":      "Google AI - Training Analyzer",
    # PMS_*
    "PMS_GeminiChat":              "Gemini Chat (PMS)",
    "PMS_NanaBanana":              "Nano Banana - Imagen IA (PMS)",
    "PMS_GeminiTTS":               "Gemini Text to Speech (PMS)",
}

WEB_DIRECTORY = "./web"

# ============================================================================
# HEALTH ENDPOINT
# ============================================================================
try:
    from server import PromptServer

    @PromptServer.instance.routes.get("/google-ai/health")
    async def health_check(request):
        return web.json_response({
            "status": "ok",
            "version": "2.0.1",
            "nodes": len(NODE_CLASS_MAPPINGS),
            "legacy_count": 12,
            "pms_count": 3,
        })

    logger.info("[GoogleAI] Ruta registrada: /google-ai/health")

except (ImportError, AttributeError) as e:
    logger.warning(f"[GoogleAI] No se registro ruta del servidor: {e}")

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS", "WEB_DIRECTORY"]

print(
    f"\n{'='*65}\n"
    f"  ComfyUI_GoogleAI v2.0.1 -- {len(NODE_CLASS_MAPPINGS)} nodos\n"
    f"  Legacy (12): Texto, Vision, NanoBanana, Imagen 4, Veo 3.1, Diag\n"
    f"  PMS_* (3):   GeminiChat, NanaBanana, GeminiTTS\n"
    f"  Workflows v1.x y v2.0 ambos funcionan.\n"
    f"{'='*65}\n"
)
