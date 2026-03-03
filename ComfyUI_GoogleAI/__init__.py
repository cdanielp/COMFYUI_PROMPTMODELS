"""
ComfyUI_GoogleAI - Suite Integral de Google AI (V2.5.0)
=======================================================
Nano Banana 2/Pro/Original | Imagen 4 | Veo 3.1 + Audio | Diagnostico

Novedades V2.5.0:
- NUEVO: GoogleAI_NanoBananaNode (nodo estrella - NB2/Pro/Original)
- NUEVO: Nano Banana 2 (gemini-3.1-flash-image-preview) - Feb 26, 2026
- 14 aspect ratios oficiales + imageSize separado (512px/0.5K/1K/2K/4K)
- ThinkingConfig inteligente: thinkingLevel (3+) / thinkingBudget (2.5)
- Model strings corregidos (gemini-3-flash-preview)
- TextNode: 5 pines de imagen multimodal
- ELIMINADO: GoogleAI_ImageBatchNode
- ELIMINADO: gemini-3-pro-preview (deprecated 9 Mar 2026)
- ImageNode simplificado: solo Imagen 4/3
- responseModalities: ["TEXT", "IMAGE"] para robustez
- call_with_backoff: HTTP 500 ahora retryable
- MIME detection mejorada (JPEG/WEBP/PNG)

Autor: Prompt Models Studio | cdanielp
Repositorio: https://github.com/cdanielp/COMFYUI_PROMPTMODELS
"""

import logging
from aiohttp import web

logger = logging.getLogger("ComfyUI_GoogleAI")

# ============================================================================
# IMPORTAR NODOS
# ============================================================================
from .google_text_node import GoogleAI_TextNode, GoogleAI_TextVisionNode
from .google_image_node import GoogleAI_NanoBananaNode, GoogleAI_ImageNode
from .google_video_node import GoogleAI_VideoGenerator, GoogleAI_VideoInterpolation, GoogleAI_VideoStoryboard
from .google_diagnostic_node import (
    GoogleAI_ModelArchitectureDetector, GoogleAI_TriggerWordExtractor,
    GoogleAI_WorkflowAnalyzer, GoogleAI_CompatibilityChecker, GoogleAI_LoRATrainingAnalyzer,
)

# ============================================================================
# NODE_CLASS_MAPPINGS
# ============================================================================
NODE_CLASS_MAPPINGS = {
    # Suite 0: Texto
    "GoogleAI_TextNode":           GoogleAI_TextNode,
    "GoogleAI_TextVisionNode":     GoogleAI_TextVisionNode,
    # Suite 1: Imagen
    "GoogleAI_NanoBananaNode":     GoogleAI_NanoBananaNode,
    "GoogleAI_ImageNode":          GoogleAI_ImageNode,
    # Suite 2: Video
    "GoogleAI_VideoGenerator":     GoogleAI_VideoGenerator,
    "GoogleAI_VideoInterpolation": GoogleAI_VideoInterpolation,
    "GoogleAI_VideoStoryboard":    GoogleAI_VideoStoryboard,
    # Suite 3: Diagnostico
    "GoogleAI_ModelArchitectureDetector": GoogleAI_ModelArchitectureDetector,
    "GoogleAI_TriggerWordExtractor":      GoogleAI_TriggerWordExtractor,
    "GoogleAI_WorkflowAnalyzer":          GoogleAI_WorkflowAnalyzer,
    "GoogleAI_CompatibilityChecker":      GoogleAI_CompatibilityChecker,
    "GoogleAI_LoRATrainingAnalyzer":      GoogleAI_LoRATrainingAnalyzer,
}

NODE_DISPLAY_NAME_MAPPINGS = {
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
}

# ============================================================================
# WEB_DIRECTORY
# ============================================================================
WEB_DIRECTORY = "./web"

# ============================================================================
# SERVIDOR - Health endpoint
# ============================================================================
try:
    from server import PromptServer

    @PromptServer.instance.routes.get("/google-ai/health")
    async def health_check(request):
        return web.json_response({
            "status": "ok",
            "version": "2.5.0",
            "nodes": len(NODE_CLASS_MAPPINGS),
            "suites": ["text", "image", "video", "diagnostic"],
            "image_models": [
                "nano-banana-2", "nano-banana-pro", "nano-banana",
                "imagen-4", "imagen-3",
            ],
        })

    logger.info("[GoogleAI] Ruta registrada: /google-ai/health")

except (ImportError, AttributeError) as e:
    logger.warning(f"[GoogleAI] No se registro ruta del servidor: {e}")

# ============================================================================
# EXPORTS
# ============================================================================
__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS", "WEB_DIRECTORY"]

_n = len(NODE_CLASS_MAPPINGS)
print(
    f"\n{'='*65}\n"
    f"  ComfyUI_GoogleAI V2.5.0 -- {_n} nodos\n"
    f"  Texto  | Vision (5 imagenes)\n"
    f"  Imagen: Nano Banana 2/Pro + Imagen 4 (14 aspect ratios)\n"
    f"  Veo 3.1 + Audio ffmpeg | Diagnostico (5 nodos)\n"
    f"  Video: transcodificacion H.264 + diagnostico automatico\n"
    f"  Error Explainer -> ComfyUI_UniversalErrorExplainer\n"
    f"{'='*65}\n"
)
