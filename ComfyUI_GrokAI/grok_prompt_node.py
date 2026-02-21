"""
grok_prompt_node.py — Grok Prompt Architect
=============================================
Nodo para enriquecimiento automático de prompts simples usando Grok.

El Prompt Architect transforma una idea simple en un prompt detallado
y optimizado para modelos generativos de imagen/video/3D.

Autor: Prompt Models Studio — xAI Integration Layer v2.0
"""

import logging
from .grok_core import PayloadRouter, DEFAULT_CHAT_MODEL

log = logging.getLogger("ComfyUI_Grok")

CHAT_MODELS = [
    "grok-4",
    "grok-4-mini",
    "grok-3",
    "grok-beta",
]

TARGET_MODELS = [
    "imagen-general",
    "grok-2-image",
    "stable-diffusion-xl",
    "flux",
    "midjourney",
    "dall-e-3",
    "video-general",
    "3d-model",
]


class Grok_Prompt_Architect:
    """
    [v2.0] Arquitecto de Prompts — Transforma ideas simples en prompts enriquecidos.

    Entrada: Una idea simple o descripción básica
    Salida:
      - prompt_enriquecido : Prompt detallado listo para usar
      - prompt_negativo    : Negative prompt sugerido
      - tags_técnicos      : Términos técnicos y estilos extraídos
    """

    CATEGORY     = "Grok/Utilidades"
    FUNCTION     = "architect"
    RETURN_TYPES = ("STRING", "STRING", "STRING")
    RETURN_NAMES = ("prompt_enriquecido", "prompt_negativo", "tags_técnicos")

    # Plantillas de sistema por modelo destino
    SYSTEM_TEMPLATES = {
        "imagen-general": """Eres un experto en prompt engineering para modelos de imagen de IA.
Tu tarea es transformar una idea simple en un prompt detallado y profesional.

REGLAS:
1. Expande la idea con: sujeto principal, acción, entorno, iluminación, estilo artístico, cámara/lente.
2. Usa vocabulario técnico preciso: "photorealistic", "8k uhd", "cinematic lighting", etc.
3. Responde SIEMPRE en JSON con exactamente estos campos:
   {
     "prompt_enriquecido": "...",
     "prompt_negativo": "...",
     "tags_técnicos": "..."
   }
Sin texto adicional fuera del JSON.""",

        "flux": """Eres un experto en prompts para FLUX. FLUX responde mejor a descripciones
en lenguaje natural fluido, sin listas de tags separados por comas.

REGLAS:
1. Escribe descripciones en prosa natural y detallada.
2. Incluye descripción de: sujeto, atmósfera, iluminación, composición, paleta de colores.
3. Responde SIEMPRE en JSON:
   {
     "prompt_enriquecido": "...",
     "prompt_negativo": "...",
     "tags_técnicos": "..."
   }""",

        "midjourney": """Eres un experto en prompts para Midjourney v6.
Midjourney responde bien a estilos artísticos, referencias visuales y parámetros --v6.

REGLAS:
1. Incluye estilo artístico, referencias de artistas si aplica, parámetros Midjourney al final.
2. Formato de Midjourney: descripción :: estilo :: --v 6 --ar 16:9 --q 2
3. Responde SIEMPRE en JSON:
   {
     "prompt_enriquecido": "...",
     "prompt_negativo": "N/A (Midjourney no usa negative prompts en el mismo campo)",
     "tags_técnicos": "..."
   }""",

        "video-general": """Eres un experto en prompt engineering para modelos de video de IA.
Los prompts de video necesitan describir: movimiento de cámara, acción temporal, duración implícita.

REGLAS:
1. Incluye siempre: tipo de plano (close-up, wide shot), movimiento de cámara, acción que evoluciona.
2. Describe el arco temporal: inicio → desarrollo → final de la escena.
3. Responde SIEMPRE en JSON:
   {
     "prompt_enriquecido": "...",
     "prompt_negativo": "...",
     "tags_técnicos": "..."
   }""",
    }

    DEFAULT_SYSTEM = SYSTEM_TEMPLATES["imagen-general"]

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "api_key":      ("STRING",       {"default": "", "multiline": False}),
                "idea_simple":  ("STRING",       {
                    "default": "un guerrero en el desierto al atardecer",
                    "multiline": True
                }),
                "modelo_destino": (TARGET_MODELS, {"default": "imagen-general"}),
                "grok_model":   (CHAT_MODELS,    {"default": "grok-4-mini"}),
                "idioma_salida":(["english", "español", "french", "japanese"], {"default": "english"}),
                "creatividad":  ("FLOAT",        {
                    "default": 0.7,
                    "min": 0.1,
                    "max": 1.5,
                    "step": 0.05,
                    "display": "slider"
                }),
            },
            "optional": {
                "contexto_adicional": ("STRING", {
                    "default": "",
                    "multiline": True,
                    "placeholder": "Ej: Para una portada de álbum de música electrónica oscura..."
                }),
                "estilo_referencia":  ("STRING", {
                    "default": "",
                    "placeholder": "Ej: en el estilo de Blade Runner, fotografía de Annie Leibovitz..."
                }),
            }
        }

    def architect(
        self,
        api_key: str,
        idea_simple: str,
        modelo_destino: str,
        grok_model: str,
        idioma_salida: str,
        creatividad: float,
        contexto_adicional: str = "",
        estilo_referencia: str = "",
    ):
        error_fallback = ("Error al generar prompt", "low quality, blurry", "")

        try:
            router = PayloadRouter(api_key)

            # ── Seleccionar plantilla de sistema ─────────────────────
            system_prompt = self.SYSTEM_TEMPLATES.get(
                modelo_destino, self.DEFAULT_SYSTEM
            )

            # ── Construir mensaje del usuario ─────────────────────────
            user_parts = [f"Idea simple: {idea_simple}"]
            if contexto_adicional.strip():
                user_parts.append(f"Contexto adicional: {contexto_adicional}")
            if estilo_referencia.strip():
                user_parts.append(f"Estilo de referencia: {estilo_referencia}")
            user_parts.append(f"Idioma de salida requerido: {idioma_salida}")

            user_message = "\n\n".join(user_parts)

            # ── Llamada a Grok ────────────────────────────────────────
            raw_response = router.chat(
                messages=[{"role": "user", "content": user_message}],
                model=grok_model,
                temperature=creatividad,
                max_tokens=1024,
                system_prompt=system_prompt
            )

            # ── Parsear JSON de la respuesta ─────────────────────────
            return self._parse_json_response(raw_response)

        except Exception as e:
            error_msg = f"[Grok_Prompt_Architect ERROR] {e}"
            log.error(error_msg)
            return (error_msg, "low quality, blurry, error", "")

    def _parse_json_response(self, raw: str) -> tuple[str, str, str]:
        """
        Extrae los campos del JSON de respuesta de Grok.
        Si el JSON falla, devuelve el texto raw como prompt enriquecido.
        """
        import json, re

        # Intentar extraer JSON incluso si hay texto extra
        json_match = re.search(r'\{[^{}]*"prompt_enriquecido"[^{}]*\}', raw, re.DOTALL)

        if json_match:
            try:
                data = json.loads(json_match.group())
                return (
                    data.get("prompt_enriquecido", raw),
                    data.get("prompt_negativo", "low quality, blurry, distorted"),
                    data.get("tags_técnicos", "")
                )
            except json.JSONDecodeError:
                pass

        # Fallback: devolver respuesta cruda como prompt
        log.warning("[Grok Prompt Architect] No se pudo parsear JSON. Devolviendo respuesta raw.")
        return (raw, "low quality, blurry, distorted", "")
