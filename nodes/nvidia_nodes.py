"""
nodes/nvidia_nodes.py — Nodos NVIDIA NIMbus v3 para promptmodels.

PMS_NimbusText : chat/completions contra NVIDIA NIM (texto puro).
PMS_NimbusVision: chat/completions multimodal con imagen (VL models).

Ambos usan core/client_rest y core/keys.  api_key es el último input.
"""
from comfy_api.latest import io

_BASE_URL = "https://integrate.api.nvidia.com/v1"

_TEXT_MODELS = [
    "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning",
    "deepseek-ai/deepseek-v4-flash",
    "deepseek-ai/deepseek-v4-pro",
    "nvidia/llama-3.1-nemotron-ultra-253b-v1",
    "nvidia/llama-3.3-nemotron-super-49b-v1",
]

_VL_MODELS = [
    "nvidia/nemotron-nano-12b-v2-vl",
    "nvidia/llama-3.1-nemotron-nano-vl-8b-v1",
    "nvidia/vila",
]


def _parse_content(raw) -> str:
    if isinstance(raw, list):
        return " ".join(p.get("text", "") for p in raw if isinstance(p, dict))
    return raw or ""


# ─────────────── PMS_NimbusText ───────────────────────────────────
class PMS_NimbusText(io.ComfyNode):
    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id="PMS_NimbusText",
            display_name="NIMbus Text (PMS)",
            category="PromptModels/NVIDIA (NIMbus)",
            inputs=[
                io.String.Input("system_prompt", optional=True, multiline=True, default="",
                                tooltip="Instrucción de sistema. Vacío = sin system."),
                io.String.Input("prompt", multiline=True,
                                default="What is a ComfyUI custom node? Answer in two sentences."),
                io.Combo.Input("model", options=_TEXT_MODELS, default=_TEXT_MODELS[0]),
                io.String.Input("custom_model", optional=True, default="",
                                tooltip="Sobreescribe el combo si no está vacío. "
                                        "Ejemplo: nvidia/nemotron-3-ultra-550b-a55b"),
                io.Float.Input("temperature", optional=True, default=0.7, min=0.0, max=2.0, step=0.05),
                io.Int.Input("max_tokens", optional=True, default=1024, min=64, max=8192, step=64),
                io.String.Input("api_key", optional=True, default=""),
            ],
            outputs=[io.String.Output("text")],
        )

    @classmethod
    def execute(cls, prompt, model, system_prompt="", custom_model="",
                temperature=0.7, max_tokens=1024, api_key="") -> io.NodeOutput:
        try:
            from ..core.keys import nvidia_key
            from ..core.client_rest import post_openai
            key = nvidia_key(api_key)
            eff_model = custom_model.strip() or model
            messages = []
            if system_prompt and system_prompt.strip():
                messages.append({"role": "system", "content": system_prompt.strip()})
            messages.append({"role": "user", "content": prompt})
            resp = post_openai(
                base_url=_BASE_URL,
                endpoint="/chat/completions",
                api_key=key,
                payload={
                    "model": eff_model,
                    "messages": messages,
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                },
                provider="NVIDIA",
            )
            return io.NodeOutput(_parse_content(resp["choices"][0]["message"]["content"]))
        except Exception as e:
            return io.NodeOutput(f"❌ Error: {str(e)}")


# ─────────────── PMS_NimbusVision ─────────────────────────────────
class PMS_NimbusVision(io.ComfyNode):
    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id="PMS_NimbusVision",
            display_name="NIMbus Vision (PMS)",
            category="PromptModels/NVIDIA (NIMbus)",
            inputs=[
                io.Image.Input("image",
                               tooltip="Imagen para análisis multimodal (VL models)."),
                io.String.Input("system_prompt", optional=True, multiline=True, default="",
                                tooltip="Instrucción de sistema. Vacío = sin system."),
                io.String.Input("prompt", multiline=True,
                                default="Describe this image in detail."),
                io.Combo.Input("model", options=_VL_MODELS, default=_VL_MODELS[0]),
                io.String.Input("custom_model", optional=True, default="",
                                tooltip="Sobreescribe el combo si no está vacío."),
                io.Boolean.Input("enable_thinking", optional=True, default=False,
                                 tooltip="Activa razonamiento extendido (nvext.thinking). "
                                         "Solo modelos que lo soporten."),
                io.Float.Input("temperature", optional=True, default=0.7, min=0.0, max=2.0, step=0.05),
                io.Int.Input("max_tokens", optional=True, default=1024, min=64, max=8192, step=64),
                io.String.Input("api_key", optional=True, default=""),
            ],
            outputs=[io.String.Output("text")],
        )

    @classmethod
    def execute(cls, image, prompt, model, system_prompt="", custom_model="",
                enable_thinking=False, temperature=0.7, max_tokens=1024,
                api_key="") -> io.NodeOutput:
        try:
            from ..core.keys import nvidia_key
            from ..core.client_rest import post_openai, image_tensor_to_jpeg_data_url
            key = nvidia_key(api_key)
            eff_model = custom_model.strip() or model
            img_url = image_tensor_to_jpeg_data_url(image, max_side=1024)
            user_content = [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": img_url}},
            ]
            messages = []
            if system_prompt and system_prompt.strip():
                messages.append({"role": "system", "content": system_prompt.strip()})
            messages.append({"role": "user", "content": user_content})
            payload: dict = {
                "model": eff_model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
            }
            if enable_thinking:
                payload["nvext"] = {"thinking": True}
            resp = post_openai(
                base_url=_BASE_URL,
                endpoint="/chat/completions",
                api_key=key,
                payload=payload,
                provider="NVIDIA",
            )
            return io.NodeOutput(_parse_content(resp["choices"][0]["message"]["content"]))
        except Exception as e:
            return io.NodeOutput(f"❌ Error: {str(e)}")
