"""
TextPromptBlocker - Custom Node para ComfyUI
Nodo de seguridad para filtrar/bloquear prompts con contenido prohibido.

Instalación:
    Copiar la carpeta 'text_prompt_blocker' completa a:
    ComfyUI/custom_nodes/

Nodos incluidos:
    - TextPromptBlocker: Bloquea/filtra prompts con palabras prohibidas
    - TextPromptBlockerPreview: Preview sin bloqueo para testing
"""

from .text_prompt_blocker import TextPromptBlocker, TextPromptBlockerPreview

# Registro de nodos para ComfyUI
NODE_CLASS_MAPPINGS = {
    "TextPromptBlocker": TextPromptBlocker,
    "TextPromptBlockerPreview": TextPromptBlockerPreview,
}

# Nombres para mostrar en la UI
NODE_DISPLAY_NAME_MAPPINGS = {
    "TextPromptBlocker": "🛡️ Text Prompt Blocker",
    "TextPromptBlockerPreview": "🔍 Text Prompt Blocker (Preview)",
}

# Metadatos del paquete
__version__ = "1.0.0"
__author__ = "Custom Node"
__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]
