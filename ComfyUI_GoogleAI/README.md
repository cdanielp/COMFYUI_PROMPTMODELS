# 🚀 ComfyUI_GoogleAI V2.4.2 Ultra — Suite Integral de Google AI

> **Nano Banana Pro/Flash** (Imagen Multimodal) · **Imagen 4** (Generación Pura) · **Veo 3.1** (Video + Audio) · **Gemini 3.1 Pro** (Texto/Diagnóstico)

![Version](https://img.shields.io/badge/Version-2.4.2-blue)
![Nodes](https://img.shields.io/badge/Nodos-12-green)

> ⚠️ **Audio (Lyria 3)** removido — `lyria-3` no tiene endpoint de API pública (Feb 2026). Disponible solo en la app de Gemini. Se reintegrará cuando Google abra la API.

---

## 📑 Tabla de Contenidos

1. [Novedades V2.4.2](#-novedades-v242-ultra)
2. [Instalación](#-instalación)
3. [Configurar API Key](#-configurar-api-key)
4. [Nodos: Texto](#-texto--gemini-31-pro)
5. [Nodos: Imagen](#-imagen--nano-banana--imagen-4)
6. [Nodos: Video](#-video--veo-31)
7. [Nodos: Diagnóstico](#-diagnóstico--gemini-31-pro)
8. [Modelos disponibles](#-modelos-disponibles)
9. [Notas Técnicas](#-notas-técnicas)

---

## 🆕 Novedades V2.4.2 Ultra

- **🎨 Nano Banana Pro/Flash** — Nuevo routing en `GoogleAI_ImageNode`:
  - `gemini-3-pro-image-preview` (Nano Banana Pro): hasta 14 referencias, hasta 4K
  - `gemini-2.5-flash-image` (Nano Banana): velocidad, hasta 1K
  - 5 pines de imagen de referencia para estilo, personaje o composición
  - Routing automático: Nano Banana → `generateContent` | Imagen 4 → `generateImages`
- **📐 Size Presets inteligentes** — Mapeo automático `size_preset → aspectRatio + resolution_hint`
- **🔒 Validación 4K** — Solo Nano Banana Pro soporta 4K; downgrade automático a 2K en otros modelos
- **🔊 Audio en TODOS los nodos de video** — VideoInterpolation y VideoStoryboard ahora incluyen output `AUDIO` (pista nativa Veo 3.1 o silencio en Veo 2.0)
- **🛡️ Blindaje de errores** — Imagen roja 512×512 con texto de error en todos los nodos (sin crasheos)
- **📋 Modelos consistentes** — Strings de API actualizados y unificados (Feb 2026)

---

## 📦 Instalación

```bash
cd ComfyUI/custom_nodes/
git clone https://github.com/cdanielp/COMFYUI_PROMPTMODELS.git ComfyUI_GoogleAI
cd ComfyUI_GoogleAI
pip install -r requirements.txt
```

> 💡 **Explicador de Errores:** Separado al plugin universal [ComfyUI_UniversalErrorExplainer](https://github.com/cdanielp/ComfyUI_UniversalErrorExplainer).

---

## 🔑 Configurar API Key

| Prioridad | Fuente | Cómo |
|:---------:|--------|------|
| 1️⃣ | Campo del nodo | Escribir directo en `api_key` |
| 2️⃣ | Settings (UI) | ⚙️ > **Google AI API Key (Gemini)** |
| 3️⃣ | Variable de entorno | `export GOOGLE_AI_API_KEY="..."` |

---

## 🔤 Texto — Gemini 3.1 Pro

### GoogleAI_TextNode
| Input | Tipo | Req | Descripción |
|-------|------|:---:|-------------|
| `prompt` | STRING | ✅ | Prompt de texto |
| `model` | COMBO | ✅ | Ver tabla de modelos abajo |
| `thinking_budget` | COMBO | ✅ | Off / Low (1024) / High (8192) |
| `api_key` | STRING | ❌ | Opcional si usas Settings |
| `system_prompt` | STRING | ❌ | Instrucción de sistema |
| `image` | IMAGE | ❌ | Análisis multimodal |
| `youtube_url` | STRING | ❌ | URL de YouTube |
| `max_tokens` | INT | ❌ | 64-65536 |
| `temperature` | FLOAT | ❌ | 0.0-2.0 |
| **Output** | `text` STRING | | |

### GoogleAI_TextVisionNode
| Input | Tipo | Req |
|-------|------|:---:|
| `image` | IMAGE | ✅ |
| `prompt` | STRING | ✅ |
| **Output** | `analysis` STRING | |

---

## 🎨 Imagen — Nano Banana + Imagen 4

Routing automático por modelo seleccionado:

| Modelo | Endpoint | Pines de Referencia | Max Resolución |
|--------|----------|:-------------------:|:--------------:|
| Nano Banana Pro (`gemini-3-pro-image-preview`) | `generateContent` | ✅ Hasta 14 | 4K |
| Nano Banana (`gemini-2.5-flash-image`) | `generateContent` | ✅ Hasta 14 | 1K |
| Imagen 4 Standard / Ultra / Fast | `generateImages` | ❌ | — |
| Imagen 3 | `generateImages` | ❌ | — |

Error HTTP 400 (seguridad) → retorna imagen roja 512×512 sin crashear.

### GoogleAI_ImageNode (Nodo Maestro)
| Input | Tipo | Req | Descripción |
|-------|------|:---:|-------------|
| `prompt` | STRING | ✅ | Prompt de generación |
| `model` | COMBO | ✅ | Nano Banana Pro/Flash o Imagen 4/3 |
| `size_preset` | COMBO | ✅ | Resolución + aspect ratio (1K / 2K / 4K) |
| `seed` | INT | ✅ | Semilla de generación |
| `randomize_seed` | BOOLEAN | ✅ | Aleatorizar semilla |
| `api_key` | STRING | ❌ | Opcional si usas Settings |
| `system_prompt` | STRING | ❌ | Solo Nano Banana |
| `negative_prompt` | STRING | ❌ | Solo Imagen 4/3 |
| `image_1` ... `image_5` | IMAGE | ❌ | Referencias (solo Nano Banana) |
| **Output** | `image` IMAGE | | |

**Size Presets disponibles:**

| Preset | Aspect Ratio | Resolución |
|--------|:------------:|:----------:|
| 1024×1024 (1:1) - 1K | 1:1 | 1K |
| 1280×720 (16:9) - 1K | 16:9 | 1K |
| 720×1280 (9:16) - 1K | 9:16 | 1K |
| 2048×2048 (1:1) - 2K | 1:1 | 2K |
| 2048×1152 (16:9) - 2K | 16:9 | 2K |
| 1152×2048 (9:16) - 2K | 9:16 | 2K |
| 4096×4096 (1:1) - 4K | 1:1 | 4K ⚠️ |
| 4096×2304 (16:9) - 4K | 16:9 | 4K ⚠️ |
| 2304×4096 (9:16) - 4K | 9:16 | 4K ⚠️ |

> ⚠️ **4K solo disponible con Nano Banana Pro** (`gemini-3-pro-image-preview`). Otros modelos → downgrade automático a 2K.

### GoogleAI_ImageBatchNode
| Input | Tipo | Req | Descripción |
|-------|------|:---:|-------------|
| `prompt` | STRING | ✅ | Prompt de generación |
| `model` | COMBO | ✅ | Imagen 4/3 recomendado (batch nativo) |
| `aspect_ratio` | COMBO | ✅ | 1:1, 16:9, 9:16, 4:3, 3:4 |
| `batch_size` | INT (1-4) | ✅ | Número de imágenes |
| `negative_prompt` | STRING | ❌ | Prompt negativo |
| **Output** | `images` IMAGE (batch) | | |

> 💡 Nano Banana no soporta batch nativo. Usa múltiples `GoogleAI_ImageNode` en paralelo.

---

## 🎬 Video — Veo 3.1

> ⚡ **FPS de salida: 24.** Configura VHS Video Combine a **24 FPS**.
>
> 🔊 **Audio nativo:** Todos los nodos de video ahora incluyen output `AUDIO` (Veo 3.1). Veo 2.0 genera silencio automáticamente.

**Resoluciones:** 1080p (16:9 / 9:16 / 1:1) y 4K (16:9 / 9:16)
**Duraciones:** 4, 6, 8 segundos | **Costo:** $0.40 USD/segundo (Standard)

### GoogleAI_VideoGenerator
1 frame → Image-to-Video | >1 frame → Video Extension (último frame)

| Input | Tipo | Req |
|-------|------|:---:|
| `prompt` | STRING | ✅ |
| `model` | COMBO | ✅ |
| `video_preset` | COMBO | ✅ |
| `duration_seconds` | COMBO | ✅ |
| `init_image_or_video` | IMAGE | ❌ |
| `negative_prompt` | STRING | ❌ |
| **Outputs** | `video_frames` IMAGE, `audio` AUDIO, `cost_estimate` STRING | |

### GoogleAI_VideoInterpolation
`last_frame` se redimensiona automáticamente al tamaño de `first_frame`.

| Input | Tipo | Req |
|-------|------|:---:|
| `first_frame` | IMAGE | ✅ |
| `last_frame` | IMAGE | ✅ |
| `prompt` | STRING | ✅ |
| `model` | COMBO | ✅ |
| **Outputs** | `video_frames` IMAGE, `audio` AUDIO, `cost_estimate` STRING | |

### GoogleAI_VideoStoryboard
⚠️ Con imágenes de referencia → duración forzada a **8 segundos**.

| Input | Tipo | Req |
|-------|------|:---:|
| `prompt` | STRING | ✅ |
| `model` | COMBO | ✅ |
| `reference_image_1/2/3` | IMAGE | ❌ |
| **Outputs** | `video_frames` IMAGE, `audio` AUDIO, `cost_estimate` STRING | |

---

## 🔍 Diagnóstico — Gemini 3.1 Pro

| Nodo | Entrada | Salida |
|------|---------|--------|
| **ArchitectureDetector** | `safetensors_path` | `architecture_report` STRING |
| **TriggerWordExtractor** | `lora_path` | `trigger_words` STRING |
| **WorkflowAnalyzer** | `workflow_json` | `analysis_report` STRING |
| **CompatibilityChecker** | `checkpoint_path` + `lora_path` | `is_compatible` BOOL + `report` STRING |
| **LoRATrainingAnalyzer** | `training_logs` (CSV/JSON) | `diagnosis_report` STRING |

---

## 📋 Modelos disponibles

### Texto / Diagnóstico
| String API | Descripción |
|-----------|-------------|
| `gemini-3.1-pro-preview` | Más avanzado — recomendado |
| `gemini-3-pro` | Gemini 3 Pro |
| `gemini-3-flash` | Gemini 3 Flash — rápido |
| `gemini-2.5-pro` | Stable (antes: preview-06-05) |
| `gemini-2.5-flash` | Stable (antes: preview-05-20) |

### Imagen — Nano Banana (generateContent)
| String API | Alias | Descripción |
|-----------|-------|-------------|
| `gemini-3-pro-image-preview` | Nano Banana Pro ⭐ | Hasta 14 refs, hasta 4K |
| `gemini-2.5-flash-image` | Nano Banana | Velocidad, hasta 1K |

### Imagen — Imagen 4/3 (generateImages)
| String API | Descripción |
|-----------|-------------|
| `imagen-4.0-generate-001` | Imagen 4 Standard ⭐ |
| `imagen-4.0-ultra-generate-001` | Imagen 4 Ultra — máxima calidad |
| `imagen-4.0-fast-generate-001` | Imagen 4 Fast — menor latencia |
| `imagen-3.0-generate-002` | Imagen 3 (fallback) |
| `imagen-3.0-fast-generate-001` | Imagen 3 Fast (fallback) |

### Video
| String API | Descripción |
|-----------|-------------|
| `veo-3.1-generate-preview` | Veo 3.1 Standard ⭐ ($0.40/s) + Audio |
| `veo-3.1-fast-generate-preview` | Veo 3.1 Fast ($0.15/s) + Audio |
| `veo-2.0-generate-001` | Veo 2 ($0.05/s) — sin audio |

> ❌ `veo-3.0-generate-preview` — ELIMINADO, deprecado desde Nov 12, 2025
> ❌ `veo-3.1` — string incorrecto, nunca funcionó

---

## 📝 Notas Técnicas

- **Cero SDKs** — Todo usa `requests` HTTP puras (imagen/texto) y `aiohttp` async (video)
- **Tensores estándar** — `[B, H, W, C]` float `0.0-1.0`
- **Video 24 FPS** — Configurar en VHS Video Combine
- **Imagen API** — Nano Banana usa `generateContent` con `responseModalities:IMAGE`; Imagen 4/3 usa `generateImages`
- **Video API** — Usa endpoint `generateVideos` con polling asíncrono
- **Audio nativo** — Veo 3.1 incluye pista de audio en el MP4; extraída con `torchaudio`
- **Error visual** — Todos los nodos de imagen y video retornan imagen roja 512×512 en caso de error
- **4K automático** — Modelos sin soporte 4K hacen downgrade silencioso a 2K
- **Retrocompatible** — Clases originales intactas, nombres de nodo sin cambios

---

Desarrollado por **[Prompt Models Studio](https://github.com/cdanielp)** 🇲🇽
