# 🚀 ComfyUI_GoogleAI V2.4.3 — Suite Integral de Google AI

> **Nano Banana Pro/Flash** (Imagen Multimodal) · **Imagen 4** (Generación Pura) · **Veo 3.1** (Video + Audio) · **Gemini 3.1 Pro** (Texto/Diagnóstico)

![Version](https://img.shields.io/badge/Version-2.4.3-blue)
![Nodes](https://img.shields.io/badge/Nodos-12-green)

> ⚠️ **Audio (Lyria 3)** removido — `lyria-3` no tiene endpoint de API pública (Feb 2026). Disponible solo en la app de Gemini. Se reintegrará cuando Google abra la API.

> ### 🧪 VERSIÓN EN PRUEBAS
> Esta versión (V2.4.3) incluye cambios significativos respecto a V2.4.2. Si encuentras nodos rojos, desconexiones o errores inesperados:
> 1. **Nodos de audio Lyria** (`MusicDirector`, `FoleyGenerator`) — fueron eliminados. Bórralos del workflow.
> 2. **Nodos de video** — ahora tienen una salida `AUDIO` adicional. Reconecta los nodos downstream.
> 3. **Video negro** — requiere ffmpeg instalado. Ver [Solución de Problemas](#-solución-de-problemas).
> 4. Reporta cualquier issue en [GitHub Issues](https://github.com/cdanielp/COMFYUI_PROMPTMODELS/issues).

---

## 📑 Tabla de Contenidos

1. [Novedades V2.4.3](#-novedades-v243)
2. [Instalación](#-instalación)
3. [Configurar API Key](#-configurar-api-key)
4. [Nodos: Texto](#-texto--gemini-31-pro)
5. [Nodos: Imagen](#-imagen--nano-banana--imagen-4)
6. [Nodos: Video](#-video--veo-31)
7. [Nodos: Diagnóstico](#-diagnóstico--gemini-31-pro)
8. [Modelos disponibles](#-modelos-disponibles)
9. [Notas Técnicas](#-notas-técnicas)
10. [Solución de Problemas](#-solución-de-problemas)

---

## 🆕 Novedades V2.4.3

### 🔧 Fixes Críticos
- **Video negro resuelto** — Los videos de Veo 3.1 usan códec HEVC/VP9 que torchvision y OpenCV no decodifican en sus builds estándar. Ahora se transcodifica automáticamente a H.264 via ffmpeg antes de extraer frames.
- **Audio funcional** — `video_bytes_to_audio()` reescrito completamente. Usa ffmpeg directo (sin torchaudio ni moviepy) para extraer la pista de audio como WAV PCM → tensor. Funciona en cualquier entorno con ffmpeg.
- **Diagnóstico automático** — El tensor de video ahora reporta `min/max/mean` en consola. Si detecta frames negros (`max < 0.01`) alerta con la causa probable.
- **Fallback graceful** — Si ffmpeg no está instalado, intenta decodificar directo (puede fallar con HEVC) en vez de crashear.

### 📦 Nuevo: `install.py`
- Instala `ffmpeg` automáticamente en Docker/ComfyDeploy durante setup del nodo.
- Instala `scipy` para lectura WAV optimizada (fallback manual si no está).
- Idempotente: si ya está instalado, no hace nada.

### Novedades V2.4.2 (anteriores)
- **Nano Banana Pro/Flash** — 5 pines de referencia, routing automático
- **Size Presets inteligentes** — Mapeo `size_preset → aspectRatio + resolution_hint`
- **Validación 4K** — Downgrade automático a 2K en modelos no-Pro
- **Audio en todos los nodos de video** — Output `AUDIO` en VideoInterpolation y VideoStoryboard

---

## 📦 Instalación

```bash
cd ComfyUI/custom_nodes/
git clone https://github.com/cdanielp/COMFYUI_PROMPTMODELS.git ComfyUI_GoogleAI
cd ComfyUI_GoogleAI
pip install -r requirements.txt
```

### ⚠️ Requisito: ffmpeg

ffmpeg es **necesario** para video (Veo 3.1) y extracción de audio. Se instala automáticamente via `install.py` en Docker/ComfyDeploy.

**Instalación manual (si es necesario):**
```bash
# Linux / Docker
apt install ffmpeg

# macOS
brew install ffmpeg

# Windows
choco install ffmpeg
# O descarga de: https://ffmpeg.org/download.html
```

**Verificar instalación:**
```bash
ffmpeg -version
ffprobe -version
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
> 🔊 **Audio nativo:** Todos los nodos de video incluyen output `AUDIO` (Veo 3.1). Veo 2.0 genera silencio automáticamente.
>
> 🛠️ **Transcodificación automática:** El video se transcodifica de HEVC/VP9 a H.264 via ffmpeg antes de extraer frames. Requiere ffmpeg instalado.

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

## 🔧 Solución de Problemas

### Video negro (pantalla negra)
**Causa:** El códec del video de Veo 3.1 (HEVC/VP9) no es compatible con torchvision/OpenCV.
**Solución:** Instalar ffmpeg. V2.4.3 transcodifica automáticamente a H.264.
```bash
# Verificar
ffprobe -v error -select_streams v:0 -show_entries stream=codec_name video.mp4

# En consola de ComfyUI deberías ver:
# [Transcode] Códec original: vp9 | pix_fmt: yuv420p | 1920x1080
# [Transcode] OK → 13909KB → 12000KB (H.264)
# [Video (TorchVision)] 192 frames, 1920x1080 | min=0.003 max=0.984 mean=0.41
```

### Audio silencioso / dummy
**Causa:** ffmpeg no instalado o el video no tiene pista de audio.
**Verificar en consola:**
- `[VideoAudio] Audio OK: torch.Size([1, 2, 352800]) @ 44100Hz` → ✅ Funciona
- `[VideoAudio] ffmpeg no disponible → dummy silencioso` → Instalar ffmpeg
- `[VideoAudio] Sin pista de audio en el MP4 → dummy` → El video no tiene audio (normal en Veo 2.0)

### ffmpeg no se instala en Docker
**Solución:** Agregar al Dockerfile:
```dockerfile
RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg && rm -rf /var/lib/apt/lists/*
```

---

## 📝 Notas Técnicas

- **Cero SDKs** — Todo usa `requests` HTTP puras (imagen/texto) y `aiohttp` async (video)
- **Tensores estándar** — `[B, H, W, C]` float `0.0-1.0`
- **Video 24 FPS** — Configurar en VHS Video Combine
- **Transcodificación** — HEVC/VP9/AV1 → H.264/yuv420p via ffmpeg antes de decodificar
- **Audio** — Extracción via ffmpeg → WAV PCM 16-bit → tensor (sin torchaudio/moviepy)
- **Imagen API** — Nano Banana usa `generateContent` con `responseModalities:IMAGE`; Imagen 4/3 usa `generateImages`
- **Video API** — Usa endpoint `predictLongRunning` con polling asíncrono
- **Error visual** — Todos los nodos de imagen y video retornan imagen roja 512×512 en caso de error
- **4K automático** — Modelos sin soporte 4K hacen downgrade silencioso a 2K
- **Retrocompatible** — Clases originales intactas, nombres de nodo sin cambios

---

Desarrollado por **[Prompt Models Studio](https://github.com/cdanielp)** 🇲🇽
