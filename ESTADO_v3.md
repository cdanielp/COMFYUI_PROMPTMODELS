# Estado migración v3 — promptmodels

> Rama: `v3-migration` | Última actualización: 2026-07-05

---

## Completado

| Bloque | Commits | Qué cubre |
|--------|---------|-----------|
| Bloques 1-3 | `dd922f6` | core/ (client_rest + keys), 38 legacy migrados a comfy_api v3, `is_deprecated=True` |
| PASO 0 fix | `a8288e3` | `core/model_aliases.py` + NB default vivo + alias `.get(model,model)` en todos los execute() |
| BLOQUE 4 | `c6d7171` | `nodes/nvidia_nodes.py`: PMS_NimbusText + PMS_NimbusVision (HTTP 200 ✓) |
| BLOQUE 5 parcial | `f8aecd2` | `nodes/gemini_nodes.py`: PMS_GeminiChatV3 (HTTP 200 ✓) |

### Arquitectura nodos nuevos v3

```
nodes/
  nvidia_nodes.py  → PMS_NimbusText, PMS_NimbusVision
  gemini_nodes.py  → PMS_GeminiChatV3  (NanoBanana pendiente)
  __init__.py      → ALL_NEW_NODES (lista en __init__.py raíz via get_node_list)
```

---

## Pendiente

### PMS_NanoBananaGen + PMS_NanoBananaEdit → diferido a v3.1.0

**Motivos:**
1. **Billing Gemini requerido** — el endpoint `/v1beta/interactions` devuelve 429 en
   free tier sin excepción. Se intentaron ~15 llamadas exploratorias; ninguna pasó.
2. **Schema `response_format` sin confirmar** — el campo `response_modalities` murió
   el 20-may-2026 y fue reemplazado por `response_format` (ver abajo). No se puede
   codificar el parsing hasta tener una respuesta HTTP 200 real.

**Schema `/v1beta/interactions` conocido (mapeado por error-probing, julio 2026):**

```json
// GENERATE (texto → imagen)
{
  "model": "gemini-3.1-flash-image",
  "input": { "type": "text", "text": "A red circle on white background" },
  "response_format": {
    "type": "image",
    "mime_type": "image/png",
    "aspect_ratio": "1:1",
    "image_size": "1K"
  }
}

// EDIT (imagen + instrucción → imagen)
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

**NOTA CRÍTICA:** el campo `response_format` es la forma correcta según julio 2026.
`response_modalities` (camelCase o snake_case) está deprecated desde 20-may-2026.
**No codificar con `response_modalities`.**

**Para retomar (v3.1.0):**
1. Cargar billing en la cuenta Gemini.
2. `curl -X POST .../v1beta/interactions?key=... -d @payload_generate.json`
   → confirmar HTTP 200 y pegar request + response COMPLETOS.
3. Hacer lo mismo para EDIT.
4. Solo entonces implementar PMS_NanoBananaGen y PMS_NanoBananaEdit.

---

### BLOQUE 6 — Grok → PARADO esperando key

**Motivo:** `XAI_API_KEY` existe en `.env` pero tiene valor **vacío**.

**Para continuar:**
1. Cargar la XAI API key en `.env`: `XAI_API_KEY=xai-...`
2. Dar OK para arrancar los nodos Grok v3.

**Nodos planeados (pendiente confirmación de spec):**
- PMS_GrokChatV3 — texto, categoría `PromptModels/Grok`
- (¿PMS_GrokImageV3, PMS_GrokTTSV3?) — confirmar qué endpoints están activos

---

## Notas para el próximo desarrollador

- Los 38 nodos legacy están en `legacy/` con `is_deprecated=True`. **No tocar.**
- Los nuevos nodos van en `nodes/` y se registran en `nodes/__init__.py`.
- `core/model_aliases.py` tiene GEMINI_TEXT y GROK_TEXT vacíos: llenar cuando caigan IDs.
- `core/client_rest.py` maneja retry 429 exponencial. No añadir otra capa de retry.
- `.env` tiene BOM UTF-8 (leeida con `encoding='utf-8-sig'`). No cambiar el encoding.
