"""
grok_core.py — Motor Central Multimodal para ComfyUI_Grok
=========================================================
Responsabilidades:
  - Conversión eficiente de tensores PyTorch → Base64
  - Construcción de payloads multimodales (texto + imágenes)
  - Enrutamiento automático al endpoint correcto (chat / imagen / video)
  - Reintentos con backoff exponencial y manejo de rate-limiting

Autor: Prompt Models Studio — xAI Integration Layer v2.0
"""

import io
import base64
import time
import logging
import requests
import numpy as np
import torch
from PIL import Image
from typing import Optional, Union

log = logging.getLogger("ComfyUI_Grok")

# ──────────────────────────────────────────────
# CONSTANTES GLOBALES
# ──────────────────────────────────────────────
XAI_BASE_URL        = "https://api.x.ai/v1"
CHAT_ENDPOINT       = f"{XAI_BASE_URL}/chat/completions"
IMAGE_ENDPOINT      = f"{XAI_BASE_URL}/images/generations"
VIDEO_ENDPOINT      = f"{XAI_BASE_URL}/video/generations"

DEFAULT_CHAT_MODEL  = "grok-4"
DEFAULT_IMAGE_MODEL = "grok-2-image"
DEFAULT_VIDEO_MODEL = "grok-video-forge"

MAX_RETRIES         = 4
RETRY_BASE_DELAY    = 2.0   # segundos — se duplica en cada intento
CHAT_TIMEOUT        = 120   # segundos
VIDEO_TIMEOUT       = 300   # video tarda mucho más


# ──────────────────────────────────────────────
# CONVERSIÓN DE TENSORES
# ──────────────────────────────────────────────

def tensor_to_pil(tensor: torch.Tensor, batch_index: int = 0) -> Image.Image:
    """
    Convierte un tensor ComfyUI [B, H, W, C] float32 (0.0–1.0)
    al objeto PIL Image correspondiente al frame `batch_index`.
    """
    if tensor.ndim == 4:
        frame = tensor[batch_index]          # [H, W, C]
    elif tensor.ndim == 3:
        frame = tensor
    else:
        raise ValueError(f"Tensor con forma inesperada: {tensor.shape}")

    # Desnormalizar → uint8 y convertir a PIL
    np_img = (frame.cpu().numpy() * 255.0).clip(0, 255).astype(np.uint8)
    return Image.fromarray(np_img, mode="RGB")


def tensor_to_base64(
    tensor: torch.Tensor,
    batch_index: int = 0,
    format: str = "JPEG",
    quality: int = 88
) -> str:
    """
    Convierte un tensor ComfyUI a string Base64 listo para la API de xAI.
    Usa JPEG por defecto para minimizar la latencia de subida.

    Args:
        tensor      : Tensor [B, H, W, C] o [H, W, C]
        batch_index : Frame a extraer cuando hay múltiples en el batch
        format      : "JPEG" (más liviano) o "PNG" (sin pérdida)
        quality     : Calidad JPEG 1–95

    Returns:
        String Base64 sin el prefijo data:image/...
    """
    pil_img = tensor_to_pil(tensor, batch_index)

    # Convertir a RGB para evitar problemas con RGBA en JPEG
    if pil_img.mode != "RGB":
        pil_img = pil_img.convert("RGB")

    buffer = io.BytesIO()
    save_kwargs = {"format": format}
    if format == "JPEG":
        save_kwargs["quality"] = quality
        save_kwargs["optimize"] = True

    pil_img.save(buffer, **save_kwargs)
    return base64.b64encode(buffer.getvalue()).decode("utf-8")


def pil_to_tensor(pil_img: Image.Image) -> torch.Tensor:
    """
    Convierte PIL Image → tensor ComfyUI [1, H, W, C] float32 (0.0–1.0).
    """
    if pil_img.mode != "RGB":
        pil_img = pil_img.convert("RGB")
    np_img = np.array(pil_img).astype(np.float32) / 255.0
    return torch.from_numpy(np_img).unsqueeze(0)   # [1, H, W, C]


def bytes_to_tensor(raw_bytes: bytes) -> torch.Tensor:
    """
    Convierte bytes de imagen (PNG/JPEG) a tensor ComfyUI.
    Útil para procesar respuestas de la API que devuelven imágenes binarias.
    """
    pil_img = Image.open(io.BytesIO(raw_bytes))
    return pil_to_tensor(pil_img)


def sample_video_frames(
    tensor: torch.Tensor,
    max_frames: int = 8,
    strategy: str = "uniform"
) -> list[torch.Tensor]:
    """
    Muestreo inteligente de frames de un tensor de video [B, H, W, C].
    Evita saturar el límite de tokens/imágenes de la API de xAI.

    Args:
        tensor    : Tensor de video completo
        max_frames: Máximo de frames a seleccionar
        strategy  : "uniform" (distribuido) o "keyframe" (cada N frames)

    Returns:
        Lista de tensores individuales [1, H, W, C]
    """
    total = tensor.shape[0]
    if total <= max_frames:
        return [tensor[i].unsqueeze(0) for i in range(total)]

    if strategy == "uniform":
        indices = np.linspace(0, total - 1, max_frames, dtype=int)
    else:  # keyframe — cada N frames
        step = max(1, total // max_frames)
        indices = list(range(0, total, step))[:max_frames]

    return [tensor[i].unsqueeze(0) for i in indices]


# ──────────────────────────────────────────────
# CONSTRUCCIÓN DE PAYLOADS
# ──────────────────────────────────────────────

def build_text_content(text: str) -> list[dict]:
    """Bloque de contenido tipo texto para mensajes multimodales."""
    return [{"type": "text", "text": text}]


def build_image_content(
    tensor: torch.Tensor,
    batch_index: int = 0,
    detail: str = "high"
) -> dict:
    """
    Construye un bloque image_url a partir de un tensor ComfyUI.
    `detail` puede ser "low", "high" o "auto" según la API de xAI.
    """
    b64 = tensor_to_base64(tensor, batch_index)
    return {
        "type": "image_url",
        "image_url": {
            "url": f"data:image/jpeg;base64,{b64}",
            "detail": detail
        }
    }


def build_multimodal_message(
    role: str,
    text: str,
    image_tensors: Optional[list[torch.Tensor]] = None,
    image_detail: str = "high"
) -> dict:
    """
    Ensambla un mensaje completo con bloques de texto e imágenes mezclados.

    Args:
        role          : "user" o "system"
        text          : Texto principal del mensaje
        image_tensors : Lista de tensores [B, H, W, C] (uno por imagen)
        image_detail  : Nivel de detalle para visión

    Returns:
        Diccionario de mensaje listo para incluir en `messages[]`
    """
    content = build_text_content(text)

    if image_tensors:
        for t in image_tensors:
            if t is not None:
                content.append(build_image_content(t, detail=image_detail))

    return {"role": role, "content": content}


# ──────────────────────────────────────────────
# ENRUTADOR DE PAYLOAD (PAYLOAD ROUTER)
# ──────────────────────────────────────────────

class PayloadRouter:
    """
    Enrutador central que decide qué endpoint usar y construye
    el JSON correcto según el tipo de petición.

    Modos soportados:
      - "chat"   → CHAT_ENDPOINT  (texto y/o visión multimodal)
      - "image"  → IMAGE_ENDPOINT (generación / edición de imágenes)
      - "video"  → VIDEO_ENDPOINT (generación / edición de video)
    """

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

    # ── Construcción de payloads ──────────────

    def build_chat_payload(
        self,
        messages: list[dict],
        model: str = DEFAULT_CHAT_MODEL,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        system_prompt: str = ""
    ) -> dict:
        """Payload para el endpoint de chat/completions."""
        all_messages = []
        if system_prompt:
            all_messages.append({"role": "system", "content": system_prompt})
        all_messages.extend(messages)

        return {
            "model": model,
            "messages": all_messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }

    def build_image_generation_payload(
        self,
        prompt: str,
        model: str = DEFAULT_IMAGE_MODEL,
        n: int = 1,
        size: str = "1024x1024",
        response_format: str = "b64_json",
        reference_image_b64: Optional[str] = None,
        mask_b64: Optional[str] = None,
        strength: float = 0.8
    ) -> dict:
        """
        Payload para generación de imágenes.
        Si se provee reference_image_b64, entra en modo image-to-image/inpainting.
        """
        payload = {
            "model": model,
            "prompt": prompt,
            "n": n,
            "size": size,
            "response_format": response_format
        }
        if reference_image_b64:
            payload["image"] = reference_image_b64
            payload["strength"] = round(float(strength), 2)
        if mask_b64:
            payload["mask"] = mask_b64

        return payload

    def build_video_payload(
        self,
        prompt: str,
        model: str = DEFAULT_VIDEO_MODEL,
        duration_seconds: int = 5,
        fps: int = 24,
        size: str = "1280x720",
        reference_video_b64: Optional[str] = None,
        reference_image_b64: Optional[str] = None,
        style_strength: float = 0.7
    ) -> dict:
        """Payload para generación/edición de video."""
        payload = {
            "model": model,
            "prompt": prompt,
            "duration_seconds": duration_seconds,
            "fps": fps,
            "size": size,
        }
        if reference_image_b64:
            payload["start_image"] = reference_image_b64
        if reference_video_b64:
            payload["reference_video"] = reference_video_b64
            payload["style_strength"] = round(float(style_strength), 2)

        return payload

    # ── Ejecutor de peticiones HTTP ───────────

    def post(
        self,
        endpoint: str,
        payload: dict,
        timeout: int = CHAT_TIMEOUT
    ) -> dict:
        """
        Ejecuta POST con reintentos y backoff exponencial.
        Maneja: rate-limit (429), errores de servidor (5xx), timeouts.

        Returns:
            Respuesta JSON parseada
        Raises:
            RuntimeError si todos los reintentos fallan
        """
        last_error = None
        delay = RETRY_BASE_DELAY

        for attempt in range(1, MAX_RETRIES + 1):
            try:
                log.info(f"[Grok] POST → {endpoint} (intento {attempt}/{MAX_RETRIES})")
                resp = requests.post(
                    endpoint,
                    headers=self.headers,
                    json=payload,
                    timeout=timeout
                )

                # Rate limiting — esperar y reintentar
                if resp.status_code == 429:
                    retry_after = float(resp.headers.get("Retry-After", delay))
                    log.warning(f"[Grok] Rate limit. Esperando {retry_after}s...")
                    time.sleep(retry_after)
                    delay *= 2
                    continue

                # Error del servidor — reintentable
                if resp.status_code >= 500:
                    log.warning(f"[Grok] Error servidor {resp.status_code}. Reintentando en {delay}s...")
                    time.sleep(delay)
                    delay *= 2
                    continue

                # Error del cliente — no reintentable
                if resp.status_code >= 400:
                    try:
                        err_body = resp.json()
                    except Exception:
                        err_body = resp.text
                    raise RuntimeError(
                        f"[Grok] Error API {resp.status_code}: {err_body}"
                    )

                return resp.json()

            except requests.exceptions.Timeout:
                last_error = f"Timeout en intento {attempt} (>{timeout}s)"
                log.warning(f"[Grok] {last_error}")
                time.sleep(delay)
                delay *= 2

            except requests.exceptions.ConnectionError as e:
                last_error = f"Error de conexión en intento {attempt}: {e}"
                log.warning(f"[Grok] {last_error}")
                time.sleep(delay)
                delay *= 2

        raise RuntimeError(
            f"[Grok] Todos los intentos fallaron. Último error: {last_error}"
        )

    # ── Métodos de alto nivel ─────────────────

    def chat(
        self,
        messages: list[dict],
        model: str = DEFAULT_CHAT_MODEL,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        system_prompt: str = ""
    ) -> str:
        """Envía un chat multimodal y devuelve el texto de respuesta."""
        payload = self.build_chat_payload(
            messages, model, temperature, max_tokens, system_prompt
        )
        result = self.post(CHAT_ENDPOINT, payload, timeout=CHAT_TIMEOUT)
        return result["choices"][0]["message"]["content"]

    def generate_image(self, **kwargs) -> list[torch.Tensor]:
        """
        Genera o edita imágenes y devuelve lista de tensores ComfyUI.
        Cada elemento es [1, H, W, C].
        """
        payload = self.build_image_generation_payload(**kwargs)
        result = self.post(IMAGE_ENDPOINT, payload, timeout=CHAT_TIMEOUT)

        tensors = []
        for item in result.get("data", []):
            if "b64_json" in item:
                raw = base64.b64decode(item["b64_json"])
                tensors.append(bytes_to_tensor(raw))
            elif "url" in item:
                img_resp = requests.get(item["url"], timeout=30)
                img_resp.raise_for_status()
                tensors.append(bytes_to_tensor(img_resp.content))

        return tensors

    def generate_video(self, **kwargs) -> torch.Tensor:
        """
        Genera o edita video. Devuelve tensor [B, H, W, C] con todos los frames.
        """
        payload = self.build_video_payload(**kwargs)
        result = self.post(VIDEO_ENDPOINT, payload, timeout=VIDEO_TIMEOUT)
        return _decode_video_response(result)


# ──────────────────────────────────────────────
# DECODIFICACIÓN DE VIDEO
# ──────────────────────────────────────────────

def _decode_video_response(api_result: dict) -> torch.Tensor:
    """
    Decodifica la respuesta de video de xAI y reconstruye un tensor
    [B, H, W, C] compatible con ComfyUI VHS/VideoCombine.

    La API puede devolver:
      - frames como lista de base64
      - URL de un archivo .mp4
      - datos binarios directos
    """
    frames_tensors = []

    # Caso 1: frames individuales en Base64
    if "frames" in api_result:
        for frame_b64 in api_result["frames"]:
            raw = base64.b64decode(frame_b64)
            frames_tensors.append(pil_to_tensor(Image.open(io.BytesIO(raw))))

    # Caso 2: URL de video .mp4
    elif "url" in api_result.get("data", [{}])[0] if api_result.get("data") else False:
        video_url = api_result["data"][0]["url"]
        frames_tensors = _download_and_decode_mp4(video_url)

    # Caso 3: video en Base64
    elif "b64_json" in api_result.get("data", [{}])[0] if api_result.get("data") else False:
        video_bytes = base64.b64decode(api_result["data"][0]["b64_json"])
        frames_tensors = _decode_mp4_bytes(video_bytes)

    if not frames_tensors:
        raise RuntimeError("[Grok Video] No se encontraron frames en la respuesta de la API.")

    # Stack de todos los frames → [B, H, W, C]
    return torch.cat(frames_tensors, dim=0)


def _download_and_decode_mp4(url: str) -> list[torch.Tensor]:
    """Descarga un .mp4 desde URL y decodifica sus frames."""
    resp = requests.get(url, timeout=120, stream=True)
    resp.raise_for_status()
    return _decode_mp4_bytes(resp.content)


def _decode_mp4_bytes(video_bytes: bytes) -> list[torch.Tensor]:
    """
    Decodifica bytes de un .mp4 a lista de tensores frame por frame.
    Requiere OpenCV (cv2) o imageio según disponibilidad.
    """
    frames = []
    try:
        import cv2
        import tempfile, os

        with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tmp:
            tmp.write(video_bytes)
            tmp_path = tmp.name

        cap = cv2.VideoCapture(tmp_path)
        while True:
            ret, frame_bgr = cap.read()
            if not ret:
                break
            frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
            pil_frame = Image.fromarray(frame_rgb)
            frames.append(pil_to_tensor(pil_frame))
        cap.release()
        os.unlink(tmp_path)

    except ImportError:
        # Fallback con imageio si cv2 no está disponible
        try:
            import imageio
            import tempfile, os

            with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tmp:
                tmp.write(video_bytes)
                tmp_path = tmp.name

            reader = imageio.get_reader(tmp_path, format="mp4")
            for frame_np in reader:
                pil_frame = Image.fromarray(frame_np)
                frames.append(pil_to_tensor(pil_frame))
            reader.close()
            os.unlink(tmp_path)

        except ImportError:
            raise RuntimeError(
                "[Grok Video] Instala 'opencv-python' o 'imageio[ffmpeg]' "
                "para decodificar video. Ejecuta: pip install opencv-python"
            )

    return frames
