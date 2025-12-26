# grok_text_node.py
"""
Nodo de generación de texto usando xAI Grok API
"""
from .grok_core import call_grok_text

# Modelos de texto disponibles - Diciembre 2025
TEXT_MODELS = [
    "grok-4",           # Más avanzado
    "grok-4.1-fast",    # Rápido
    "grok-3-mini",      # Ligero
    "grok-2",           # Estable
    "grok-2-mini",      # Económico
]


class GrokTextNode:
    """
    Nodo completo de generación de texto con Grok
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "api_key": ("STRING", {"default": "", "multiline": False}),
                "model": (TEXT_MODELS, {"default": "grok-4"}),
                "prompt": ("STRING", {"default": "", "multiline": True}),
                "system_prompt": ("STRING", {
                    "default": "You are a helpful AI assistant.",
                    "multiline": True
                }),
            },
            "optional": {
                "temperature": ("FLOAT", {
                    "default": 1.0,
                    "min": 0.0,
                    "max": 2.0,
                    "step": 0.1
                }),
                "max_tokens": ("INT", {
                    "default": 1024,
                    "min": 32,
                    "max": 8192,
                    "step": 64
                }),
                "custom_model": ("STRING", {"default": "", "multiline": False}),
            }
        }
    
    RETURN_TYPES = ("STRING", "STRING",)
    RETURN_NAMES = ("text", "status",)
    FUNCTION = "generate"
    CATEGORY = "xAI/Grok"
    
    def generate(self, api_key, model, prompt, system_prompt,
                 temperature=1.0, max_tokens=1024, custom_model=""):
        
        # Usar modelo personalizado si se proporciona
        active_model = custom_model.strip() if custom_model.strip() else model
        
        if not api_key.strip():
            return ("", "❌ Error: API key is required")
        
        if not prompt.strip():
            return ("", "❌ Error: Prompt is required")
        
        try:
            text = call_grok_text(
                model=active_model,
                prompt=prompt,
                system_prompt=system_prompt,
                api_key=api_key,
                temperature=temperature,
                max_tokens=max_tokens
            )
            return (text, f"✅ Generated with {active_model}")
        except Exception as e:
            return ("", f"❌ Error: {str(e)}")


class GrokTextNodeSimple:
    """
    Versión simplificada del nodo de texto
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "api_key": ("STRING", {"default": "", "multiline": False}),
                "model": (TEXT_MODELS, {"default": "grok-4.1-fast"}),
                "prompt": ("STRING", {"default": "", "multiline": True}),
            }
        }
    
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("text",)
    FUNCTION = "generate"
    CATEGORY = "xAI/Grok"
    
    def generate(self, api_key, model, prompt):
        if not api_key.strip():
            return ("❌ Error: API key is required",)
        
        if not prompt.strip():
            return ("❌ Error: Prompt is required",)
        
        try:
            text = call_grok_text(
                model=model,
                prompt=prompt,
                api_key=api_key
            )
            return (text,)
        except Exception as e:
            return (f"❌ Error: {str(e)}",)


NODE_CLASS_MAPPINGS = {
    "Grok_Text": GrokTextNode,
    "Grok_Text_Simple": GrokTextNodeSimple,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "Grok_Text": "🧠 Grok Text Generator",
    "Grok_Text_Simple": "🧠 Grok Text (Simple)",
}
