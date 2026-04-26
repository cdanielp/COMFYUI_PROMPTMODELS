"""
grok_tts_node.py - PMS_GrokTTS v2.0.0
========================================
Text-to-Speech con Grok via xAI API.
Endpoint: POST https://api.x.ai/v1/audio/speech
La API devuelve audio MP3 binario.
Conversion: MP3 -> torchaudio (primario) -> ffmpeg+scipy (fallback).
Speech tags soportados: [laugh] [sigh] [whisper]
Precio: $4.20/1M chars
"""

import os
import io
import logging
import requests
import torch
import numpy as np

logger = logging.getLogger("ComfyUI_PromptModels")

_XAI_BASE    = "https://api.x.ai/v1"
_TTS_VOICES  = ["ara", "eve", "leo", "rex", "sal"]


class PMS_GrokTTS:
    """
    Grok Text to Speech.
    Speech tags: usa [laugh] [sigh] [whisper] inline en el texto.
    Precio: $4.20/1M chars.
    Output: tensor AUDIO de ComfyUI + nombre de voz usada.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {
                    "multiline": True,
                    "default": "Hola, soy Grok. [laugh] Me alegra hablar contigo.",
                    "tooltip": "Speech tags: [laugh] [sigh] [whisper] inline en el texto.",
                }),
                "voice": (_TTS_VOICES, {
                    "default": "ara",
                    "tooltip": "ara=femenina neutra | eve | leo | rex | sal",
                }),
                "speed": ("FLOAT", {
                    "default": 1.0, "min": 0.5, "max": 2.0, "step": 0.1,
                    "tooltip": "Velocidad del habla (0.5=lento, 2.0=rapido).",
                }),
            },
            "optional": {
                "api_key": ("STRING", {"default": ""}),
            },
        }

    RETURN_TYPES = ("AUDIO", "STRING")
    RETURN_NAMES = ("audio", "voz_usada")
    FUNCTION = "sintetizar"
    CATEGORY = "PromptModels/Grok"

    def sintetizar(self, text, voice, speed, api_key=""):
        key = (api_key or "").strip() or os.getenv("XAI_API_KEY", "")
        if not key:
            logger.error("[PMS_GrokTTS] API Key no configurada.")
            return (_silence(), voice)

        headers = {
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model":           "grok-tts",
            "input":           text,
            "voice":           voice,
            "speed":           speed,
            "response_format": "mp3",
        }

        try:
            logger.info(f"[PMS_GrokTTS] voice={voice} | speed={speed} | chars={len(text)}")
            response = requests.post(
                f"{_XAI_BASE}/audio/speech",
                headers=headers,
                json=payload,
                timeout=120,
            )
            response.raise_for_status()
            mp3_bytes = response.content

            audio_dict = _mp3_to_audio_tensor(mp3_bytes)
            logger.info(f"[PMS_GrokTTS] Audio OK: {audio_dict['waveform'].shape}")
            return (audio_dict, voice)

        except Exception as e:
            logger.error(f"[PMS_GrokTTS] Error: {e}")
            return (_silence(), voice)


def _mp3_to_audio_tensor(mp3_bytes: bytes) -> dict:
    """Convierte MP3 bytes a tensor AUDIO de ComfyUI. Fallback scipy+ffmpeg."""
    buf = io.BytesIO(mp3_bytes)

    # Intento primario: torchaudio
    try:
        import torchaudio
        waveform, sample_rate = torchaudio.load(buf)
        waveform = waveform.float()
        max_val = waveform.abs().max()
        if max_val > 1.0:
            waveform = waveform / max_val
        return {"waveform": waveform.unsqueeze(0), "sample_rate": sample_rate}
    except ImportError:
        pass
    except Exception as e:
        logger.warning(f"[PMS_GrokTTS] torchaudio fallo ({e}). Intentando fallback ffmpeg+scipy.")

    # Fallback: ffmpeg convierte MP3 -> WAV, scipy lo lee
    import tempfile, subprocess, os as _os
    tmp_mp3 = tmp_wav = None
    try:
        from scipy.io import wavfile
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
            f.write(mp3_bytes)
            tmp_mp3 = f.name
        tmp_wav = tmp_mp3.replace(".mp3", ".wav")
        subprocess.run(
            ["ffmpeg", "-y", "-i", tmp_mp3, "-ar", "44100", tmp_wav],
            capture_output=True, timeout=30, check=True,
        )
        sr, data = wavfile.read(tmp_wav)
        audio = data.astype(np.float32) / 32768.0
        if audio.ndim == 1:
            audio = audio[np.newaxis, :]
        else:
            audio = audio.T
        return {"waveform": torch.from_numpy(audio).unsqueeze(0), "sample_rate": sr}
    except Exception as e2:
        logger.error(f"[PMS_GrokTTS] Fallback ffmpeg+scipy fallo: {e2}")
        return _silence()
    finally:
        for p in [tmp_mp3, tmp_wav]:
            if p and _os.path.exists(p):
                try:
                    _os.unlink(p)
                except OSError:
                    pass


def _silence() -> dict:
    return {"waveform": torch.zeros((1, 1, 22050)), "sample_rate": 22050}
