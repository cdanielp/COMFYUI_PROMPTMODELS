# ============================================================
#  PROMPTMODELS STUDIO - Custom Node Loader for ComfyUI
# ============================================================

__version__ = "1.0.0"
__author__ = "Prompt Models Studio"

GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
RESET = "\033[0m"

print(f"{GREEN}[PromptModels Studio] 🚀 Loading custom nodes for ComfyUI...{RESET}")

NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}

# ============================================================
#  IMPORTACIÓN DE MÓDULOS
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

# --- GETSETNODE_PRO ---
try:
    from .GETSETNODE_PRO import (
        NODE_CLASS_MAPPINGS as PRO_SETGET_CLASS,
        NODE_DISPLAY_NAME_MAPPINGS as PRO_SETGET_NAMES,
    )
    NODE_CLASS_MAPPINGS.update(PRO_SETGET_CLASS)
    NODE_DISPLAY_NAME_MAPPINGS.update(PRO_SETGET_NAMES)
    print(f"{GREEN}[GETSETNODE_PRO] ✅ Loaded{RESET}")
except Exception as e:
    print(f"{RED}[GETSETNODE_PRO] ⚠️ Failed: {e}{RESET}")

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

# --- comfyui_selectores_pro ---
try:
    from .comfyui_selectores_pro import (
        NODE_CLASS_MAPPINGS as SELECTORES_CLASS,
        NODE_DISPLAY_NAME_MAPPINGS as SELECTORES_NAMES,
    )
    NODE_CLASS_MAPPINGS.update(SELECTORES_CLASS)
    NODE_DISPLAY_NAME_MAPPINGS.update(SELECTORES_NAMES)
    print(f"{GREEN}[Selectores Pro] ✅ Loaded{RESET}")
except Exception as e:
    print(f"{RED}[Selectores Pro] ⚠️ Failed: {e}{RESET}")

# ============================================================
#  LOG FINAL
# ============================================================
print(f"{YELLOW}[PromptModels Studio] 📦 Total nodes loaded: {len(NODE_CLASS_MAPPINGS)}{RESET}")
print(f"{GREEN}[PromptModels Studio] ✅ Ready!{RESET}")

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]
