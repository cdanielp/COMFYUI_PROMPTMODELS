# ============================================================
#  PROMPTMODELS STUDIO - Custom Node Loader for ComfyUI
# ============================================================

# Colores para logs en consola
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
RESET = "\033[0m"

print(f"{GREEN}[PromptModels Studio] 🚀 Loading custom nodes for ComfyUI...{RESET}")

NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}

# ============================================================
#  Importación segura de módulos
# ============================================================

def safe_import(name, import_func):
    """Evita que un error en un módulo bloquee los demás."""
    try:
        import_func()
        print(f"{GREEN}[{name}] ✅ Loaded successfully!{RESET}")
    except Exception as e:
        print(f"{RED}[{name}] ⚠️ Failed to load: {e}{RESET}")

# --- Get Last Frame ---
safe_import("GetLastFrame", lambda: _import_get_last_frame())
def _import_get_last_frame():
    from .get_last_frame import (
        NODE_CLASS_MAPPINGS as M1,
        NODE_DISPLAY_NAME_MAPPINGS as N1,
    )
    NODE_CLASS_MAPPINGS.update(M1)
    NODE_DISPLAY_NAME_MAPPINGS.update(N1)

# --- Text Prompt Blocker ---
safe_import("TextPromptBlocker", lambda: _import_text_prompt_blocker())
def _import_text_prompt_blocker():
    from .text_prompt_blocker import (
        NODE_CLASS_MAPPINGS as M2,
        NODE_DISPLAY_NAME_MAPPINGS as N2,
    )
    NODE_CLASS_MAPPINGS.update(M2)
    NODE_DISPLAY_NAME_MAPPINGS.update(N2)

# --- Divisor De Prompts ---
safe_import("DivisorDePrompts", lambda: _import_divisor_prompts())
def _import_divisor_prompts():
    from .DivisorDePrompts import (
        NODE_CLASS_MAPPINGS as M3,
        NODE_DISPLAY_NAME_MAPPINGS as N3,
    )
    NODE_CLASS_MAPPINGS.update(M3)
    NODE_DISPLAY_NAME_MAPPINGS.update(N3)

# --- WJSetGetPlus ---
safe_import("WJSetGetPlus", lambda: _import_wjsetgetplus())
def _import_wjsetgetplus():
    from .ComfyUI_WJSetGetPlus import (
        NODE_CLASS_MAPPINGS as M4,
        NODE_DISPLAY_NAME_MAPPINGS as N4,
    )
    NODE_CLASS_MAPPINGS.update(M4)
    NODE_DISPLAY_NAME_MAPPINGS.update(N4)

# --- Google AI ---
safe_import("ComfyUI-GoogleAI", lambda: _import_googleai())
def _import_googleai():
    from .ComfyUI_GoogleAI import (
        NODE_CLASS_MAPPINGS as M5,
        NODE_DISPLAY_NAME_MAPPINGS as N5,
    )
    NODE_CLASS_MAPPINGS.update(M5)
    NODE_DISPLAY_NAME_MAPPINGS.update(N5)

# ============================================================
#  Resumen dinámico
# ============================================================

loaded_nodes = list(NODE_DISPLAY_NAME_MAPPINGS.values())
print(f"{YELLOW}[PromptModels Studio] 📦 Total nodes loaded: {len(loaded_nodes)}{RESET}")
for name in loaded_nodes:
    print(f"   • {name}")

print(f"{GREEN}[PromptModels Studio] ✅ All available nodes are ready in ComfyUI!{RESET}")

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]
