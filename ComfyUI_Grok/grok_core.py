# grok_core.py
"""
Módulo central para conexión con xAI API (Grok)
"""
import os
import requests
import base64
from io import BytesIO
from PIL import Image

XAI_API_BASE = "https://api.x.ai/v1"


def get_api_key(key: str = None) -> str:
    """
    Obtiene API key del parámetro o variable de entorno
    """
    if key and key.strip():
        return key.strip()
    return os.getenv("XAI_API_KEY", "")


def call_grok_text(
    model: str,
    prompt: str,
    system_prompt: str = "",
    api_key: str = None,
    temperature: float = 1.0,
    max_tokens: int = 1024
) -> str:
    """
    Llamada a la API de chat/completions de xAI
    """
    key = get_api_key(api_key)
    if not key:
        raise ValueError("API key is required. Set XAI_API_KEY or provide api_key parameter.")
    
    headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json"
    }
    
    messages = []
    if system_prompt and system_prompt.strip():
        messages.append({"role": "system", "content": system_prompt.strip()})
    messages.append({"role": "user", "content": prompt})
    
    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens
    }
    
    response = requests.post(
        f"{XAI_API_BASE}/chat/completions",
        headers=headers,
        json=payload,
        timeout=120
    )
    
    if response.status_code != 200:
        error_data = response.json() if response.content else {}
        error_msg = error_data.get("error", {}).get("message", response.text)
        raise Exception(f"API Error ({response.status_code}): {error_msg}")
    
    data = response.json()
    return data["choices"][0]["message"]["content"]


def call_grok_image(
    model: str,
    prompt: str,
    size: str = "1024x1024",
    n: int = 1,
    api_key: str = None,
    response_format: str = "b64_json"
) -> bytes:
    """
    Llamada a la API de images/generations de xAI
    Retorna bytes de la imagen
    """
    key = get_api_key(api_key)
    if not key:
        raise ValueError("API key is required. Set XAI_API_KEY or provide api_key parameter.")
    
    headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": model,
        "prompt": prompt,
        "size": size,
        "n": n,
        "response_format": response_format
    }
    
    response = requests.post(
        f"{XAI_API_BASE}/images/generations",
        headers=headers,
        json=payload,
        timeout=180
    )
    
    if response.status_code != 200:
        error_data = response.json() if response.content else {}
        error_msg = error_data.get("error", {}).get("message", response.text)
        raise Exception(f"API Error ({response.status_code}): {error_msg}")
    
    data = response.json()
    
    # Manejar respuesta base64 o URL
    image_data = data["data"][0]
    if "b64_json" in image_data:
        return base64.b64decode(image_data["b64_json"])
    elif "url" in image_data:
        img_response = requests.get(image_data["url"], timeout=60)
        return img_response.content
    else:
        raise Exception("No image data in response")


def image_bytes_to_tensor(img_bytes: bytes):
    """
    Convierte bytes de imagen a tensor de ComfyUI
    Format: [B, H, W, C] con valores 0-1
    """
    import torch
    import numpy as np
    
    image = Image.open(BytesIO(img_bytes)).convert("RGB")
    img_np = np.array(image).astype(np.float32) / 255.0
    tensor = torch.from_numpy(img_np).unsqueeze(0)
    
    return tensor


def tensor_to_base64(tensor) -> str:
    """
    Convierte tensor de ComfyUI a base64
    """
    import torch
    import numpy as np
    
    # Tomar primera imagen del batch
    if len(tensor.shape) == 4:
        tensor = tensor[0]
    
    # Convertir a numpy y escalar a 0-255
    img_np = (tensor.cpu().numpy() * 255).astype(np.uint8)
    
    # Crear imagen PIL
    img = Image.fromarray(img_np)
    
    # Convertir a base64
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode("utf-8")
