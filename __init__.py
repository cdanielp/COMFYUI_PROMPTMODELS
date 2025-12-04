# Root initializer for COMFYUI_PROMPTMODELS
# This allows ComfyUI to detect submodules like get_last_frame

from .get_last_frame import NODE_CLASS_MAPPINGS as _nodes1, NODE_DISPLAY_NAME_MAPPINGS as _display1

NODE_CLASS_MAPPINGS = {}
NODE_CLASS_MAPPINGS.update(_nodes1)

NODE_DISPLAY_NAME_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS.update(_display1)

print("[ComfyDeploy] ✅ COMFYUI_PROMPTMODELS root module loaded successfully.")
