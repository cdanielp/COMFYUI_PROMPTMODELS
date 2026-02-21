"""
__init__.py — ComfyUI_Grok
===========================
Punto de entrada del paquete. Registra todos los nodos en ComfyUI.

POLÍTICA DE RETROCOMPATIBILIDAD:
  ✅ Los nodos v1 (GrokTextNode, GrokImageNode) NUNCA se eliminan ni renombran.
     Sus claves en NODE_CLASS_MAPPINGS son permanentes para no romper workflows .json.
  ✅ Los nodos v2 se registran con nuevas claves sin afectar los v1.

Estructura del paquete:
  grok_core.py        — Motor central: tensores, HTTP, payloads
  grok_text_node.py   — GrokTextNode (v1) + Grok_Multimodal_Vision (v2)
  grok_image_node.py  — GrokImageNode (v1) + Grok_Image_Master (v2)
  grok_video_node.py  — Grok_Video_Forge (v2)
  grok_prompt_node.py — Grok_Prompt_Architect (v2)
  js/grok_ui.js       — Extensiones de UI (estilos, badges de estado)

Autor: Prompt Models Studio — xAI Integration Layer v2.0
"""

import os
import logging

log = logging.getLogger("ComfyUI_Grok")

# ── Importaciones robustas ────────────────────────────────────────────────────
# Cada módulo se importa en un try/except independiente para que un error en
# un nodo no impida la carga de los demás.

_load_errors = []

try:
    from .grok_text_node import GrokTextNode, Grok_Multimodal_Vision
except Exception as e:
    _load_errors.append(f"grok_text_node: {e}")
    GrokTextNode = None
    Grok_Multimodal_Vision = None

try:
    from .grok_image_node import GrokImageNode, Grok_Image_Master
except Exception as e:
    _load_errors.append(f"grok_image_node: {e}")
    GrokImageNode = None
    Grok_Image_Master = None

try:
    from .grok_video_node import Grok_Video_Forge
except Exception as e:
    _load_errors.append(f"grok_video_node: {e}")
    Grok_Video_Forge = None

try:
    from .grok_prompt_node import Grok_Prompt_Architect
except Exception as e:
    _load_errors.append(f"grok_prompt_node: {e}")
    Grok_Prompt_Architect = None

if _load_errors:
    log.warning(f"[ComfyUI_Grok] Errores de importación parciales: {_load_errors}")


# ══════════════════════════════════════════════════════════════════════════════
# NODE_CLASS_MAPPINGS
# ─────────────────────────────────────────────────────────────────────────────
# ⚠️ REGLA CRÍTICA: Las claves de este dict son los IDs permanentes de los nodos.
# Una vez publicados, NUNCA se cambian. Romperían todos los workflows existentes.
#
# Nomenclatura:
#   - Nodos v1 (legado): "GrokTextNode", "GrokImageNode"  ← Permanentes
#   - Nodos v2 (nuevos): "Grok_Multimodal_Vision", etc.   ← Permanentes desde v2
# ══════════════════════════════════════════════════════════════════════════════

NODE_CLASS_MAPPINGS = {}

# ── V1 LEGADO — No tocar estas claves jamás ───────────────────────────────────
if GrokTextNode is not None:
    NODE_CLASS_MAPPINGS["GrokTextNode"] = GrokTextNode

if GrokImageNode is not None:
    NODE_CLASS_MAPPINGS["GrokImageNode"] = GrokImageNode

# ── V2 NUEVOS — Registrados con nombres definitivos ──────────────────────────
if Grok_Multimodal_Vision is not None:
    NODE_CLASS_MAPPINGS["Grok_Multimodal_Vision"] = Grok_Multimodal_Vision

if Grok_Image_Master is not None:
    NODE_CLASS_MAPPINGS["Grok_Image_Master"] = Grok_Image_Master

if Grok_Video_Forge is not None:
    NODE_CLASS_MAPPINGS["Grok_Video_Forge"] = Grok_Video_Forge

if Grok_Prompt_Architect is not None:
    NODE_CLASS_MAPPINGS["Grok_Prompt_Architect"] = Grok_Prompt_Architect


# ══════════════════════════════════════════════════════════════════════════════
# NODE_DISPLAY_NAME_MAPPINGS
# Nombres amigables mostrados en el menú de ComfyUI (pueden cambiar sin romper nada)
# ══════════════════════════════════════════════════════════════════════════════

NODE_DISPLAY_NAME_MAPPINGS = {
    # V1 Legado
    "GrokTextNode":            "Grok Text [v1 Legacy]",
    "GrokImageNode":           "Grok Image [v1 Legacy]",
    # V2 Nuevos
    "Grok_Multimodal_Vision":  "🔭 Grok Multimodal Vision",
    "Grok_Image_Master":       "🎨 Grok Image Master",
    "Grok_Video_Forge":        "🎬 Grok Video Forge",
    "Grok_Prompt_Architect":   "✍️ Grok Prompt Architect",
}


# ── Ruta a los archivos JS para que ComfyUI los sirva ────────────────────────
WEB_DIRECTORY = os.path.join(os.path.dirname(__file__), "js")


# ── Log de inicio ────────────────────────────────────────────────────────────
loaded_nodes = list(NODE_CLASS_MAPPINGS.keys())
log.info(f"[ComfyUI_Grok] ✅ Nodos cargados ({len(loaded_nodes)}): {loaded_nodes}")

if _load_errors:
    log.error(f"[ComfyUI_Grok] ⚠️ Nodos con errores: {_load_errors}")


# ── Exports requeridos por ComfyUI ────────────────────────────────────────────
__all__ = [
    "NODE_CLASS_MAPPINGS",
    "NODE_DISPLAY_NAME_MAPPINGS",
    "WEB_DIRECTORY",
]
