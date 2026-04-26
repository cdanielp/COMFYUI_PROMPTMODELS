"""
grok_stt_node.py - PMS_GrokSTT v2.0.0
========================================
Speech-to-Text con Grok via xAI API.
Endpoint: POST https://api.x.ai/v1/audio/transcriptions
Input: tensor AUDIO de ComfyUI -> WAV temporal -> multipart/form-data.
Output: transcripcion (STRING) + idioma detectado (STRING).
"""

import os
import io
import logging
import tempfile
import requests
import torch
import numpy as np

logger = logging.getLogger("ComfyUI_PromptModels")

_XAI_BASE = "https://api.x.ai/v1"


class PMS_GrokSTT:
    """
    Grok Speech to Text.
    Convierte tensor AUDIO de ComfyUI a texto via xAI transcriptions API.
    Conversion: tensor -> WAV en memoria -> multipart/form-data.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "audio": ("AUDIO", {
                    "tooltip": "Tensor AUDIO de ComfyUI {waveform, sample_rate}.",
                }),
            },
            "optional": {
                "language": ("STRING", {
                    "default": "es",
                    "tooltip": "Codigo ISO 639-1 del idioma. ej: es, en, fr, de.",
                }),
                "api_key": ("STRING", {"default": ""}),
            },
        }

    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("transcripcion", "idioma_detectado")
    FUNCTION = "transcribir"
    CATEGORY = "PromptModels/Grok"

    def transcribir(self, audio, language="es", api_key=""):
        key = (api_key or "").strip() or os.getenv("XAI_API_KEY", "")
        if not key:
            logger.error("[PMS_GrokSTT] API Key no configurada.")
            return ("Error: API Key de xAI requerida.", language)

        try:
            wav_bytes = _audio_tensor_to_wav(audio)
            if wav_bytes is None:
                return ("Error: no se pudo convertir el audio a WAV.", language)

            headers = {"Authorization": f"Bearer {key}"}
            files = {
                "file":            ("audio.wav", wav_bytes, "audio/wav"),
                "model":           (None, "grok-stt"),
                "language":        (None, language),
                "response_format": (None, "json"),
            }

            logger.info(f"[PMS_GrokSTT] Transcribiendo audio ({len(wav_bytes)} bytes, lang={language})...")
            response = requests.post(
                f"{_XAI_BASE}/audio/transcriptions",
                headers=headers,
                files=files,
                timeout=120,
            )
            response.raise_for_status()
            data = response.json()

            transcripcion     = data.get("text", "")
            idioma_detectado  = data.get("language", language)
            logger.info(f"[PMS_GrokSTT] Transcripcion OK: {len(transcripcion)} chars.")
            return (transcripcion, idioma_detectado)

        except Exception as e:
            logger.error(f"[PMS_GrokSTT] Error: {e}")
            return (f"Error: {str(e)}", language)


def _audio_tensor_to_wav(audio_dict: dict):
    """
    Convierte tensor AUDIO de ComfyUI {waveform, sample_rate} a bytes WAV.
    waveform shape esperado: [batch, channels, samples].
    Retorna bytes o None si falla.
    """
    try:
        waveform    = audio_dict.get("waveform")
        sample_rate = audio_dict.get("sample_rate", 44100)

        if waveform is None:
            return None

        # Normalizar a [channels, samples]
        if waveform.dim() == 3:
            waveform = waveform[0]
        if waveform.dim() == 2:
            waveform = waveform.mean(dim=0, keepdim=True)

        audio_np = (waveform[0].cpu().numpy() * 32767).clip(-32768, 32767).astype(np.int16)

        buf = io.BytesIO()

        # Intento primario: torchaudio
        try:
            import torchaudio
            torchaudio.save(
                buf,
                torch.from_numpy(audio_np).unsqueeze(0),
                sample_rate,
                format="wav",
            )
            return buf.getvalue()
        except ImportError:
            pass
        except Exception as e:
            logger.warning(f"[PMS_GrokSTT] torchaudio.save fallo ({e}). Intentando scipy.")

        # Fallback: scipy.io.wavfile
        from scipy.io import wavfile
        wavfile.write(buf, sample_rate, audio_np)
        return buf.getvalue()

    except Exception as e:
        logger.error(f"[PMS_GrokSTT] Error convirtiendo audio a WAV: {e}")
        return None
