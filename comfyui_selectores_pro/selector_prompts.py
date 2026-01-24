"""
Selector de Prompts
===================
Selecciona y combina múltiples prompts de texto.
"""

from typing import Dict, Any, Tuple, List

# Configuración
N_SLOTS: int = 12
CATEGORY: str = "Selectores Pro"


class SelectorDePrompts:
    """
    Selecciona y combina múltiples prompts de texto.
    - 1 prompt activo → texto simple
    - 2+ prompts activos → unidos con separador
    """
    
    @classmethod
    def INPUT_TYPES(cls) -> Dict[str, Any]:
        inputs: Dict[str, Any] = {
            "required": {
                "fallback": (["error", "p1"], {"default": "p1"}),
                "join_with": (["\\n\\n", "\\n", "|", ","], {"default": "\\n\\n"}),
                "mode": (["auto", "single_only", "join_only"], {"default": "auto"}),
            },
            "optional": {}
        }
        
        for i in range(1, N_SLOTS + 1):
            inputs["optional"][f"p{i}"] = ("STRING", {"multiline": True, "default": ""})
            inputs["required"][f"on{i}"] = ("BOOLEAN", {"default": i == 1})
        
        return inputs
    
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("text",)
    FUNCTION = "execute"
    CATEGORY = CATEGORY
    
    SEPARATORS = {
        "\\n\\n": "\n\n",
        "\\n": "\n",
        "|": " | ",
        ",": ", ",
    }
    
    def execute(self, fallback: str, join_with: str, mode: str, **kwargs) -> Tuple[str]:
        separator = self.SEPARATORS.get(join_with, "\n\n")
        active_prompts: List[Dict[str, Any]] = []
        
        for i in range(1, N_SLOTS + 1):
            if kwargs.get(f"on{i}", False):
                text = kwargs.get(f"p{i}", "") or ""
                text_stripped = text.strip()
                
                if text_stripped:
                    active_prompts.append({"index": i, "text": text_stripped})
        
        if len(active_prompts) == 0:
            if fallback == "error":
                raise ValueError("❌ Ningún prompt activo o todos están vacíos.")
            else:
                p1 = kwargs.get("p1", "") or ""
                return (p1.strip(),)
        
        if mode == "single_only" and len(active_prompts) > 1:
            slots = [str(p["index"]) for p in active_prompts]
            raise ValueError(
                f"❌ Modo single_only con {len(active_prompts)} prompts activos: {', '.join(slots)}.\n"
                f"Desactiva hasta dejar 1 o cambia el modo."
            )
        
        if len(active_prompts) == 1:
            return (active_prompts[0]["text"],)
        
        texts = [p["text"] for p in active_prompts]
        return (separator.join(texts),)
