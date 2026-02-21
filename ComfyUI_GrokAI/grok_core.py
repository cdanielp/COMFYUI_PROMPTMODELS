"""
grok_core.py - Motor Central de la API de xAI / Grok (V1.0)
=============================================================
Maneja TODAS las comunicaciones HTTP con la API REST de xAI.
Regla de Oro: CERO SDKs. Solo requests HTTP puras.

Autor: Prompt Models Studio | cdanielp
"""

import requests
import base64
import json
import io
import os
import logging
from typing import Optional, Dict, Any, List

import torch
import numpy as np
from PIL import Image, ImageDraw, ImageFont

logger = logging.getLogger("ComfyUI_GrokAI")

# ============================================================================
# CONSTANTES DE LA API
# ============================================================================
XAI_BASE_URL = "https://api.x.ai/v1"
XAI_CHAT_ENDPOINT = f"{XAI_BASE_URL}/chat/completions"
XAI_IMAGE_GEN_ENDPOINT = f"{XAI_BASE_URL}/images/generations"
XAI_IMAGE_EDIT_ENDPOINT = f"{XAI_BASE_URL}/images/edits"

# Modelos disponibles
TEXT_MODELS = [
    "grok-4.1-fast-reasoning",
    "grok-4.1-fast-non-reasoning",
    "grok-3-mini",
    "grok-code-fast-1",
]

IMAGE_MODELS = [
    "grok-2-image-1212",
    "grok-2-image",
]

# System Prompts hardcoded
SYSTEM_PROMPT_WORKFLOW_DEBUGGER = (
    "Eres un ingeniero experto en ComfyUI y PyTorch. Analiza las keys "
    "'class_type' de este JSON de workflow. Enumera el repositorio exacto "
    "de GitHub para instalar cada custom node. Advierte sobre nodos con "
    "múltiples forks conflictivos. Da pasos de solución concretos."
)

SYSTEM_PROMPT_WORKFLOW_DEBUGGER_FUN = (
    "Eres un ingeniero experto en ComfyUI con un humor sarcástico e irónico "
    "nivel maestro. Analiza este workflow con todo el sarcasmo que puedas, "
    "pero SIEMPRE da la solución real al final. Haz observaciones graciosas "
    "sobre las decisiones del usuario, pero sé útil. Responde en español."
)

SYSTEM_PROMPT_METADATA_READER = (
    "Eres un experto en modelos de difusión. Analiza estos keys y metadata "
    "de un archivo .safetensors. Determina: 1) La arquitectura exacta "
    "(Flux, SDXL, SD 1.5, SD 3, Pony, etc.) 2) Si tiene trigger words "
    "en ss_tag_frequency, extráelas en una cadena limpia. Responde en español."
)

SYSTEM_PROMPT_JSON_FORMATTER = (
    "Eres un asistente que SOLO responde en JSON válido. No incluyas markdown, "
    "explicaciones ni texto fuera del JSON. Tu respuesta debe ser parseable "
    "directamente con json.loads()."
)


class GrokCore:
    """
    Motor central para la API de xAI (Grok).
    CERO SDKs — Solo requests HTTP puras.
    """

    # ========================================================================
    # RESOLUCIÓN DE API KEY
    # ========================================================================
    @staticmethod
    def resolve_api_key(node_key: str = "") -> str:
        """
        Busca la API Key en orden estricto:
        1. Campo api_key del nodo
        2. Variable de entorno XAI_API_KEY
        3. ValueError si no hay nada
        """
        if node_key and node_key.strip():
            return node_key.strip()

        env_key = os.environ.get("XAI_API_KEY", "").strip()
        if env_key:
            return env_key

        raise ValueError(
            "❌ API Key de xAI no encontrada. Configúrala en:\n"
            "  1. El campo 'api_key' del nodo, O\n"
            "  2. La variable de entorno XAI_API_KEY"
        )

    # ========================================================================
    # HEADERS COMUNES
    # ========================================================================
    @staticmethod
    def _headers(api_key: str) -> Dict[str, str]:
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        }

    # ========================================================================
    # CHAT COMPLETIONS (Texto + Visión)
    # ========================================================================
    @staticmethod
    def chat_completion(
        api_key: str,
        messages: List[Dict],
        model: str = "grok-4.1-fast-reasoning",
        reasoning_effort: Optional[str] = None,
        response_format: Optional[Dict] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        timeout: int = 120,
    ) -> Dict[str, Any]:
        """
        POST /v1/chat/completions
        Retorna el JSON de respuesta completo.
        """
        payload: Dict[str, Any] = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        # Reasoning effort: solo enviar si no es "Off"
        if reasoning_effort and reasoning_effort != "Off":
            payload["reasoning_effort"] = reasoning_effort.lower()

        # Structured outputs (JSON mode)
        if response_format:
            payload["response_format"] = response_format

        try:
            response = requests.post(
                XAI_CHAT_ENDPOINT,
                headers=GrokCore._headers(api_key),
                json=payload,
                timeout=timeout,
            )
            response.raise_for_status()
            return response.json()

        except requests.exceptions.HTTPError as e:
            status = e.response.status_code if e.response else "N/A"
            body = ""
            try:
                body = e.response.json().get("error", {}).get("message", "")
            except Exception:
                body = e.response.text[:500] if e.response else str(e)
            raise RuntimeError(f"Error HTTP {status} de xAI:\n{body}") from e

        except requests.exceptions.Timeout:
            raise RuntimeError(
                f"Timeout ({timeout}s) al contactar la API de xAI."
            )
        except requests.exceptions.ConnectionError:
            raise RuntimeError(
                "No se pudo conectar a la API de xAI. Verifica tu conexión."
            )

    @staticmethod
    def chat_text(
        api_key: str,
        prompt: str,
        model: str = "grok-4.1-fast-reasoning",
        system_prompt: Optional[str] = None,
        reasoning_effort: Optional[str] = None,
        extra_content: Optional[List[Dict]] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> str:
        """
        Llamada simplificada: retorna solo el texto de la respuesta.
        extra_content permite inyectar imágenes en el array content del user.
        """
        messages = []

        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        # Construir content del user
        if extra_content:
            user_content = list(extra_content)
            user_content.append({"type": "text", "text": prompt})
            messages.append({"role": "user", "content": user_content})
        else:
            messages.append({"role": "user", "content": prompt})

        result = GrokCore.chat_completion(
            api_key=api_key,
            messages=messages,
            model=model,
            reasoning_effort=reasoning_effort,
            temperature=temperature,
            max_tokens=max_tokens,
        )

        return GrokCore.extract_text(result)

    @staticmethod
    def extract_text(response: Dict) -> str:
        """Extrae el texto de la respuesta de chat completions."""
        try:
            choices = response.get("choices", [])
            if not choices:
                return "[Sin respuesta del modelo]"
            return choices[0].get("message", {}).get("content", "[Respuesta vacía]")
        except (KeyError, IndexError, TypeError) as e:
            logger.error(f"Error extrayendo texto: {e}")
            return f"[Error al parsear respuesta: {str(e)}]"

    # ========================================================================
    # GENERACIÓN DE IMAGEN
    # ========================================================================
    @staticmethod
    def generate_image(
        api_key: str,
        prompt: str,
        model: str = "grok-2-image-1212",
        n: int = 1,
        size: str = "1024x1024",
        timeout: int = 120,
    ) -> List[str]:
        """
        POST /v1/images/generations
        Retorna lista de strings base64 de las imágenes generadas.
        """
        payload = {
            "model": model,
            "prompt": prompt,
            "n": n,
            "size": size,
            "response_format": "b64_json",
        }

        try:
            response = requests.post(
                XAI_IMAGE_GEN_ENDPOINT,
                headers=GrokCore._headers(api_key),
                json=payload,
                timeout=timeout,
            )
            response.raise_for_status()
            data = response.json()

            images_b64 = []
            for item in data.get("data", []):
                b64 = item.get("b64_json", "")
                if b64:
                    images_b64.append(b64)

            return images_b64

        except requests.exceptions.HTTPError as e:
            status = e.response.status_code if e.response else "N/A"
            body = ""
            try:
                body = e.response.json().get("error", {}).get("message", "")
            except Exception:
                body = e.response.text[:500] if e.response else str(e)
            raise RuntimeError(f"Error HTTP {status} al generar imagen: {body}")

    # ========================================================================
    # EDICIÓN DE IMAGEN
    # ========================================================================
    @staticmethod
    def edit_image(
        api_key: str,
        image_b64: str,
        prompt: str,
        model: str = "grok-2-image-1212",
        n: int = 1,
        timeout: int = 120,
    ) -> List[str]:
        """
        POST /v1/images/edits
        Envía la imagen como archivo multipart.
        Retorna lista de strings base64.
        """
        image_bytes = base64.b64decode(image_b64)

        try:
            response = requests.post(
                XAI_IMAGE_EDIT_ENDPOINT,
                headers={"Authorization": f"Bearer {api_key}"},
                files={"image": ("image.png", image_bytes, "image/png")},
                data={
                    "model": model,
                    "prompt": prompt,
                    "n": str(n),
                    "response_format": "b64_json",
                },
                timeout=timeout,
            )
            response.raise_for_status()
            data = response.json()

            images_b64 = []
            for item in data.get("data", []):
                b64 = item.get("b64_json", "")
                if b64:
                    images_b64.append(b64)

            return images_b64

        except requests.exceptions.HTTPError as e:
            status = e.response.status_code if e.response else "N/A"
            body = ""
            try:
                body = e.response.json().get("error", {}).get("message", "")
            except Exception:
                body = e.response.text[:500] if e.response else str(e)
            raise RuntimeError(f"Error HTTP {status} al editar imagen: {body}")

    # ========================================================================
    # CONVERSIÓN DE TENSORES (ComfyUI ↔ Base64)
    # ========================================================================
    @staticmethod
    def tensor_to_base64(tensor: torch.Tensor, index: int = 0) -> str:
        """Convierte tensor [B, H, W, C] float 0-1 a base64 PNG."""
        if tensor.dim() == 4:
            img_tensor = tensor[index]
        elif tensor.dim() == 3:
            img_tensor = tensor
        else:
            raise ValueError(f"Tensor con forma inesperada: {tensor.shape}")

        img_np = (img_tensor.cpu().numpy() * 255).clip(0, 255).astype(np.uint8)
        img = Image.fromarray(img_np, "RGB")
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        return base64.b64encode(buffer.getvalue()).decode("utf-8")

    @staticmethod
    def base64_to_tensor(b64_string: str) -> torch.Tensor:
        """Decodifica base64 a tensor [1, H, W, C] float 0.0-1.0."""
        img_bytes = base64.b64decode(b64_string)
        img = Image.open(io.BytesIO(img_bytes)).convert("RGB")
        img_np = np.array(img).astype(np.float32) / 255.0
        return torch.from_numpy(img_np).unsqueeze(0)

    # ========================================================================
    # ANTI-CRASH: Imagen Roja de Error
    # ========================================================================
    @staticmethod
    def create_error_image(error_msg: str, width: int = 512, height: int = 512) -> torch.Tensor:
        """
        Crea tensor de imagen roja 512x512 con texto de error.
        Usado para HTTP 400 (safety/NSFW) o 429 (rate limit) sin crashear.
        Retorna [1, H, W, C] float 0.0-1.0.
        """
        img = Image.new("RGB", (width, height), color=(180, 30, 30))
        draw = ImageDraw.Draw(img)

        try:
            font = ImageFont.truetype(
                "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16
            )
        except (IOError, OSError):
            try:
                font = ImageFont.truetype("arial.ttf", 16)
            except (IOError, OSError):
                font = ImageFont.load_default()

        margin = 20
        max_w = width - (margin * 2)
        lines = ["⚠️ GROK API ERROR", "=" * 28, ""]
        current = ""

        for word in error_msg.split():
            test = f"{current} {word}".strip()
            try:
                bbox = draw.textbbox((0, 0), test, font=font)
                lw = bbox[2] - bbox[0]
            except AttributeError:
                lw = len(test) * 8
            if lw <= max_w:
                current = test
            else:
                lines.append(current)
                current = word
        if current:
            lines.append(current)

        y = margin
        for line in lines:
            draw.text((margin, y), line, fill=(255, 255, 255), font=font)
            y += 22
            if y > height - margin:
                break

        img_np = np.array(img).astype(np.float32) / 255.0
        return torch.from_numpy(img_np).unsqueeze(0)

    # ========================================================================
    # UTILIDAD: Aspect Ratio → Size string
    # ========================================================================
    @staticmethod
    def aspect_ratio_to_size(ratio: str) -> str:
        """Convierte aspect ratio a tamaño de imagen para la API."""
        mapping = {
            "1:1": "1024x1024",
            "16:9": "1344x768",
            "9:16": "768x1344",
            "4:3": "1152x896",
            "3:4": "896x1152",
        }
        return mapping.get(ratio, "1024x1024")
