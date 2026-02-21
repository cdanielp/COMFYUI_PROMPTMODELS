"""
google_core.py - Motor Central de la API de Google AI (V2.3)
============================================================
Maneja TODAS las comunicaciones HTTP con la API REST de Google.
Regla de Oro: CERO SDKs. Solo requests puras (+ aiohttp para video async).

V2.3 Cambios:
  - generate_video → formato estructurado instances/parameters (Vertex/Veo)
  - Polling URL corregida con normalización de operation_name
  - Extracción de video soporta bytesBase64Encoded, URI e inlineData

V2.2 Cambios:
  - video_bytes_to_audio() → extrae audio de MP4 con fallback silencio

V2.1 Cambios:
  - generate_video → async (aiohttp + asyncio.sleep)
  - safe_seed() → sanitización 64→32 bits
  - generate_image ahora acepta reference_images_b64

Autor: Prompt Models Studio | cdanielp
"""

import requests
import base64
import json
import io
import os
import tempfile
import time
import asyncio
import aiohttp
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
GEMINI_MODELS_ENDPOINT = "{base}/models/{model}:generateContent?key={key}"

# Veo 3.1 - Video Generation (API asíncrona con polling)
VEO_PREDICT_ENDPOINT = "{base}/models/{model}:predictLongRunning?key={key}"

# Modelos por defecto
DEFAULT_TEXT_MODEL = "gemini-3.1-pro-preview"
DEFAULT_IMAGE_MODEL = "imagen-3.0-generate-002"
DEFAULT_VIDEO_MODEL = "veo-3.1"
DEFAULT_AUDIO_MODEL = "lyria-3"

# Costo estimado de video por segundo (USD)
VIDEO_COST_PER_SECOND = 0.05

# Presets de resolución para Veo 3.1
VEO_RESOLUTION_PRESETS = {
    "1920x1080 (16:9)": (1920, 1080),
    "1080x1920 (9:16)": (1080, 1920),
    "1080x1080 (1:1)": (1080, 1080),
    "3840x2160 (16:9 4K)": (3840, 2160),
    "2160x3840 (9:16 4K)": (2160, 3840),
}

# Duraciones permitidas para video (segundos)
VEO_DURATION_OPTIONS = [4, 6, 8]

# ============================================================================
# SYSTEM PROMPTS HARDCODED (Solo Diagnóstico)
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
    Video: polling asíncrono con aiohttp (V2.3).
    """

    # ========================================================================
    # RESOLUCIÓN DE API KEY
    # ========================================================================
    @staticmethod
    def resolve_api_key(node_key: str = "") -> str:
        """
        Busca la API Key en orden estricto:
        1. Campo api_key del nodo (el usuario escribió algo)
        2. Clave inyectada por el frontend JS (llega al mismo campo del nodo)
        3. Variable de entorno GOOGLE_AI_API_KEY
        4. ValueError si no hay nada
        """
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
    # SANITIZACIÓN DE SEMILLAS (64-bit → 32-bit)
    # ========================================================================
    @staticmethod
    def safe_seed(seed: int) -> int:
        """
        Sanitiza semillas de 64 bits generadas por otros nodos de ComfyUI
        a 32 bits (max 2147483647) para evitar crashes con APIs de Google.
        """
        return int(seed) % 2147483648

    # ========================================================================
    # PETICIONES HTTP CENTRALES
    # ========================================================================
    @staticmethod
    def _build_url(model: str, key: str, endpoint_template: str = None) -> str:
        """Construye la URL completa de la API."""
        if endpoint_template is None:
            endpoint_template = GEMINI_MODELS_ENDPOINT
        return endpoint_template.format(
            base=GEMINI_BASE_URL, model=model, key=key
        )

    @staticmethod
    def call_gemini(
        api_key: str,
        model: str,
        contents: List[Dict],
        system_instruction: Optional[str] = None,
        generation_config: Optional[Dict] = None,
        timeout: int = 120,
    ) -> Dict[str, Any]:
        """Llamada genérica a la API de Gemini (generateContent)."""
        url = GoogleAICore._build_url(model, api_key)
        payload: Dict[str, Any] = {"contents": contents}

        if system_instruction:
            payload["systemInstruction"] = {
                "parts": [{"text": system_instruction}]
            }
        if generation_config:
            payload["generationConfig"] = generation_config

        headers = {"Content-Type": "application/json"}

        try:
            response = requests.post(
                url, headers=headers, json=payload, timeout=timeout
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
        """Llamada simplificada para obtener solo el texto de respuesta."""
        parts = []
        if extra_parts:
            parts.extend(extra_parts)
        parts.append({"text": prompt})

        contents = [{"role": "user", "parts": parts}]
        gen_config = generation_config or {}

        # Thinking budget (para modelos que lo soportan)
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
        """Extrae el texto limpio de una respuesta de Gemini."""
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
    # GENERACIÓN DE IMÁGENES (Imagen 3)
    # ========================================================================
    @staticmethod
    def generate_image(
        api_key: str,
        prompt: str,
        model: str = DEFAULT_IMAGE_MODEL,
        negative_prompt: str = "",
        aspect_ratio: str = "1:1",
        num_images: int = 1,
        seed: Optional[int] = None,
        reference_images_b64: Optional[List[str]] = None,
    ) -> List[bytes]:
        """
        Genera imágenes usando Imagen 3. Retorna lista de bytes PNG.
        Acepta hasta 5 imágenes de referencia y semilla sanitizada.
        """
        url = GoogleAICore._build_url(model, api_key)

        # Construir parts con imágenes de referencia + prompt
        parts = []
        if reference_images_b64:
            for ref_b64 in reference_images_b64:
                parts.append({
                    "inlineData": {"mimeType": "image/png", "data": ref_b64}
                })
        parts.append({"text": prompt})

        gen_config: Dict[str, Any] = {
            "responseModalities": ["IMAGE"],
            "imageSizes": aspect_ratio,
        }
        if negative_prompt:
            gen_config["negativePrompt"] = negative_prompt
        if seed is not None:
            gen_config["seed"] = GoogleAICore.safe_seed(seed)

        payload = {
            "contents": [{"parts": parts}],
            "generationConfig": gen_config,
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
            for candidate in data.get("candidates", []):
                for part in candidate.get("content", {}).get("parts", []):
                    if "inlineData" in part:
                        images.append(base64.b64decode(part["inlineData"]["data"]))
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
    # GENERACIÓN DE VIDEO (Veo 3.1) — Polling Asíncrono (V2.3)
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
        poll_interval: int = 15,
        max_wait: int = 600,
    ) -> bytes:
        """
        Genera video usando Veo 3.1 con polling asíncrono no bloqueante.
        Usa el formato estructurado (instances / parameters) de Vertex AI.
        Retorna bytes MP4.
        """
        url = VEO_PREDICT_ENDPOINT.format(
            base=GEMINI_BASE_URL, model=model, key=api_key
        )

        # Parsear resolución y aspecto para los parameters
        aspect_ratio = "16:9"
        api_resolution = "1080p"

        if "9:16" in resolution_preset:
            aspect_ratio = "9:16"
        elif "1:1" in resolution_preset:
            aspect_ratio = "1:1"

        if "4K" in resolution_preset:
            api_resolution = "4k"
        elif "1080" in resolution_preset:
            api_resolution = "1080p"
        elif "720" in resolution_preset:
            api_resolution = "720p"

        # Construir instancia en formato Vertex/Veo
        instance = {
            "prompt": prompt
        }

        # 1. Imagen inicial (Img2Vid)
        if init_images_b64 and len(init_images_b64) > 0:
            instance["image"] = {
                "mimeType": "image/png",
                "bytesBase64Encoded": init_images_b64[0]
            }

        # 2. Último frame (Interpolación)
        if last_frame_b64:
            instance["lastFrame"] = {
                "mimeType": "image/png",
                "bytesBase64Encoded": last_frame_b64
            }

        # 3. Imágenes de referencia (Storyboard)
        if reference_images_b64:
            refs = []
            for ref_b64 in reference_images_b64:
                refs.append({
                    "mimeType": "image/png",
                    "bytesBase64Encoded": ref_b64
                })
            instance["referenceImages"] = refs

        payload = {
            "instances": [instance],
            "parameters": {
                "aspectRatio": aspect_ratio,
                "resolution": api_resolution,
                "durationSeconds": int(duration_seconds),
            }
        }

        try:
            timeout_cfg = aiohttp.ClientTimeout(
                total=None, sock_connect=30, sock_read=120
            )
            async with aiohttp.ClientSession(timeout=timeout_cfg) as session:
                # 1. Iniciar operación (POST)
                async with session.post(
                    url,
                    headers={"Content-Type": "application/json"},
                    json=payload,
                ) as response:
                    if not response.ok:
                        err_text = await response.text()
                        try:
                            err_msg = json.loads(err_text).get("error", {}).get("message", err_text[:500])
                        except (json.JSONDecodeError, AttributeError):
                            err_msg = err_text[:500]
                        raise RuntimeError(
                            f"Error HTTP {response.status} en Veo 3.1: {err_msg}"
                        )
                    operation = await response.json()
                    operation_name = operation.get("name", "")

                if not operation_name:
                    raise RuntimeError("La API no retornó un nombre de operación válido.")

                logger.info(f"[Veo 3.1] Operación iniciada: {operation_name}")

                # Asegurar formato correcto de URL de polling
                if not operation_name.startswith("operations/"):
                    operation_name = f"operations/{operation_name}"

                # 2. Polling asíncrono (no bloquea el event loop de ComfyUI)
                elapsed = 0
                while elapsed < max_wait:
                    await asyncio.sleep(poll_interval)
                    elapsed += poll_interval

                    poll_url = f"{GEMINI_BASE_URL}/{operation_name}?key={api_key}"
                    async with session.get(poll_url) as poll_resp:
                        if not poll_resp.ok:
                            err_text = await poll_resp.text()
                            try:
                                err_msg = json.loads(err_text).get("error", {}).get("message", err_text[:500])
                            except (json.JSONDecodeError, AttributeError):
                                err_msg = err_text[:500]
                            raise RuntimeError(
                                f"Error HTTP {poll_resp.status} en polling Veo: {err_msg}"
                            )
                        poll_data = await poll_resp.json()

                    if poll_data.get("done", False):
                        result = poll_data.get("response", {})

                        # Extraer video — soporta bytesBase64Encoded, URI e inlineData
                        generated = result.get("generatedVideos", [])
                        if generated:
                            vid_obj = generated[0].get("video", {})

                            if "bytesBase64Encoded" in vid_obj:
                                logger.info(f"[Veo 3.1] ✅ Video recibido (Base64) en {elapsed}s")
                                return base64.b64decode(vid_obj["bytesBase64Encoded"])

                            video_uri = vid_obj.get("uri", "")
                            if video_uri:
                                async with session.get(f"{video_uri}&key={api_key}") as vid_resp:
                                    if vid_resp.ok:
                                        logger.info(f"[Veo 3.1] ✅ Video recibido (URI) en {elapsed}s")
                                        return await vid_resp.read()

                        # Fallback formato tradicional (inlineData)
                        for cand in result.get("candidates", []):
                            for part in cand.get("content", {}).get("parts", []):
                                if "inlineData" in part:
                                    logger.info(f"[Veo 3.1] ✅ Video recibido (inlineData) en {elapsed}s")
                                    return base64.b64decode(part["inlineData"]["data"])

                        raise RuntimeError("Operación finalizada pero no se encontró video en la respuesta.")

                    metadata = poll_data.get("metadata", {})
                    progress = metadata.get("progress", "desconocido")
                    logger.info(f"[Veo 3.1] Generando... Progreso: {progress}% | {elapsed}s/{max_wait}s")

                raise RuntimeError(f"Timeout: La generación excedió {max_wait}s.")

        except RuntimeError:
            raise
        except Exception as e:
            raise RuntimeError(f"Error inesperado en Veo 3.1: {str(e)}") from e

   # ========================================================================
    # GENERACIÓN DE AUDIO (Lyria 3)
    # ========================================================================
    @staticmethod
    def generate_audio(
        api_key: str,
        prompt: str,
        model: str = DEFAULT_AUDIO_MODEL,
        duration_seconds: int = 30,
        include_vocals: bool = False,
        init_image_b64: Optional[str] = None,
        video_frames_b64: Optional[List[str]] = None,
    ) -> bytes:
        """
        Genera audio usando Lyria 3. Retorna bytes WAV.
        Filtra warnings de SynthID automáticamente sin crashear.
        """
        url = GoogleAICore._build_url(model, api_key)

        parts = []
        if init_image_b64:
            parts.append({"inlineData": {"mimeType": "image/png", "data": init_image_b64}})

        if video_frames_b64:
            for frame_b64 in video_frames_b64:
                parts.append({"inlineData": {"mimeType": "image/png", "data": frame_b64}})

        vocal_tag = " Include vocals and singing." if include_vocals else " Instrumental only, no vocals."

        # La API rechaza 'audioDuration' en el JSON →
        # se inyecta la duración directamente en el texto que lee el modelo.
        final_prompt = f"{prompt}{vocal_tag} Make the track approximately {duration_seconds} seconds long."
        parts.append({"text": final_prompt})

        payload = {
            "contents": [{"parts": parts}],
            "generationConfig": {
                "responseModalities": ["AUDIO"],
            },
        }

        try:
            response = requests.post(
                url,
                headers={"Content-Type": "application/json"},
                json=payload,
                timeout=180,
            )
            response.raise_for_status()
            data = response.json()

            # Filtrar warnings de SynthID (no deben crashear)
            for warning in data.get("warnings", []):
                logger.info(f"[Lyria 3] SynthID Warning (ignorado): {warning}")

            for candidate in data.get("candidates", []):
                for part in candidate.get("content", {}).get("parts", []):
                    if "inlineData" in part:
                        return base64.b64decode(part["inlineData"]["data"])

            raise RuntimeError("La API no retornó datos de audio.")

        except requests.exceptions.HTTPError as e:
            status = e.response.status_code if e.response else "N/A"
            body = ""
            try:
                body = e.response.json().get("error", {}).get("message", "")
            except Exception:
                body = str(e)
            raise RuntimeError(f"Error HTTP {status} en Lyria 3: {body}")

    # ========================================================================
    # UTILIDADES DE CONVERSIÓN (Tensores ComfyUI)
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
    def base64_to_video_tensor(b64_string: str) -> torch.Tensor:
        """
        Decodifica MP4 base64 a tensor [B, H, W, C] usando OpenCV + tempfile.
        ⚡ FPS estándar de Veo: 24. Configurar VHS Video Combine a 24 FPS.
        """
        import cv2

        video_bytes = base64.b64decode(b64_string)
        with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tmp:
            tmp.write(video_bytes)
            tmp_path = tmp.name

        try:
            cap = cv2.VideoCapture(tmp_path)
            if not cap.isOpened():
                raise RuntimeError("No se pudo abrir el video decodificado.")

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

    @staticmethod
    def base64_to_audio_tensor(b64_string: str) -> Dict[str, Any]:
        """
        Decodifica audio base64 a formato ComfyUI audio.
        Retorna: {"waveform": tensor [B, C, S], "sample_rate": int}
        """
        import torchaudio

        audio_bytes = base64.b64decode(b64_string)
        waveform, sample_rate = torchaudio.load(io.BytesIO(audio_bytes))
        if waveform.dim() == 2:
            waveform = waveform.unsqueeze(0)
        return {"waveform": waveform, "sample_rate": sample_rate}

    @staticmethod
    def video_bytes_to_tensor(video_bytes: bytes) -> torch.Tensor:
        """Wrapper: bytes de video MP4 → tensor [B, H, W, C]."""
        b64 = base64.b64encode(video_bytes).decode("utf-8")
        return GoogleAICore.base64_to_video_tensor(b64)

    @staticmethod
    def video_bytes_to_audio(video_bytes: bytes) -> dict:
        """
        Extrae audio de bytes MP4 usando torchaudio.
        Fallback: silencio estéreo (1, 2, 44100) si el video es mudo o falta FFmpeg.
        """
        dummy_audio = {"waveform": torch.zeros((1, 2, 44100)), "sample_rate": 44100}
        try:
            import torchaudio
            with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tmp:
                tmp.write(video_bytes)
                tmp_path = tmp.name
            try:
                waveform, sample_rate = torchaudio.load(tmp_path)
                return {"waveform": waveform.unsqueeze(0), "sample_rate": sample_rate}
            except Exception as e:
                logger.warning(f"[video_bytes_to_audio] No se pudo extraer audio: {e} → silencio")
                return dummy_audio
            finally:
                try:
                    os.unlink(tmp_path)
                except OSError:
                    pass
        except Exception as e:
            logger.warning(f"[video_bytes_to_audio] torchaudio no disponible: {e} → silencio")
            return dummy_audio

    @staticmethod
    def audio_bytes_to_dict(audio_bytes: bytes) -> Dict[str, Any]:
        """Wrapper: bytes de audio → dict ComfyUI {"waveform", "sample_rate"}."""
        b64 = base64.b64encode(audio_bytes).decode("utf-8")
        return GoogleAICore.base64_to_audio_tensor(b64)

    # ========================================================================
    # UTILIDADES DE IMAGEN
    # ========================================================================
    @staticmethod
    def resize_tensor_to_match(source: torch.Tensor, target: torch.Tensor) -> torch.Tensor:
        """Redimensiona source al H,W de target. Ambos [B, H, W, C]."""
        target_h, target_w = target.shape[1], target.shape[2]
        if source.shape[1] == target_h and source.shape[2] == target_w:
            return source
        source_perm = source.permute(0, 3, 1, 2)
        resized = torch.nn.functional.interpolate(
            source_perm, size=(target_h, target_w), mode="bilinear", align_corners=False,
        )
        return resized.permute(0, 2, 3, 1)

    @staticmethod
    def create_error_image(error_msg: str, width: int = 512, height: int = 512) -> torch.Tensor:
        """
        Crea tensor de imagen roja 512x512 con el texto de error impreso.
        Usado para HTTP 400 (violación de seguridad) sin crashear el workflow.
        Retorna [1, H, W, C] float 0.0-1.0.
        """
        img = Image.new("RGB", (width, height), color=(180, 30, 30))
        draw = ImageDraw.Draw(img)

        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)
        except (IOError, OSError):
            try:
                font = ImageFont.truetype("arial.ttf", 16)
            except (IOError, OSError):
                font = ImageFont.load_default()

        margin = 20
        max_width = width - (margin * 2)
        lines = ["⚠️ ERROR DE SEGURIDAD", "=" * 30, ""]
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
        """Retorna string con costo estimado: $0.05/segundo."""
        cost = duration_seconds * VIDEO_COST_PER_SECOND
        return f"💰 Costo estimado: ${cost:.2f} USD ({duration_seconds}s × ${VIDEO_COST_PER_SECOND}/s)"
