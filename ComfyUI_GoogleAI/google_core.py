# google_core.py
import requests
import base64
from io import BytesIO
from PIL import Image

BASE_URL = "https://generativelanguage.googleapis.com/v1beta"

class GoogleAICore:
    def __init__(self, api_key: str, model: str):
        self.api_key = api_key
        self.model = model

    def generate_text(self, prompt: str, system_prompt: str = ""):
        """
        Genera texto usando Gemini API
        """
        headers = {
            "Content-Type": "application/json",
            "x-goog-api-key": self.api_key
        }

        parts = [{"text": prompt}]

        payload = {
            "contents": [{"parts": parts}],
        }

        # System instruction como campo separado (método correcto en Gemini)
        if system_prompt:
            payload["systemInstruction"] = {
                "parts": [{"text": system_prompt}]
            }

        response = requests.post(
            f"{BASE_URL}/models/{self.model}:generateContent",
            headers=headers,
            json=payload,
            timeout=120
        )

        return response.json()

    def generate_image(self, prompt: str, system_prompt: str = "", images: list = None, 
                       width: int = 1024, height: int = 1024):
        """
        Genera imagen usando Gemini API (modelos con capacidad de imagen)
        """
        headers = {
            "Content-Type": "application/json",
            "x-goog-api-key": self.api_key
        }

        parts = []
        
        # Agregar imágenes de referencia primero
        if images:
            for img_data in images:
                parts.append({
                    "inlineData": {
                        "mimeType": "image/png",
                        "data": img_data
                    }
                })
        
        # Agregar el prompt
        parts.append({"text": prompt})

        payload = {
            "contents": [{"parts": parts}],
            "generationConfig": {
                "responseModalities": ["TEXT", "IMAGE"],
            }
        }

        # System instruction
        if system_prompt:
            payload["systemInstruction"] = {
                "parts": [{"text": system_prompt}]
            }

        response = requests.post(
            f"{BASE_URL}/models/{self.model}:generateContent",
            headers=headers,
            json=payload,
            timeout=300
        )

        return response.json()

    @staticmethod
    def get_available_models(api_key: str):
        """
        Obtiene lista de modelos disponibles
        """
        headers = {
            "x-goog-api-key": api_key
        }
        
        response = requests.get(
            f"{BASE_URL}/models",
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            models = [m.get("name", "").replace("models/", "") for m in data.get("models", [])]
            return models
        return []

    @staticmethod
    def tensor_to_base64(tensor):
        """
        Convierte tensor de ComfyUI a base64
        ComfyUI IMAGE format: [B, H, W, C] con valores 0-1
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

    @staticmethod
    def base64_to_tensor(b64_string):
        """
        Convierte base64 a tensor de ComfyUI
        """
        import torch
        import numpy as np
        
        img_bytes = base64.b64decode(b64_string)
        img = Image.open(BytesIO(img_bytes)).convert("RGB")
        
        # Convertir a numpy y normalizar a 0-1
        img_np = np.array(img).astype(np.float32) / 255.0
        
        # Convertir a tensor [B, H, W, C]
        tensor = torch.from_numpy(img_np).unsqueeze(0)
        
        return tensor
