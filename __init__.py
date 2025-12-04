import importlib
import pkgutil
import os
import sys

# Asegura que el path actual está disponible para importación
sys.path.append(os.path.dirname(__file__))

NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}

def _try_import_submodules():
    current_dir = os.path.dirname(__file__)
    for _, module_name, _ in pkgutil.iter_modules([current_dir]):
        try:
            # Solo importar subcarpetas (como get_last_frame)
            if module_name.startswith("_"):
                continue
            module = importlib.import_module(f"{__name__}.{module_name}")
            if hasattr(module, "NODE_CLASS_MAPPINGS"):
                NODE_CLASS_MAPPINGS.update(module.NODE_CLASS_MAPPINGS)
            if hasattr(module, "NODE_DISPLAY_NAME_MAPPINGS"):
                NODE_DISPLAY_NAME_MAPPINGS.update(module.NODE_DISPLAY_NAME_MAPPINGS)
            print(f"[ComfyDeploy] ✅ Loaded submodule: {module_name}")
        except Exception as e:
            print(f"[ComfyDeploy] ❌ Failed to import {module_name}: {e}")

_try_import_submodules()

print("[ComfyDeploy] ✅ COMFYUI_PROMPTMODELS root module loaded successfully.")
