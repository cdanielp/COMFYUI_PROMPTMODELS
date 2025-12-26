# __init__.py
from .google_text_node import GoogleAI_TextNode, GoogleAI_TextNode_Simple
from .google_image_node import GoogleAI_ImageNode, GoogleAI_ImageNode_Simple

NODE_CLASS_MAPPINGS = {
    "GoogleAI_TextNode": GoogleAI_TextNode,
    "GoogleAI_TextNode_Simple": GoogleAI_TextNode_Simple,
    "GoogleAI_ImageNode": GoogleAI_ImageNode,
    "GoogleAI_ImageNode_Simple": GoogleAI_ImageNode_Simple,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "GoogleAI_TextNode": "🧠 Google AI Text Generator",
    "GoogleAI_TextNode_Simple": "🧠 Google AI Text (Simple)",
    "GoogleAI_ImageNode": "🎨 Google AI Image Generator",
    "GoogleAI_ImageNode_Simple": "🎨 Google AI Image (Simple)",
}

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]

print("\033[92m[ComfyUI-GoogleAI] Loaded successfully!\033[0m")
