"""
google_core.py - Motor Central de la API de Google AI (V2.5.0)
==============================================================
Maneja TODAS las comunicaciones HTTP con la API REST de Google.
Regla de Oro: CERO SDKs externos. Solo requests/aiohttp puras.

Cambios V2.5.0:
- Nano Banana 2 (gemini-3.1-flash-image-preview) agregado
- ThinkingConfig: thinkingLevel (Gemini 3+) vs thinkingBudget (Gemini 2.5)
- responseModalities: ["TEXT", "IMAGE"] para mayor robustez
- MIME detection: JPEG + WEBP + PNG
- call_with_backoff: HTTP 500 ahora retryable
- 14 aspect ratios oficiales + 5 imageSize valores
- Validación de resolución por modelo

Cambios V2.4.3:
- FIX CRÍTICO: video_bytes_to_tensor() transcodifica a H.264
- FIX AUDIO: video_bytes_to_audio() reescrito con ffmpeg directo

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
import subprocess
import shutil
from typing import Optional, Dict, Any, List, Tuple

import torch
import numpy as np
from PIL import Image, ImageDraw, ImageFont

logger = logging.getLogger("ComfyUI_GoogleAI")

# ============================================================================
# CONSTANTES DE LA API
# ============================================================================
GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta"

GEMINI_TEXT_ENDPOINT     = "{base}/models/{model}:generateContent?key={key}"
IMAGEN_GENERATE_ENDPOINT = "{base}/models/{model}:generateImages?key={key}"
VEO_GENERATE_ENDPOINT    = "{base}/models/{model}:predictLongRunning?key={key}"
VEO_POLL_ENDPOINT        = "{base}/{operation_name}?key={key}"

# Modelos por defecto — strings exactos de la API (Mar 2026)
DEFAULT_TEXT_MODEL  = "gemini-3.1-pro-preview"
DEFAULT_IMAGE_MODEL = "imagen-4.0-generate-001"
DEFAULT_VIDEO_MODEL = "veo-3.1-generate-preview"

# Familias de modelos para routing interno
GEMINI_IMAGE_MODELS = (
    "gemini-3.1-flash-image-preview",  # Nano Banana 2 (Feb 26, 2026)
    "gemini-3-pro-image-preview",      # Nano Banana Pro
    "gemini-2.5-flash-image",          # Nano Banana (original)
)
IMAGEN_MODELS = ("imagen-4.0", "imagen-3.0")

# ============================================================================
# ASPECT RATIOS Y RESOLUCIONES — API Feb 2026
# ============================================================================
# 14 aspect ratios oficiales para Nano Banana (generateContent)
NB_ASPECT_RATIOS = [
    "1:1", "1:4", "1:8", "2:3", "3:2", "3:4", "4:1",
    "4:3", "4:5", "5:4", "8:1", "9:16", "16:9", "21:9",
]

# imageSize values para Nano Banana
NB_IMAGE_SIZES = ["512px", "0.5K", "1K", "2K", "4K"]

# Aspect ratios para Imagen 4 (generateImages — subset limitado)
IMAGEN_ASPECT_RATIOS = ["1:1", "16:9", "9:16", "4:3", "3:4"]

# Resolución máxima por modelo Nano Banana
NB_MAX_RESOLUTION = {
    "gemini-3.1-flash-image-preview": "4K",   # NB2 — también soporta 0.5K
    "gemini-3-pro-image-preview":     "4K",   # NB Pro
    "gemini-2.5-flash-image":         "1K",   # NB original — solo hasta 1K
}

# Modelos que soportan 0.5K (exclusivo NB2)
NB_SUPPORTS_HALF_K = {"gemini-3.1-flash-image-preview"}

# Jerarquía de resoluciones para downgrade automático
_RESOLUTION_ORDER = ["512px", "0.5K", "1K", "2K", "4K"]

# ============================================================================
# THINKING CONFIG — Gemini 3+ vs Gemini 2.5
# ============================================================================
# Gemini 3.1 Pro / Gemini 3 Flash: thinkingLevel (string)
# Gemini 2.5 Pro / Flash: thinkingBudget (numérico)
THINKING_LEVEL_MAP = {
    "Low":    "low",
    "Medium": "medium",
    "High":   "high",
}

THINKING_BUDGET_MAP = {
    "Low":    1024,
    "Medium": 4096,
    "High":   8192,
}


def _build_thinking_config(model: str, thinking_budget: str) -> Optional[Dict]:
    """
    Construye thinkingConfig correcto según familia del modelo.
    Gemini 3+  → thinkingLevel (string: low/medium/high)
    Gemini 2.5 → thinkingBudget (numérico: 1024/4096/8192)
    """
    if not thinking_budget or thinking_budget == "Off":
        return None

    # Gemini 3.x usa thinkingLevel
    if model.startswith("gemini-3"):
        level = THINKING_LEVEL_MAP.get(thinking_budget, "low")
        return {"thinkingLevel": level}

    # Gemini 2.5 usa thinkingBudget
    if model.startswith("gemini-2.5"):
        budget = THINKING_BUDGET_MAP.get(thinking_budget, 1024)
        return {"thinkingBudget": budget}

    # Otros modelos: no soportan thinking
    logger.warning(f"[ThinkingConfig] Modelo '{model}' no soporta thinking. Ignorando.")
    return None


def _validate_image_size(model: str, image_size: str) -> str:
    """
    Valida y ajusta imageSize según capacidades del modelo.
    Retorna imageSize válido (con posible downgrade).
    """
    max_res = NB_MAX_RESOLUTION.get(model, "2K")
    max_idx = _RESOLUTION_ORDER.index(max_res) if max_res in _RESOLUTION_ORDER else 3

    # 0.5K solo NB2
    if image_size == "0.5K" and model not in NB_SUPPORTS_HALF_K:
        logger.warning(
            f"[ImageSize] 0.5K no soportado por '{model}' → usando 1K. "
            f"Solo gemini-3.1-flash-image-preview soporta 0.5K."
        )
        return "1K"

    req_idx = _RESOLUTION_ORDER.index(image_size) if image_size in _RESOLUTION_ORDER else 3

    if req_idx > max_idx:
        downgraded = _RESOLUTION_ORDER[max_idx]
        logger.warning(
            f"[ImageSize] {image_size} no soportado por '{model}' (max: {max_res}) "
            f"→ downgrade a {downgraded}."
        )
        return downgraded

    return image_size


# ============================================================================
# MIME DETECTION
# ============================================================================
def _detect_mime_from_b64(b64_data: str) -> str:
    """Detecta MIME type real desde los primeros bytes del base64."""
    if b64_data.startswith("/9j/"):
        return "image/jpeg"
    if b64_data.startswith("UklGR"):
        return "image/webp"
    if b64_data.startswith("iVBOR"):
        return "image/png"
    return "image/png"  # fallback seguro


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
VEO_RESOLUTION_PRESETS = {
    "1920x1080 (16:9)":    ("1080p", "16:9"),
    "1080x1920 (9:16)":    ("1080p", "9:16"),
    "1080x1080 (1:1)":     ("1080p", "1:1"),
    "3840x2160 (16:9 4K)": ("4k",    "16:9"),
    "2160x3840 (9:16 4K)": ("4k",    "9:16"),
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


# ============================================================================
# UTILIDAD — Transcodificación segura a H.264
# ============================================================================
def _transcode_to_h264(input_path: str) -> Optional[str]:
    """
    Transcodifica cualquier MP4 a H.264/yuv420p usando ffmpeg.
    Retorna la ruta del archivo transcodificado, o None si ffmpeg
    no está disponible (permite fallback a decodificación directa).
    """
    if not shutil.which("ffmpeg"):
        logger.warning(
            "⚠️ [Transcode] ffmpeg no encontrado en PATH. "
            "Se intentará decodificar directamente (puede fallar con HEVC/VP9). "
            "Para mejor compatibilidad instala ffmpeg:\n"
            "  apt install ffmpeg  (Linux/Docker)\n"
            "  brew install ffmpeg (macOS)\n"
            "  choco install ffmpeg (Windows)"
        )
        return None

    h264_path = input_path.replace(".mp4", "_h264.mp4")

    try:
        probe = subprocess.run(
            [
                "ffprobe", "-v", "error",
                "-select_streams", "v:0",
                "-show_entries", "stream=codec_name,width,height,pix_fmt",
                "-of", "json",
                input_path,
            ],
            capture_output=True, text=True, timeout=10,
        )
        if probe.returncode == 0:
            probe_data = json.loads(probe.stdout)
            streams = probe_data.get("streams", [{}])
            if streams:
                codec = streams[0].get("codec_name", "desconocido")
                pix_fmt = streams[0].get("pix_fmt", "desconocido")
                w = streams[0].get("width", "?")
                h = streams[0].get("height", "?")
                logger.info(
                    f"[Transcode] Códec original: {codec} | "
                    f"pix_fmt: {pix_fmt} | {w}x{h}"
                )
                if codec == "h264" and pix_fmt in ("yuv420p", "yuvj420p"):
                    logger.info("[Transcode] Ya es H.264/yuv420p → skip transcodificación")
                    return input_path
    except Exception as e:
        logger.warning(f"[Transcode] ffprobe falló (no crítico): {e}")

    result = subprocess.run(
        [
            "ffmpeg", "-y",
            "-i", input_path,
            "-c:v", "libx264",
            "-preset", "fast",
            "-crf", "18",
            "-pix_fmt", "yuv420p",
            "-an",
            "-movflags", "+faststart",
            h264_path,
        ],
        capture_output=True, text=True, timeout=120,
    )

    if result.returncode != 0:
        stderr_snippet = result.stderr[-500:] if result.stderr else "sin detalle"
        raise RuntimeError(
            f"❌ ffmpeg falló al transcodificar (exit {result.returncode}):\n"
            f"{stderr_snippet}"
        )

    if not os.path.exists(h264_path):
        raise RuntimeError("ffmpeg terminó OK pero no creó archivo de salida.")

    out_size = os.path.getsize(h264_path)
    in_size = os.path.getsize(input_path)
    logger.info(
        f"[Transcode] OK → {in_size/1024:.0f}KB → {out_size/1024:.0f}KB (H.264)"
    )

    if out_size < 1024:
        raise RuntimeError(
            f"Archivo transcodificado sospechosamente pequeño ({out_size} bytes). "
            f"El video original podría estar corrupto."
        )

    return h264_path


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

        # V2.5.0: ThinkingConfig inteligente por familia de modelo
        if thinking_budget and thinking_budget != "Off":
            thinking_cfg = _build_thinking_config(model, thinking_budget)
            if thinking_cfg:
                gen_config["thinkingConfig"] = thinking_cfg

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
    # IMAGEN — Nano Banana → generateContent + responseModalities:TEXT+IMAGE
    # ========================================================================
    @staticmethod
    def generate_image_gemini(
        api_key: str,
        prompt: str,
        model: str,
        system_instruction: Optional[str] = None,
        reference_images_b64: Optional[List[str]] = None,
        aspect_ratio: str = "1:1",
        image_size: str = "2K",
        seed: int = 0,
        safety_settings: Optional[List[Dict]] = None,
        timeout: int = 300,
    ) -> Tuple[bytes, str]:
        """
        Genera imagen con Nano Banana (NB2/Pro/original).
        Endpoint: generateContent con responseModalities: ["TEXT", "IMAGE"]
        Soporta hasta 14 imágenes de referencia como inlineData.
        Seed para reproducibilidad (0 = sin fijar).

        V2.5.0:
        - responseModalities incluye TEXT para mayor robustez
        - image_size separado de aspect_ratio
        - Validación automática de resolución por modelo
        - MIME detection mejorada (JPEG/WEBP/PNG)

        Retorna tupla: (bytes_imagen_PNG, texto_descripcion)
        """
        url = GEMINI_TEXT_ENDPOINT.format(
            base=GEMINI_BASE_URL, model=model, key=api_key
        )

        # Validar imageSize para este modelo
        validated_size = _validate_image_size(model, image_size)

        # Construir parts: primero las referencias, luego el prompt
        parts = []
        if reference_images_b64:
            for img_b64 in reference_images_b64[:14]:
                mime = _detect_mime_from_b64(img_b64)
                parts.append({
                    "inlineData": {"mimeType": mime, "data": img_b64}
                })

        parts.append({"text": prompt})

        # V2.5.0: TEXT + IMAGE para mayor robustez (compatible con Vertex AI)
        gen_config: Dict[str, Any] = {
            "responseModalities": ["TEXT", "IMAGE"],
            "imageConfig": {
                "aspectRatio": aspect_ratio,
                "imageSize": validated_size,
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

            # Extraer imagen y texto de la respuesta
            image_bytes = None
            text_description = ""

            for candidate in data.get("candidates", []):
                for part in candidate.get("content", {}).get("parts", []):
                    if "inlineData" in part:
                        mime = part["inlineData"].get("mimeType", "")
                        if "image" in mime and image_bytes is None:
                            image_bytes = base64.b64decode(part["inlineData"]["data"])
                    elif "text" in part:
                        text_description += part["text"]

            if image_bytes is None:
                raise RuntimeError("La API no retornó imagen en la respuesta.")

            return (image_bytes, text_description)

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
        """Genera imágenes via Imagen 4 (generateImages). Retorna lista de bytes PNG."""
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
                    lro_error = poll_data.get("error", {})
                    if lro_error:
                        raise RuntimeError(
                            f"[Veo] Operación fallida — "
                            f"code: {lro_error.get('code', 'N/A')} | "
                            f"message: {lro_error.get('message', 'Sin detalle')}"
                        )
                    resp_data = poll_data.get("response", {})

                    logger.warning(f"[DEBUG VEO] LLAVES EN LA RESPUESTA DE GOOGLE: {list(resp_data.keys())}")

                    # 1. FORMATO PREDICT
                    predictions = resp_data.get("predictions", [])
                    if predictions:
                        first_pred = predictions[0]
                        if "bytesBase64Encoded" in first_pred:
                            logger.info("[Veo] Video extraído exitosamente desde Base64 nativo.")
                            return base64.b64decode(first_pred["bytesBase64Encoded"])
                        if "video" in first_pred and "uri" in first_pred["video"]:
                            video_uri = first_pred["video"]["uri"]
                            async with session.get(f"{video_uri}&key={api_key}", timeout=180) as vid_resp:
                                vid_resp.raise_for_status()
                                return await vid_resp.read()

                    # 2. FORMATO generateVideoResponse
                    gen_response = resp_data.get("generateVideoResponse", {})
                    samples = gen_response.get("generatedSamples", [])
                    if samples:
                        video_uri = samples[0].get("video", {}).get("uri", "")
                        if video_uri:
                            async with session.get(f"{video_uri}&key={api_key}", timeout=180) as vid_resp:
                                vid_resp.raise_for_status()
                                return await vid_resp.read()

                    # 3. FORMATO generatedVideos
                    generated = resp_data.get("generatedVideos", [])
                    if generated:
                        video_uri = generated[0].get("video", {}).get("uri", "")
                        if video_uri:
                            async with session.get(f"{video_uri}&key={api_key}", timeout=180) as vid_resp:
                                vid_resp.raise_for_status()
                                return await vid_resp.read()

                    raise RuntimeError("Operación completada pero no se encontró la ruta del video en el JSON.")

                metadata = poll_data.get("metadata", {})
                state = metadata.get("state", "PROCESSING")
                progress = metadata.get("progressPercent", 0)
                logger.info(f"[Veo] Estado: {state} | {progress}% | {elapsed:.0f}s transcurridos")

            raise RuntimeError(f"Timeout: La generación de video excedió {max_wait}s.")

    # ========================================================================
    # AUDIO — Extracción via ffmpeg directo
    # ========================================================================
    @staticmethod
    def video_bytes_to_audio(video_bytes: bytes) -> Dict:
        """
        Extrae audio del MP4 de Veo 3.1 usando ffmpeg → WAV → tensor.
        Sin dependencias extra: solo ffmpeg (sistema) + numpy/torch.
        Si ffmpeg no está o el video no tiene audio → dummy silencioso.
        """
        tmp_video = None
        tmp_wav = None
        try:
            if not shutil.which("ffmpeg"):
                logger.warning("[VideoAudio] ffmpeg no disponible → dummy silencioso.")
                return _make_dummy_audio()

            with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as f:
                f.write(video_bytes)
                tmp_video = f.name

            tmp_wav = tmp_video.replace(".mp4", "_audio.wav")

            result = subprocess.run(
                [
                    "ffmpeg", "-y", "-i", tmp_video,
                    "-vn", "-acodec", "pcm_s16le",
                    "-ar", "44100", "-ac", "2",
                    tmp_wav,
                ],
                capture_output=True, text=True, timeout=30,
            )

            if result.returncode != 0 or not os.path.exists(tmp_wav):
                logger.info("[VideoAudio] Sin pista de audio en el MP4 → dummy.")
                return _make_dummy_audio()

            wav_size = os.path.getsize(tmp_wav)
            if wav_size < 1024:
                logger.info("[VideoAudio] Audio vacío → dummy.")
                return _make_dummy_audio()

            sample_rate = 44100
            try:
                from scipy.io import wavfile
                sample_rate, data = wavfile.read(tmp_wav)
            except ImportError:
                with open(tmp_wav, "rb") as wf:
                    wf.read(44)
                    raw = wf.read()
                data = np.frombuffer(raw, dtype=np.int16).reshape(-1, 2)

            audio = data.astype(np.float32) / 32768.0

            if audio.ndim == 1:
                audio = audio[:, np.newaxis]

            if np.max(np.abs(audio)) < 1e-6:
                logger.info("[VideoAudio] Pista silenciosa → dummy.")
                return _make_dummy_audio()

            waveform = torch.from_numpy(audio.T).unsqueeze(0)

            logger.info(f"[VideoAudio] Audio OK: {waveform.shape} @ {sample_rate}Hz")
            return {"waveform": waveform, "sample_rate": sample_rate}

        except Exception as e:
            logger.warning(f"[VideoAudio] Error extrayendo audio ({e}) → dummy.")
            return _make_dummy_audio()
        finally:
            for p in [tmp_video, tmp_wav]:
                if p:
                    try:
                        os.unlink(p)
                    except OSError:
                        pass

    # ========================================================================
    # CONVERSIÓN — Tensores ComfyUI
    # ========================================================================
    @staticmethod
    def tensor_to_base64(tensor: torch.Tensor, index: int = 0) -> str:
        """Convierte tensor [B, H, W, C] a base64 PNG."""
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
    def bytes_to_image_tensor(img_bytes: bytes) -> torch.Tensor:
        """Convierte bytes de imagen a tensor [1, H, W, C] float 0.0-1.0."""
        img = Image.open(io.BytesIO(img_bytes)).convert("RGB")
        img_np = np.array(img).astype(np.float32) / 255.0
        tensor = torch.from_numpy(img_np).unsqueeze(0)
        del img_np, img
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        return tensor

    # ========================================================================
    # VIDEO → TENSOR (V2.4.3 — transcodificación H.264)
    # ========================================================================
    @staticmethod
    def video_bytes_to_tensor(video_bytes: bytes) -> torch.Tensor:
        """
        Convierte bytes MP4 a tensor [B, H, W, C] float32 0.0-1.0.
        Transcodifica automáticamente a H.264/yuv420p antes de decodificar.
        """
        tmp_path = None
        h264_path = None

        try:
            with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tmp:
                tmp.write(video_bytes)
                tmp_path = tmp.name

            logger.info(f"[Video] Archivo temporal: {tmp_path} ({len(video_bytes)/1024:.0f}KB)")

            transcode_result = _transcode_to_h264(tmp_path)

            if transcode_result is not None:
                h264_path = transcode_result
                decode_path = h264_path
            else:
                decode_path = tmp_path

            # Intento 1: TorchVision
            try:
                import torchvision.io
                frames_t, audio_t, info = torchvision.io.read_video(
                    decode_path, pts_unit="sec", output_format="TCHW"
                )
                frames_t = frames_t.permute(0, 2, 3, 1)
                if frames_t.dtype == torch.uint8:
                    frames_t = frames_t.float() / 255.0

                fmin = frames_t.min().item()
                fmax = frames_t.max().item()
                fmean = frames_t.mean().item()
                logger.info(
                    f"[Video (TorchVision)] {frames_t.shape[0]} frames, "
                    f"{frames_t.shape[2]}x{frames_t.shape[1]} | "
                    f"min={fmin:.4f} max={fmax:.4f} mean={fmean:.4f}"
                )

                if fmax < 0.01:
                    if transcode_result is None:
                        logger.error(
                            "⚠️ [Video] FRAMES NEGROS — ffmpeg no disponible."
                        )
                    else:
                        logger.error(
                            "⚠️ [Video] FRAMES NEGROS después de transcodificar."
                        )

                return frames_t

            except Exception as tv_e:
                logger.warning(f"[Video] Falló torchvision: {tv_e} → fallback OpenCV")

                import cv2
                cap = cv2.VideoCapture(decode_path)
                if not cap.isOpened():
                    raise RuntimeError(
                        f"No se pudo abrir el video con OpenCV. "
                        f"Archivo: {decode_path}, existe: {os.path.exists(decode_path)}"
                    )

                frames = []
                while True:
                    ret, frame = cap.read()
                    if not ret:
                        break
                    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB).astype(np.float32) / 255.0
                    frames.append(rgb)
                cap.release()

                if not frames:
                    raise RuntimeError("El video no contiene frames descifrables.")

                stacked = np.stack(frames, axis=0)
                tensor = torch.from_numpy(stacked)

                fmin = tensor.min().item()
                fmax = tensor.max().item()
                fmean = tensor.mean().item()
                logger.info(
                    f"[Video (OpenCV)] {tensor.shape[0]} frames, "
                    f"{tensor.shape[2]}x{tensor.shape[1]} | "
                    f"min={fmin:.4f} max={fmax:.4f} mean={fmean:.4f}"
                )

                if fmax < 0.01:
                    if transcode_result is None:
                        logger.error("⚠️ [Video] FRAMES NEGROS — ffmpeg no disponible.")
                    else:
                        logger.error("⚠️ [Video] FRAMES NEGROS después de transcodificar.")

                return tensor

        finally:
            for path in [tmp_path, h264_path]:
                if path and os.path.exists(path):
                    try:
                        os.unlink(path)
                    except OSError:
                        pass
            if torch.cuda.is_available():
                torch.cuda.empty_cache()

    # ========================================================================
    # UTILIDADES DE IMAGEN
    # ========================================================================
    @staticmethod
    def resize_tensor_to_match(
        source: torch.Tensor, target: torch.Tensor
    ) -> torch.Tensor:
        target_h, target_w = target.shape[1], target.shape[2]
        if source.shape[1] == target_h and source.shape[2] == target_w:
            return source
        source_perm = source.permute(0, 3, 1, 2)
        resized = torch.nn.functional.interpolate(
            source_perm, size=(target_h, target_w), mode="bilinear", align_corners=False,
        )
        return resized.permute(0, 2, 3, 1)

    @staticmethod
    def create_error_image(
        error_msg: str, width: int = 512, height: int = 512
    ) -> torch.Tensor:
        """Imagen roja 512x512 con texto de error. [1, H, W, C] float 0.0-1.0."""
        img = Image.new("RGB", (width, height), color=(180, 30, 30))
        draw = ImageDraw.Draw(img)
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)
        except (IOError, OSError):
            try:
                font = ImageFont.truetype("arial.ttf", 16)
            except (IOError, OSError):
                font = ImageFont.load_default()

        margin, max_width = 20, width - 40
        lines = ["⚠️ ERROR", "=" * 30, ""]
        current_line = ""
        for word in error_msg.split():
            test_line = f"{current_line} {word}".strip()
            try:
                bbox = draw.textbbox((0, 0), test_line, font=font)
                lw = bbox[2] - bbox[0]
            except AttributeError:
                lw = len(test_line) * 8
            if lw <= max_width:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word
        if current_line:
            lines.append(current_line)

        y = margin
        for line in lines:
            draw.text((margin, y), line, fill=(255, 255, 255), font=font)
            y += 22
            if y > height - margin:
                break

        return torch.from_numpy(
            np.array(img).astype(np.float32) / 255.0
        ).unsqueeze(0)

    # ========================================================================
    # COSTO
    # ========================================================================
    @staticmethod
    def estimate_video_cost(duration_seconds: int) -> str:
        cost = duration_seconds * VIDEO_COST_PER_SECOND
        return (
            f"💰 Costo estimado: ${cost:.2f} USD "
            f"({duration_seconds}s × ${VIDEO_COST_PER_SECOND}/s — Veo 3.1 Standard)"
        )

    @staticmethod
    def run_async_in_thread(coro) -> Any:
        """Ejecuta una coroutine en hilo aislado. Propaga excepciones al hilo principal."""
        result_container: Dict[str, Any] = {"value": None, "error": None}

        def _target():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                result_container["value"] = loop.run_until_complete(coro)
            except Exception as e:
                result_container["error"] = e
            finally:
                loop.close()
                asyncio.set_event_loop(None)

        t = threading.Thread(target=_target, daemon=True)
        t.start()
        t.join()

        if result_container["error"] is not None:
            raise result_container["error"]
        return result_container["value"]

    @staticmethod
    def compress_image_for_api(tensor: torch.Tensor, index: int = 0, max_bytes: int = 2_000_000) -> str:
        """
        Convierte tensor IMAGE [B,H,W,C] a base64 puro sin prefijo data:URI.
        Si el PNG supera max_bytes, recomprime a WEBP calidad 80.
        """
        img_np = (tensor[index].cpu().numpy() * 255).clip(0, 255).astype(np.uint8)
        img = Image.fromarray(img_np, "RGB")

        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        png_size = buffer.tell()

        if png_size <= max_bytes:
            return base64.b64encode(buffer.getvalue()).decode("utf-8")

        # PNG demasiado grande → recomprimir a WEBP
        buffer = io.BytesIO()
        img.save(buffer, format="WEBP", quality=80)
        logger.info(
            f"[compress_image_for_api] PNG era {png_size/1024:.0f}KB → "
            f"WEBP: {buffer.tell()/1024:.0f}KB"
        )
        del img_np, img
        return base64.b64encode(buffer.getvalue()).decode("utf-8")

    @staticmethod
    def call_with_backoff(fn, *args, max_retries: int = 5, **kwargs) -> Any:
        """
        Envuelve cualquier callable con exponential backoff con jitter.
        V2.5.0: Ahora reintenta en 429, 500 y 503 (500 = transiente en Google AI).
        """
        import random as _random
        for attempt in range(max_retries):
            try:
                return fn(*args, **kwargs)
            except (RuntimeError, requests.exceptions.HTTPError) as e:
                retryable = False
                status_label = "???"

                if isinstance(e, requests.exceptions.HTTPError):
                    code = e.response.status_code if e.response else 0
                    if code in (429, 500, 503):
                        retryable = True
                        status_label = str(code)
                elif isinstance(e, RuntimeError):
                    msg = str(e)
                    if "429" in msg or "500" in msg or "503" in msg:
                        retryable = True
                        status_label = "429" if "429" in msg else ("500" if "500" in msg else "503")

                if retryable:
                    delay = min(1.0 * (2 ** attempt) + _random.random(), 60.0)
                    logger.warning(
                        f"[call_with_backoff] Error {status_label} — "
                        f"intento {attempt + 1}/{max_retries}. "
                        f"Reintentando en {delay:.1f}s..."
                    )
                    time.sleep(delay)
                else:
                    raise
        raise RuntimeError(
            f"[call_with_backoff] Se agotaron {max_retries} intentos por errores transitorios (429/500/503)."
        )
