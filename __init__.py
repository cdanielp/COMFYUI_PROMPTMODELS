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
#  FUNCIONES DE IMPORTACIÓN
# ============================================================

def _import_get_last_frame():
    from .get_last_frame import (
        NODE_CLASS_MAPPINGS as M1,
        NODE_DISPLAY_NAME_MAPPINGS as N1,
    )
    NODE_CLASS_MAPPINGS.update(M1)
    NODE_DISPLAY_NAME_MAPPINGS.update(N1)

def _import_text_prompt_blocker():
    from .text_prompt_blocker import (
        NODE_CLASS_MAPPINGS as M2,
        NODE_DISPLAY_NAME_MAPPINGS as N2,
    )
    NODE_CLASS_MAPPINGS.update(M2)
    NODE_DISPLAY_NAME_MAPPINGS.update(N2)

def _import_divisor_prompts():
    from .DivisorDePrompts import (
        NODE_CLASS_MAPPINGS as M3,
        NODE_DISPLAY_NAME_MAPPINGS as N3,
    )
    NODE_CLASS_MAPPINGS.update(M3)
    NODE_DISPLAY_NAME_MAPPINGS.update(N3)

def _import_wjsetgetplus():
    from .ComfyUI_WJSetGetPlus import (
        NODE_CLASS_MAPPINGS as M4,
        NODE_DISPLAY_NAME_MAPPINGS as N4,
    )
    NODE_CLASS_MAPPINGS.update(M4)
    NODE_DISPLAY_NAME_MAPPINGS.update(N4)

def _import_googleai():
    from .ComfyUI_GoogleAI import (
        NODE_CLASS_MAPPINGS as M5,
        NODE_DISPLAY_NAME_MAPPINGS as N5,
    )
    NODE_CLASS_MAPPINGS.update(M5)
    NODE_DISPLAY_NAME_MAPPINGS.update(N5)

# ============================================================
#  IMPORTACIÓN SEGURA DE MÓDULOS
# ============================================================

def safe_import(name, func):
    try:
        func()
        print(f"{GREEN}[{name}] ✅ Loaded successfully!{RESET}")
    except Exception as e:
        print(f"{RED}[{name}] ⚠️ Failed to load: {e}{RESET}")

safe_import("GetLastFrame", _import_get_last_frame)
safe_import("TextPromptBlocker", _import_text_prompt_blocker)
safe_import("DivisorDePrompts", _import_divisor_prompts)
safe_import("WJSetGetPlus", _import_wjsetgetplus)
safe_import("ComfyUI-GoogleAI", _import_googleai)

# ============================================================
#  LOG FINAL
# ============================================================

loaded_nodes = list(NODE_DISPLAY_NAME_MAPPINGS.values())
print(f"{YELLOW}[PromptModels Studio] 📦 Total nodes loaded: {len(loaded_nodes)}{RESET}")
for name in loaded_nodes:
    print(f"   • {name}")

print(f"{GREEN}[PromptModels Studio] ✅ All available nodes are ready in ComfyUI!{RESET}")

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]
