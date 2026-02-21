"""
google_core.py - Motor Central de la API de Google AI (V2.0)
============================================================
Maneja TODAS las comunicaciones HTTP con la API REST de Google.
Regla de Oro: CERO SDKs. Solo requests puras.

Autor: Prompt Models Studio | cdanielp
"""

import requests
import base64
import json
import io
import os
import tempfile
import time
import logging
from typing import Optional, Dict, Any, List, Tuple, Union

import torch
import numpy as np
from PIL import Image, ImageDraw, ImageFont

logger = logging.getLogger("ComfyUI_GoogleAI")

# ============================================================================
# CONSTANTES DE LA API
# ============================================================================
GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta"

# Endpoints correctos por tipo de generación
GEMINI_TEXT_ENDPOINT   = "{base}/models/{model}:generateContent?key={key}"
IMAGEN_GENERATE_ENDPOINT = "{base}/models/{model}:generateImages?key={key}"
VEO_GENERATE_ENDPOINT  = "{base}/models/{model}:generateVideos?key={key}"
VEO_POLL_ENDPOINT      = "{base}/{operation_name}?key={key}"

# Modelos por defecto (strings exactos de la API — Feb 2026)
DEFAULT_TEXT_MODEL  = "gemini-3.1-pro-preview"
DEFAULT_IMAGE_MODEL = "imagen-4.0-generate-001"
DEFAULT_VIDEO_MODEL = "veo-3.1-generate-preview"

# Costo estimado Veo 3.1 Standard (USD/segundo)
VIDEO_COST_PER_SECOND = 0.40

# Presets de resolución para Veo 3.1
# Valor: (resolution_api, aspect_ratio_api)
VEO_RESOLUTION_PRESETS = {
    "1920x1080 (16:9)":    ("1080p", "16:9"),
    "1080x1920 (9:16)":    ("1080p", "9:16"),
    "1080x1080 (1:1)":     ("1080p", "1:1"),
    "3840x2160 (16:9 4K)": ("4k",   "16:9"),
    "2160x3840 (9:16 4K)": ("4k",   "9:16"),
}

# Duraciones permitidas (segundos) — Veo 3.x soporta 4, 6 y 8s
VEO_DURATION_OPTIONS = [4, 6, 8]

# ============================================================================
# SYSTEM PROMPTS (Diagnóstico)
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


class GoogleAICore:
    """
    Motor central para todas las comunicaciones con la API de Google AI.
    Usa EXCLUSIVAMENTE requests HTTP puras. CERO SDKs.
    """

    # ========================================================================
    # RESOLUCIÓN DE API KEY
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
    # TEXTO — Gemini generateContent
    # ========================================================================
    @staticmethod
    def call_gemini(
        api_key: str,
        model: str,
        contents: List[Dict],
        system_instruction: Optional[str] = None,
        generation_config: Optional[Dict] = None,
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

        try:
            response = requests.post(
                url,
                headers={"Content-Type": "application/json"},
                json=payload,
                timeout=timeout,
            )
            response.raise_for_status()
            return response.json()

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
            raise RuntimeError(
                f"Timeout ({timeout}s) al contactar la API de Gemini. "
                "Intenta con un prompt más corto o verifica tu conexión."
            )
        except requests.exceptions.ConnectionError:
            raise RuntimeError(
                "No se pudo conectar a la API de Gemini. "
                "Verifica tu conexión a internet."
            )

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
            logger.error(f"Error extrayendo texto de respuesta: {e}")
            return f"[Error al parsear respuesta: {str(e)}]"

    # ========================================================================
    # IMAGEN — Imagen 4 / generateImages
    # ========================================================================
    @staticmethod
    def generate_image(
        api_key: str,
        prompt: str,
        model: str = DEFAULT_IMAGE_MODEL,
        negative_prompt: str = "",
        aspect_ratio: str = "1:1",
        num_images: int = 1,
    ) -> List[bytes]:
        """
        Genera imágenes usando la API de Imagen (generateImages).
        Retorna lista de bytes PNG.
        Compatible con Imagen 3 e Imagen 4.
        """
        url = IMAGEN_GENERATE_ENDPOINT.format(
            base=GEMINI_BASE_URL, model=model, key=api_key
        )

        config: Dict[str, Any] = {
            "numberOfImages": num_images,
            "aspectRatio": aspect_ratio,
        }
        if negative_prompt:
            config["negativePrompt"] = negative_prompt

        payload = {
            "prompt": prompt,
            "config": config,
        }

        try:
            response = requests.post(
                url,
                headers={"Content-Type": "application/json"},
                json=payload,
                timeout=120,
            )
            response.raise_for_status()
            data = response.json()

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
            raise RuntimeError(
                f"Error HTTP {status_code} al generar imagen: {error_msg}"
            )

    # ========================================================================
    # VIDEO — Veo 3.1 / generateVideos (API asíncrona con polling)
    # ========================================================================
    @staticmethod
    def generate_video(
        api_key: str,
        prompt: str,
        model: str = DEFAULT_VIDEO_MODEL,
        resolution_preset: str = "1920x1080 (16:9)",
        duration_seconds: int = 6,
        init_images_b64: Optional[List[str]] = None,
        last_frame_b64: Optional[str] = None,
        reference_images_b64: Optional[List[str]] = None,
        poll_interval: int = 15,
        max_wait: int = 600,
    ) -> bytes:
        """
        Genera video usando Veo 3.1 (generateVideos, API asíncrona con polling).
        Retorna bytes MP4.
        """
        start_url = VEO_GENERATE_ENDPOINT.format(
            base=GEMINI_BASE_URL, model=model, key=api_key
        )

        # Resolución y aspect ratio desde preset
        resolution, aspect_ratio = VEO_RESOLUTION_PRESETS.get(
            resolution_preset, ("1080p", "16:9")
        )

        # Config base
        video_config: Dict[str, Any] = {
            "resolution": resolution,
            "aspectRatio": aspect_ratio,
            "durationSeconds": duration_seconds,
            "numberOfVideos": 1,
        }

        # Imágenes de referencia para Storyboard
        if reference_images_b64:
            video_config["referenceImages"] = [
                {
                    "image": {"imageBytes": b64, "mimeType": "image/png"},
                    "referenceType": "asset",
                }
                for b64 in reference_images_b64
            ]

        # Last frame para interpolación
        if last_frame_b64:
            video_config["lastFrame"] = {
                "imageBytes": last_frame_b64,
                "mimeType": "image/png",
            }

        # Payload principal
        payload: Dict[str, Any] = {
            "prompt": prompt,
            "config": video_config,
        }

        # Imagen inicial (image-to-video o video extension)
        if init_images_b64:
            payload["image"] = {
                "imageBytes": init_images_b64[0],
                "mimeType": "image/png",
            }

        try:
            # 1. Iniciar operación
            response = requests.post(
                start_url,
                headers={"Content-Type": "application/json"},
                json=payload,
                timeout=60,
            )
            response.raise_for_status()
            operation = response.json()
            operation_name = operation.get("name", "")

            if not operation_name:
                raise RuntimeError("La API no retornó un nombre de operación válido.")

            logger.info(f"[Veo] Operación iniciada: {operation_name}")

            # 2. Polling hasta completar
            elapsed = 0
            while elapsed < max_wait:
                time.sleep(poll_interval)
                elapsed += poll_interval

                poll_url = VEO_POLL_ENDPOINT.format(
                    base=GEMINI_BASE_URL,
                    operation_name=operation_name,
                    key=api_key,
                )
                poll_resp = requests.get(poll_url, timeout=30)
                poll_resp.raise_for_status()
                poll_data = poll_resp.json()

                if poll_data.get("done", False):
                    resp = poll_data.get("response", {})

                    # Formato Gemini API: generateVideoResponse.generatedSamples
                    gen_response = resp.get("generateVideoResponse", {})
                    samples = gen_response.get("generatedSamples", [])
                    if samples:
                        video_uri = samples[0].get("video", {}).get("uri", "")
                        if video_uri:
                            vid_resp = requests.get(
                                f"{video_uri}&key={api_key}", timeout=180
                            )
                            vid_resp.raise_for_status()
                            return vid_resp.content

                    # Formato alternativo: generatedVideos
                    generated = resp.get("generatedVideos", [])
                    if generated:
                        video_uri = generated[0].get("video", {}).get("uri", "")
                        if video_uri:
                            vid_resp = requests.get(
                                f"{video_uri}&key={api_key}", timeout=180
                            )
                            vid_resp.raise_for_status()
                            return vid_resp.content

                    # Formato inline (poco común pero posible)
                    for cand in resp.get("candidates", []):
                        for part in cand.get("content", {}).get("parts", []):
                            if "inlineData" in part:
                                return base64.b64decode(part["inlineData"]["data"])

                    raise RuntimeError("Operación finalizada pero no se encontró video.")

                progress = poll_data.get("metadata", {}).get("state", "PROCESSING")
                logger.info(f"[Veo] Estado: {progress} | {elapsed}s transcurridos")

            raise RuntimeError(f"Timeout: La generación excedió {max_wait}s.")

        except requests.exceptions.HTTPError as e:
            status = e.response.status_code if e.response else "N/A"
            body = ""
            try:
                body = e.response.json().get("error", {}).get("message", "")
            except Exception:
                body = str(e)
            raise RuntimeError(f"Error HTTP {status} en Veo: {body}")

    # ========================================================================
    # UTILIDADES DE CONVERSIÓN — Tensores ComfyUI
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
    def base64_to_image_tensor(b64_string: str) -> torch.Tensor:
        """Decodifica imagen base64 a tensor [1, H, W, C] float 0.0-1.0."""
        img_bytes = base64.b64decode(b64_string)
        img = Image.open(io.BytesIO(img_bytes)).convert("RGB")
        img_np = np.array(img).astype(np.float32) / 255.0
        return torch.from_numpy(img_np).unsqueeze(0)

    @staticmethod
    def bytes_to_image_tensor(img_bytes: bytes) -> torch.Tensor:
        """Convierte bytes de imagen a tensor [1, H, W, C] float 0.0-1.0."""
        img = Image.open(io.BytesIO(img_bytes)).convert("RGB")
        img_np = np.array(img).astype(np.float32) / 255.0
        return torch.from_numpy(img_np).unsqueeze(0)

    @staticmethod
    def video_bytes_to_tensor(video_bytes: bytes) -> torch.Tensor:
        """
        Convierte bytes MP4 a tensor [B, H, W, C] usando OpenCV + tempfile.
        ⚡ FPS estándar de Veo: 24. Configurar VHS Video Combine a 24 FPS.
        """
        import cv2

        with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tmp:
            tmp.write(video_bytes)
            tmp_path = tmp.name

        try:
            cap = cv2.VideoCapture(tmp_path)
            if not cap.isOpened():
                raise RuntimeError("No se pudo abrir el video.")

            frames = []
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frames.append(frame_rgb.astype(np.float32) / 255.0)
            cap.release()

            if not frames:
                raise RuntimeError("El video decodificado no contiene frames.")

            tensor = torch.from_numpy(np.stack(frames, axis=0))
            logger.info(
                f"[Video] Decodificado: {tensor.shape[0]} frames, "
                f"{tensor.shape[2]}x{tensor.shape[1]}, 24 FPS asumido"
            )
            return tensor
        finally:
            try:
                os.unlink(tmp_path)
            except OSError:
                pass

    # ========================================================================
    # UTILIDADES DE IMAGEN
    # ========================================================================
    @staticmethod
    def resize_tensor_to_match(
        source: torch.Tensor, target: torch.Tensor
    ) -> torch.Tensor:
        """Redimensiona source al H,W de target. Ambos [B, H, W, C]."""
        target_h, target_w = target.shape[1], target.shape[2]
        if source.shape[1] == target_h and source.shape[2] == target_w:
            return source
        source_perm = source.permute(0, 3, 1, 2)
        resized = torch.nn.functional.interpolate(
            source_perm,
            size=(target_h, target_w),
            mode="bilinear",
            align_corners=False,
        )
        return resized.permute(0, 2, 3, 1)

    @staticmethod
    def create_error_image(
        error_msg: str, width: int = 512, height: int = 512
    ) -> torch.Tensor:
        """
        Crea tensor de imagen roja 512x512 con el texto de error impreso.
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
        max_width = width - (margin * 2)
        lines = ["⚠️ ERROR", "=" * 30, ""]
        current_line = ""

        for word in error_msg.split():
            test_line = f"{current_line} {word}".strip()
            try:
                bbox = draw.textbbox((0, 0), test_line, font=font)
                line_width = bbox[2] - bbox[0]
            except AttributeError:
                line_width = len(test_line) * 8

            if line_width <= max_width:
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

        img_np = np.array(img).astype(np.float32) / 255.0
        return torch.from_numpy(img_np).unsqueeze(0)

    # ========================================================================
    # UTILIDADES DE COSTO
    # ========================================================================
    @staticmethod
    def estimate_video_cost(duration_seconds: int) -> str:
        """Retorna string con costo estimado: $0.40/segundo (Veo 3.1 Standard)."""
        cost = duration_seconds * VIDEO_COST_PER_SECOND
        return (
            f"💰 Costo estimado: ${cost:.2f} USD "
            f"({duration_seconds}s × ${VIDEO_COST_PER_SECOND}/s — Veo 3.1 Standard)"
        )
