"""
google_text_node.py - Nodo Multimodal Maestro para ComfyUI (V2.1)
==================================================================
Gemini 3.1 Pro | Fusiona texto + visión + video + audio + documentos.

V2.1 Cambios:
  - TextNode ahora es multimodal maestro (fusiona TextVisionNode)
  - 5 puertos image_1..image_5 opcionales
  - video_frames (IMAGE) para compatibilidad VHS/Load Video
  - video_path (STRING) para ruta de archivo local
  - audio (AUDIO) para análisis de audio
  - files (cualquier tipo) para documentos
  - seed con sanitización 64→32 bits
  - TextVisionNode mantenido por retrocompatibilidad

Autor: Prompt Models Studio | cdanielp
"""

import os
import base64
import logging
from .google_core import GoogleAICore

logger = logging.getLogger("ComfyUI_GoogleAI")

TEXT_MODELS = [
    "gemini-3.1-pro-preview",
    "gemini-2.5-pro-preview-06-05",
    "gemini-2.5-flash-preview-05-20",
    "gemini-2.5-flash-lite-preview-06-17",
]


class GoogleAI_TextNode:
    """
    Nodo multimodal maestro con Gemini.
    Acepta texto, hasta 5 imágenes, video (frames o path), audio,
    documentos, YouTube y thinking budget. Un solo nodo para todo.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "prompt": ("STRING", {
                    "multiline": True,
                    "default": "Describe esta imagen en detalle.",
                }),
                "model": (TEXT_MODELS, {"default": "gemini-3.1-pro-preview"}),
                "thinking_budget": (["Off", "Low", "High"], {
                    "default": "Off",
                    "tooltip": "Low=1024 tokens, High=8192 tokens de razonamiento.",
                }),
            },
            "optional": {
                "api_key": ("STRING", {"default": ""}),
                "system_prompt": ("STRING", {
                    "multiline": True,
                    "default": "",
                    "tooltip": "Instrucción de sistema para guiar el comportamiento de Gemini.",
                }),
                # --- Imágenes (hasta 5) ---
                "image_1": ("IMAGE", {"tooltip": "Imagen de entrada 1."}),
                "image_2": ("IMAGE", {"tooltip": "Imagen de entrada 2."}),
                "image_3": ("IMAGE", {"tooltip": "Imagen de entrada 3."}),
                "image_4": ("IMAGE", {"tooltip": "Imagen de entrada 4."}),
                "image_5": ("IMAGE", {"tooltip": "Imagen de entrada 5."}),
                # --- Video ---
                "video_frames": ("IMAGE", {
                    "tooltip": "Frames de video [B,H,W,C] desde Load Video / VHS.",
                }),
                "video_path": ("STRING", {
                    "default": "",
                    "tooltip": "Ruta local a un archivo de video (.mp4, .webm).",
                }),
                # --- Audio ---
                "audio": ("AUDIO", {
                    "tooltip": "Diccionario de audio ComfyUI {waveform, sample_rate}.",
                }),
                # --- Documentos ---
                "files": ("*", {
                    "tooltip": "Cualquier dato para inyectar como contexto textual.",
                }),
                # --- URLs ---
                "youtube_url": ("STRING", {
                    "default": "",
                    "tooltip": "URL de YouTube para análisis de video.",
                }),
                # --- Parámetros de generación ---
                "max_tokens": ("INT", {"default": 4096, "min": 64, "max": 65536, "step": 64}),
                "temperature": ("FLOAT", {"default": 0.7, "min": 0.0, "max": 2.0, "step": 0.05}),
                "seed": ("INT", {
                    "default": 0,
                    "min": 0,
                    "max": 0xFFFFFFFFFFFFFFFF,
                    "tooltip": "Seed de 64 bits. Se sanitiza a 32 bits.",
                }),
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("text",)
    FUNCTION = "generate_text"
    CATEGORY = "Google AI/Text"

    def generate_text(self, prompt, model, thinking_budget,
                      api_key="", system_prompt="",
                      image_1=None, image_2=None, image_3=None,
                      image_4=None, image_5=None,
                      video_frames=None, video_path="",
                      audio=None, files=None, youtube_url="",
                      max_tokens=4096, temperature=0.7, seed=0):
        try:
            key = GoogleAICore.resolve_api_key(api_key)
            extra_parts = []

            # === Imágenes (hasta 5) ===
            for idx, img in enumerate([image_1, image_2, image_3, image_4, image_5], 1):
                if img is not None:
                    img_b64 = GoogleAICore.tensor_to_base64(img, index=0)
                    extra_parts.append({
                        "inlineData": {"mimeType": "image/png", "data": img_b64}
                    })
                    logger.info(f"[TextNode] Imagen {idx} adjunta ({img.shape})")

            # === Video frames (tensor IMAGE de VHS/Load Video) ===
            if video_frames is not None:
                total_frames = video_frames.shape[0]
                # Enviar frames espaciados (máx 8 para no exceder contexto)
                max_send = min(8, total_frames)
                if total_frames <= max_send:
                    indices = list(range(total_frames))
                else:
                    step = total_frames / max_send
                    indices = [int(i * step) for i in range(max_send)]

                for fi in indices:
                    frame_b64 = GoogleAICore.tensor_to_base64(video_frames, fi)
                    extra_parts.append({
                        "inlineData": {"mimeType": "image/png", "data": frame_b64}
                    })
                logger.info(f"[TextNode] Video: {len(indices)}/{total_frames} frames adjuntos")

            # === Video path (archivo local) ===
            if video_path and video_path.strip() and os.path.isfile(video_path.strip()):
                vpath = video_path.strip()
                ext = os.path.splitext(vpath)[1].lower()
                mime_map = {".mp4": "video/mp4", ".webm": "video/webm", ".avi": "video/x-msvideo"}
                mime = mime_map.get(ext, "video/mp4")
                try:
                    with open(vpath, "rb") as vf:
                        vb64 = base64.b64encode(vf.read()).decode("utf-8")
                    extra_parts.append({
                        "inlineData": {"mimeType": mime, "data": vb64}
                    })
                    logger.info(f"[TextNode] Video file adjunto: {vpath}")
                except Exception as ve:
                    logger.warning(f"[TextNode] No se pudo leer video: {ve}")

            # === Audio ===
            if audio is not None:
                try:
                    import torchaudio
                    import io as _io
                    waveform = audio.get("waveform", audio.get("audio"))
                    sr = audio.get("sample_rate", 48000)
                    if waveform is not None:
                        if waveform.dim() == 3:
                            waveform = waveform.squeeze(0)
                        buf = _io.BytesIO()
                        torchaudio.save(buf, waveform, sr, format="wav")
                        audio_b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
                        extra_parts.append({
                            "inlineData": {"mimeType": "audio/wav", "data": audio_b64}
                        })
                        logger.info(f"[TextNode] Audio adjunto: {waveform.shape} @ {sr}Hz")
                except Exception as ae:
                    logger.warning(f"[TextNode] No se pudo procesar audio: {ae}")

            # === Documentos / Files (stringify) ===
            if files is not None:
                try:
                    file_text = str(files)[:10000]
                    extra_parts.append({"text": f"[DOCUMENTO ADJUNTO]\n{file_text}"})
                    logger.info(f"[TextNode] Documento adjunto ({len(file_text)} chars)")
                except Exception as fe:
                    logger.warning(f"[TextNode] No se pudo procesar files: {fe}")

            # === YouTube URL ===
            if youtube_url and youtube_url.strip():
                extra_parts.append({
                    "fileData": {"mimeType": "video/*", "fileUri": youtube_url.strip()}
                })
                logger.info(f"[TextNode] YouTube URL adjunta: {youtube_url.strip()}")

            # === Configuración de generación ===
            safe_seed = GoogleAICore.safe_seed(seed)
            gen_config = {
                "maxOutputTokens": max_tokens,
                "temperature": temperature,
                "seed": safe_seed,
            }
            tb = thinking_budget if thinking_budget != "Off" else None

            result = GoogleAICore.call_gemini_text(
                api_key=key,
                prompt=prompt,
                model=model,
                system_instruction=system_prompt if system_prompt else None,
                thinking_budget=tb,
                extra_parts=extra_parts if extra_parts else None,
                generation_config=gen_config,
            )
            return (result,)

        except Exception as e:
            logger.error(f"[TextNode] Error: {e}")
            return (f"❌ Error: {str(e)}",)


class GoogleAI_TextVisionNode:
    """
    Análisis de imágenes con Gemini Vision. Requiere imagen obligatoria.
    ⚠️ Retrocompatibilidad: Usa GoogleAI_TextNode con image_1 para la misma función.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "prompt": ("STRING", {"multiline": True, "default": "Describe esta imagen en detalle."}),
                "model": (TEXT_MODELS, {"default": "gemini-3.1-pro-preview"}),
            },
            "optional": {
                "api_key": ("STRING", {"default": ""}),
                "system_prompt": ("STRING", {"multiline": True, "default": ""}),
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("analysis",)
    FUNCTION = "analyze_image"
    CATEGORY = "Google AI/Text"

    def analyze_image(self, image, prompt, model, api_key="", system_prompt=""):
        try:
            key = GoogleAICore.resolve_api_key(api_key)
            img_b64 = GoogleAICore.tensor_to_base64(image, index=0)
            extra_parts = [{"inlineData": {"mimeType": "image/png", "data": img_b64}}]

            result = GoogleAICore.call_gemini_text(
                api_key=key, prompt=prompt, model=model,
                system_instruction=system_prompt if system_prompt else None,
                extra_parts=extra_parts,
            )
            return (result,)

        except Exception as e:
            logger.error(f"[TextVisionNode] Error: {e}")
            return (f"❌ Error: {str(e)}",)
