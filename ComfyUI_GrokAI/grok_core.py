# ==============================================================================
# grok_core.py - Motor Central de ComfyUI_Grok (V2.0)
# ==============================================================================
# Capa de comunicacion REST pura (sin SDKs) con la API de xAI.
# Maneja tensores estandar [B, H, W, C], conversion a Base64 y payloads multimodales.
# ==============================================================================

import os
import json
import time
import base64
import requests
from io import BytesIO
from PIL import Image
import torch
import numpy as np
import logging

log = logging.getLogger("ComfyUI_GrokCore")

XAI_API_BASE = "https://api.x.ai/v1"

# -- Modelos actualizados (xAI API - Marzo 2026) ------------------------------
TEXT_MODELS = [
    "grok-4.20-0309-reasoning",
    "grok-4.20-0309-non-reasoning",
    "grok-4-1-fast-reasoning",
    "grok-4-1-fast-non-reasoning",
]

IMAGE_MODELS = [
    "grok-imagine-image",
    "grok-imagine-image-pro",
]

VIDEO_MODELS = [
    "grok-imagine-video",
]

# -- Aspect ratios soportados por la API --------------------------------------
IMAGE_ASPECT_RATIOS = [
    "1:1", "16:9", "9:16", "4:3", "3:4",
    "3:2", "2:3", "2:1", "1:2",
    "19.5:9", "9:19.5", "20:9", "9:20", "auto",
]

VIDEO_ASPECT_RATIOS = [
    "1:1", "16:9", "9:16", "4:3", "3:4", "3:2", "2:3",
]

# -- System Prompts para nodos de diagnostico ----------------------------------
SYSTEM_PROMPT_WORKFLOW_DEBUGGER = (
    "You are a ComfyUI workflow analyst. The user will provide a list of "
    "class_type names extracted from a ComfyUI workflow JSON.\n\n"
    "For each custom node (not built-in ComfyUI nodes), provide:\n"
    "1. The most likely GitHub repository URL.\n"
    "2. Whether the node is well-maintained or potentially abandoned.\n"
    "3. Known conflicts with other popular custom nodes.\n\n"
    "At the end, provide:\n"
    "- A summary of potential issues.\n"
    "- Step-by-step installation instructions for any missing nodes.\n"
    "- Warnings about known fork conflicts.\n\n"
    "Be concise but thorough. Use markdown formatting."
)

SYSTEM_PROMPT_WORKFLOW_DEBUGGER_FUN = (
    "You are a ComfyUI workflow analyst with a sarcastic personality. "
    "You roast the user's node choices with dry humor, but you ALWAYS "
    "provide the real, accurate solution after each joke.\n\n"
    "The user will provide a list of class_type names from a ComfyUI workflow.\n\n"
    "For each custom node (not built-in), provide:\n"
    "1. A sarcastic one-liner about their choice.\n"
    "2. The actual GitHub repository URL.\n"
    "3. Whether it's maintained or abandoned (with a joke if abandoned).\n"
    "4. Known conflicts.\n\n"
    "End with a genuinely helpful summary and installation steps.\n"
    "Use markdown formatting. Be funny but never unhelpful."
)

SYSTEM_PROMPT_METADATA_READER = (
    "You are an expert in Stable Diffusion model architectures. "
    "The user will provide tensor key names and metadata extracted from a "
    ".safetensors file.\n\n"
    "Analyze the data and provide:\n"
    "1. **Architecture**: Identify the model type (SD 1.5, SDXL, Flux, etc.) "
    "based on key patterns.\n"
    "2. **Model Type**: Checkpoint, LoRA, LyCORIS, ControlNet, VAE, etc.\n"
    "3. **Trigger Words**: Extract from ss_tag_frequency or metadata if available.\n"
    "4. **Training Info**: Epochs, learning rate, resolution - if present in metadata.\n"
    "5. **Recommendations**: Best use cases, compatible pipelines, and settings.\n\n"
    "Be precise and technical. Use markdown formatting."
)


class GrokCore:
    def __init__(self, api_key: str):
        self.api_key = api_key.strip()
        if not self.api_key:
            raise ValueError("API Key de xAI no proporcionada.")

        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    # -- Resolucion de API Key -------------------------------------------------
    @staticmethod
    def resolve_api_key(api_key: str = "") -> str:
        """Resuelve la API Key desde el nodo o variable de entorno XAI_API_KEY."""
        key = (api_key or "").strip() or os.getenv("XAI_API_KEY", "").strip()
        if not key:
            raise ValueError(
                "API Key de xAI no encontrada. "
                "Proporcionala en el nodo o configura XAI_API_KEY."
            )
        return key

    # -- Metodo estatico de chat (para nodos de diagnostico) -------------------
    @staticmethod
    def chat_text(api_key: str, prompt: str, model: str,
                  system_prompt: str = "", **kwargs) -> str:
        """Wrapper estatico para chat completions que devuelve solo el texto."""
        core = GrokCore(api_key)
        res = core.chat_completion(
            model=model, prompt=prompt, system_prompt=system_prompt, **kwargs,
        )
        if res.get("error"):
            return f"API Error: {res.get('message')}"
        try:
            return res["choices"][0]["message"]["content"]
        except (KeyError, IndexError) as e:
            return f"Error parseando respuesta de la API: {e}"

    # -- Conversion de Tensores ------------------------------------------------
    @staticmethod
    def tensor_to_base64(tensor: torch.Tensor, format="JPEG", quality=85) -> str:
        """Convierte tensor [B, H, W, C] (float 0-1) a Base64."""
        try:
            if len(tensor.shape) == 4:
                tensor = tensor[0]
            image_np = (tensor.cpu().numpy() * 255.0).clip(0, 255).astype(np.uint8)
            img = Image.fromarray(image_np)
            buffered = BytesIO()
            img.save(buffered, format=format, quality=quality)
            return base64.b64encode(buffered.getvalue()).decode("utf-8")
        except Exception as e:
            log.error(f"[GrokCore] Error convirtiendo tensor a Base64: {e}")
            return ""

    @staticmethod
    def base64_to_tensor(b64_string: str) -> torch.Tensor:
        """Convierte Base64 a tensor [1, H, W, C]."""
        try:
            img_bytes = base64.b64decode(b64_string)
            img = Image.open(BytesIO(img_bytes)).convert("RGB")
            image_np = np.array(img).astype(np.float32) / 255.0
            return torch.from_numpy(image_np).unsqueeze(0)
        except Exception as e:
            log.error(f"[GrokCore] Error convirtiendo Base64 a tensor: {e}")
            return GrokCore.create_error_tensor()

    @staticmethod
    def url_to_tensor(url: str) -> torch.Tensor:
        """Descarga imagen desde URL temporal y la convierte a tensor."""
        try:
            response = requests.get(url, timeout=60)
            response.raise_for_status()
            img = Image.open(BytesIO(response.content)).convert("RGB")
            image_np = np.array(img).astype(np.float32) / 255.0
            return torch.from_numpy(image_np).unsqueeze(0)
        except Exception as e:
            log.error(f"[GrokCore] Error descargando imagen desde URL: {e}")
            return GrokCore.create_error_tensor()

    @staticmethod
    def create_error_tensor() -> torch.Tensor:
        """Genera una imagen ROJA de 512x512 para el sistema Anti-Crash."""
        error_tensor = torch.zeros(1, 512, 512, 3)
        error_tensor[:, :, :, 0] = 0.8
        return error_tensor

    # -- Llamadas REST a la API de xAI -----------------------------------------
    def chat_completion(self, model: str, prompt: str, system_prompt: str = "",
                        images_b64: list = None, **kwargs):
        """Endpoint universal para Texto y Vision via /v1/chat/completions."""
        url = f"{XAI_API_BASE}/chat/completions"
        messages = []

        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        if images_b64 and len(images_b64) > 0:
            user_content = [{"type": "text", "text": prompt}]
            for b64 in images_b64:
                if b64:
                    user_content.append({
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{b64}",
                            "detail": "high",
                        },
                    })
            messages.append({"role": "user", "content": user_content})
        else:
            messages.append({"role": "user", "content": prompt})

        payload = {"model": model, "messages": messages}
        payload.update(kwargs)

        try:
            log.info(f"[GrokCore] Enviando request a {model}... (Multimodal: {bool(images_b64)})")
            response = requests.post(url, headers=self.headers, json=payload, timeout=120)
            if not response.ok:
                err_msg = response.json().get("error", {}).get("message", response.text)
                log.error(f"[GrokCore] API HTTP Error {response.status_code}: {err_msg}")
                return {"error": True, "message": f"HTTP {response.status_code}: {err_msg}"}
            return response.json()
        except requests.exceptions.Timeout:
            return {"error": True, "message": "Timeout: La API de xAI tardo demasiado."}
        except Exception as e:
            return {"error": True, "message": f"Excepcion: {str(e)}"}

    def generate_image(self, prompt: str, model: str = "grok-imagine-image", **kwargs):
        """POST /v1/images/generations - generacion de imagenes (xAI 2026)."""
        url = f"{XAI_API_BASE}/images/generations"
        payload = {"prompt": prompt, "model": model, "response_format": "b64_json"}
        payload.update(kwargs)
        try:
            log.info(f"[GrokCore] Generando imagen con {model}...")
            response = requests.post(url, headers=self.headers, json=payload, timeout=180)
            if not response.ok:
                err_msg = response.json().get("error", {}).get("message", response.text)
                log.error(f"[GrokCore] Error generando imagen: {err_msg}")
                return {"error": True, "message": err_msg}
            return response.json()
        except Exception as e:
            log.error(f"[GrokCore] Fallo critico de red: {e}")
            return {"error": True, "message": str(e)}

    def edit_image(self, prompt: str, image_url: str,
                   model: str = "grok-imagine-image", **kwargs):
        """POST /v1/images/edits - edicion de imagenes (xAI 2026)."""
        url = f"{XAI_API_BASE}/images/edits"
        payload = {
            "prompt": prompt, "model": model,
            "image_url": image_url, "response_format": "b64_json",
        }
        payload.update(kwargs)
        try:
            log.info(f"[GrokCore] Editando imagen con {model}...")
            response = requests.post(url, headers=self.headers, json=payload, timeout=180)
            if not response.ok:
                err_msg = response.json().get("error", {}).get("message", response.text)
                log.error(f"[GrokCore] Error editando imagen: {err_msg}")
                return {"error": True, "message": err_msg}
            return response.json()
        except Exception as e:
            log.error(f"[GrokCore] Fallo critico de red: {e}")
            return {"error": True, "message": str(e)}

    # -- Video: submit + polling -----------------------------------------------
    def submit_video(self, endpoint: str, payload: dict) -> dict:
        """POST a endpoint de video, retorna JSON con request_id o error."""
        url = f"{XAI_API_BASE}{endpoint}"
        try:
            log.info(f"[GrokCore] Enviando peticion de video a {endpoint}...")
            response = requests.post(url, headers=self.headers, json=payload, timeout=60)
            if not response.ok:
                err_msg = response.json().get("error", {}).get("message", response.text)
                return {"error": True, "message": f"HTTP {response.status_code}: {err_msg}"}
            return response.json()
        except Exception as e:
            log.error(f"[GrokCore] Fallo en submit_video: {e}")
            return {"error": True, "message": str(e)}

    def poll_video(self, request_id: str, timeout: int = 300,
                   interval: int = 5) -> dict:
        """GET /v1/videos/{id} polling hasta done/failed/expired o timeout."""
        url = f"{XAI_API_BASE}/videos/{request_id}"
        start = time.time()
        while True:
            elapsed = time.time() - start
            if elapsed > timeout:
                return {"error": True, "message": f"Timeout: video no listo en {timeout}s."}
            try:
                response = requests.get(url, headers=self.headers, timeout=30)
                if not response.ok:
                    err_msg = response.json().get("error", {}).get("message", response.text)
                    return {"error": True, "message": f"HTTP {response.status_code}: {err_msg}"}
                data = response.json()
                status = data.get("status", "")
                if status == "done":
                    log.info(f"[GrokCore] Video listo tras {elapsed:.0f}s.")
                    return data
                elif status in ("failed", "expired"):
                    return {"error": True, "message": f"Video status: {status}"}
                log.info(f"[GrokCore] Video pendiente... ({elapsed:.0f}s / {timeout}s)")
                time.sleep(interval)
            except Exception as e:
                log.error(f"[GrokCore] Error en polling de video: {e}")
                return {"error": True, "message": str(e)}
