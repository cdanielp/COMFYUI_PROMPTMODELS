# Root initializer for COMFYUI_PROMPTMODELS
# This file allows ComfyUI / ComfyDeploy to detect all submodules under this repo

# Import existing Utility nodes
from .get_last_frame import (
    NODE_CLASS_MAPPINGS as GET_LAST_FRAME_CLASS_MAPPINGS,
    NODE_DISPLAY_NAME_MAPPINGS as GET_LAST_FRAME_NAME_MAPPINGS,
)

# Import Text Prompt Blocker nodes
from .text_prompt_blocker import (
    NODE_CLASS_MAPPINGS as TEXT_PROMPT_BLOCKER_CLASS_MAPPINGS,
    NODE_DISPLAY_NAME_MAPPINGS as TEXT_PROMPT_BLOCKER_NAME_MAPPINGS,
)

# Import Prompt-related nodes
from .nodes.prompt_model_loader import PromptModelLoader
from .nodes.prompt_refiner import PromptRefiner
from .nodes.prompt_info import PromptInfo

# Base node registry
NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}

# Merge Utility nodes
NODE_CLASS_MAPPINGS.update(GET_LAST_FRAME_CLASS_MAPPINGS)
NODE_DISPLAY_NAME_MAPPINGS.update(GET_LAST_FRAME_NAME_MAPPINGS)

# Merge Text Prompt Blocker nodes
NODE_CLASS_MAPPINGS.update(TEXT_PROMPT_BLOCKER_CLASS_MAPPINGS)
NODE_DISPLAY_NAME_MAPPINGS.update(TEXT_PROMPT_BLOCKER_NAME_MAPPINGS)

# Register Prompt Models
NODE_CLASS_MAPPINGS.update({
    "PromptModelLoader": PromptModelLoader,
    "PromptRefiner": PromptRefiner,
    "PromptInfo": PromptInfo,
})

NODE_DISPLAY_NAME_MAPPINGS.update({
    "PromptModelLoader": "🧠 Prompt Model Loader",
    "PromptRefiner": "✨ Prompt Refiner",
    "PromptInfo": "ℹ️ Prompt Info",
})

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]

print("[COMFYUI_PROMPTMODELS] ✅ Nodes registered: PromptModelLoader, PromptRefiner, PromptInfo, GetLastFrame, GetFrameByIndex, TextPromptBlocker, TextPromptBlockerPreview")
