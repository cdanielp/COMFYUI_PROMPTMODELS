# ComfyUI_GrokAI V2.0.0 - Suite de xAI (Grok) para ComfyUI

> **Grok 4.20** (Reasoning/Non-Reasoning) - **Grok Imagine** (Image/Video) - **Diagnostico** (Workflows + Modelos)

![Version](https://img.shields.io/badge/Version-2.0.0-blue)
![License](https://img.shields.io/badge/License-MIT-yellow)
![Nodes](https://img.shields.io/badge/Nodos-10-green)

---

## Changelog V2.0.0

### Breaking Changes
- Todos los model IDs actualizados a la API xAI de Marzo 2026
- Modelos eliminados: `grok-2-1212`, `grok-2-vision-1212`, `grok-vision-beta`, `grok-2-image-1212`, `grok-2-image`, `grok-video-preview`, `grok-video`
- Parametro `size` en pixeles eliminado, reemplazado por `aspect_ratio` + `resolution`

### Crash Fixes (P1)
- `grok_core.py`: nuevos exports `TEXT_MODELS`, `IMAGE_MODELS`, `VIDEO_MODELS`, system prompts, `resolve_api_key()`, `chat_text()`, `url_to_tensor()`, `edit_image()`, `submit_video()`, `poll_video()`
- `grok_diagnostic_node.py`: corregidas importaciones rotas, ahora usa simbolos de `grok_core`
- `grok_video_node.py`: reescrito completo para API asincrona (POST -> request_id -> polling)
- `__init__.py`: registrados `Grok_Workflow_Debugger` y `Grok_Metadata_Reader`

### API Correctness (P2)
- Imagen: `aspect_ratio` directo en payload (14 ratios soportados), parametro `resolution` (1k/2k)
- Video: `aspect_ratio` (7 ratios), `resolution` (480p/720p), `duration` (1-15s)
- Prompt Architect: parsing JSON robusto con fallback a texto plano

### New Features (P3)
- `Grok_Video_Editor`: edicion de video con lenguaje natural (POST /v1/videos/edits)
- `Grok_Video_Extension`: extension de video hasta 15s total (POST /v1/videos/extensions)
- Batch image generation: parametro `n` (1-10 imagenes por request)

---

## Modelos Soportados (xAI API Marzo 2026)

| Tipo | Modelo | Contexto / Nota |
|------|--------|-----------------|
| Texto (flagship) | `grok-4.20-0309-reasoning` | 2M tokens, reasoning |
| Texto (flagship) | `grok-4.20-0309-non-reasoning` | 2M tokens |
| Texto (budget) | `grok-4-1-fast-reasoning` | 2M tokens, reasoning |
| Texto (budget) | `grok-4-1-fast-non-reasoning` | 2M tokens |
| Imagen | `grok-imagine-image` | $0.02/imagen |
| Imagen (pro) | `grok-imagine-image-pro` | $0.07/imagen |
| Video | `grok-imagine-video` | $0.05/segundo |

---

## Nodos (10 total)

### Texto y Vision

| Nodo | Categoria | Descripcion |
|------|-----------|-------------|
| Grok Text [v1 Legacy] | Grok/Legado | Texto basico, retrocompatible |
| Grok Multimodal Vision | xAI/Grok | Hasta 5 imagenes + texto, reasoning_effort |
| Grok Prompt Architect | xAI/Grok | Expande ideas en positive/negative prompts (JSON) |

### Imagen

| Nodo | Categoria | Descripcion |
|------|-----------|-------------|
| Grok Image [v1 Legacy] | Grok/Legado | Text-to-Image basico, retrocompatible |
| Grok Image Master | xAI/Grok | Text-to-Image + Image-to-Image, batch 1-10, 14 aspect ratios |

### Video

| Nodo | Categoria | Descripcion |
|------|-----------|-------------|
| Grok Video Forge | xAI/Grok | Text-to-Video / Image-to-Video, 1-15s, 480p/720p |
| Grok Video Editor | xAI/Grok | Edicion de video existente con prompt |
| Grok Video Extension | xAI/Grok | Extension de video, hasta 15s total |

### Diagnostico

| Nodo | Categoria | Descripcion |
|------|-----------|-------------|
| Grok Workflow Debugger | Grok AI/Diagnostic | Analiza workflow JSON, identifica repos y conflictos |
| Grok Metadata Reader | Grok AI/Diagnostic | Lee .safetensors, identifica arquitectura y triggers |

---

## Instalacion

```bash
cd ComfyUI/custom_nodes/
git clone https://github.com/cdanielp/COMFYUI_PROMPTMODELS.git
pip install -r COMFYUI_PROMPTMODELS/ComfyUI_GrokAI/requirements.txt
```

Reinicia ComfyUI. Los 10 nodos aparecen en las categorias `xAI/Grok`, `Grok/Legado` y `Grok AI/Diagnostic`.

---

## Configurar API Key

Obten tu API Key en [console.x.ai](https://console.x.ai).

| Prioridad | Fuente | Como |
|:---------:|--------|------|
| 1 | Campo del nodo | Escribir directo en `api_key` |
| 2 | Variable de entorno | `set XAI_API_KEY=xai-...` (Windows) |

---

## Notas Tecnicas

- **Cero SDKs** -- Toda la comunicacion usa `requests` HTTP puras contra `api.x.ai/v1`
- **Anti-Crash** -- Errores retornan imagen roja 512x512 en vez de crashear
- **Video Asincrono** -- Submit + polling (configurable timeout e intervalo)
- **Tensores estandar** -- `[B, H, W, C]` float `0.0-1.0` (formato PyTorch de ComfyUI)
- **Batch Images** -- Parametro `n` genera hasta 10 imagenes, retornadas como tensor batch

---

## Licencia

MIT

---

Desarrollado por **[Prompt Models Studio](https://github.com/cdanielp)**
