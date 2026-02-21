"""
google_audio_node.py - Nodos de Audio para ComfyUI (V2.0)
==========================================================
Lyria 3 | SynthID warnings filtrados automáticamente.

Autor: Prompt Models Studio | cdanielp
"""

import logging
import torch
from .google_core import GoogleAICore, DEFAULT_AUDIO_MODEL

logger = logging.getLogger("ComfyUI_GoogleAI")

AUDIO_MODELS = ["lyria-3"]


class GoogleAI_MusicDirector:
    """Genera 30s de música. Soporta imagen de referencia y control de voces."""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "prompt": ("STRING", {"multiline": True, "default": "An upbeat electronic track with synth pads and a driving beat"}),
                "vocals": ("BOOLEAN", {"default": False, "tooltip": "True=voces, False=instrumental."}),
            },
            "optional": {
                "api_key": ("STRING", {"default": ""}),
                "model": (AUDIO_MODELS, {"default": "lyria-3"}),
                "init_image": ("IMAGE", {"tooltip": "Imagen de referencia contextual."}),
            },
        }

    RETURN_TYPES = ("AUDIO",)
    RETURN_NAMES = ("audio",)
    FUNCTION = "generate_music"
    CATEGORY = "Google AI/Audio"

    def generate_music(self, prompt, vocals, api_key="", model="lyria-3", init_image=None):
        try:
            key = GoogleAICore.resolve_api_key(api_key)
            init_b64 = GoogleAICore.tensor_to_base64(init_image, 0) if init_image is not None else None

            audio_bytes = GoogleAICore.generate_audio(
                api_key=key, prompt=prompt, model=model,
                duration_seconds=30, include_vocals=vocals, init_image_b64=init_b64,
            )
            audio_dict = GoogleAICore.audio_bytes_to_dict(audio_bytes)
            logger.info(f"[MusicDirector] Audio: {audio_dict['waveform'].shape} @ {audio_dict['sample_rate']}Hz")
            return (audio_dict,)

        except Exception as e:
            logger.error(f"[MusicDirector] Error: {e}")
            return ({"waveform": torch.zeros(1, 1, 48000 * 5), "sample_rate": 48000},)


class GoogleAI_FoleyGenerator:
    """Genera sonido Foley a partir de frames de video espaciados."""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "video_frames": ("IMAGE", {"tooltip": "Tensor 4D [B, H, W, C] de frames."}),
                "prompt": ("STRING", {"multiline": True, "default": "Generate realistic foley sound effects for this video"}),
            },
            "optional": {
                "api_key": ("STRING", {"default": ""}),
                "model": (AUDIO_MODELS, {"default": "lyria-3"}),
                "max_frames_to_send": ("INT", {"default": 8, "min": 2, "max": 16}),
            },
        }

    RETURN_TYPES = ("AUDIO",)
    RETURN_NAMES = ("foley_audio",)
    FUNCTION = "generate_foley"
    CATEGORY = "Google AI/Audio"

    def generate_foley(self, video_frames, prompt, api_key="",
                       model="lyria-3", max_frames_to_send=8):
        try:
            key = GoogleAICore.resolve_api_key(api_key)
            total = video_frames.shape[0]

            if total <= max_frames_to_send:
                indices = list(range(total))
            else:
                step = total / max_frames_to_send
                indices = [int(i * step) for i in range(max_frames_to_send)]

            frames_b64 = [GoogleAICore.tensor_to_base64(video_frames, idx) for idx in indices]
            estimated_dur = min(30, max(5, total // 24))

            audio_bytes = GoogleAICore.generate_audio(
                api_key=key, prompt=prompt, model=model,
                duration_seconds=estimated_dur, video_frames_b64=frames_b64,
            )
            audio_dict = GoogleAICore.audio_bytes_to_dict(audio_bytes)
            logger.info(f"[FoleyGenerator] Foley: {audio_dict['waveform'].shape} @ {audio_dict['sample_rate']}Hz")
            return (audio_dict,)

        except Exception as e:
            logger.error(f"[FoleyGenerator] Error: {e}")
            return ({"waveform": torch.zeros(1, 1, 48000 * 5), "sample_rate": 48000},)
