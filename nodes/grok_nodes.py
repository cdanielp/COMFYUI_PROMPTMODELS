"""
nodes/grok_nodes.py — Nodos Grok v3 para promptmodels.

ESTADO: INACTIVOS en v3.0.0 — fuera de get_node_list hasta v3.1.0.
Razón: XAI_API_KEY vacía; no hay HTTP 200 real para confirmar endpoints.
Los nodos legacy Grok (GrokTextNode, PMS_GrokImageGen, etc.) siguen activos.

PMS_GrokChat       : chat/completions xAI (texto).
PMS_GrokImageGenV3 : images/generations xAI (texto → imagen).
PMS_GrokImageEdit  : images/edits xAI (imagen + instrucción → imagen).
"""
from comfy_api.latest import io

_XAI_BASE = "https://api.x.ai/v1"

_TEXT_MODELS = [
    "grok-4.3",
    "grok-4.1",
    "grok-4.1-fast",
]

_IMG_MODELS = [
    "grok-2-image-1212",
]

_ASPECT_RATIOS = ["1:1", "16:9", "9:16", "4:3", "3:4"]


def _parse_content(raw) -> str:
    if isinstance(raw, list):
        return " ".join(p.get("text", "") for p in raw if isinstance(p, dict))
    return raw or ""


# ─────────────── PMS_GrokChat ─────────────────────────────────────
class PMS_GrokChat(io.ComfyNode):
    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id="PMS_GrokChat",
            display_name="Grok Chat V3 (PMS)",
            category="PromptModels/Grok",
            inputs=[
                io.String.Input("system_prompt", optional=True, multiline=True, default="",
                                tooltip="Instrucción de sistema. Vacío = sin system."),
                io.String.Input("prompt", multiline=True,
                                default="Escribe tu mensaje aquí..."),
                io.Combo.Input("model", options=_TEXT_MODELS, default=_TEXT_MODELS[0]),
                io.String.Input("custom_model", optional=True, default="",
                                tooltip="Sobreescribe el combo si no está vacío."),
                io.Float.Input("temperature", optional=True, default=0.7,
                               min=0.0, max=2.0, step=0.05),
                io.Int.Input("max_tokens", optional=True, default=1024,
                             min=64, max=8192, step=64),
                io.String.Input("api_key", optional=True, default=""),
            ],
            outputs=[io.String.Output("text")],
        )

    @classmethod
    def execute(cls, prompt, model, system_prompt="", custom_model="",
                temperature=0.7, max_tokens=1024, api_key="") -> io.NodeOutput:
        try:
            from ..core.keys import grok_key
            from ..core.client_rest import post_openai
            from ..core.model_aliases import GROK_TEXT
            key = grok_key(api_key)
            eff_model = GROK_TEXT.get(custom_model.strip() or model,
                                      custom_model.strip() or model)
            messages = []
            if system_prompt and system_prompt.strip():
                messages.append({"role": "system", "content": system_prompt.strip()})
            messages.append({"role": "user", "content": prompt})
            resp = post_openai(
                base_url=_XAI_BASE,
                endpoint="/chat/completions",
                api_key=key,
                payload={
                    "model": eff_model,
                    "messages": messages,
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                },
                provider="Grok",
            )
            return io.NodeOutput(_parse_content(resp["choices"][0]["message"]["content"]))
        except Exception as e:
            return io.NodeOutput(f"❌ Error: {str(e)}")


# ─────────────── PMS_GrokImageGenV3 ───────────────────────────────
class PMS_GrokImageGenV3(io.ComfyNode):
    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id="PMS_GrokImageGenV3",
            display_name="Grok Image Gen V3 (PMS)",
            category="PromptModels/Grok",
            inputs=[
                io.String.Input("prompt", multiline=True,
                                default="A futuristic city in cyberpunk style"),
                io.Combo.Input("model", options=_IMG_MODELS, default=_IMG_MODELS[0]),
                io.Combo.Input("aspect_ratio", options=_ASPECT_RATIOS, default="1:1"),
                io.Int.Input("n", default=1, min=1, max=4, step=1,
                             tooltip="Número de imágenes a generar (1–4)."),
                io.String.Input("api_key", optional=True, default=""),
            ],
            outputs=[io.Image.Output("image"), io.String.Output("revised_prompt")],
        )

    @classmethod
    def execute(cls, prompt, model, aspect_ratio="1:1", n=1,
                api_key="") -> io.NodeOutput:
        try:
            import requests
            from ..core.keys import grok_key
            from ..core.client_rest import image_tensor_to_jpeg_data_url
            key = grok_key(api_key)
            resp = requests.post(
                f"{_XAI_BASE}/images/generations",
                headers={"Authorization": f"Bearer {key}",
                         "Content-Type": "application/json"},
                json={
                    "model": model,
                    "prompt": prompt,
                    "n": n,
                    "response_format": "url",
                    "aspect_ratio": aspect_ratio,
                },
                timeout=120,
            )
            resp.raise_for_status()
            data = resp.json().get("data", [])
            if not data:
                raise RuntimeError("La API no retornó imágenes.")
            url = data[0].get("url", "")
            revised = data[0].get("revised_prompt", prompt)
            # Descargar imagen desde URL
            img_resp = requests.get(url, timeout=60)
            img_resp.raise_for_status()
            from PIL import Image
            import io as _io, torch, numpy as np
            img = Image.open(_io.BytesIO(img_resp.content)).convert("RGB")
            tensor = torch.from_numpy(
                np.array(img).astype(np.float32) / 255.0
            ).unsqueeze(0)
            return io.NodeOutput(tensor, revised)
        except Exception as e:
            from ..ComfyUI_GoogleAI.google_core import GoogleAICore
            return io.NodeOutput(GoogleAICore.create_error_image(str(e)), f"❌ Error: {str(e)}")


# ─────────────── PMS_GrokImageEdit ────────────────────────────────
class PMS_GrokImageEdit(io.ComfyNode):
    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id="PMS_GrokImageEdit",
            display_name="Grok Image Edit (PMS)",
            category="PromptModels/Grok",
            inputs=[
                io.Image.Input("image", tooltip="Imagen a editar."),
                io.String.Input("prompt", multiline=True,
                                default="Change the background to a starry night sky"),
                io.Combo.Input("model", options=_IMG_MODELS, default=_IMG_MODELS[0]),
                io.String.Input("api_key", optional=True, default=""),
            ],
            outputs=[io.Image.Output("image"), io.String.Output("revised_prompt")],
        )

    @classmethod
    def execute(cls, image, prompt, model, api_key="") -> io.NodeOutput:
        try:
            import requests
            import io as _io
            from PIL import Image
            import torch, numpy as np
            from ..core.keys import grok_key
            key = grok_key(api_key)

            # Convertir tensor a PNG bytes
            frame = image[0] if image.dim() == 4 else image
            img_np = (frame.cpu().numpy() * 255).clip(0, 255).astype("uint8")
            buf = _io.BytesIO()
            Image.fromarray(img_np, "RGB").save(buf, format="PNG")
            buf.seek(0)

            resp = requests.post(
                f"{_XAI_BASE}/images/edits",
                headers={"Authorization": f"Bearer {key}"},
                files={"image": ("image.png", buf, "image/png")},
                data={"model": model, "prompt": prompt, "response_format": "url"},
                timeout=120,
            )
            resp.raise_for_status()
            data = resp.json().get("data", [])
            if not data:
                raise RuntimeError("La API no retornó imágenes editadas.")
            url = data[0].get("url", "")
            revised = data[0].get("revised_prompt", prompt)
            img_r = requests.get(url, timeout=60)
            img_r.raise_for_status()
            img_out = Image.open(_io.BytesIO(img_r.content)).convert("RGB")
            tensor = torch.from_numpy(
                np.array(img_out).astype(np.float32) / 255.0
            ).unsqueeze(0)
            return io.NodeOutput(tensor, revised)
        except Exception as e:
            from ..ComfyUI_GoogleAI.google_core import GoogleAICore
            return io.NodeOutput(GoogleAICore.create_error_image(str(e)), f"❌ Error: {str(e)}")
