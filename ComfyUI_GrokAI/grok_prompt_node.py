# ==============================================================================
# grok_prompt_node.py — Grok Prompt Architect (Agente de Ingeniería de Prompts)
# ==============================================================================
# Utiliza el razonamiento de xAI para expandir ideas simples en prompts
# profesionales. Fuerza a la API a responder en formato JSON estructurado
# para separar el prompt positivo del negativo perfectamente.
# ==============================================================================

import os
import json
import logging
from .grok_core import GrokCore

log = logging.getLogger("ComfyUI_GrokPrompt")

GROK_TEXT_MODELS = [
    "grok-4.1-fast-reasoning",
    "grok-2-1212"
]

STYLES = [
    "Photorealistic / RAW",
    "Cinematic / Movie Still",
    "Anime / Manga",
    "Digital Illustration",
    "3D Render / Unreal Engine",
    "Concept Art",
    "Cyberpunk / Neon",
    "Fantasy / Magic"
]

COMPLEXITY_LEVELS = [
    "Detailed (Standard)",
    "Masterpiece (Highly Complex)",
    "Simple (Core Subject Only)"
]

class Grok_Prompt_Architect:
    """
    Nodo V2: Agente experto en creación de prompts.
    Recibe una idea base y la expande usando el formato JSON nativo de xAI.
    """
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "idea_base": ("STRING", {"multiline": True, "default": "A futuristic city with flying cars"}),
                "model": (GROK_TEXT_MODELS, {"default": "grok-2-1212"}),
                "style_target": (STYLES, {"default": "Cinematic / Movie Still"}),
                "complexity": (COMPLEXITY_LEVELS, {"default": "Masterpiece (Highly Complex)"}),
                "api_key": ("STRING", {"multiline": False, "default": ""}),
            }
        }

    # Retorna dos textos separados: Positivo y Negativo
    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("positive_prompt", "negative_prompt")
    FUNCTION = "build_prompt"
    CATEGORY = "xAI/Grok"

    def build_prompt(self, idea_base, model, style_target, complexity, api_key):
        key = api_key.strip() or os.getenv("XAI_API_KEY", "")
        if not key:
            err = "⚠️ Error: API Key de xAI requerida."
            return (err, err)

        try:
            core = GrokCore(key)
            
            # 1. Diseñamos el System Prompt del Agente
            system_prompt = (
                "You are an elite AI Prompt Engineer for image generation models like Stable Diffusion, Midjourney, and Flux. "
                "Your job is to take a simple user idea and expand it into a highly effective, comma-separated prompt. "
                "You must ONLY reply with a valid JSON object containing exactly two keys: 'positive' and 'negative'. "
                "Do not include markdown blocks or any other text outside the JSON."
            )

            # 2. Construimos la instrucción del usuario
            user_prompt = (
                f"Create a prompt based on these parameters:\n"
                f"- Base Idea: {idea_base}\n"
                f"- Target Style: {style_target}\n"
                f"- Complexity Level: {complexity}\n\n"
                f"The 'positive' prompt should describe the subject, lighting, camera angle, and style.\n"
                f"The 'negative' prompt should list things to avoid (e.g., ugly, deformed, low quality, bad anatomy)."
            )

            log.info(f"[Grok_Prompt_Architect] Diseñando prompt para: '{idea_base[:30]}...'")

            # 3. Petición a la API forzando el formato JSON (Structured Outputs)
            res = core.chat_completion(
                model=model,
                prompt=user_prompt,
                system_prompt=system_prompt,
                temperature=0.7,
                response_format={"type": "json_object"} # 🔥 Le decimos a xAI que devuelva JSON puro
            )

            if res.get("error"):
                log.error(f"[Grok_Prompt_Architect] API Error: {res.get('message')}")
                return (f"API Error: {res.get('message')}", "Error")

            # Extraemos el contenido de la respuesta
            content = res["choices"][0]["message"]["content"]
            
            # 4. Parseamos el JSON de forma segura
            try:
                # A veces el modelo devuelve el JSON envuelto en bloques de código markdown
                if content.startswith("```json"):
                    content = content.replace("```json\n", "").replace("\n```", "")
                
                prompt_data = json.loads(content)
                positive_prompt = prompt_data.get("positive", idea_base)
                negative_prompt = prompt_data.get("negative", "ugly, bad quality, blurry")
                
                log.info("[Grok_Prompt_Architect] ✅ Prompts generados exitosamente.")
                return (positive_prompt, negative_prompt)
                
            except json.JSONDecodeError as e:
                log.error(f"[Grok_Prompt_Architect] Error parseando JSON de Grok: {e}. Contenido crudo: {content}")
                # Fallback: Si Grok se confunde y no da JSON, devolvemos todo el texto en el positivo
                return (content.strip(), "low quality, blurry, deformed")

        except Exception as e:
            err_msg = f"❌ Error interno del nodo: {str(e)}"
            log.error(err_msg)
            return (err_msg, "Error")
