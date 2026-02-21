"""
grok_text_node.py — Nodo de Visión y Razonamiento Multimodal
=============================================================
Nodos incluidos:
  - GrokTextNode           (v1 — legado, mantiene retrocompatibilidad)
  - Grok_Multimodal_Vision (v2 — analista visual con hasta 5 imágenes + video)

Autor: Prompt Models Studio — xAI Integration Layer v2.0
"""

import logging
import torch
from typing import Optional

from .grok_core import (
    PayloadRouter,
    build_multimodal_message,
    sample_video_frames,
    DEFAULT_CHAT_MODEL,
)

log = logging.getLogger("ComfyUI_Grok")

# Modelos disponibles para el widget de selección
CHAT_MODELS = [
    "grok-4",
    "grok-4-mini",
    "grok-3",
    "grok-3-mini",
    "grok-beta",
]


# ══════════════════════════════════════════════
# V1 — NODO LEGADO (No modificar su clase ni registro)
# Mantiene compatibilidad con workflows .json existentes
# ══════════════════════════════════════════════

class GrokTextNode:
    """
    [LEGADO v1.0] Nodo de texto simple para Grok.
    Mantenido para retrocompatibilidad — no usar en workflows nuevos.
    """

    CATEGORY  = "Grok/Legado"
    FUNCTION  = "run"
    RETURN_TYPES  = ("STRING",)
    RETURN_NAMES  = ("response",)

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "api_key":    ("STRING",  {"default": "", "multiline": False}),
                "prompt":     ("STRING",  {"default": "Hola Grok", "multiline": True}),
                "model":      (CHAT_MODELS, {"default": "grok-4"}),
                "temperature":("FLOAT",   {"default": 0.7, "min": 0.0, "max": 2.0, "step": 0.05}),
                "max_tokens": ("INT",     {"default": 1024, "min": 64, "max": 8192, "step": 64}),
            }
        }

    def run(self, api_key, prompt, model, temperature, max_tokens):
        try:
            router = PayloadRouter(api_key)
            messages = [{"role": "user", "content": prompt}]
            response = router.chat(
                messages=messages,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens
            )
            return (response,)
        except Exception as e:
            error_msg = f"[GrokTextNode ERROR] {e}"
            log.error(error_msg)
            return (error_msg,)


# ══════════════════════════════════════════════
# V2 — GROK MULTIMODAL VISION
# Analista visual avanzado con soporte de imágenes + video frames
# ══════════════════════════════════════════════

class Grok_Multimodal_Vision:
    """
    [v2.0] Nodo de visión multimodal.

    Entradas:
      - Texto / prompt obligatorio
      - Hasta 5 pines de imagen tipo IMAGE (todos opcionales)
      - Pin de video (tensor [B, H, W, C] con múltiples frames)
      - Controles de modelo, temperatura, tokens y nivel de detalle

    Salidas:
      - STRING con el análisis o descripción generado por Grok-4
    """

    CATEGORY     = "Grok/Visión"
    FUNCTION     = "analyze"
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("análisis",)

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "api_key":      ("STRING",   {"default": "", "multiline": False}),
                "prompt":       ("STRING",   {"default": "Describe y analiza estas imágenes en detalle.", "multiline": True}),
                "model":        (CHAT_MODELS, {"default": "grok-4"}),
                "temperature":  ("FLOAT",    {"default": 0.4, "min": 0.0, "max": 2.0, "step": 0.05}),
                "max_tokens":   ("INT",      {"default": 2048, "min": 64, "max": 16384, "step": 64}),
                "image_detail": (["high", "low", "auto"], {"default": "high"}),
                "system_prompt":("STRING",   {
                    "default": "Eres un analista visual experto. Responde en el idioma del prompt del usuario.",
                    "multiline": True
                }),
            },
            "optional": {
                # 5 pines de imagen independientes
                "image_1":      ("IMAGE",),
                "image_2":      ("IMAGE",),
                "image_3":      ("IMAGE",),
                "image_4":      ("IMAGE",),
                "image_5":      ("IMAGE",),
                # Pin de video — tensor con muchos frames en el batch
                "video_frames": ("IMAGE",),
                "max_video_frames": ("INT", {"default": 8, "min": 1, "max": 24, "step": 1}),
            }
        }

    def analyze(
        self,
        api_key: str,
        prompt: str,
        model: str,
        temperature: float,
        max_tokens: int,
        image_detail: str,
        system_prompt: str,
        image_1=None,
        image_2=None,
        image_3=None,
        image_4=None,
        image_5=None,
        video_frames=None,
        max_video_frames: int = 8,
    ):
        try:
            router = PayloadRouter(api_key)

            # ── Recopilar imágenes conectadas ────────────────────────
            # Los pines de imagen envían el primer frame del batch
            image_tensors: list[torch.Tensor] = []
            for img_pin in [image_1, image_2, image_3, image_4, image_5]:
                if img_pin is not None:
                    # Extraer solo el primer frame si hay batch
                    single = img_pin[[0]] if img_pin.ndim == 4 else img_pin.unsqueeze(0)
                    image_tensors.append(single)

            # ── Procesar video frames con muestreo inteligente ───────
            if video_frames is not None and video_frames.shape[0] > 0:
                total_frames = video_frames.shape[0]
                log.info(f"[Grok Vision] Video detectado: {total_frames} frames. "
                         f"Muestreando hasta {max_video_frames}...")

                sampled = sample_video_frames(
                    video_frames,
                    max_frames=max_video_frames,
                    strategy="uniform"
                )
                image_tensors.extend(sampled)

                # Añadir contexto de video al prompt
                video_context = (
                    f"\n\n[CONTEXTO: Se proporcionan {len(sampled)} frames "
                    f"muestreados de un video de {total_frames} frames totales. "
                    f"Analiza la secuencia temporal y el movimiento.]"
                )
                prompt = prompt + video_context

            # ── Log informativo ──────────────────────────────────────
            total_images = len(image_tensors)
            if total_images > 0:
                log.info(f"[Grok Vision] Enviando {total_images} imagen(es) a {model}")
            else:
                log.info(f"[Grok Vision] Modo texto puro → {model}")

            # ── Construir mensaje multimodal ─────────────────────────
            user_message = build_multimodal_message(
                role="user",
                text=prompt,
                image_tensors=image_tensors if image_tensors else None,
                image_detail=image_detail
            )

            # ── Llamada a la API ─────────────────────────────────────
            response = router.chat(
                messages=[user_message],
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
                system_prompt=system_prompt
            )

            return (response,)

        except Exception as e:
            error_msg = f"[Grok_Multimodal_Vision ERROR] {e}"
            log.error(error_msg)
            return (error_msg,)
