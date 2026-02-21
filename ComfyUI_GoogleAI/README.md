# 🚀 ComfyUI_GoogleAI V2.0.1 — Suite Integral de Google AI

> **Gemini 3.1 Pro** (Texto/Diagnóstico) · **Imagen 4** (Imágenes) · **Veo 3.1** (Video)

![Version](https://img.shields.io/badge/Version-2.0.1-blue)
![Nodes](https://img.shields.io/badge/Nodos-12-green)

> ⚠️ **Audio (Lyria 3)** removido en V2.0.1 — `lyria-3` no tiene endpoint de API pública (Feb 2026). Disponible solo en la app de Gemini. Se reintegrará cuando Google abra la API.

---

## 📑 Tabla de Contenidos

1. [Instalación](#-instalación)
2. [Configurar API Key](#-configurar-api-key)
3. [Nodos: Texto](#-texto--gemini-31-pro)
4. [Nodos: Imagen](#-imagen--imagen-4)
5. [Nodos: Video](#-video--veo-31)
6. [Nodos: Diagnóstico](#-diagnóstico--gemini-31-pro)
7. [Modelos disponibles](#-modelos-disponibles)
8. [Notas Técnicas](#-notas-técnicas)

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

## 🎨 Imagen — Imagen 4

Error HTTP 400 (seguridad) → retorna imagen roja 512×512 sin crashear.

### GoogleAI_ImageNode
| Input | Tipo | Req |
|-------|------|:---:|
| `prompt` | STRING | ✅ |
| `model` | COMBO | ✅ |
| `aspect_ratio` | COMBO | ✅ |
| `negative_prompt` | STRING | ❌ |
| **Output** | `image` IMAGE | |

### GoogleAI_ImageBatchNode
| Input | Tipo | Req |
|-------|------|:---:|
| `batch_size` | INT (1-4) | ✅ |
| **Output** | `images` IMAGE (batch) | |

---

## 🎬 Video — Veo 3.1

> ⚡ **FPS de salida: 24.** Configura VHS Video Combine a **24 FPS**.

**Resoluciones:** 1080p (16:9 / 9:16 / 1:1) y 4K (16:9 / 9:16)
**Duraciones:** 4, 6, 8 segundos | **Costo:** $0.40 USD/segundo (Standard)

### GoogleAI_VideoGenerator
1 frame → Image-to-Video | >1 frame → Video Extension (último frame)

| Input | Tipo | Req |
|-------|------|:---:|
| `prompt` | STRING | ✅ |
| `video_preset` | COMBO | ✅ |
| `duration_seconds` | COMBO | ✅ |
| `init_image_or_video` | IMAGE | ❌ |
| **Outputs** | `video_frames` IMAGE, `cost_estimate` STRING | |

### GoogleAI_VideoInterpolation
`last_frame` se redimensiona automáticamente al tamaño de `first_frame`.

| Input | Tipo | Req |
|-------|------|:---:|
| `first_frame` | IMAGE | ✅ |
| `last_frame` | IMAGE | ✅ |
| **Outputs** | `video_frames` IMAGE, `cost_estimate` STRING | |

### GoogleAI_VideoStoryboard
⚠️ Con imágenes de referencia → duración forzada a **8 segundos**.

| Input | Tipo | Req |
|-------|------|:---:|
| `reference_image_1/2/3` | IMAGE | ❌ |
| **Outputs** | `video_frames` IMAGE, `cost_estimate` STRING | |

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
| `gemini-2.5-flash-lite` | Más económico |

### Imagen
| String API | Descripción |
|-----------|-------------|
| `imagen-4.0-generate-001` | Imagen 4 Standard ⭐ |
| `imagen-4.0-ultra-generate-001` | Imagen 4 Ultra — máxima calidad |
| `imagen-4.0-fast-generate-001` | Imagen 4 Fast — menor latencia |
| `imagen-3.0-generate-002` | Imagen 3 (fallback) |

### Video
| String API | Descripción |
|-----------|-------------|
| `veo-3.1-generate-preview` | Veo 3.1 Standard ⭐ ($0.40/s) |
| `veo-3.1-fast-generate-preview` | Veo 3.1 Fast ($0.15/s) |
| `veo-2.0-generate-001` | Veo 2 ($0.05/s) |

> ❌ `veo-3.0-generate-preview` — ELIMINADO, deprecado desde Nov 12, 2025
> ❌ `veo-3.1` — string incorrecto, nunca funcionó

---

## 📝 Notas Técnicas

- **Cero SDKs** — Todo usa `requests` HTTP puras
- **Tensores estándar** — `[B, H, W, C]` float `0.0-1.0`
- **Video 24 FPS** — Configurar en VHS Video Combine
- **Imagen API** — Usa endpoint `generateImages` (correcto para Imagen 3/4)
- **Video API** — Usa endpoint `generateVideos` con polling asíncrono
- **Retrocompatible** — Clases originales intactas

---

Desarrollado por **[Prompt Models Studio](https://github.com/cdanielp)** 🇲🇽
