"""
ComfyUI_GoogleAI - Suite Integral de Google AI (V2.0)
======================================================
Gemini 3.1 Pro | Imagen 4 | Veo 3.1 | Diagnóstico

⚠️ RETROCOMPATIBILIDAD: Clases originales NO se renombran ni eliminan.
📦 Audio (Lyria) REMOVIDO — lyria-3 no tiene API pública (Feb 2026).
📦 El "Explicador de Errores" fue movido a ComfyUI_UniversalErrorExplainer.

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
from .google_image_node import GoogleAI_ImageNode, GoogleAI_ImageBatchNode
from .google_video_node import GoogleAI_VideoGenerator, GoogleAI_VideoInterpolation, GoogleAI_VideoStoryboard
from .google_diagnostic_node import (
    GoogleAI_ModelArchitectureDetector, GoogleAI_TriggerWordExtractor,
    GoogleAI_WorkflowAnalyzer, GoogleAI_CompatibilityChecker, GoogleAI_LoRATrainingAnalyzer,
)

# ============================================================================
# NODE_CLASS_MAPPINGS (Retrocompatible + Nuevos)
# ============================================================================
NODE_CLASS_MAPPINGS = {
    # Suite 0: Texto
    "GoogleAI_TextNode": GoogleAI_TextNode,
    "GoogleAI_TextVisionNode": GoogleAI_TextVisionNode,
    # Suite 0: Imagen
    "GoogleAI_ImageNode": GoogleAI_ImageNode,
    "GoogleAI_ImageBatchNode": GoogleAI_ImageBatchNode,
    # Suite 1: Video
    "GoogleAI_VideoGenerator": GoogleAI_VideoGenerator,
    "GoogleAI_VideoInterpolation": GoogleAI_VideoInterpolation,
    "GoogleAI_VideoStoryboard": GoogleAI_VideoStoryboard,
    # Suite 2: Diagnóstico
    "GoogleAI_ModelArchitectureDetector": GoogleAI_ModelArchitectureDetector,
    "GoogleAI_TriggerWordExtractor": GoogleAI_TriggerWordExtractor,
    "GoogleAI_WorkflowAnalyzer": GoogleAI_WorkflowAnalyzer,
    "GoogleAI_CompatibilityChecker": GoogleAI_CompatibilityChecker,
    "GoogleAI_LoRATrainingAnalyzer": GoogleAI_LoRATrainingAnalyzer,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "GoogleAI_TextNode": "🔤 Google AI - Text Generator",
    "GoogleAI_TextVisionNode": "👁️ Google AI - Vision Analyzer",
    "GoogleAI_ImageNode": "🎨 Google AI - Image Generator",
    "GoogleAI_ImageBatchNode": "🖼️ Google AI - Image Batch",
    "GoogleAI_VideoGenerator": "🎬 Google AI - Video Generator (Veo 3.1)",
    "GoogleAI_VideoInterpolation": "🔀 Google AI - Video Interpolation",
    "GoogleAI_VideoStoryboard": "📖 Google AI - Video Storyboard",
    "GoogleAI_ModelArchitectureDetector": "🔍 Google AI - Architecture Detector",
    "GoogleAI_TriggerWordExtractor": "🏷️ Google AI - Trigger Word Extractor",
    "GoogleAI_WorkflowAnalyzer": "📋 Google AI - Workflow Analyzer",
    "GoogleAI_CompatibilityChecker": "✅ Google AI - Compatibility Checker",
    "GoogleAI_LoRATrainingAnalyzer": "📊 Google AI - Training Analyzer",
}

# ============================================================================
# WEB_DIRECTORY
# ============================================================================
WEB_DIRECTORY = "./web"

# ============================================================================
# SERVIDOR — Health endpoint
# ============================================================================
try:
    from server import PromptServer

    @PromptServer.instance.routes.get("/google-ai/health")
    async def health_check(request):
        return web.json_response({
            "status": "ok",
            "version": "2.0.1",
            "nodes": len(NODE_CLASS_MAPPINGS),
            "suites": ["text", "image", "video", "diagnostic"],
        })

    logger.info("[GoogleAI] Ruta registrada: /google-ai/health")

except (ImportError, AttributeError) as e:
    logger.warning(f"[GoogleAI] No se registró ruta del servidor: {e}")

# ============================================================================
# EXPORTS
# ============================================================================
__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS", "WEB_DIRECTORY"]

print(
    f"\n{'='*60}\n"
    f"  ✅ ComfyUI_GoogleAI V2.0.1 — {len(NODE_CLASS_MAPPINGS)} nodos\n"
    f"  🔤 Texto  | 👁️ Vision | 🎨 Imagen 4 | 🎬 Veo 3.1\n"
    f"  🔍 Diagnóstico (5 nodos)\n"
    f"  ⚠️  Audio (Lyria) removido — sin API pública aún\n"
    f"  💡 Error Explainer → ComfyUI_UniversalErrorExplainer\n"
    f"{'='*60}\n"
)
