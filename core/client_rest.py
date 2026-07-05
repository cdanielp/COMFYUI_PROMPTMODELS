"""
core/client_rest.py — Cliente REST compartido para promptmodels 3.x.

- POST genérico para APIs OpenAI-compatible (NVIDIA, Grok) y Gemini.
- Retry exponencial en 429: delays 2/4/8/16s, hasta 5 intentos totales.
- Timeout 120s por defecto.
- Errores amigables por código HTTP.
- Política de error: el cliente lanza RuntimeError. Los nodos String la capturan
  y la devuelven como string. Los nodos IMAGE la dejan subir para parar el workflow.
- Sin SDKs externos: solo requests + PIL.
"""
import base64
import io
import logging
import time

import requests
from PIL import Image

log = logging.getLogger("promptmodels.client")

# --------------------------------------------------------------------------- #
# Constantes
# --------------------------------------------------------------------------- #

_TIMEOUT = 120
_BACKOFF_DELAYS = [2, 4, 8, 16]  # segundos; 4 retries → 5 intentos totales


# --------------------------------------------------------------------------- #
# Manejo de errores HTTP
# --------------------------------------------------------------------------- #

def _friendly_error(resp: requests.Response, provider: str) -> None:
    status = resp.status_code

    if status == 402:
        raise RuntimeError("ERROR: créditos NVIDIA agotados")

    if status == 403 and provider == "NVIDIA":
        raise RuntimeError(
            "ERROR: la API key no tiene scope Public API Endpoints, "
            "regenérala en build.nvidia.com marcando esa casilla"
        )

    if status == 401:
        raise RuntimeError(
            "ERROR: key inválida o ausente (revisa .env o variable de entorno)"
        )

    try:
        body = resp.json()
        err = body.get("error", {})
        msg = err.get("message", "") if isinstance(err, dict) else str(err)
    except Exception:
        msg = resp.text[:300]

    raise RuntimeError(f"ERROR HTTP {status} de {provider}: {msg or resp.text[:200]}")


# --------------------------------------------------------------------------- #
# Núcleo: POST con backoff
# --------------------------------------------------------------------------- #

def post_json(
    url: str,
    headers: dict,
    payload: dict,
    provider: str,
    timeout: int = _TIMEOUT,
) -> dict:
    """POST genérico con retry exponencial en 429."""
    for attempt, delay in enumerate([0] + _BACKOFF_DELAYS):
        if delay:
            log.warning(
                "[%s] 429 rate-limit — reintento %d/4 en %ds…",
                provider, attempt, delay,
            )
            time.sleep(delay)

        try:
            resp = requests.post(url, headers=headers, json=payload, timeout=timeout)
        except requests.exceptions.Timeout:
            raise RuntimeError(
                f"ERROR: timeout ({timeout}s) al contactar {provider}"
            )
        except requests.exceptions.ConnectionError:
            raise RuntimeError(
                f"ERROR: no se pudo conectar a {provider}"
            )

        if resp.status_code == 200:
            return resp.json()

        if resp.status_code == 429 and attempt < len(_BACKOFF_DELAYS):
            continue  # sleep ya aplicado al inicio del siguiente ciclo

        _friendly_error(resp, provider)

    raise RuntimeError(
        f"ERROR: rate-limit de {provider} tras 5 intentos consecutivos"
    )


# --------------------------------------------------------------------------- #
# Helpers por proveedor
# --------------------------------------------------------------------------- #

def post_openai(
    base_url: str,
    endpoint: str,
    api_key: str,
    payload: dict,
    provider: str,
    timeout: int = _TIMEOUT,
) -> dict:
    """POST a API compatible con OpenAI (NVIDIA NIM, Grok)."""
    url = base_url.rstrip("/") + endpoint
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    return post_json(url, headers, payload, provider, timeout)


def post_gemini(
    api_key: str,
    model: str,
    endpoint_suffix: str,
    payload: dict,
    provider: str = "Gemini",
    base_url: str = "https://generativelanguage.googleapis.com/v1beta",
    timeout: int = _TIMEOUT,
) -> dict:
    """POST a la API de Gemini (key en query param, no en header)."""
    url = f"{base_url}/models/{model}:{endpoint_suffix}?key={api_key}"
    headers = {"Content-Type": "application/json"}
    return post_json(url, headers, payload, provider, timeout)


def post_gemini_raw(
    api_key: str,
    full_path: str,
    payload: dict,
    provider: str = "Gemini",
    base_url: str = "https://generativelanguage.googleapis.com/v1beta",
    timeout: int = _TIMEOUT,
) -> dict:
    """POST a endpoint Gemini con path arbitrario (ej. /interactions)."""
    url = f"{base_url}{full_path}?key={api_key}"
    headers = {"Content-Type": "application/json"}
    return post_json(url, headers, payload, provider, timeout)


# --------------------------------------------------------------------------- #
# Utilidad: tensor IMAGE → data-URL JPEG
# --------------------------------------------------------------------------- #

def image_tensor_to_jpeg_data_url(image, max_side: int = 1024) -> str:
    """
    Convierte tensor IMAGE de ComfyUI [B,H,W,C] float 0-1 a data-URL JPEG.
    Toma el primer frame del batch. Reescala el lado mayor a max_side con PIL.
    No usa cv2.
    """
    import torch  # importación local: no penaliza la carga del módulo

    if image.dim() == 4:
        frame = image[0]
    else:
        frame = image

    img_np = (frame.cpu().numpy() * 255).clip(0, 255).astype("uint8")
    img = Image.fromarray(img_np, "RGB")

    w, h = img.size
    if max(w, h) > max_side:
        scale = max_side / max(w, h)
        img = img.resize((max(1, int(w * scale)), max(1, int(h * scale))), Image.LANCZOS)

    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=85)
    b64 = base64.b64encode(buf.getvalue()).decode("ascii")
    return f"data:image/jpeg;base64,{b64}"
