# 🚀 ComfyUI_GoogleAI V2.0 — Suite Integral de Google AI

> **Gemini 3.1 Pro** (Texto/Diagnóstico) · **Imagen 3** (Imágenes) · **Veo 3.1** (Video) · **Lyria 3** (Audio)

![Version](https://img.shields.io/badge/Version-2.0.0-blue)
![Nodes](https://img.shields.io/badge/Nodos-14-green)

---

## 📑 Tabla de Contenidos

1. [Instalación](#-instalación)
2. [Configurar API Key](#-configurar-api-key)
3. [Nodos: Texto](#-texto--gemini-31-pro)
4. [Nodos: Imagen](#-imagen--imagen-3)
5. [Nodos: Video](#-video--veo-31)
6. [Nodos: Audio](#-audio--lyria-3)
7. [Nodos: Diagnóstico](#-diagnóstico--gemini-31-pro)
8. [Notas Técnicas](#-notas-técnicas)

---

## 📦 Instalación

```bash
cd ComfyUI/custom_nodes/
git clone https://github.com/cdanielp/COMFYUI_PROMPTMODELS.git ComfyUI_GoogleAI
cd ComfyUI_GoogleAI
pip install -r requirements.txt
```

> 💡 **Explicador de Errores:** Fue separado al plugin universal [ComfyUI_UniversalErrorExplainer](https://github.com/cdanielp/ComfyUI_UniversalErrorExplainer). Compatible con Gemini, OpenAI, Anthropic y Ollama.

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
| `model` | COMBO | ✅ | gemini-3.1-pro-preview, etc. |
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

## 🎨 Imagen — Imagen 3

### GoogleAI_ImageNode
Error HTTP 400 (seguridad) → retorna imagen roja 512×512 sin crashear.

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

**Resoluciones:** 1920×1080, 1080×1920, 1080×1080, 3840×2160, 2160×3840  
**Duraciones:** 4, 6, 8 segundos | **Costo:** $0.05 USD/segundo

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

## 🎵 Audio — Lyria 3

SynthID warnings se filtran automáticamente.

### GoogleAI_MusicDirector
| Input | Tipo | Req | Descripción |
|-------|------|:---:|-------------|
| `prompt` | STRING | ✅ | Descripción de la música |
| `vocals` | BOOL | ✅ | True=voces, False=instrumental |
| `init_image` | IMAGE | ❌ | Referencia contextual |
| **Output** | `audio` AUDIO (30s) | | |

### GoogleAI_FoleyGenerator
| Input | Tipo | Req |
|-------|------|:---:|
| `video_frames` | IMAGE | ✅ |
| `prompt` | STRING | ✅ |
| `max_frames_to_send` | INT | ❌ |
| **Output** | `foley_audio` AUDIO | |

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

## 📝 Notas Técnicas

- **Cero SDKs** — Todo usa `requests` HTTP puras
- **Tensores estándar** — `[B, H, W, C]` float `0.0-1.0`
- **Video 24 FPS** — Configurar en VHS Video Combine
- **Retrocompatible** — Clases originales intactas

---

Desarrollado por **[Prompt Models Studio](https://github.com/cdanielp)** 🇲🇽
