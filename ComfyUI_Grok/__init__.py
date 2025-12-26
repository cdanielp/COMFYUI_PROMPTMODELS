# __init__.py
"""
ComfyUI-Grok: Nodos para integración con xAI API
"""

GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
RESET = "\033[0m"

NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}

# --- Grok Text ---
try:
    from .grok_text_node import (
        NODE_CLASS_MAPPINGS as TEXT_CLASS,
        NODE_DISPLAY_NAME_MAPPINGS as TEXT_NAMES,
    )
    NODE_CLASS_MAPPINGS.update(TEXT_CLASS)
    NODE_DISPLAY_NAME_MAPPINGS.update(TEXT_NAMES)
except Exception as e:
    print(f"{RED}[Grok Text] ⚠️ Failed: {e}{RESET}")

# --- Grok Image ---
try:
    from .grok_image_node import (
        NODE_CLASS_MAPPINGS as IMAGE_CLASS,
        NODE_DISPLAY_NAME_MAPPINGS as IMAGE_NAMES,
    )
    NODE_CLASS_MAPPINGS.update(IMAGE_CLASS)
    NODE_DISPLAY_NAME_MAPPINGS.update(IMAGE_NAMES)
except Exception as e:
    print(f"{RED}[Grok Image] ⚠️ Failed: {e}{RESET}")

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]

print(f"{GREEN}[ComfyUI-Grok] 🚀 Ready — Integrated with xAI API (Text + Image){RESET}")
