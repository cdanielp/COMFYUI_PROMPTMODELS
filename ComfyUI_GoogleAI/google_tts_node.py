"""
google_tts_node.py - PMS_GeminiTTS v2.0.0
==========================================
Text-to-Speech con Gemini via generateContent + responseModalities AUDIO.
Modelo: gemini-3.1-flash-tts-preview.
La respuesta viene como PCM s16le en base64 (24000 Hz mono).
"""

import base64
import io
import logging
import requests
import torch
import numpy as np

from .google_core import GoogleAICore, GEMINI_BASE_URL, GEMINI_TEXT_ENDPOINT

logger = logging.getLogger("ComfyUI_PromptModels")

_GEMINI_TTS_MODEL = "gemini-3.1-flash-tts-preview"
_PCM_SAMPLE_RATE  = 24000


class PMS_GeminiTTS:
    """
    Gemini Text to Speech.
    Convierte texto a audio via generateContent con responseModalities AUDIO.
    La respuesta viene como PCM s16le mono a 24000 Hz en base64.
    Outputs: tensor AUDIO de ComfyUI.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {
                    "multiline": True,
                    "default": "Hola, soy Gemini. Encantado de hablar contigo.",
                }),
            },
            "optional": {
                "voice_name": ("STRING", {
                    "default": "Aoede",
                    "tooltip": "Nombre de voz preconfigurada: Aoede, Charon, Fenrir, Kore, Puck.",
                }),
                "language_code": ("STRING", {
                    "default": "es-419",
                    "tooltip": "Codigo de idioma BCP-47. ej: es-419, en-US, fr-FR.",
                }),
                "api_key": ("STRING", {"default": ""}),
            },
        }

    RETURN_TYPES = ("AUDIO",)
    RETURN_NAMES = ("audio",)
    FUNCTION = "sintetizar"
    CATEGORY = "PromptModels/Google"

    def sintetizar(self, text, voice_name="Aoede", language_code="es-419", api_key=""):
        try:
            key = GoogleAICore.resolve_api_key(api_key)

            url = GEMINI_TEXT_ENDPOINT.format(
                base=GEMINI_BASE_URL, model=_GEMINI_TTS_MODEL, key=key
            )
            payload = {
                "contents": [{"role": "user", "parts": [{"text": text}]}],
                "generationConfig": {
                    "responseModalities": ["AUDIO"],
                    "speechConfig": {
                        "voiceConfig": {
                            "prebuiltVoiceConfig": {"voiceName": voice_name}
                        }
                    },
                },
            }

            logger.info(f"[PMS_GeminiTTS] voice={voice_name} | lang={language_code} | chars={len(text)}")
            response = requests.post(
                url,
                headers={"Content-Type": "application/json"},
                json=payload,
                timeout=120,
            )
            response.raise_for_status()
            data = response.json()

            audio_b64 = None
            for candidate in data.get("candidates", []):
                for part in candidate.get("content", {}).get("parts", []):
                    if "inlineData" in part:
                        mime = part["inlineData"].get("mimeType", "")
                        if "audio" in mime:
                            audio_b64 = part["inlineData"]["data"]
                            break
                if audio_b64:
                    break

            if audio_b64 is None:
                raise RuntimeError("La API no retorno datos de audio en la respuesta.")

            pcm_bytes = base64.b64decode(audio_b64)
            audio_tensor = _pcm_to_audio_tensor(pcm_bytes, _PCM_SAMPLE_RATE)
            logger.info(f"[PMS_GeminiTTS] Audio OK: {audio_tensor['waveform'].shape} @ {audio_tensor['sample_rate']}Hz")
            return (audio_tensor,)

        except Exception as e:
            logger.error(f"[PMS_GeminiTTS] Error: {e}")
            return (_silence(_PCM_SAMPLE_RATE),)


def _pcm_to_audio_tensor(pcm_bytes: bytes, sample_rate: int = 24000) -> dict:
    """Convierte PCM s16le a tensor AUDIO de ComfyUI {waveform, sample_rate}."""
    try:
        import torchaudio
        buf = io.BytesIO(pcm_bytes)
        try:
            waveform, sr = torchaudio.load(
                buf, format="raw", channels_first=True,
                encoding="PCM_S", bits_per_sample=16
            )
            waveform = waveform.float() / 32768.0
            return {"waveform": waveform.unsqueeze(0), "sample_rate": sr}
        except Exception:
            pass
    except ImportError:
        pass

    # Fallback manual: PCM s16le mono
    audio = np.frombuffer(pcm_bytes, dtype=np.int16).astype(np.float32) / 32768.0
    waveform = torch.from_numpy(audio).unsqueeze(0).unsqueeze(0)
    return {"waveform": waveform, "sample_rate": sample_rate}


def _silence(sample_rate: int = 24000) -> dict:
    return {"waveform": torch.zeros((1, 1, sample_rate)), "sample_rate": sample_rate}
