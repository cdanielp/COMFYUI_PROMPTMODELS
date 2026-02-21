# ==============================================================================
# grok_core.py — Motor Central de ComfyUI_Grok (V2.0)
# ==============================================================================
# Capa de comunicación REST pura (sin SDKs) con la API de xAI.
# Maneja tensores estándar [B, H, W, C], conversión a Base64 y payloads multimodales.
# ==============================================================================

import os
import json
import base64
import requests
from io import BytesIO
from PIL import Image
import torch
import numpy as np
import logging

log = logging.getLogger("ComfyUI_GrokCore")

XAI_API_BASE = "https://api.x.ai/v1"

class GrokCore:
    def __init__(self, api_key: str):
        self.api_key = api_key.strip()
        if not self.api_key:
            raise ValueError("API Key de xAI no proporcionada.")
            
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

    # ── Conversión de Tensores ────────────────────────────────────────────────
    @staticmethod
    def tensor_to_base64(tensor: torch.Tensor, format="JPEG", quality=85) -> str:
        """
        Convierte un tensor de ComfyUI [B, H, W, C] (float 0.0-1.0) a Base64.
        Toma el primer frame del batch para enviarlo a la API.
        """
        try:
            # Asegurar que tenemos la dimensión correcta (tomamos el índice 0 del batch)
            if len(tensor.shape) == 4:
                tensor = tensor[0]
            
            # Desnormalizar de 0.0-1.0 a 0-255 y convertir a entero de 8 bits
            image_np = (tensor.cpu().numpy() * 255.0).clip(0, 255).astype(np.uint8)
            
            # Crear imagen PIL
            img = Image.fromarray(image_np)
            
            # Escribir en buffer de memoria
            buffered = BytesIO()
            # Usamos JPEG por defecto para reducir el tamaño del payload (menor latencia)
            img.save(buffered, format=format, quality=quality)
            
            # Codificar a Base64 string
            img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
            return img_str
            
        except Exception as e:
            log.error(f"[GrokCore] Error convirtiendo tensor a Base64: {e}")
            return ""

    @staticmethod
    def base64_to_tensor(b64_string: str) -> torch.Tensor:
        """
        Convierte un string Base64 devuelto por la API a un tensor de ComfyUI.
        """
        try:
            img_bytes = base64.b64decode(b64_string)
            img = Image.open(BytesIO(img_bytes)).convert("RGB")
            
            # Normalizar a float 0.0-1.0
            image_np = np.array(img).astype(np.float32) / 255.0
            # Añadir dimensión de Batch [1, H, W, C]
            tensor = torch.from_numpy(image_np).unsqueeze(0)
            return tensor
        except Exception as e:
            log.error(f"[GrokCore] Error convirtiendo Base64 a tensor: {e}")
            return GrokCore.create_error_tensor()

    @staticmethod
    def create_error_tensor() -> torch.Tensor:
        """
        Genera una imagen ROJA de 512x512 para el sistema Anti-Crash.
        Evita que ComfyUI detenga el workflow por un error HTTP 400/429.
        """
        error_tensor = torch.zeros(1, 512, 512, 3)
        error_tensor[:, :, :, 0] = 0.8  # Canal Rojo al 80%
        return error_tensor

    # ── Llamadas REST a la API de xAI ─────────────────────────────────────────
    def chat_completion(self, model: str, prompt: str, system_prompt: str = "", images_b64: list = None, **kwargs):
        """
        Endpoint universal para Texto y Visión.
        Si detecta imágenes en `images_b64`, cambia la estructura del payload a Multimodal.
        """
        url = f"{XAI_API_BASE}/chat/completions"
        messages = []
        
        # 1. Añadir System Prompt si existe
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
            
        # 2. Construir el mensaje del usuario (Texto o Multimodal)
        if images_b64 and len(images_b64) > 0:
            # Formato de Array (Visión)
            user_content = [{"type": "text", "text": prompt}]
            for b64 in images_b64:
                if b64:  # Ignorar strings vacíos
                    user_content.append({
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{b64}",
                            "detail": "high"  # Usar alta resolución por defecto para Grok Vision
                        }
                    })
            messages.append({"role": "user", "content": user_content})
        else:
            # Formato Simple (Texto puro)
            messages.append({"role": "user", "content": prompt})

        # 3. Empaquetar payload con parámetros adicionales (temperature, json_format, etc)
        payload = {
            "model": model,
            "messages": messages,
        }
        payload.update(kwargs)

        try:
            log.info(f"[GrokCore] Enviando request a {model}... (Multimodal: {bool(images_b64)})")
            response = requests.post(url, headers=self.headers, json=payload, timeout=120)
            
            # Manejar errores HTTP amigablemente
            if not response.ok:
                err_msg = response.json().get("error", {}).get("message", response.text)
                log.error(f"[GrokCore] API HTTP Error {response.status_code}: {err_msg}")
                return {"error": True, "message": f"HTTP {response.status_code}: {err_msg}"}
                
            return response.json()
            
        except requests.exceptions.Timeout:
            return {"error": True, "message": "Timeout: La API de xAI tardó demasiado en responder."}
        except Exception as e:
            return {"error": True, "message": f"Excepción en la petición: {str(e)}"}

    def generate_image(self, prompt: str, model: str = "grok-2-image-1212", **kwargs):
        """
        Endpoint para generación de imágenes desde cero (Text-to-Image).
        """
        url = f"{XAI_API_BASE}/images/generations"
        
        payload = {
            "prompt": prompt,
            "model": model,
            "response_format": "b64_json" # Fundamental para recibir el string base64 directo
        }
        payload.update(kwargs)

        try:
            log.info(f"[GrokCore] Generando imagen con {model}...")
            response = requests.post(url, headers=self.headers, json=payload, timeout=180)
            
            if not response.ok:
                err_msg = response.json().get("error", {}).get("message", response.text)
                log.error(f"[GrokCore] Error generando imagen HTTP {response.status_code}: {err_msg}")
                return {"error": True, "message": err_msg}
                
            return response.json()
            
        except Exception as e:
            log.error(f"[GrokCore] Fallo crítico de red: {e}")
            return {"error": True, "message": str(e)}
