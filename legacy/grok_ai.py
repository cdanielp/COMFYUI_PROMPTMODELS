from comfy_api.latest import io

_TEXT_MODELS = ["grok-4.20", "grok-4.1", "grok-4.1-fast"]
_IMG_ASPECT = ["1:1", "2:3", "3:2"]
_VID_ASPECT = ["16:9", "9:16", "1:1", "4:3"]
_TTS_VOICES = ["ara", "eve", "leo", "rex", "sal"]


# ─────────────── GrokTextNode ─────────────────────────────────────
class GrokTextNode(io.ComfyNode):
    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id="GrokTextNode",
            display_name="Grok Chat (PMS)",
            category="PromptModels/Grok",
            inputs=[
                io.String.Input("prompt", multiline=True, default="Escribe tu mensaje aqui..."),
                io.Combo.Input("model", options=_TEXT_MODELS, default="grok-4.1"),
                io.String.Input("system_prompt", optional=True, multiline=True,
                                default="You are a helpful assistant."),
                io.Float.Input("temperature", optional=True, default=0.7, min=0.0, max=2.0, step=0.1),
                io.String.Input("api_key", optional=True, default=""),
            ],
            outputs=[io.String.Output("texto")],
            is_deprecated=True,
        )

    @classmethod
    def execute(cls, prompt, model, system_prompt="", temperature=0.7,
                api_key="") -> io.NodeOutput:
        try:
            from ..core.keys import grok_key
            from ..core.client_rest import post_openai
            key = grok_key(api_key)
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            resp = post_openai(
                base_url="https://api.x.ai/v1",
                endpoint="/chat/completions",
                api_key=key,
                payload={"model": model, "messages": messages, "temperature": temperature},
                provider="Grok",
            )
            content = resp["choices"][0]["message"]["content"]
            if isinstance(content, list):
                content = content[0].get("text", "") if content else ""
            return io.NodeOutput(content)
        except Exception as e:
            return io.NodeOutput(f"Error: {str(e)}")


# ─────────────── PMS_GrokImageGen ─────────────────────────────────
class PMS_GrokImageGen(io.ComfyNode):
    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id="PMS_GrokImageGen",
            display_name="Grok Image Gen (PMS)",
            category="PromptModels/Grok",
            inputs=[
                io.String.Input("prompt", multiline=True, default="A futuristic city in cyberpunk style"),
                io.Combo.Input("aspect_ratio", options=_IMG_ASPECT, default="1:1"),
                io.Int.Input("n", default=1, min=1, max=4, step=1,
                             tooltip="Numero de imagenes a generar (1-4)."),
                io.Image.Input("image_ref", optional=True,
                               tooltip="Imagen de referencia para edicion (image-to-image)."),
                io.String.Input("api_key", optional=True, default=""),
            ],
            outputs=[io.Image.Output("imagen"), io.String.Output("url_o_error")],
            is_deprecated=True,
        )

    @classmethod
    def execute(cls, prompt, aspect_ratio, n, image_ref=None,
                api_key="") -> io.NodeOutput:
        try:
            from ..core.keys import grok_key
            from ..core.client_rest import post_openai, image_tensor_to_jpeg_data_url
            import base64, io as bio
            import torch, numpy as np
            from PIL import Image
            key = grok_key(api_key)

            if image_ref is None:
                resp = post_openai(
                    base_url="https://api.x.ai/v1",
                    endpoint="/images/generations",
                    api_key=key,
                    payload={"model": "grok-imagine-image-quality", "prompt": prompt,
                             "n": n, "aspect_ratio": aspect_ratio, "response_format": "b64_json"},
                    provider="Grok",
                )
            else:
                data_uri = image_tensor_to_jpeg_data_url(image_ref)
                resp = post_openai(
                    base_url="https://api.x.ai/v1",
                    endpoint="/images/edits",
                    api_key=key,
                    payload={"model": "grok-imagine-image-quality", "prompt": prompt,
                             "image": {"url": data_uri, "type": "image_url"},
                             "n": n, "response_format": "b64_json"},
                    provider="Grok",
                )

            data_list = resp.get("data", [])
            if not data_list:
                raise RuntimeError("Respuesta vacía de la API.")
            tensors = []
            for item in data_list:
                b64 = item.get("b64_json", "") or ""
                if b64:
                    img_bytes = base64.b64decode(b64)
                    img = Image.open(bio.BytesIO(img_bytes)).convert("RGB")
                    arr = np.array(img).astype(np.float32) / 255.0
                    tensors.append(torch.from_numpy(arr).unsqueeze(0))
            if not tensors:
                raise RuntimeError("Sin imágenes válidas en respuesta.")
            tensor = torch.cat(tensors, dim=0)
            url = data_list[0].get("url", "")
            return io.NodeOutput(tensor, url)
        except Exception as e:
            import torch
            err_tensor = torch.zeros(1, 512, 512, 3)
            err_tensor[:, :, :, 0] = 0.8
            return io.NodeOutput(err_tensor, f"Error: {str(e)}")


# ─────────────── PMS_GrokVideoGen ─────────────────────────────────
class PMS_GrokVideoGen(io.ComfyNode):
    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id="PMS_GrokVideoGen",
            display_name="Grok Video Gen (PMS)",
            category="PromptModels/Grok",
            inputs=[
                io.String.Input("prompt", multiline=True,
                                default="A cinematic shot of a futuristic neon city."),
                io.Int.Input("duration", default=8, min=1, max=15, step=1,
                             tooltip="Duración del video en segundos (1-15)."),
                io.Combo.Input("aspect_ratio", options=_VID_ASPECT, default="16:9"),
                io.Combo.Input("resolution", options=["720p", "1080p"], default="720p"),
                io.Image.Input("source_image", optional=True,
                               tooltip="Imagen de inicio para image-to-video (opcional)."),
                io.String.Input("api_key", optional=True, default=""),
            ],
            outputs=[io.String.Output("video_url"), io.String.Output("status")],
            is_deprecated=True,
        )

    @classmethod
    def execute(cls, prompt, duration, aspect_ratio, resolution,
                source_image=None, api_key="") -> io.NodeOutput:
        try:
            from ..core.keys import grok_key
            from ..ComfyUI_GrokAI.grok_video_gen import PMS_GrokVideoGen as V1
            key = grok_key(api_key)
            result = V1().generar(prompt=prompt, duration=duration, aspect_ratio=aspect_ratio,
                                  resolution=resolution, source_image=source_image, api_key=key)
            return io.NodeOutput(*result)
        except Exception as e:
            return io.NodeOutput("", f"Error: {str(e)}")


# ─────────────── PMS_GrokTTS ──────────────────────────────────────
class PMS_GrokTTS(io.ComfyNode):
    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id="PMS_GrokTTS",
            display_name="Grok Text to Speech (PMS)",
            category="PromptModels/Grok",
            inputs=[
                io.String.Input("text", multiline=True,
                                default="Hola, soy Grok. [laugh] Me alegra hablar contigo.",
                                tooltip="Speech tags: [laugh] [sigh] [whisper] inline en el texto."),
                io.Combo.Input("voice", options=_TTS_VOICES, default="ara",
                               tooltip="ara=femenina neutra | eve | leo | rex | sal"),
                io.Float.Input("speed", default=1.0, min=0.5, max=2.0, step=0.1,
                               tooltip="Velocidad del habla (0.5=lento, 2.0=rapido)."),
                io.String.Input("api_key", optional=True, default=""),
            ],
            outputs=[io.Audio.Output("audio"), io.String.Output("voz_usada")],
            is_deprecated=True,
        )

    @classmethod
    def execute(cls, text, voice, speed, api_key="") -> io.NodeOutput:
        try:
            from ..core.keys import grok_key
            from ..ComfyUI_GrokAI.grok_tts_node import PMS_GrokTTS as V1
            key = grok_key(api_key)
            result = V1().sintetizar(text=text, voice=voice, speed=speed, api_key=key)
            return io.NodeOutput(*result)
        except Exception as e:
            import torch
            silence = {"waveform": torch.zeros((1, 1, 22050)), "sample_rate": 22050}
            return io.NodeOutput(silence, voice)


# ─────────────── PMS_GrokSTT ──────────────────────────────────────
class PMS_GrokSTT(io.ComfyNode):
    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id="PMS_GrokSTT",
            display_name="Grok Speech to Text (PMS)",
            category="PromptModels/Grok",
            inputs=[
                io.Audio.Input("audio",
                               tooltip="Tensor AUDIO de ComfyUI {waveform, sample_rate}."),
                io.String.Input("language", optional=True, default="es",
                                tooltip="Código ISO 639-1. ej: es, en, fr."),
                io.String.Input("api_key", optional=True, default=""),
            ],
            outputs=[io.String.Output("transcripcion"), io.String.Output("idioma_detectado")],
            is_deprecated=True,
        )

    @classmethod
    def execute(cls, audio, language="es", api_key="") -> io.NodeOutput:
        try:
            from ..core.keys import grok_key
            from ..ComfyUI_GrokAI.grok_stt_node import PMS_GrokSTT as V1
            key = grok_key(api_key)
            result = V1().transcribir(audio=audio, language=language, api_key=key)
            return io.NodeOutput(*result)
        except Exception as e:
            return io.NodeOutput(f"Error: {str(e)}", language)
