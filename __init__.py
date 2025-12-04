# Root initializer for COMFYUI_PROMPTMODELS
# This file allows ComfyUI / ComfyDeploy to detect all submodules under this repo

from .get_last_frame import NODE_CLASS_MAPPINGS as GET_LAST_FRAME_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS as GET_LAST_FRAME_NAME_MAPPINGS

NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}

# Register submodules (add more here if you create new nodes later)
NODE_CLASS_MAPPINGS.update(GET_LAST_FRAME_CLASS_MAPPINGS)
NODE_DISPLAY_NAME_MAPPINGS.update(GET_LAST_FRAME_NAME_MAPPINGS)

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]

print("[ComfyDeploy] ✅ COMFYUI_PROMPTMODELS module loaded successfully.")
