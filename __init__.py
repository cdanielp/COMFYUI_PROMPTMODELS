# ============================================================
#  PROMPTMODELS STUDIO - Custom Node Loader for ComfyUI
# ============================================================
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
RESET = "\033[0m"

print(f"{GREEN}[PromptModels Studio] 🚀 Loading custom nodes for ComfyUI...{RESET}")

NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}

# ============================================================
#  IMPORTACIÓN SEGURA DE MÓDULOS
# ============================================================

# --- GetLastFrame ---
try:
    from .get_last_frame import (
        NODE_CLASS_MAPPINGS as GET_LAST_FRAME_CLASS,
        NODE_DISPLAY_NAME_MAPPINGS as GET_LAST_FRAME_NAMES,
    )
    NODE_CLASS_MAPPINGS.update(GET_LAST_FRAME_CLASS)
    NODE_DISPLAY_NAME_MAPPINGS.update(GET_LAST_FRAME_NAMES)
    print(f"{GREEN}[GetLastFrame] ✅ Loaded{RESET}")
except Exception as e:
    print(f"{RED}[GetLastFrame] ⚠️ Failed: {e}{RESET}")

# --- TextPromptBlocker ---
try:
    from .text_prompt_blocker import (
        NODE_CLASS_MAPPINGS as TEXT_PROMPT_BLOCKER_CLASS,
        NODE_DISPLAY_NAME_MAPPINGS as TEXT_PROMPT_BLOCKER_NAMES,
    )
    NODE_CLASS_MAPPINGS.update(TEXT_PROMPT_BLOCKER_CLASS)
    NODE_DISPLAY_NAME_MAPPINGS.update(TEXT_PROMPT_BLOCKER_NAMES)
    print(f"{GREEN}[TextPromptBlocker] ✅ Loaded{RESET}")
except Exception as e:
    print(f"{RED}[TextPromptBlocker] ⚠️ Failed: {e}{RESET}")

# --- DivisorDePrompts ---
try:
    from .DivisorDePrompts import (
        NODE_CLASS_MAPPINGS as DIVISOR_CLASS,
        NODE_DISPLAY_NAME_MAPPINGS as DIVISOR_NAMES,
    )
    NODE_CLASS_MAPPINGS.update(DIVISOR_CLASS)
    NODE_DISPLAY_NAME_MAPPINGS.update(DIVISOR_NAMES)
    print(f"{GREEN}[DivisorDePrompts] ✅ Loaded{RESET}")
except Exception as e:
    print(f"{RED}[DivisorDePrompts] ⚠️ Failed: {e}{RESET}")

# --- WJSetGetPlus ---
try:
    from .ComfyUI_WJSetGetPlus import (
        NODE_CLASS_MAPPINGS as WJSETGET_CLASS,
        NODE_DISPLAY_NAME_MAPPINGS as WJSETGET_NAMES,
    )
    NODE_CLASS_MAPPINGS.update(WJSETGET_CLASS)
    NODE_DISPLAY_NAME_MAPPINGS.update(WJSETGET_NAMES)
    print(f"{GREEN}[WJSetGetPlus] ✅ Loaded{RESET}")
except Exception as e:
    print(f"{RED}[WJSetGetPlus] ⚠️ Failed: {e}{RESET}")

# --- ComfyUI-GoogleAI ---
try:
    from .ComfyUI_GoogleAI import (
        NODE_CLASS_MAPPINGS as GOOGLEAI_CLASS,
        NODE_DISPLAY_NAME_MAPPINGS as GOOGLEAI_NAMES,
    )
    NODE_CLASS_MAPPINGS.update(GOOGLEAI_CLASS)
    NODE_DISPLAY_NAME_MAPPINGS.update(GOOGLEAI_NAMES)
    print(f"{GREEN}[ComfyUI-GoogleAI] ✅ Loaded{RESET}")
except Exception as e:
    print(f"{RED}[ComfyUI-GoogleAI] ⚠️ Failed: {e}{RESET}")

# --- ComfyUI-Grok (xAI) ---
try:
    from .ComfyUI_Grok import (
        NODE_CLASS_MAPPINGS as GROK_CLASS,
        NODE_DISPLAY_NAME_MAPPINGS as GROK_NAMES,
    )
    NODE_CLASS_MAPPINGS.update(GROK_CLASS)
    NODE_DISPLAY_NAME_MAPPINGS.update(GROK_NAMES)
    print(f"{GREEN}[ComfyUI-Grok] ✅ Loaded{RESET}")
except Exception as e:
    print(f"{RED}[ComfyUI-Grok] ⚠️ Failed: {e}{RESET}")

# --- Titan Suite 🇪🇸 (Maestro, Inspector, MultiLora) ---
try:
    from .titan_nodes_comfyui import (
        NODE_CLASS_MAPPINGS as TITAN_CLASS,
        NODE_DISPLAY_NAME_MAPPINGS as TITAN_NAMES,
    )
    NODE_CLASS_MAPPINGS.update(TITAN_CLASS)
    NODE_DISPLAY_NAME_MAPPINGS.update(TITAN_NAMES)
    print(f"{GREEN}[Titan Suite 🇪🇸] ✅ Loaded (7 nodes){RESET}")
except Exception as e:
    print(f"{RED}[Titan Suite 🇪🇸] ⚠️ Failed: {e}{RESET}")

# ============================================================
#  LOG FINAL
# ============================================================
print(f"{YELLOW}[PromptModels Studio] 📦 Total nodes loaded: {len(NODE_CLASS_MAPPINGS)}{RESET}")
print(f"{GREEN}[PromptModels Studio] ✅ Ready!{RESET}")

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]
