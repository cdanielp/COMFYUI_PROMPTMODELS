# ==============================================================================
# grok_prompt_node.py - Grok Prompt Architect
# ==============================================================================
# Utiliza razonamiento de xAI para expandir ideas simples en prompts
# profesionales. Fuerza JSON estructurado para separar positivo/negativo.
# ==============================================================================

import os
import json
import logging
from .grok_core import GrokCore, TEXT_MODELS

log = logging.getLogger("ComfyUI_GrokPrompt")

STYLES = [
    "Photorealistic / RAW",
    "Cinematic / Movie Still",
    "Anime / Manga",
    "Digital Illustration",
    "3D Render / Unreal Engine",
    "Concept Art",
    "Cyberpunk / Neon",
    "Fantasy / Magic",
]

COMPLEXITY_LEVELS = [
    "Detailed (Standard)",
    "Masterpiece (Highly Complex)",
    "Simple (Core Subject Only)",
]


class Grok_Prompt_Architect:
    """Agente experto en creacion de prompts con JSON estructurado."""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "idea_base": ("STRING", {"multiline": True, "default": "A futuristic city with flying cars"}),
                "model": (TEXT_MODELS, {"default": "grok-4-1-fast-non-reasoning"}),
                "style_target": (STYLES, {"default": "Cinematic / Movie Still"}),
                "complexity": (COMPLEXITY_LEVELS, {"default": "Masterpiece (Highly Complex)"}),
                "api_key": ("STRING", {"multiline": False, "default": ""}),
            },
        }

    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("positive_prompt", "negative_prompt")
    FUNCTION = "build_prompt"
    CATEGORY = "xAI/Grok"

    def build_prompt(self, idea_base, model, style_target, complexity, api_key):
        key = api_key.strip() or os.getenv("XAI_API_KEY", "")
        if not key:
            err = "Error: API Key de xAI requerida."
            return (err, err)

        try:
            core = GrokCore(key)

            system_prompt = (
                "You are an elite AI Prompt Engineer for image generation models "
                "like Stable Diffusion, Midjourney, and Flux. "
                "Your job is to take a simple user idea and expand it into a "
                "highly effective, comma-separated prompt. "
                "You must ONLY reply with a valid JSON object containing exactly "
                "two keys: 'positive' and 'negative'. "
                "Do not include markdown blocks or any other text outside the JSON."
            )

            user_prompt = (
                f"Create a prompt based on these parameters:\n"
                f"- Base Idea: {idea_base}\n"
                f"- Target Style: {style_target}\n"
                f"- Complexity Level: {complexity}\n\n"
                f"The 'positive' prompt should describe the subject, lighting, "
                f"camera angle, and style.\n"
                f"The 'negative' prompt should list things to avoid "
                f"(e.g., ugly, deformed, low quality, bad anatomy)."
            )

            log.info(f"[Grok_Prompt_Architect] Disenando prompt para: '{idea_base[:30]}...'")

            res = core.chat_completion(
                model=model,
                prompt=user_prompt,
                system_prompt=system_prompt,
                temperature=0.7,
                response_format={"type": "json_object"},
            )

            if res.get("error"):
                log.error(f"[Grok_Prompt_Architect] API Error: {res.get('message')}")
                return (f"API Error: {res.get('message')}", "Error")

            content = res["choices"][0]["message"]["content"]

            # Robust JSON parsing
            try:
                if isinstance(content, str):
                    clean = content.strip()
                    # Strip markdown code blocks if present
                    if clean.startswith("```json"):
                        clean = clean[7:]
                        if clean.endswith("```"):
                            clean = clean[:-3]
                        clean = clean.strip()
                    elif clean.startswith("```"):
                        clean = clean[3:]
                        if clean.endswith("```"):
                            clean = clean[:-3]
                        clean = clean.strip()
                    prompt_data = json.loads(clean)
                elif isinstance(content, dict):
                    prompt_data = content
                else:
                    prompt_data = json.loads(str(content))

                positive = prompt_data.get("positive", idea_base)
                negative = prompt_data.get("negative", "ugly, bad quality, blurry")

                log.info("[Grok_Prompt_Architect] Prompts generados exitosamente.")
                return (positive, negative)

            except (json.JSONDecodeError, TypeError, AttributeError) as e:
                log.error(f"[Grok_Prompt_Architect] Error parseando JSON: {e}")
                fallback = content if isinstance(content, str) else str(content)
                return (fallback.strip(), "low quality, blurry, deformed")

        except Exception as e:
            err_msg = f"Error interno del nodo: {str(e)}"
            log.error(err_msg)
            return (err_msg, "Error")
