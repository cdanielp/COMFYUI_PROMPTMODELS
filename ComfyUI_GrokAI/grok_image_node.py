"""
grok_image_node.py — Nodo Editor Maestro de Imágenes
=====================================================
Nodos incluidos:
  - GrokImageNode     (v1 — legado, mantiene retrocompatibilidad)
  - Grok_Image_Master (v2 — generación + i2i + inpainting con máscara)

Lógica de enrutamiento automático:
  1. Sin imagen base   → Generación pura desde texto
  2. Con imagen base   → Image-to-Image (strength controla fidelidad)
  3. Con imagen + mask → Inpainting (solo rellena área de la máscara)

Autor: Prompt Models Studio — xAI Integration Layer v2.0
"""

import logging
import torch
import base64
import io
import numpy as np
from PIL import Image
from typing import Optional

from .grok_core import (
    PayloadRouter,
    tensor_to_base64,
    bytes_to_tensor,
    DEFAULT_IMAGE_MODEL,
)

log = logging.getLogger("ComfyUI_Grok")

# Modelos de imagen disponibles
IMAGE_MODELS = [
    "grok-2-image",
    "grok-2-image-turbo",
    "grok-2-image-mini",
]

IMAGE_SIZES = [
    "1024x1024",
    "1280x720",
    "720x1280",
    "1920x1080",
    "512x512",
]


# ══════════════════════════════════════════════
# V1 — NODO LEGADO (Retrocompatibilidad)
# ══════════════════════════════════════════════

class GrokImageNode:
    """
    [LEGADO v1.0] Generador de imágenes simple.
    Mantenido para retrocompatibilidad con workflows antiguos.
    """

    CATEGORY     = "Grok/Legado"
    FUNCTION     = "generate"
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "api_key": ("STRING",     {"default": "", "multiline": False}),
                "prompt":  ("STRING",     {"default": "A futuristic city", "multiline": True}),
                "model":   (IMAGE_MODELS, {"default": "grok-2-image"}),
                "size":    (IMAGE_SIZES,  {"default": "1024x1024"}),
            }
        }

    def generate(self, api_key, prompt, model, size):
        try:
            router = PayloadRouter(api_key)
            tensors = router.generate_image(
                prompt=prompt,
                model=model,
                size=size,
                response_format="b64_json"
            )
            if not tensors:
                raise RuntimeError("La API no devolvió imágenes.")
            return (tensors[0],)
        except Exception as e:
            error_msg = f"[GrokImageNode ERROR] {e}"
            log.error(error_msg)
            # Devolver imagen de error en negro para no romper el flujo
            black = torch.zeros(1, 512, 512, 3)
            return (black,)


# ══════════════════════════════════════════════
# V2 — GROK IMAGE MASTER
# Generación + Image-to-Image + Inpainting
# ══════════════════════════════════════════════

class Grok_Image_Master:
    """
    [v2.0] Editor Maestro de Imágenes con tres modos automáticos.

    MODO 1 — Generación pura:
      Solo conectar `prompt`. Sin imagen base.

    MODO 2 — Image-to-Image:
      Conectar `prompt` + `reference_image`.
      `strength` controla cuánto cambia la imagen (0.1=sutil → 1.0=total).

    MODO 3 — Inpainting:
      Conectar `prompt` + `reference_image` + `mask`.
      Solo los píxeles blancos de la máscara se regeneran.

    Salidas:
      - IMAGE  : tensor [B, H, W, C] con la imagen resultante
      - STRING : descripción del modo usado y parámetros enviados
    """

    CATEGORY     = "Grok/Imagen"
    FUNCTION     = "master_edit"
    RETURN_TYPES = ("IMAGE", "STRING")
    RETURN_NAMES = ("imagen_resultado", "info_modo")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "api_key":     ("STRING",     {"default": "", "multiline": False}),
                "prompt":      ("STRING",     {"default": "A hyper-realistic scene...", "multiline": True}),
                "model":       (IMAGE_MODELS, {"default": "grok-2-image"}),
                "size":        (IMAGE_SIZES,  {"default": "1024x1024"}),
                "num_images":  ("INT",        {"default": 1, "min": 1, "max": 4, "step": 1}),
                "strength":    ("FLOAT",      {
                    "default": 0.8,
                    "min": 0.05,
                    "max": 1.0,
                    "step": 0.05,
                    "display": "slider"
                }),
                "negative_prompt": ("STRING", {
                    "default": "blurry, low quality, distorted",
                    "multiline": True
                }),
            },
            "optional": {
                "reference_image": ("IMAGE",),
                "mask":            ("MASK",),
                "image_quality":   (["JPEG_88", "JPEG_95", "PNG"], {"default": "JPEG_88"}),
            }
        }

    def master_edit(
        self,
        api_key: str,
        prompt: str,
        model: str,
        size: str,
        num_images: int,
        strength: float,
        negative_prompt: str,
        reference_image=None,
        mask=None,
        image_quality: str = "JPEG_88",
    ):
        # ── Fallback en caso de error crítico ────────────────────────
        black_img = torch.zeros(1, 512, 512, 3)

        try:
            router = PayloadRouter(api_key)

            # ── Determinar modo de operación ─────────────────────────
            has_image = reference_image is not None
            has_mask  = mask is not None and has_image

            if has_mask:
                mode = "inpainting"
            elif has_image:
                mode = "image-to-image"
            else:
                mode = "generación"

            log.info(f"[Grok Image Master] Modo: {mode.upper()} | Strength: {strength}")

            # ── Enriquecer prompt con negativo ───────────────────────
            full_prompt = prompt
            if negative_prompt.strip():
                full_prompt += f"\n\nNegative: {negative_prompt}"

            # ── Convertir imagen de referencia a Base64 ──────────────
            ref_b64 = None
            if has_image:
                fmt, quality = self._parse_quality(image_quality)
                ref_b64 = tensor_to_base64(
                    reference_image,
                    batch_index=0,
                    format=fmt,
                    quality=quality
                )

            # ── Convertir máscara a Base64 ───────────────────────────
            mask_b64 = None
            if has_mask:
                mask_b64 = self._mask_to_base64(mask, reference_image)

            # ── Llamada a la API ─────────────────────────────────────
            tensors = router.generate_image(
                prompt=full_prompt,
                model=model,
                n=num_images,
                size=size,
                response_format="b64_json",
                reference_image_b64=ref_b64,
                mask_b64=mask_b64,
                strength=strength if has_image else 1.0
            )

            if not tensors:
                raise RuntimeError("La API no devolvió imágenes.")

            # ── Combinar múltiples imágenes en un batch ──────────────
            result_tensor = torch.cat(tensors, dim=0)  # [N, H, W, C]

            info = (
                f"Modo: {mode}\n"
                f"Modelo: {model} | Tamaño: {size}\n"
                f"Imágenes generadas: {len(tensors)}\n"
                f"Strength: {strength if has_image else 'N/A (generación pura)'}\n"
                f"Inpainting: {'Sí' if has_mask else 'No'}"
            )

            return (result_tensor, info)

        except Exception as e:
            error_msg = f"[Grok_Image_Master ERROR] {e}"
            log.error(error_msg)
            return (black_img, error_msg)

    # ── Helpers privados ──────────────────────────────────────────────

    def _parse_quality(self, quality_str: str) -> tuple[str, int]:
        """Convierte el widget de calidad a parámetros PIL."""
        if quality_str == "PNG":
            return "PNG", 100
        elif quality_str == "JPEG_95":
            return "JPEG", 95
        else:  # JPEG_88 por defecto
            return "JPEG", 88

    def _mask_to_base64(
        self,
        mask: torch.Tensor,
        reference_image: torch.Tensor
    ) -> str:
        """
        Convierte un tensor de máscara MASK ComfyUI [H, W] o [B, H, W]
        a Base64 en escala de grises.

        La máscara se redimensiona para coincidir con la imagen de referencia
        en caso de que tengan diferentes resoluciones.
        """
        # Extraer máscara 2D
        if mask.ndim == 3:
            m = mask[0]   # [H, W]
        elif mask.ndim == 2:
            m = mask
        else:
            raise ValueError(f"Forma de máscara inesperada: {mask.shape}")

        # Normalizar a uint8 [0, 255]
        m_np = (m.cpu().numpy() * 255.0).clip(0, 255).astype(np.uint8)
        pil_mask = Image.fromarray(m_np, mode="L")

        # Redimensionar si la máscara no coincide con la imagen base
        ref_h, ref_w = reference_image.shape[1], reference_image.shape[2]
        if pil_mask.size != (ref_w, ref_h):
            log.warning(
                f"[Grok Image] Máscara {pil_mask.size} ≠ imagen {(ref_w, ref_h)}. "
                "Redimensionando máscara automáticamente."
            )
            pil_mask = pil_mask.resize((ref_w, ref_h), Image.NEAREST)

        buffer = io.BytesIO()
        pil_mask.save(buffer, format="PNG")
        return base64.b64encode(buffer.getvalue()).decode("utf-8")
