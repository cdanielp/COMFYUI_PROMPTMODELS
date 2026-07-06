"""
core/model_aliases.py — Alias muerto→vivo para model IDs en promptmodels 3.x.

Cada execute() legacy que reciba `model` hace:
    model = DICT.get(model, model)
antes del HTTP call, para que workflows guardados con IDs preview sigan funcionando.
"""

GEMINI_IMAGE: dict[str, str] = {
    "gemini-3.1-flash-image-preview": "gemini-3.1-flash-image",
    "gemini-3-pro-image-preview":      "gemini-3-pro-image",
    "gemini-2.5-flash-image":          "gemini-3.1-flash-image",
}

GEMINI_TEXT: dict[str, str] = {}

GROK_TEXT: dict[str, str] = {
    "grok-4.1":      "grok-4.3",
    "grok-4.20":     "grok-4.3",
    "grok-4.1-fast": "grok-4.3",
}
