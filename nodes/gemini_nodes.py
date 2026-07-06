"""
nodes/gemini_nodes.py — Nodos Gemini v3 para promptmodels.

PMS_GeminiChatV3   : generateContent (texto / multimodal).
PMS_NanoBananaGen  : /v1beta/interactions (generar imagen nueva).  [pendiente OK]
PMS_NanoBananaEdit : /v1beta/interactions (editar imagen existente). [pendiente OK]

Todos usan core/client_rest y core/keys.
"""
from comfy_api.latest import io

_TEXT_MODELS = [
    "gemini-3.1-pro-preview",
    "gemini-3-flash-preview",
    "gemini-2.5-pro",
    "gemini-2.5-flash",
]

_THINKING = ["Off", "Low", "Medium", "High"]

# Gemini 3.x → thinkingLevel; 2.5 → thinkingBudget
_THINKING_LEVEL  = {"Low": "low",  "Medium": "medium",  "High": "high"}
_THINKING_BUDGET = {"Low": 1024,   "Medium": 4096,       "High": 8192}


def _build_thinking(model: str, budget: str) -> dict | None:
    if not budget or budget == "Off":
        return None
    if model.startswith("gemini-3"):
        return {"thinkingLevel": _THINKING_LEVEL.get(budget, "low")}
    if model.startswith("gemini-2.5"):
        return {"thinkingBudget": _THINKING_BUDGET.get(budget, 1024)}
    return None


# ─────────────── PMS_GeminiChatV3 ─────────────────────────────────
class PMS_GeminiChatV3(io.ComfyNode):
    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id="PMS_GeminiChatV3",
            display_name="Gemini Chat V3 (PMS)",
            category="PromptModels/Google",
            inputs=[
                io.String.Input("system_prompt", optional=True, multiline=True, default="",
                                tooltip="Instrucción de sistema. Vacío = sin system."),
                io.String.Input("prompt", multiline=True,
                                default="Describe esta imagen en detalle."),
                io.Combo.Input("model", options=_TEXT_MODELS, default=_TEXT_MODELS[0]),
                io.String.Input("custom_model", optional=True, default="",
                                tooltip="Sobreescribe el combo si no está vacío."),
                io.Combo.Input("thinking_budget", options=_THINKING, default="Off",
                               tooltip="Off = sin thinking. Gemini 3+: thinkingLevel. "
                                       "Gemini 2.5: thinkingBudget."),
                io.Image.Input("image_1", optional=True, tooltip="Imagen 1 (multimodal)."),
                io.Image.Input("image_2", optional=True, tooltip="Imagen 2 (opcional)."),
                io.Image.Input("image_3", optional=True, tooltip="Imagen 3 (opcional)."),
                io.Image.Input("image_4", optional=True, tooltip="Imagen 4 (opcional)."),
                io.Image.Input("image_5", optional=True, tooltip="Imagen 5 (opcional)."),
                io.Float.Input("temperature", optional=True, default=0.7,
                               min=0.0, max=2.0, step=0.05),
                io.Int.Input("max_tokens", optional=True, default=4096,
                             min=64, max=65536, step=64),
                io.String.Input("api_key", optional=True, default=""),
            ],
            outputs=[io.String.Output("text")],
        )

    @classmethod
    def execute(cls, prompt, model, system_prompt="", custom_model="",
                thinking_budget="Off",
                image_1=None, image_2=None, image_3=None, image_4=None, image_5=None,
                temperature=0.7, max_tokens=4096, api_key="") -> io.NodeOutput:
        try:
            from ..core.keys import gemini_key
            from ..core.client_rest import post_gemini, image_tensor_to_jpeg_data_url
            from ..core.model_aliases import GEMINI_TEXT
            key = gemini_key(api_key)
            eff_model = GEMINI_TEXT.get(custom_model.strip() or model, custom_model.strip() or model)

            parts = []
            for img in [image_1, image_2, image_3, image_4, image_5]:
                if img is not None:
                    data_url = image_tensor_to_jpeg_data_url(img, max_side=1024)
                    b64 = data_url.split(",", 1)[1]
                    parts.append({"inlineData": {"mimeType": "image/jpeg", "data": b64}})
            parts.append({"text": prompt})

            gen_config: dict = {"maxOutputTokens": max_tokens, "temperature": temperature}
            tc = _build_thinking(eff_model, thinking_budget)
            if tc:
                gen_config["thinkingConfig"] = tc

            payload: dict = {
                "contents": [{"role": "user", "parts": parts}],
                "generationConfig": gen_config,
            }
            if system_prompt and system_prompt.strip():
                payload["systemInstruction"] = {
                    "parts": [{"text": system_prompt.strip()}]
                }

            resp = post_gemini(
                api_key=key,
                model=eff_model,
                endpoint_suffix="generateContent",
                payload=payload,
                provider="Gemini",
            )
            candidates = resp.get("candidates", [])
            if not candidates:
                return io.NodeOutput("[Sin respuesta del modelo]")
            parts_resp = candidates[0].get("content", {}).get("parts", [])
            text = "\n".join(
                p["text"] for p in parts_resp
                if "text" in p and not p.get("thought", False)
            )
            return io.NodeOutput(text or "[Respuesta vacía]")
        except Exception as e:
            return io.NodeOutput(f"❌ Error: {str(e)}")
