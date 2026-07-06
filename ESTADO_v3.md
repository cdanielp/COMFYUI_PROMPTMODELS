# Estado migracion v3 — promptmodels

> Rama: `v3-migration` | Ultima actualizacion: 2026-07-05

---

## v3.0.0 — Activo

### Nodos nuevos (sin deprecar, en get_node_list)

| Nodo | Archivo | HTTP 200 |
|------|---------|----------|
| PMS_NimbusText | nodes/nvidia_nodes.py | nemotron-3-nano-omni ✓ |
| PMS_NimbusVision | nodes/nvidia_nodes.py | nemotron-nano-12b-v2-vl ✓ |
| PMS_GeminiChatV3 | nodes/gemini_nodes.py | gemini-2.5-flash ✓ |

### 38 nodos legacy (is_deprecated=True, en get_node_list)

Listados en docs/inventario_legacy.md. No tocar.

### Commits del branch

| Commit | Contenido |
|--------|-----------|
| dd922f6 | Bloques 1-3: core/, 38 legacy migrados v3 |
| a8288e3 | PASO 0: model_aliases.py, NB default vivo |
| c6d7171 | BLOQUE 4: PMS_NimbusText + PMS_NimbusVision |
| f8aecd2 | BLOQUE 5 parcial: PMS_GeminiChatV3 |
| 64b09a1 | docs: ESTADO_v3.md inicial |
| (actual) | BLOQUE 6 codigo + BLOQUE 7 cierre v3.0.0 |

---

## Pendiente para v3.1.0

### Nano Banana Gen + Edit — DIFERIDO

**Archivos preparados:** `nodes/gemini_nodes.py` (PMS_NanoBananaGen y PMS_NanoBananaEdit estan en el archivo, FUERA de get_node_list)

**Bloqueos:**
1. **Billing Gemini requerido** — `/v1beta/interactions` siempre 429 en free tier.
2. **Schema response_format sin confirmar** — `response_modalities` murio el 20-may-2026.
   El campo correcto es `response_format` (ver abajo). NO codificar hasta tener HTTP 200 real.

**Schema /v1beta/interactions conocido (error-probing julio 2026):**
```json
// GENERATE
{
  "model": "gemini-3.1-flash-image",
  "input": { "type": "text", "text": "..." },
  "response_format": {
    "type": "image",
    "mime_type": "image/png",
    "aspect_ratio": "1:1",
    "image_size": "1K"
  }
}

// EDIT
{
  "model": "gemini-3.1-flash-image",
  "input": [
    { "type": "image", "data": "<BASE64>", "mime_type": "image/png" },
    { "type": "text", "text": "Change color to blue" }
  ],
  "response_format": {
    "type": "image",
    "mime_type": "image/png",
    "aspect_ratio": "1:1",
    "image_size": "1K"
  }
}
```

**Para retomar:**
1. Activar billing en la cuenta Gemini.
2. Curl 200 real a /v1beta/interactions (generate Y edit).
3. Confirmar estructura de respuesta (candidates[], inlineData, etc.).
4. Implementar en gemini_nodes.py y agregar a get_node_list.

---

### Grok completo — DIFERIDO

**Archivos preparados:** `nodes/grok_nodes.py` (PMS_GrokChat, PMS_GrokImageGenV3, PMS_GrokImageEdit, FUERA de get_node_list)

**Bloqueo:** `XAI_API_KEY` vacia en `.env`.

**Para retomar:**
1. Cargar `XAI_API_KEY=xai-...` en `.env`.
2. Ejecutar prueba real con PMS_GrokChat.
3. Confirmar endpoints de imagen (generations + edits) con HTTP 200.
4. Agregar los 3 nodos a get_node_list.

**Aliases GROK_TEXT activos (para el legacy):**
- grok-4.1, grok-4.20, grok-4.1-fast → grok-4.3

---

## Arquitectura v3.0.0

```
COMFYUI_PROMPTMODELS/
  __init__.py              # PromptModelsExtension: get_node_list = legacy + new
  core/
    client_rest.py         # POST generico + retry 429 + helpers
    keys.py                # Resolucion de keys: nodo > env > .env
    model_aliases.py       # GEMINI_IMAGE, GEMINI_TEXT, GROK_TEXT
  nodes/
    nvidia_nodes.py        # PMS_NimbusText, PMS_NimbusVision  [ACTIVOS]
    gemini_nodes.py        # PMS_GeminiChatV3  [ACTIVO]
                           # PMS_NanoBananaGen, PMS_NanoBananaEdit [v3.1.0]
    grok_nodes.py          # PMS_GrokChat, PMS_GrokImageGenV3, PMS_GrokImageEdit [v3.1.0]
    __init__.py            # ALL_NEW_NODES (solo los activos)
  legacy/                  # 38 nodos migrados, is_deprecated=True
  ComfyUI_GoogleAI/        # google_core.py y nodos originales (usados por legacy)
  ComfyUI_GrokAI/          # grok_core.py y nodos originales (usados por legacy)
  docs/inventario_legacy.md
```

---

## Notas para el siguiente ciclo

- `core/model_aliases.py`: GEMINI_TEXT vacio, listo para futuros IDs muertos.
- `.env` usa BOM UTF-8 (`utf-8-sig`). No cambiar el encoding.
- `core/client_rest.py`: retry 429 exponencial integrado. No anadir otra capa.
- Los 38 legacy NO deben tocarse. Cualquier fix va en el archivo legacy/, no en las carpetas originales.
