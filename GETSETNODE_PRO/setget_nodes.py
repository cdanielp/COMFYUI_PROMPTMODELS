"""
SetNode y GetNode - PRO Version
Renombrados con prefijo PRO_ y categoría GetSetNode_Pro
"""

from .qwen_cache import QwenCache, get_cache, COMFY_TYPES

# ============================================================================
# TIPO ANY
# ============================================================================
class AnyType(str):
    def __eq__(self, other):
        return True
    def __ne__(self, other):
        return False
    def __hash__(self):
        return hash("*")

ANY_TYPE = AnyType("*")

# ============================================================================
# PRO_SetNode
# ============================================================================
class PRO_SetNode:
    def __init__(self):
        pass
    
    @classmethod
    def INPUT_TYPES(cls):
        optional_inputs = {
            "MODEL": ("MODEL", {}),
            "CLIP": ("CLIP", {}),
            "VAE": ("VAE", {}),
            "CONTROL_NET": ("CONTROL_NET", {}),
            "CLIP_VISION": ("CLIP_VISION", {}),
            "STYLE_MODEL": ("STYLE_MODEL", {}),
            "UPSCALE_MODEL": ("UPSCALE_MODEL", {}),
            "LATENT": ("LATENT", {}),
            "IMAGE": ("IMAGE", {}),
            "MASK": ("MASK", {}),
            "CONDITIONING": ("CONDITIONING", {}),
            "SAMPLER": ("SAMPLER", {}),
            "SIGMAS": ("SIGMAS", {}),
            "NOISE": ("NOISE", {}),
            "GUIDER": ("GUIDER", {}),
            "*": (ANY_TYPE, {}),
        }
        
        return {
            "required": {},
            "optional": optional_inputs,
            "hidden": {"unique_id": "UNIQUE_ID", "prompt": "PROMPT", "extra_pnginfo": "EXTRA_PNGINFO"}
        }

    RETURN_TYPES = (ANY_TYPE,)
    RETURN_NAMES = ("*",)
    INPUT_IS_LIST = False
    OUTPUT_IS_LIST = (False,)
    OUTPUT_NODE = True
    FUNCTION = "set_value"
    CATEGORY = "GetSetNode_Pro/utils"
    
    @classmethod
    def IS_CHANGED(cls, **kwargs):
        return float("NaN")

    def set_value(self, unique_id=None, prompt=None, extra_pnginfo=None, **kwargs):
        cache = get_cache()
        value = None
        input_type = "*"
        
        for key, val in kwargs.items():
            if val is not None:
                value = val
                input_type = key
                break
        
        if value is None:
            return (None,)
        
        var_name = self._get_var_name(unique_id, prompt, extra_pnginfo, input_type)
        cache.set(var_name, value, input_type)
        return (value,)
    
    def _get_var_name(self, unique_id, prompt, extra_pnginfo, fallback):
        var_name = fallback
        if prompt and unique_id:
            try:
                node_info = prompt.get(str(unique_id), {})
                inputs = node_info.get("inputs", {})
                if isinstance(inputs, dict): var_name = inputs.get("name", var_name)
            except: pass
        
        if extra_pnginfo and var_name == fallback:
            try:
                workflow = extra_pnginfo.get("workflow", {})
                for node in workflow.get("nodes", []):
                    if str(node.get("id")) == str(unique_id):
                        title = node.get("title", "")
                        # Soporte para PRO_Set_NOMBRE o Set_NOMBRE
                        if title.startswith("Set_") or title.startswith("PRO_Set_"):
                            parts = title.split("_", 1)
                            if len(parts) > 1: var_name = parts[1]
                        elif "_" in title:
                            var_name = title.split("_", 1)[1]
                        wv = node.get("widgets_values", [])
                        if wv and isinstance(wv[0], str): var_name = wv[0]
                        break
            except: pass
        return var_name

# ============================================================================
# PRO_GetNode
# ============================================================================
class PRO_GetNode:
    def __init__(self):
        pass
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {},
            "optional": {"name": ("STRING", {"default": "my_variable", "multiline": False})},
            "hidden": {"unique_id": "UNIQUE_ID", "prompt": "PROMPT", "extra_pnginfo": "EXTRA_PNGINFO"}
        }

    RETURN_TYPES = (ANY_TYPE,)
    RETURN_NAMES = ("*",)
    OUTPUT_NODE = False
    FUNCTION = "get_value"
    CATEGORY = "GetSetNode_Pro/utils"
    
    @classmethod
    def IS_CHANGED(cls, **kwargs):
        return float("NaN")

    def get_value(self, name="my_variable", unique_id=None, prompt=None, extra_pnginfo=None):
        cache = get_cache()
        actual_name = self._get_var_name(name, unique_id, prompt, extra_pnginfo)
        
        if not cache.exists(actual_name):
            available = cache.list_names()
            available_str = ", ".join(available) if available else "(none)"
            raise ValueError(
                f"[PRO_GetNode] ✗ Variable '{actual_name}' not found!\n"
                f"Available: {available_str}\n"
            )
        
        value, dtype = cache.get_with_type(actual_name)
        return (value,)
    
    def _get_var_name(self, default_name, unique_id, prompt, extra_pnginfo):
        var_name = default_name
        if extra_pnginfo:
            try:
                workflow = extra_pnginfo.get("workflow", {})
                for node in workflow.get("nodes", []):
                    if str(node.get("id")) == str(unique_id):
                        wv = node.get("widgets_values", [])
                        if wv and isinstance(wv[0], str): var_name = wv[0]
                        title = node.get("title", "")
                        if title.startswith("Get_") or title.startswith("PRO_Get_"):
                            parts = title.split("_", 1)
                            if len(parts) > 1: var_name = parts[1]
                        break
            except: pass
        
        if var_name == default_name and prompt and unique_id:
            try:
                node_info = prompt.get(str(unique_id), {})
                inputs = node_info.get("inputs", {})
                if isinstance(inputs, dict) and "name" in inputs: var_name = inputs["name"]
            except: pass
        return var_name

# ============================================================================
# Versiones alternativas y Utilidades
# ============================================================================
class PRO_SetNodeNamed:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "value": (ANY_TYPE, {}),
                "name": ("STRING", {"default": "my_variable"}),
            },
        }
    RETURN_TYPES = (ANY_TYPE,)
    RETURN_NAMES = ("value",)
    OUTPUT_NODE = True
    FUNCTION = "set_value"
    CATEGORY = "GetSetNode_Pro/utils"

    def set_value(self, value, name):
        cache = get_cache()
        cache.set(name, value)
        return (value,)

class PRO_ListCacheNode:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {},
            "optional": {"trigger": (ANY_TYPE, {})}
        }
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("info",)
    FUNCTION = "list_cache"
    CATEGORY = "GetSetNode_Pro/utils"

    def list_cache(self, trigger=None):
        cache = get_cache()
        items = cache.list_all()
        if not items:
            info = "[PRO_Cache] Empty"
        else:
            lines = [f"[PRO_Cache] {len(items)} variable(s):"]
            for name, dtype in items.items():
                lines.append(f"  • {name}: {dtype}")
            info = "\n".join(lines)
        print(info)
        return (info,)

class PRO_ClearCacheNode:
    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {"confirm": ("BOOLEAN", {"default": False})}}
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("status",)
    OUTPUT_NODE = True
    FUNCTION = "clear_cache"
    CATEGORY = "GetSetNode_Pro/utils"

    def clear_cache(self, confirm=False):
        cache = get_cache()
        if confirm:
            count = len(cache.list_names())
            cache.clear()
            status = f"[PRO_Cache] ✓ Cleared {count} variable(s)"
        else:
            status = "[PRO_Cache] Skipped"
        print(status)
        return (status,)