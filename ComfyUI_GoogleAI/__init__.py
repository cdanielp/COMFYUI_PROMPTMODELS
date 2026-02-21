"""
ComfyUI_GoogleAI - Suite Integral de Google AI (V2.1)
======================================================
Gemini 3.1 Pro | Imagen 3 | Veo 3.1 | Lyria 3 | Diagnóstico

V2.1: Async video polling | Seed sanitization | Multimodal master node
      folder_paths dropdowns | Type Mismatch fallback audio

⚠️ RETROCOMPATIBILIDAD: Clases originales NO se renombran ni eliminan.
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
from .google_audio_node import GoogleAI_MusicDirector, GoogleAI_FoleyGenerator
from .google_diagnostic_node import (
    GoogleAI_ModelArchitectureDetector, GoogleAI_TriggerWordExtractor,
    GoogleAI_WorkflowAnalyzer, GoogleAI_CompatibilityChecker, GoogleAI_LoRATrainingAnalyzer,
)

# ============================================================================
# NODE_CLASS_MAPPINGS (Retrocompatible + Nuevos)
# ============================================================================
NODE_CLASS_MAPPINGS = {
    # Suite 0: Texto (existentes, NO renombrados)
    "GoogleAI_TextNode": GoogleAI_TextNode,
    "GoogleAI_TextVisionNode": GoogleAI_TextVisionNode,
    # Suite 0: Imagen (existentes, NO renombrados)
    "GoogleAI_ImageNode": GoogleAI_ImageNode,
    "GoogleAI_ImageBatchNode": GoogleAI_ImageBatchNode,
    # Suite 1: Video (NUEVOS)
    "GoogleAI_VideoGenerator": GoogleAI_VideoGenerator,
    "GoogleAI_VideoInterpolation": GoogleAI_VideoInterpolation,
    "GoogleAI_VideoStoryboard": GoogleAI_VideoStoryboard,
    # Suite 2: Audio (NUEVOS)
    "GoogleAI_MusicDirector": GoogleAI_MusicDirector,
    "GoogleAI_FoleyGenerator": GoogleAI_FoleyGenerator,
    # Suite 3: Diagnóstico (NUEVOS)
    "GoogleAI_ModelArchitectureDetector": GoogleAI_ModelArchitectureDetector,
    "GoogleAI_TriggerWordExtractor": GoogleAI_TriggerWordExtractor,
    "GoogleAI_WorkflowAnalyzer": GoogleAI_WorkflowAnalyzer,
    "GoogleAI_CompatibilityChecker": GoogleAI_CompatibilityChecker,
    "GoogleAI_LoRATrainingAnalyzer": GoogleAI_LoRATrainingAnalyzer,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "GoogleAI_TextNode": "🔤 Google AI - Multimodal Text (Gemini 3.1)",
    "GoogleAI_TextVisionNode": "👁️ Google AI - Vision Analyzer",
    "GoogleAI_ImageNode": "🎨 Google AI - Image Generator (Imagen 3)",
    "GoogleAI_ImageBatchNode": "🖼️ Google AI - Image Batch",
    "GoogleAI_VideoGenerator": "🎬 Google AI - Video Generator (Veo 3.1)",
    "GoogleAI_VideoInterpolation": "🔀 Google AI - Video Interpolation",
    "GoogleAI_VideoStoryboard": "📖 Google AI - Video Storyboard",
    "GoogleAI_MusicDirector": "🎵 Google AI - Music Director (Lyria 3)",
    "GoogleAI_FoleyGenerator": "🔊 Google AI - Foley Generator",
    "GoogleAI_ModelArchitectureDetector": "🔍 Google AI - Architecture Detector",
    "GoogleAI_TriggerWordExtractor": "🏷️ Google AI - Trigger Word Extractor",
    "GoogleAI_WorkflowAnalyzer": "📋 Google AI - Workflow Analyzer",
    "GoogleAI_CompatibilityChecker": "✅ Google AI - Compatibility Checker",
    "GoogleAI_LoRATrainingAnalyzer": "📊 Google AI - Training Analyzer",
}

# ============================================================================
# WEB_DIRECTORY - Carga el frontend JS
# ============================================================================
WEB_DIRECTORY = "./web"

# ============================================================================
# SERVIDOR - Endpoint de health
# ============================================================================
try:
    from server import PromptServer

    @PromptServer.instance.routes.get("/google-ai/health")
    async def health_check(request):
        """Endpoint de verificación de salud."""
        return web.json_response({
            "status": "ok",
            "version": "2.1.0",
            "nodes": len(NODE_CLASS_MAPPINGS),
            "suites": ["text", "image", "video", "audio", "diagnostic"],
            "video_polling": "async (aiohttp)",
            "seed_sanitization": "64→32 bits",
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
    f"  ✅ ComfyUI_GoogleAI V2.1 — {len(NODE_CLASS_MAPPINGS)} nodos\n"
    f"  🔤 Multimodal | 🎨 Imagen | 🎬 Video (async)\n"
    f"  🎵 Audio     | 🔍 Diagnóstico (folder_paths)\n"
    f"  🛡️ Seed 64→32 | opencv-headless | Type-safe audio\n"
    f"  💡 Error Explainer → ComfyUI_UniversalErrorExplainer\n"
    f"{'='*60}\n"
)
