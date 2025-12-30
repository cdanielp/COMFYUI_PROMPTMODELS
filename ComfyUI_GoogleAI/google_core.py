# google_core.py
import requests
import base64
import random
from io import BytesIO
from PIL import Image

BASE_URL = "https://generativelanguage.googleapis.com/v1beta"


class GoogleAICore:
    def __init__(self, api_key: str, model: str):
        self.api_key = api_key
        self.model = model

    def generate_text(self, prompt: str, system_prompt: str = "", temperature: float = 1.0,
                      images: list = None, audio_data: list = None, video_data: list = None,
                      file_data: list = None, seed: int = 0):
        """
        Genera texto usando Gemini API con soporte multimodal
        
        Args:
            prompt: Texto del prompt
            system_prompt: Instrucciones del sistema
            temperature: Creatividad (0.0-2.0)
            images: Lista de imágenes en base64
            audio_data: Lista de audio en base64 con mime_type
            video_data: Lista de video en base64 con mime_type
            file_data: Lista de archivos en base64 con mime_type
            seed: Semilla para reproducibilidad
        """
        headers = {
            "Content-Type": "application/json",
            "x-goog-api-key": self.api_key
        }

        parts = []

        # Agregar imágenes
        if images:
            for img_data in images:
                parts.append({
                    "inlineData": {
                        "mimeType": "image/png",
                        "data": img_data
                    }
                })

        # Agregar audio
        if audio_data:
            for audio in audio_data:
                if isinstance(audio, dict):
                    parts.append({
                        "inlineData": {
                            "mimeType": audio.get("mime_type", "audio/wav"),
                            "data": audio.get("data", "")
                        }
                    })
                else:
                    parts.append({
                        "inlineData": {
                            "mimeType": "audio/wav",
                            "data": audio
                        }
                    })

        # Agregar video
        if video_data:
            for video in video_data:
                if isinstance(video, dict):
                    parts.append({
                        "inlineData": {
                            "mimeType": video.get("mime_type", "video/mp4"),
                            "data": video.get("data", "")
                        }
                    })
                else:
                    parts.append({
                        "inlineData": {
                            "mimeType": "video/mp4",
                            "data": video
                        }
                    })

        # Agregar archivos (PDF, etc)
        if file_data:
            for file in file_data:
                if isinstance(file, dict):
                    parts.append({
                        "inlineData": {
                            "mimeType": file.get("mime_type", "application/pdf"),
                            "data": file.get("data", "")
                        }
                    })
                else:
                    parts.append({
                        "inlineData": {
                            "mimeType": "application/pdf",
                            "data": file
                        }
                    })

        # Agregar el prompt de texto
        parts.append({"text": prompt})

        # Configuración de generación
        generation_config = {
            "temperature": temperature
        }

        # Agregar seed si no es 0
        if seed != 0:
            generation_config["seed"] = seed

        payload = {
            "contents": [{"parts": parts}],
            "generationConfig": generation_config
        }

        # System instruction como campo separado
        if system_prompt:
            payload["systemInstruction"] = {
                "parts": [{"text": system_prompt}]
            }

        response = requests.post(
            f"{BASE_URL}/models/{self.model}:generateContent",
            headers=headers,
            json=payload,
            timeout=180
        )

        return response.json()

    def generate_image(self, prompt: str, system_prompt: str = "", images: list = None,
                       aspect_ratio: str = "1:1", image_size: str = "1K",
                       seed: int = 0, response_modalities: list = None):
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

        # Configuración de generación
        generation_config = {
            "responseModalities": response_modalities or ["TEXT", "IMAGE"],
            "imageConfig": {
                "aspectRatio": aspect_ratio,
                "imageSize": image_size
            }
        }

        # Agregar seed si no es 0
        if seed != 0:
            generation_config["seed"] = seed

        payload = {
            "contents": [{"parts": parts}],
            "generationConfig": generation_config
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
    def get_random_seed():
        """Genera una semilla aleatoria"""
        return random.randint(1, 2147483647)

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

    @staticmethod
    def audio_to_base64(audio_tensor, sample_rate: int = 44100):
        """
        Convierte tensor de audio a base64 WAV
        """
        import torch
        import numpy as np
        import wave
        import struct

        # Convertir tensor a numpy
        if isinstance(audio_tensor, torch.Tensor):
            audio_np = audio_tensor.cpu().numpy()
        else:
            audio_np = np.array(audio_tensor)

        # Normalizar a int16
        if audio_np.max() <= 1.0:
            audio_np = (audio_np * 32767).astype(np.int16)
        else:
            audio_np = audio_np.astype(np.int16)

        # Crear WAV en memoria
        buffer = BytesIO()
        with wave.open(buffer, 'wb') as wav:
            wav.setnchannels(1)
            wav.setsampwidth(2)
            wav.setframerate(sample_rate)
            wav.writeframes(audio_np.tobytes())

        buffer.seek(0)
        return base64.b64encode(buffer.read()).decode("utf-8")
