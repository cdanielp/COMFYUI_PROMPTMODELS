"""
google_audio_node.py - Nodos de Audio para ComfyUI (V2.1)
==========================================================
Lyria 3 | SynthID warnings filtrados | Video-to-Music

V2.1 Cambios:
  - MusicDirector: nuevo puerto video_frames (IMAGE) para Video-to-Music
  - ⚠️ Type Mismatch Fallback: NUNCA devolver imagen de error.
    En caso de HTTP 400/safety/fallo → audio silencioso (1 seg @ 48kHz).
  - Sin seed manual (Lyria 3 no lo soporta).

Autor: Prompt Models Studio | cdanielp
"""

import logging
import torch
from .google_core import GoogleAICore, DEFAULT_AUDIO_MODEL

logger = logging.getLogger("ComfyUI_GoogleAI")

AUDIO_MODELS = ["lyria-3"]

# Audio silencioso estándar: 1 segundo @ 48kHz mono
SILENT_AUDIO = {"waveform": torch.zeros(1, 1, 48000), "sample_rate": 48000}


class GoogleAI_MusicDirector:
    """
    Genera 30s de música con Lyria 3.
    Soporta imagen de referencia, video frames y control de voces.
    ⚠️ Error → audio silencioso (nunca imagen roja, evita Type Mismatch).
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "prompt": ("STRING", {
                    "multiline": True,
                    "default": "An upbeat electronic track with synth pads and a driving beat",
                }),
                "vocals": ("BOOLEAN", {
                    "default": False,
                    "tooltip": "True=voces y canto, False=instrumental.",
                }),
            },
            "optional": {
                "api_key": ("STRING", {"default": ""}),
                "model": (AUDIO_MODELS, {"default": "lyria-3"}),
                "init_image": ("IMAGE", {
                    "tooltip": "Imagen de referencia contextual para la música.",
                }),
                "video_frames": ("IMAGE", {
                    "tooltip": "Frames de video [B,H,W,C] para Video-to-Music (Lyria 3).",
                }),
            },
        }

    RETURN_TYPES = ("AUDIO",)
    RETURN_NAMES = ("audio",)
    FUNCTION = "generate_music"
    CATEGORY = "Google AI/Audio"

    def generate_music(self, prompt, vocals, api_key="", model="lyria-3",
                       init_image=None, video_frames=None):
        try:
            key = GoogleAICore.resolve_api_key(api_key)

            # Imagen de referencia (máx 1)
            init_b64 = None
            if init_image is not None:
                init_b64 = GoogleAICore.tensor_to_base64(init_image, 0)
                logger.info("[MusicDirector] Imagen de referencia adjunta")

            # Video frames para Video-to-Music
            frames_b64 = None
            if video_frames is not None:
                total = video_frames.shape[0]
                max_send = min(8, total)
                if total <= max_send:
                    indices = list(range(total))
                else:
                    step = total / max_send
                    indices = [int(i * step) for i in range(max_send)]

                frames_b64 = [GoogleAICore.tensor_to_base64(video_frames, idx) for idx in indices]
                logger.info(f"[MusicDirector] Video-to-Music: {len(indices)}/{total} frames adjuntos")

            audio_bytes = GoogleAICore.generate_audio(
                api_key=key,
                prompt=prompt,
                model=model,
                duration_seconds=30,
                include_vocals=vocals,
                init_image_b64=init_b64,
                video_frames_b64=frames_b64,
            )

            audio_dict = GoogleAICore.audio_bytes_to_dict(audio_bytes)
            logger.info(
                f"[MusicDirector] ✅ Audio: {audio_dict['waveform'].shape} "
                f"@ {audio_dict['sample_rate']}Hz"
            )
            return (audio_dict,)

        except Exception as e:
            # ⚠️ CRÍTICO: Devolver audio silencioso, NUNCA imagen de error
            logger.error(f"[MusicDirector] Error (devolviendo audio silencioso): {e}")
            return ({"waveform": torch.zeros(1, 1, 48000), "sample_rate": 48000},)


class GoogleAI_FoleyGenerator:
    """
    Genera sonido Foley a partir de frames de video espaciados.
    ⚠️ Error → audio silencioso (nunca imagen roja, evita Type Mismatch).
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "video_frames": ("IMAGE", {
                    "tooltip": "Tensor 4D [B, H, W, C] de frames de video.",
                }),
                "prompt": ("STRING", {
                    "multiline": True,
                    "default": "Generate realistic foley sound effects for this video",
                }),
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
                api_key=key,
                prompt=prompt,
                model=model,
                duration_seconds=estimated_dur,
                video_frames_b64=frames_b64,
            )

            audio_dict = GoogleAICore.audio_bytes_to_dict(audio_bytes)
            logger.info(
                f"[FoleyGenerator] ✅ Foley: {audio_dict['waveform'].shape} "
                f"@ {audio_dict['sample_rate']}Hz"
            )
            return (audio_dict,)

        except Exception as e:
            # ⚠️ CRÍTICO: Devolver audio silencioso, NUNCA imagen de error
            logger.error(f"[FoleyGenerator] Error (devolviendo audio silencioso): {e}")
            return ({"waveform": torch.zeros(1, 1, 48000), "sample_rate": 48000},)
