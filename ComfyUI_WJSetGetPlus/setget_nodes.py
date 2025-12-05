"""
SetNode y GetNode - Compatible con rgthree-comfy y workflows existentes
Implementación que replica el comportamiento exacto de los nodos originales.

NOTA: Esta versión incluye inputs/outputs para todos los tipos comunes
para garantizar compatibilidad con workflows JSON existentes.
"""

from .qwen_cache import QwenCache, get_cache, COMFY_TYPES


# ============================================================================
# TIPO ANY - Truco para aceptar cualquier conexión en ComfyUI
# ============================================================================
class AnyType(str):
    """
    Tipo especial que ComfyUI interpreta como comodín.
    Sobrescribe __eq__ y __ne__ para que cualquier comparación de tipo sea válida.
    Esto permite conectar cualquier salida a este input.
    """
    def __eq__(self, other):
        return True
    
    def __ne__(self, other):
        return False
    
    def __hash__(self):
        return hash("*")


# Instancias del tipo ANY
ANY_TYPE = AnyType("*")


# ============================================================================
# SetNode - Almacena valores con nombre
# ============================================================================
class SetNode:
    """
    Almacena cualquier valor (MODEL, CLIP, VAE, IMAGE, etc.) con un nombre.
    100% compatible con workflows rgthree SetNode.
    
    Tiene inputs para todos los tipos comunes de ComfyUI.
    Solo uno debe estar conectado a la vez.
    """
    
    def __init__(self):
        pass
    
    @classmethod
    def INPUT_TYPES(cls):
        # Crear inputs para todos los tipos comunes
        # Esto garantiza compatibilidad con workflows existentes
        optional_inputs = {
            # Tipos de modelo
            "MODEL": ("MODEL", {}),
            "CLIP": ("CLIP", {}),
            "VAE": ("VAE", {}),
            "CONTROL_NET": ("CONTROL_NET", {}),
            "CLIP_VISION": ("CLIP_VISION", {}),
            "STYLE_MODEL": ("STYLE_MODEL", {}),
            "UPSCALE_MODEL": ("UPSCALE_MODEL", {}),
            # Tipos de datos
            "LATENT": ("LATENT", {}),
            "IMAGE": ("IMAGE", {}),
            "MASK": ("MASK", {}),
            "CONDITIONING": ("CONDITIONING", {}),
            # Tipos de sampler
            "SAMPLER": ("SAMPLER", {}),
            "SIGMAS": ("SIGMAS", {}),
            "NOISE": ("NOISE", {}),
            "GUIDER": ("GUIDER", {}),
            # Comodín para tipos no listados
            "*": (ANY_TYPE, {}),
        }
        
        return {
            "required": {},
            "optional": optional_inputs,
            "hidden": {
                "unique_id": "UNIQUE_ID",
                "prompt": "PROMPT",
                "extra_pnginfo": "EXTRA_PNGINFO",
            }
        }

    # Output es passthrough (pasa el mismo valor)
    RETURN_TYPES = (ANY_TYPE,)
    RETURN_NAMES = ("*",)
    
    INPUT_IS_LIST = False
    OUTPUT_IS_LIST = (False,)
    OUTPUT_NODE = True
    
    FUNCTION = "set_value"
    CATEGORY = "utils"
    
    @classmethod
    def IS_CHANGED(cls, **kwargs):
        return float("NaN")  # Siempre re-ejecutar

    def set_value(self, unique_id=None, prompt=None, extra_pnginfo=None, **kwargs):
        """
        Almacena el valor en caché.
        
        El nombre de la variable viene del widget 'name' en el prompt,
        o del título del nodo (Set_NOMBRE → NOMBRE).
        """
        cache = get_cache()
        
        # Encontrar el valor conectado (el primer kwarg no-None)
        value = None
        input_type = "*"
        
        for key, val in kwargs.items():
            if val is not None:
                value = val
                input_type = key
                break
        
        if value is None:
            print(f"[SetNode] Warning: No input connected")
            return (None,)
        
        # Obtener nombre de la variable desde el prompt
        var_name = self._get_var_name(unique_id, prompt, extra_pnginfo, input_type)
        
        # Almacenar en caché
        detected_type = cache.set(var_name, value, input_type)
        print(f"[SetNode] ✓ '{var_name}' stored (type: {detected_type})")
        
        return (value,)
    
    def _get_var_name(self, unique_id, prompt, extra_pnginfo, fallback):
        """Extrae el nombre de la variable desde el prompt o título."""
        var_name = fallback
        
        # Intentar obtener desde prompt (widgets_values)
        if prompt is not None and unique_id is not None:
            try:
                node_info = prompt.get(str(unique_id), {})
                inputs = node_info.get("inputs", {})
                
                # Buscar widget "name" o primer valor de widgets
                if isinstance(inputs, dict):
                    var_name = inputs.get("name", var_name)
            except:
                pass
        
        # Intentar obtener desde extra_pnginfo (título del nodo)
        if extra_pnginfo is not None and var_name == fallback:
            try:
                workflow = extra_pnginfo.get("workflow", {})
                for node in workflow.get("nodes", []):
                    if str(node.get("id")) == str(unique_id):
                        title = node.get("title", "")
                        # Extraer nombre del título: "Set_NOMBRE" → "NOMBRE"
                        if title.startswith("Set_"):
                            var_name = title[4:]
                        elif "_" in title:
                            var_name = title.split("_", 1)[1]
                        # También revisar widgets_values
                        wv = node.get("widgets_values", [])
                        if wv and isinstance(wv[0], str):
                            var_name = wv[0]
                        break
            except:
                pass
        
        return var_name


# ============================================================================
# GetNode - Recupera valores por nombre
# ============================================================================
class GetNode:
    """
    Recupera un valor previamente almacenado con SetNode.
    100% compatible con workflows rgthree GetNode.
    
    Tiene outputs para todos los tipos comunes de ComfyUI.
    El output correcto se activa según el tipo almacenado.
    """
    
    def __init__(self):
        pass
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {},
            "optional": {
                "name": ("STRING", {
                    "default": "my_variable",
                    "multiline": False,
                }),
            },
            "hidden": {
                "unique_id": "UNIQUE_ID",
                "prompt": "PROMPT",
                "extra_pnginfo": "EXTRA_PNGINFO",
            }
        }

    # Outputs para todos los tipos comunes
    # ComfyUI usará el que coincida con la conexión del workflow
    RETURN_TYPES = (ANY_TYPE,)
    RETURN_NAMES = ("*",)
    
    OUTPUT_NODE = False
    FUNCTION = "get_value"
    CATEGORY = "utils"
    
    @classmethod
    def IS_CHANGED(cls, **kwargs):
        return float("NaN")

    def get_value(self, name="my_variable", unique_id=None, prompt=None, extra_pnginfo=None):
        """
        Recupera el valor del caché.
        """
        cache = get_cache()
        
        # Intentar obtener nombre desde widgets_values o título
        actual_name = self._get_var_name(name, unique_id, prompt, extra_pnginfo)
        
        if not cache.exists(actual_name):
            available = cache.list_names()
            available_str = ", ".join(available) if available else "(none)"
            raise ValueError(
                f"[GetNode] ✗ Variable '{actual_name}' not found!\n"
                f"Available: {available_str}\n"
                f"Tip: Make sure SetNode runs BEFORE GetNode in the graph."
            )
        
        value, dtype = cache.get_with_type(actual_name)
        print(f"[GetNode] ✓ '{actual_name}' retrieved (type: {dtype})")
        
        return (value,)
    
    def _get_var_name(self, default_name, unique_id, prompt, extra_pnginfo):
        """Extrae el nombre de la variable desde el prompt o título."""
        var_name = default_name
        
        # Primero intentar desde extra_pnginfo (widgets_values del nodo)
        if extra_pnginfo is not None:
            try:
                workflow = extra_pnginfo.get("workflow", {})
                for node in workflow.get("nodes", []):
                    if str(node.get("id")) == str(unique_id):
                        # widgets_values contiene el nombre
                        wv = node.get("widgets_values", [])
                        if wv and isinstance(wv[0], str):
                            var_name = wv[0]
                        # También del título: "Get_NOMBRE" → "NOMBRE"
                        title = node.get("title", "")
                        if title.startswith("Get_"):
                            var_name = title[4:]
                        break
            except:
                pass
        
        # Fallback a prompt
        if var_name == default_name and prompt is not None and unique_id is not None:
            try:
                node_info = prompt.get(str(unique_id), {})
                inputs = node_info.get("inputs", {})
                if isinstance(inputs, dict) and "name" in inputs:
                    var_name = inputs["name"]
            except:
                pass
        
        return var_name


# ============================================================================
# Versiones alternativas con widget explícito
# ============================================================================
class SetNodeNamed:
    """SetNode con widget explícito para el nombre."""
    
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
    CATEGORY = "utils"

    def set_value(self, value, name):
        cache = get_cache()
        detected_type = cache.set(name, value)
        print(f"[SetNode] ✓ '{name}' stored (type: {detected_type})")
        return (value,)


# ============================================================================
# Nodos de utilidad
# ============================================================================
class ListCacheNode:
    """Muestra todas las variables en caché (para debug)."""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {},
            "optional": {
                "trigger": (ANY_TYPE, {}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("info",)
    FUNCTION = "list_cache"
    CATEGORY = "utils"

    def list_cache(self, trigger=None):
        cache = get_cache()
        items = cache.list_all()
        
        if not items:
            info = "[Cache] Empty"
        else:
            lines = [f"[Cache] {len(items)} variable(s):"]
            for name, dtype in items.items():
                lines.append(f"  • {name}: {dtype}")
            info = "\n".join(lines)
        
        print(info)
        return (info,)


class ClearCacheNode:
    """Limpia todo el caché."""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "confirm": ("BOOLEAN", {"default": False}),
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("status",)
    OUTPUT_NODE = True
    FUNCTION = "clear_cache"
    CATEGORY = "utils"

    def clear_cache(self, confirm=False):
        cache = get_cache()
        
        if confirm:
            count = len(cache.list_names())
            cache.clear()
            status = f"[Cache] ✓ Cleared {count} variable(s)"
        else:
            status = "[Cache] Skipped (confirm=False)"
        
        print(status)
        return (status,)
