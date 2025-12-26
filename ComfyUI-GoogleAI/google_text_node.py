# google_text_node.py
from .google_core import GoogleAICore

# Modelos de texto conocidos
TEXT_MODELS = [
    "gemini-2.5-pro-preview-06-05",
    "gemini-2.5-flash-preview-05-20",
    "gemini-2.0-flash",
    "gemini-2.0-flash-lite",
    "gemini-1.5-pro",
    "gemini-1.5-flash",
    "gemini-1.5-flash-8b",
]

class GoogleAI_TextNode:
    """
    Nodo de generación de texto usando Gemini API
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "api_key": ("STRING", {"default": "", "multiline": False}),
                "model": (TEXT_MODELS, {"default": "gemini-2.5-flash-preview-05-20"}),
                "prompt": ("STRING", {"default": "", "multiline": True}),
            },
            "optional": {
                "system_prompt": ("STRING", {"default": "", "multiline": True, "forceInput": True}),
                "custom_model": ("STRING", {"default": "", "multiline": False}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("text",)
    FUNCTION = "generate_text"
    CATEGORY = "GoogleAI"

    def generate_text(self, api_key, model, prompt, system_prompt="", custom_model=""):
        # Usar modelo personalizado si se proporciona
        active_model = custom_model.strip() if custom_model.strip() else model
        
        if not api_key.strip():
            return ("Error: API key is required",)
        
        if not prompt.strip():
            return ("Error: Prompt is required",)
        
        client = GoogleAICore(api_key.strip(), active_model)
        result = client.generate_text(prompt, system_prompt)
        
        try:
            text = result["candidates"][0]["content"]["parts"][0]["text"]
            return (text,)
        except KeyError:
            error_msg = result.get("error", {}).get("message", str(result))
            return (f"Error: {error_msg}",)
        except Exception as e:
            return (f"Error: {str(e)} | Response: {result}",)


class GoogleAI_TextNode_Simple:
    """
    Versión simplificada del nodo de texto (sin system prompt)
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "api_key": ("STRING", {"default": "", "multiline": False}),
                "model": (TEXT_MODELS, {"default": "gemini-2.5-flash-preview-05-20"}),
                "prompt": ("STRING", {"default": "", "multiline": True}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("text",)
    FUNCTION = "generate_text"
    CATEGORY = "GoogleAI"

    def generate_text(self, api_key, model, prompt):
        if not api_key.strip():
            return ("Error: API key is required",)
        
        if not prompt.strip():
            return ("Error: Prompt is required",)
        
        client = GoogleAICore(api_key.strip(), model)
        result = client.generate_text(prompt)
        
        try:
            text = result["candidates"][0]["content"]["parts"][0]["text"]
            return (text,)
        except KeyError:
            error_msg = result.get("error", {}).get("message", str(result))
            return (f"Error: {error_msg}",)
        except Exception as e:
            return (f"Error: {str(e)} | Response: {result}",)


NODE_CLASS_MAPPINGS = {
    "GoogleAI_TextNode": GoogleAI_TextNode,
    "GoogleAI_TextNode_Simple": GoogleAI_TextNode_Simple,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "GoogleAI_TextNode": "🧠 Google AI Text Generator",
    "GoogleAI_TextNode_Simple": "🧠 Google AI Text (Simple)",
}
