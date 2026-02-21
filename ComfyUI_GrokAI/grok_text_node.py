"""
grok_text_node.py - Nodos de Texto, Visión y JSON para ComfyUI
================================================================
Suite 1: Grok_Text_Advanced, Grok_Vision_Analyzer, Grok_JSON_Formatter

Autor: Prompt Models Studio | cdanielp
"""

import json
import logging
from .grok_core import GrokCore, TEXT_MODELS, SYSTEM_PROMPT_JSON_FORMATTER

logger = logging.getLogger("ComfyUI_GrokAI")


class Grok_Text_Advanced:
    """
    Generación de texto con control de razonamiento.
    reasoning_effort: Off (no envía el parámetro), Low, High.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "prompt": ("STRING", {
                    "multiline": True,
                    "default": "Explica la teoría de la relatividad en 3 párrafos.",
                }),
                "model": (TEXT_MODELS, {"default": "grok-4.1-fast-reasoning"}),
                "reasoning_effort": (["Off", "Low", "High"], {
                    "default": "Off",
                    "tooltip": "Off=no envía el parámetro. Low/High activan razonamiento.",
                }),
            },
            "optional": {
                "api_key": ("STRING", {"default": ""}),
                "system_prompt": ("STRING", {
                    "multiline": True,
                    "default": "",
                    "tooltip": "Instrucción de sistema para guiar el modelo.",
                }),
                "temperature": ("FLOAT", {
                    "default": 0.7, "min": 0.0, "max": 2.0, "step": 0.05,
                }),
                "max_tokens": ("INT", {
                    "default": 4096, "min": 64, "max": 131072, "step": 64,
                }),
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("text",)
    FUNCTION = "generate"
    CATEGORY = "Grok AI/Text"
    DESCRIPTION = "Genera texto con Grok. Soporta reasoning_effort (Off/Low/High)."

    def generate(self, prompt, model, reasoning_effort,
                 api_key="", system_prompt="", temperature=0.7, max_tokens=4096):
        try:
            key = GrokCore.resolve_api_key(api_key)
            effort = reasoning_effort if reasoning_effort != "Off" else None

            result = GrokCore.chat_text(
                api_key=key,
                prompt=prompt,
                model=model,
                system_prompt=system_prompt if system_prompt else None,
                reasoning_effort=effort,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            return (result,)

        except Exception as e:
            logger.error(f"[Grok_Text_Advanced] Error: {e}")
            return (f"❌ Error: {str(e)}",)


class Grok_Vision_Analyzer:
    """
    Describe tensores de imagen de ComfyUI con Grok Vision.
    Envía la imagen como base64 en el array content del mensaje.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE", {"tooltip": "Imagen a analizar."}),
                "prompt": ("STRING", {
                    "multiline": True,
                    "default": "Describe esta imagen en detalle.",
                }),
                "model": (TEXT_MODELS, {"default": "grok-4.1-fast-non-reasoning"}),
                "detail": (["low", "high"], {
                    "default": "high",
                    "tooltip": "Nivel de detalle del análisis visual.",
                }),
            },
            "optional": {
                "api_key": ("STRING", {"default": ""}),
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("analysis",)
    FUNCTION = "analyze"
    CATEGORY = "Grok AI/Text"
    DESCRIPTION = "Analiza imágenes con Grok Vision. Envía el tensor como base64."

    def analyze(self, image, prompt, model, detail, api_key=""):
        try:
            key = GrokCore.resolve_api_key(api_key)

            # Convertir tensor a base64
            img_b64 = GrokCore.tensor_to_base64(image, index=0)

            # Construir content multimodal
            image_content = {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/png;base64,{img_b64}",
                    "detail": detail,
                },
            }

            result = GrokCore.chat_text(
                api_key=key,
                prompt=prompt,
                model=model,
                extra_content=[image_content],
            )
            return (result,)

        except Exception as e:
            logger.error(f"[Grok_Vision_Analyzer] Error: {e}")
            return (f"❌ Error: {str(e)}",)


class Grok_JSON_Formatter:
    """
    Fuerza a Grok a devolver JSON estricto (Structured Outputs).
    Ideal para parsear prompts en formato estructurado.

    Ejemplo de json_schema:
    {"subject": "string", "style": "string", "mood": "string"}
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "prompt": ("STRING", {
                    "multiline": True,
                    "default": "Genera un prompt creativo para una pintura al óleo.",
                }),
                "json_schema": ("STRING", {
                    "multiline": True,
                    "default": '{"subject": "string", "style": "string", "mood": "string"}',
                    "tooltip": "Esquema JSON que define la estructura de la respuesta.",
                }),
            },
            "optional": {
                "api_key": ("STRING", {"default": ""}),
                "model": (TEXT_MODELS, {"default": "grok-4.1-fast-non-reasoning"}),
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("json_string",)
    FUNCTION = "format_json"
    CATEGORY = "Grok AI/Text"
    DESCRIPTION = "Fuerza respuesta en JSON estricto. Ideal para parsear prompts."

    def format_json(self, prompt, json_schema, api_key="",
                    model="grok-4.1-fast-non-reasoning"):
        try:
            key = GrokCore.resolve_api_key(api_key)

            # Validar que el schema es JSON válido
            try:
                schema = json.loads(json_schema)
            except json.JSONDecodeError:
                return (f"❌ json_schema no es JSON válido: {json_schema[:200]}",)

            # System prompt que fuerza JSON
            sys_prompt = (
                f"{SYSTEM_PROMPT_JSON_FORMATTER}\n\n"
                f"Tu respuesta DEBE seguir exactamente este esquema JSON:\n"
                f"{json.dumps(schema, indent=2)}"
            )

            # Intentar con response_format json_object
            messages = [
                {"role": "system", "content": sys_prompt},
                {"role": "user", "content": prompt},
            ]

            result = GrokCore.chat_completion(
                api_key=key,
                messages=messages,
                model=model,
                response_format={"type": "json_object"},
                temperature=0.3,
            )

            text = GrokCore.extract_text(result)

            # Validar que la respuesta es JSON parseable
            try:
                parsed = json.loads(text)
                # Re-serializar limpio
                return (json.dumps(parsed, indent=2, ensure_ascii=False),)
            except json.JSONDecodeError:
                # Si no es JSON puro, intentar extraer JSON del texto
                start = text.find("{")
                end = text.rfind("}") + 1
                if start >= 0 and end > start:
                    try:
                        parsed = json.loads(text[start:end])
                        return (json.dumps(parsed, indent=2, ensure_ascii=False),)
                    except json.JSONDecodeError:
                        pass
                return (f"⚠️ Respuesta no es JSON puro:\n{text}",)

        except Exception as e:
            logger.error(f"[Grok_JSON_Formatter] Error: {e}")
            return (f"❌ Error: {str(e)}",)
