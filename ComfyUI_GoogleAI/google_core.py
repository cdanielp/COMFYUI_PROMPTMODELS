"""
google_core.py - Motor Central de la API de Google AI (V2.4.2)
==============================================================
Maneja TODAS las comunicaciones HTTP con la API REST de Google.
Regla de Oro: CERO SDKs externos. Solo requests/aiohttp puras.

Cambios V2.4.2:
- generate_image_gemini() → nuevo método para Nano Banana Pro/Flash
  Usa generateContent con responseModalities:IMAGE (≠ Imagen 4)
  Soporta hasta 14 imágenes de referencia como inlineData

Autor: Prompt Models Studio | cdanielp
"""

import requests
import aiohttp
import asyncio
import base64
import json
import io
import os
import tempfile
import time
import threading
import logging
from typing import Optional, Dict, Any, List

import torch
import numpy as np
from PIL import Image, ImageDraw, ImageFont

logger = logging.getLogger("ComfyUI_GoogleAI")

# ============================================================================
# CONSTANTES DE LA API
# ============================================================================
GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta"

GEMINI_TEXT_ENDPOINT = "{base}/models/{model}:generateContent?key={key}"
IMAGEN_GENERATE_ENDPOINT = "{base}/models/{model}:generateImages?key={key}"
VEO_GENERATE_ENDPOINT = "{base}/models/{model}:predictLongRunning?key={key}"
VEO_POLL_ENDPOINT = "{base}/{operation_name}?key={key}"

# Modelos por defecto — strings exactos de la API (Feb 2026)
DEFAULT_TEXT_MODEL = "gemini-3.1-pro-preview"
DEFAULT_IMAGE_MODEL = "imagen-4.0-generate-001"
DEFAULT_VIDEO_MODEL = "veo-3.1-generate-preview"

# Familias de modelos para routing interno
GEMINI_IMAGE_MODELS = ("gemini-3-pro-image-preview", "gemini-2.5-flash-image")
IMAGEN_MODELS = ("imagen-4.0", "imagen-3.0")

# Costo Veo 3.1 Standard (USD/segundo)
VIDEO_COST_PER_SECOND = 0.40

# Categorías de seguridad disponibles en la API de Google AI
HARM_CATEGORIES = [
    "HARM_CATEGORY_HARASSMENT",
    "HARM_CATEGORY_HATE_SPEECH",
    "HARM_CATEGORY_SEXUALLY_EXPLICIT",
    "HARM_CATEGORY_DANGEROUS_CONTENT",
]

# Niveles de bloqueo disponibles (de menos a más restrictivo)
SAFETY_THRESHOLDS = [
    "BLOCK_ONLY_HIGH",
    "BLOCK_MEDIUM_AND_ABOVE",
    "BLOCK_LOW_AND_ABOVE",
]

# Presets resolución Veo 3.1: (resolution_api, aspect_ratio_api)
# ⚠️ Convención INVERSA a SIZE_PRESETS de imagen que usa (aspect_ratio, resolution_hint)
#    Video: (resolution_api, aspect_ratio_api)  — ej. ("1080p", "16:9")
#    Imagen: (aspect_ratio, resolution_hint)    — ej. ("16:9", "2K")
VEO_RESOLUTION_PRESETS = {
    "1920x1080 (16:9)": ("1080p", "16:9"),
    "1080x1920 (9:16)": ("1080p", "9:16"),
    "1080x1080 (1:1)": ("1080p", "1:1"),
    "3840x2160 (16:9 4K)": ("4k", "16:9"),
    "2160x3840 (9:16 4K)": ("4k", "9:16"),
}

VEO_DURATION_OPTIONS = [4, 6, 8]

# ============================================================================
# SYSTEM PROMPTS — Diagnóstico
# ============================================================================
SYSTEM_PROMPT_ARCHITECTURE_DETECTOR = (
    "Eres un experto en modelos de difusión. Analiza estos keys de un archivo "
    ".safetensors y determina la arquitectura exacta del modelo: Flux, SDXL, "
    "SD 1.5, SD 3, Pony, etc. Explica brevemente cómo lo determinaste."
)
SYSTEM_PROMPT_TRIGGER_EXTRACTOR = (
    "Formatea las siguientes tags de frecuencia de un LoRA de Stable Diffusion "
    "en una cadena limpia de trigger words separadas por comas. Ordénalas por "
    "frecuencia descendente. Solo devuelve la cadena de texto, sin explicaciones."
)
SYSTEM_PROMPT_WORKFLOW_ANALYZER = (
    "Analiza las keys 'class_type' de este JSON de ComfyUI. "
    "Enumera el repositorio exacto de GitHub para instalar cada custom node. "
    "Advierte explícitamente si hay nodos con múltiples forks conflictivos "
    "(ej. IP-Adapter)."
)
SYSTEM_PROMPT_COMPATIBILITY_CHECKER = (
    "Analiza las dimensiones de tensores de un modelo checkpoint y un LoRA. "
    "Determina si son compatibles (ej. ambos SD 1.5, ambos SDXL, etc.). "
    "Explica la compatibilidad en español simple."
)
SYSTEM_PROMPT_TRAINING_ANALYZER = (
    "Eres un experto en entrenamiento de modelos de IA. Analiza estos datos de "
    "loss de entrenamiento. Evalúa si hay señales de sobreentrenamiento (overfitting) "
    "comparando los valores de epoch y loss. Da un diagnóstico claro en español "
    "con recomendaciones concretas."
)


def _make_dummy_audio() -> Dict:
    """Silencio estéreo 1s @ 44100Hz — garantizado para Veo 2.0 o MP4 sin audio."""
    return {"waveform": torch.zeros((1, 2, 44100)), "sample_rate": 44100}


class GoogleAICore:
    """
    Motor central para todas las comunicaciones con la API de Google AI.
    - Texto/Imagen: requests síncronas
    - Video: aiohttp async (llamar desde nodos via asyncio bridge)
    """

    # ========================================================================
    # API KEY
    # ========================================================================
    @staticmethod
    def resolve_api_key(node_key: str = "") -> str:
        if node_key and node_key.strip():
            return node_key.strip()
        env_key = os.environ.get("GOOGLE_AI_API_KEY", "").strip()
        if env_key:
            return env_key
        raise ValueError(
            "❌ API Key no encontrada. Configúrala en:\n"
            "  1. El campo 'api_key' del nodo, O\n"
            "  2. Los Ajustes de ComfyUI (⚙️ > Google AI API Key), O\n"
            "  3. La variable de entorno GOOGLE_AI_API_KEY"
        )

    # ========================================================================
    # TEXTO — generateContent (síncrono)
    # ========================================================================
    @staticmethod
    def call_gemini(
        api_key: str,
        model: str,
        contents: List[Dict],
        system_instruction: Optional[str] = None,
        generation_config: Optional[Dict] = None,
        safety_settings: Optional[List[Dict]] = None,
        timeout: int = 120,
    ) -> Dict[str, Any]:
        url = GEMINI_TEXT_ENDPOINT.format(
            base=GEMINI_BASE_URL, model=model, key=api_key
        )
        payload: Dict[str, Any] = {"contents": contents}
        if system_instruction:
            payload["systemInstruction"] = {"parts": [{"text": system_instruction}]}
        if generation_config:
            payload["generationConfig"] = generation_config
        if safety_settings:
            payload["safetySettings"] = safety_settings

        def _do_request():
            response = requests.post(
                url,
                headers={"Content-Type": "application/json"},
                json=payload,
                timeout=timeout,
            )
            response.raise_for_status()
            return response.json()

        try:
            return GoogleAICore.call_with_backoff(_do_request)
        except requests.exceptions.HTTPError as e:
            status_code = e.response.status_code if e.response else "N/A"
            error_body = ""
            try:
                error_body = e.response.json().get("error", {}).get("message", "")
            except Exception:
                error_body = e.response.text[:500] if e.response else ""
            raise RuntimeError(
                f"Error HTTP {status_code} de la API de Gemini:\n{error_body}"
            ) from e
        except requests.exceptions.Timeout:
            raise RuntimeError(f"Timeout ({timeout}s) al contactar la API de Gemini.")
        except requests.exceptions.ConnectionError:
            raise RuntimeError("No se pudo conectar a la API de Gemini.")

    @staticmethod
    def call_gemini_text(
        api_key: str,
        prompt: str,
        model: str = DEFAULT_TEXT_MODEL,
        system_instruction: Optional[str] = None,
        thinking_budget: Optional[str] = None,
        extra_parts: Optional[List[Dict]] = None,
        generation_config: Optional[Dict] = None,
    ) -> str:
        parts = []
        if extra_parts:
            parts.extend(extra_parts)
        parts.append({"text": prompt})

        contents = [{"role": "user", "parts": parts}]
        gen_config = generation_config or {}

        if thinking_budget:
            budget_map = {"Low": 1024, "High": 8192}
            if thinking_budget in budget_map:
                gen_config["thinkingConfig"] = {
                    "thinkingBudget": budget_map[thinking_budget]
                }

        result = GoogleAICore.call_gemini(
            api_key=api_key,
            model=model,
            contents=contents,
            system_instruction=system_instruction,
            generation_config=gen_config if gen_config else None,
        )
        return GoogleAICore.extract_text_from_response(result)

    @staticmethod
    def extract_text_from_response(response: Dict) -> str:
        try:
            candidates = response.get("candidates", [])
            if not candidates:
                return "[Sin respuesta del modelo]"
            parts = candidates[0].get("content", {}).get("parts", [])
            text_parts = [p["text"] for p in parts if "text" in p]
            return "\n".join(text_parts) if text_parts else "[Respuesta vacía]"
        except (KeyError, IndexError, TypeError) as e:
            return f"[Error al parsear respuesta: {str(e)}]"

    # ========================================================================
    # IMAGEN — Nano Banana Pro/Flash → generateContent + responseModalities:IMAGE
    # ========================================================================
    @staticmethod
    def generate_image_gemini(
        api_key: str,
        prompt: str,
        model: str,
        system_instruction: Optional[str] = None,
        reference_images_b64: Optional[List[str]] = None,
        aspect_ratio: str = "1:1",
        resolution_hint: str = "2K",
        seed: int = 0,
        safety_settings: Optional[List[Dict]] = None,
        timeout: int = 180,
    ) -> bytes:
        """
        Genera imagen con Nano Banana Pro/Flash (modelos Gemini multimodales).
        Endpoint: generateContent con responseModalities: ["IMAGE"]
        Soporta hasta 14 imágenes de referencia como inlineData.
        Seed para reproducibilidad (0 = sin fijar).
        Retorna bytes PNG de la imagen generada.
        """
        url = GEMINI_TEXT_ENDPOINT.format(
            base=GEMINI_BASE_URL, model=model, key=api_key
        )

        # Construir parts: primero las referencias, luego el prompt
        parts = []
        if reference_images_b64:
            for img_b64 in reference_images_b64[:14]:  # Límite de 14 según documentación
                # Detectar formato real: compress_image_for_api puede retornar WEBP
                mime = "image/webp" if img_b64.startswith("UklGR") else "image/png"
                parts.append({
                    "inlineData": {"mimeType": mime, "data": img_b64}
                })

        parts.append({"text": prompt})

        # camelCase directo — REST API exige esta convención exacta
        gen_config: Dict[str, Any] = {
            "responseModalities": ["IMAGE"],
            "imageConfig": {
                "aspectRatio": aspect_ratio,
                "imageSize": resolution_hint,
            },
        }
        if seed:
            gen_config["seed"] = seed

        payload: Dict[str, Any] = {
            "contents": [{"role": "user", "parts": parts}],
            "generationConfig": gen_config,
        }

        if system_instruction:
            payload["systemInstruction"] = {"parts": [{"text": system_instruction}]}
        if safety_settings:
            payload["safetySettings"] = safety_settings

        # Validar tamaño total del payload de imágenes
        if reference_images_b64:
            total_image_bytes = sum(len(b64) * 3 // 4 for b64 in reference_images_b64)
            if total_image_bytes > 18_000_000:
                raise ValueError(
                    f"Payload de imágenes ({total_image_bytes / 1_000_000:.1f}MB) "
                    f"excede el límite de 18MB. Reduce el número o tamaño de referencias."
                )
            visual_tokens = len(reference_images_b64) * 765
            if visual_tokens > 8_000:
                logger.warning(
                    f"[generate_image_gemini] {visual_tokens} tokens visuales estimados "
                    f"({len(reference_images_b64)} imágenes × 765). "
                    f"Considera reducir el número de referencias."
                )

        def _do_request():
            response = requests.post(
                url,
                headers={"Content-Type": "application/json"},
                json=payload,
                timeout=timeout,
            )
            response.raise_for_status()
            return response.json()

        try:
            data = GoogleAICore.call_with_backoff(_do_request)

            # Extraer imagen de la respuesta
            for candidate in data.get("candidates", []):
                for part in candidate.get("content", {}).get("parts", []):
                    if "inlineData" in part:
                        mime = part["inlineData"].get("mimeType", "")
                        if "image" in mime:
                            return base64.b64decode(part["inlineData"]["data"])

            raise RuntimeError("La API no retornó imagen en la respuesta.")

        except requests.exceptions.HTTPError as e:
            status_code = e.response.status_code if e.response else "N/A"
            error_msg = ""
            try:
                error_msg = e.response.json().get("error", {}).get("message", "")
            except Exception:
                error_msg = str(e)
            raise RuntimeError(
                f"Error HTTP {status_code} en Nano Banana ({model}): {error_msg}"
            )

    # ========================================================================
    # IMAGEN — Imagen 4/3 → generateImages (síncrono)
    # ========================================================================
    @staticmethod
    def generate_image(
        api_key: str,
        prompt: str,
        model: str = DEFAULT_IMAGE_MODEL,
        negative_prompt: str = "",
        aspect_ratio: str = "1:1",
        num_images: int = 1,
        seed: int = 0,
    ) -> List[bytes]:
        """Genera imágenes via Imagen 4 (generateImages). Seed para reproducibilidad. Retorna lista de bytes PNG."""
        url = IMAGEN_GENERATE_ENDPOINT.format(
            base=GEMINI_BASE_URL, model=model, key=api_key
        )
        config: Dict[str, Any] = {
            "numberOfImages": num_images,
            "aspectRatio": aspect_ratio,
            "seed": seed,
        }
        if negative_prompt:
            config["negativePrompt"] = negative_prompt

        payload = {"prompt": prompt, "config": config}

        def _do_request():
            response = requests.post(
                url,
                headers={"Content-Type": "application/json"},
                json=payload,
                timeout=120,
            )
            response.raise_for_status()
            return response.json()

        try:
            data = GoogleAICore.call_with_backoff(_do_request)
            images = []
            for item in data.get("generatedImages", []):
                img_data = item.get("image", {}).get("imageBytes", "")
                if img_data:
                    images.append(base64.b64decode(img_data))
            return images
        except requests.exceptions.HTTPError as e:
            status_code = e.response.status_code if e.response else "N/A"
            error_msg = ""
            try:
                error_msg = e.response.json().get("error", {}).get("message", "")
            except Exception:
                error_msg = str(e)
            raise RuntimeError(f"Error HTTP {status_code} al generar imagen: {error_msg}")

    # ========================================================================
    # VIDEO — Veo 3.1 → generateVideos (ASYNC con aiohttp + polling)
    # Llamar desde nodos síncronos con _run_async() en google_video_node.py
    # ========================================================================
    @staticmethod
    async def generate_video(
        api_key: str,
        prompt: str,
        model: str = DEFAULT_VIDEO_MODEL,
        resolution_preset: str = "1920x1080 (16:9)",
        duration_seconds: int = 6,
        init_images_b64: Optional[List[str]] = None,
        last_frame_b64: Optional[str] = None,
        reference_images_b64: Optional[List[str]] = None,
    ) -> bytes:
        """Genera video con Veo 3.1 (async). Retorna bytes MP4."""
        start_url = VEO_GENERATE_ENDPOINT.format(
            base=GEMINI_BASE_URL, model=model, key=api_key
        )

        resolution, aspect_ratio = VEO_RESOLUTION_PRESETS.get(
            resolution_preset, ("1080p", "16:9")
        )

        # Timeout dinámico según resolución y duración
        RESOLUTION_MULTIPLIER = {"1080p": 1.0, "4k": 2.5}
        max_wait = 300 + int(duration_seconds * 60 * RESOLUTION_MULTIPLIER.get(resolution, 1.0))
        logger.info(f"[Veo] Timeout máximo calculado: {max_wait}s (resolución={resolution}, duración={duration_seconds}s)")

        parameters: Dict[str, Any] = {
            "resolution": resolution,
            "aspectRatio": aspect_ratio,
            "durationSeconds": duration_seconds,
        }

        if reference_images_b64:
            parameters["referenceImages"] = [
                {
                    "image": {"bytesBase64Encoded": b64, "mimeType": "image/png"},
                    "referenceType": "asset",
                }
                for b64 in reference_images_b64
            ]

        if last_frame_b64:
            parameters["lastFrame"] = {
                "bytesBase64Encoded": last_frame_b64,
                "mimeType": "image/png",
            }

        instance: Dict[str, Any] = {"prompt": prompt}
        if init_images_b64:
            instance["image"] = {
                "bytesBase64Encoded": init_images_b64[0],
                "mimeType": "image/png",
            }

        payload: Dict[str, Any] = {
            "instances": [instance],
            "parameters": parameters
        }

        headers = {"Content-Type": "application/json"}

        async with aiohttp.ClientSession() as session:
            # 1. Iniciar operación
            try:
                async with session.post(
                    start_url,
                    headers=headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=60),
                ) as resp:
                    if resp.status >= 400:
                        body = await resp.text()
                        try:
                            err_msg = json.loads(body).get("error", {}).get("message", body[:500])
                        except Exception:
                            err_msg = body[:500]
                        raise RuntimeError(f"Error HTTP {resp.status} al iniciar Veo: {err_msg}")
                    operation = await resp.json()
            except aiohttp.ClientError as e:
                raise RuntimeError(f"Error de conexión al iniciar Veo: {e}")

            operation_name = operation.get("name", "")
            if not operation_name:
                raise RuntimeError("La API no retornó un nombre de operación válido.")

            logger.info(f"[Veo] Operación iniciada: {operation_name}")

            # 2. Polling asíncrono
            poll_url = VEO_POLL_ENDPOINT.format(
                base=GEMINI_BASE_URL,
                operation_name=operation_name,
                key=api_key,
            )
            elapsed = 0.0
            poll_n = 0
            while elapsed < max_wait:
                interval = min(5.0 * (1.5 ** poll_n), 20.0)
                await asyncio.sleep(interval)
                elapsed += interval
                poll_n += 1

                try:
                    async with session.get(
                        poll_url, timeout=aiohttp.ClientTimeout(total=30)
                    ) as poll_resp:
                        if poll_resp.status >= 400:
                            body = await poll_resp.text()
                            raise RuntimeError(f"Error HTTP {poll_resp.status} en polling: {body[:300]}")
                        poll_data = await poll_resp.json()
                except aiohttp.ClientError as e:
                    logger.warning(f"[Veo] Error en polling (reintentando): {e}")
                    continue

                if poll_data.get("done", False):
                    # Verificar si la LRO terminó en estado FAILED
                    lro_error = poll_data.get("error", {})
                    if lro_error:
                        raise RuntimeError(
                            f"[Veo] Operación fallida — "
                            f"code: {lro_error.get('code', 'N/A')} | "
                            f"message: {lro_error.get('message', 'Sin detalle')}"
                        )
                    resp_data = poll_data.get("response", {})

                    # Formato: generateVideoResponse.generatedSamples
                    gen_response = resp_data.get("generateVideoResponse", {})
                    samples = gen_response.get("generatedSamples", [])
                    if samples:
                        video_uri = samples[0].get("video", {}).get("uri", "")
                        if video_uri:
                            async with session.get(
                                f"{video_uri}&key={api_key}",
                                timeout=aiohttp.ClientTimeout(total=180),
                            ) as vid_resp:
                                vid_resp.raise_for_status()
                                return await vid_resp.read()

                    # Formato alternativo: generatedVideos
                    generated = resp_data.get("generatedVideos", [])
                    if generated:
                        video_uri = generated[0].get("video", {}).get("uri", "")
                        if video_uri:
                            async with session.get(
                                f"{video_uri}&key={api_key}",
                                timeout=aiohttp.ClientTimeout(total=180),
                            ) as vid_resp:
                                vid_resp.raise_for_status()
                                return await vid_resp.read()

                    # Inline data (caso raro)
                    for cand in resp_data.get("candidates", []):
                        for part in cand.get("content", {}).get("parts", []):
                            if "inlineData" in part:
                                return base64.b64decode(part["inlineData"]["data"])

                    raise RuntimeError("Operación completada pero no se encontró video.")

                metadata = poll_data.get("metadata", {})
                state = metadata.get("state", "PROCESSING")
                progress = metadata.get("progressPercent", 0)
                logger.info(f"[Veo] Estado: {state} | {progress}% | {elapsed:.0f}s transcurridos")

            raise RuntimeError(f"Timeout: La generación de video excedió {max_wait}s.")

    # ========================================================================
    # AUDIO — Extracción de pista nativa del MP4 (Veo 3.1)
    # ========================================================================
    @staticmethod
    def video_bytes_to_audio(video_bytes: bytes)