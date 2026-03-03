# ComfyUI_GoogleAI V2.5.0

**Suite completa de Google AI para ComfyUI** — Nano Banana 2/Pro | Imagen 4 | Veo 3.1 + Audio | Diagnostico

> **Autor:** [Prompt Models Studio](https://github.com/cdanielp) | cdanielp
> **Licencia:** MIT

---

## Novedades V2.5.0

### Nuevo nodo estrella: Nano Banana (NB2/Pro)

Nodo dedicado exclusivamente a los modelos Nano Banana con todas sus capacidades:

| Modelo | String API | Max Res | Aspect Ratios | Notas |
|--------|-----------|---------|---------------|-------|
| **Nano Banana 2** | `gemini-3.1-flash-image-preview` | 4K | 14 (incl. 1:4, 8:1) | Pro quality @ Flash speed. Free: 500 imgs/dia |
| **Nano Banana Pro** | `gemini-3-pro-image-preview` | 4K | 14 | Hasta 14 imagenes de referencia |
| **Nano Banana** | `gemini-2.5-flash-image` | 1K | 14 | Velocidad maxima |

### Cambios criticos

- **ThinkingConfig corregido**: `thinkingLevel` (string) para Gemini 3+, `thinkingBudget` (numerico) para Gemini 2.5
- **Model strings corregidos**: `gemini-3-flash-preview` (no `gemini-3-flash`)
- **gemini-3-pro-preview eliminado** — deprecated 9 Mar 2026
- **ImageBatchNode eliminado** — usar multiples nodos en paralelo
- **14 aspect ratios**: `1:1, 1:4, 1:8, 2:3, 3:2, 3:4, 4:1, 4:3, 4:5, 5:4, 8:1, 9:16, 16:9, 21:9`
- **5 imageSize separados**: `512px, 0.5K, 1K, 2K, 4K`
- **responseModalities**: `["TEXT", "IMAGE"]` para compatibilidad con Vertex AI
- **HTTP 500 retryable**: call_with_backoff ahora reintenta errores 500 transitorios
- **MIME detection**: JPEG + WEBP + PNG (antes solo WEBP/PNG)

---

## Instalacion

### ComfyUI Manager (recomendado)

Busca `ComfyUI_GoogleAI` o `COMFYUI_PROMPTMODELS` en el Manager e instala.

### Manual

```bash
cd ComfyUI/custom_nodes
git clone https://github.com/cdanielp/COMFYUI_PROMPTMODELS.git
cd COMFYUI_PROMPTMODELS
pip install -r requirements.txt
```

### API Key

1. Obtener en [Google AI Studio](https://aistudio.google.com/apikey)
2. Configurar en **ComfyUI Settings** > **Google AI API Key**, O
3. Variable de entorno: `GOOGLE_AI_API_KEY=tu_key`

---

## Nodos disponibles (12)

### Texto (2 nodos)

| Nodo | Funcion |
|------|---------|
| **Text Generator** | Texto con Gemini. 5 imagenes, YouTube, thinking. |
| **Vision Analyzer** | Analisis de imagenes. 1 obligatoria + 4 opcionales. |

**Modelos de texto:**
- `gemini-3.1-pro-preview` — thinkingLevel (low/medium/high)
- `gemini-3-flash-preview` — thinkingLevel (low/medium/high)
- `gemini-2.5-pro` — thinkingBudget (1024/4096/8192)
- `gemini-2.5-flash` — thinkingBudget (1024/4096/8192)

### Imagen (2 nodos)

| Nodo | API | Modelos |
|------|-----|---------|
| **Nano Banana (NB2/Pro)** | generateContent | NB2, NB Pro, NB Original |
| **Image Generator (Imagen 4)** | generateImages | Imagen 4/3 Standard/Ultra/Fast |

**Nano Banana Node** — Inputs:
- `prompt`, `model`, `aspect_ratio` (14 opciones), `image_size` (5 opciones)
- `seed`, `randomize_seed`, `system_prompt`, `safety_threshold`
- `image_1..image_5` — pines de referencia opcionales
- **Outputs:** IMAGE + STRING (descripcion)

**Image Generator** — Inputs:
- `prompt`, `model`, `aspect_ratio` (5 opciones: 1:1, 16:9, 9:16, 4:3, 3:4)
- `seed`, `randomize_seed`, `negative_prompt`
- **Output:** IMAGE

### Video (3 nodos)

| Nodo | Funcion |
|------|---------|
| **Video Generator** | Text/Image-to-Video con Veo 3.1 |
| **Video Interpolation** | Transicion entre 2 frames |
| **Video Storyboard** | Video estilizado con hasta 3 referencias |

**Modelos de video:**
- `veo-3.1-generate-preview` — Standard, audio nativo
- `veo-3.1-fast-generate-preview` — Fast, audio nativo
- `veo-2.0-generate-001` — Sin audio (silencio automatico)

**Resoluciones:** 1080p (16:9, 9:16, 1:1) | 4K (16:9, 9:16)
**Duracion:** 4, 6, 8 segundos | **FPS:** 24
**Costo:** $0.40 USD/segundo (Veo 3.1 Standard)

### Diagnostico (5 nodos)

| Nodo | Funcion |
|------|---------|
| **Architecture Detector** | Identifica arquitectura de .safetensors |
| **Trigger Word Extractor** | Extrae trigger words de LoRAs |
| **Workflow Analyzer** | Analiza workflows JSON, encuentra repos |
| **Compatibility Checker** | Verifica checkpoint + LoRA compatibilidad |
| **Training Analyzer** | Diagnostica overfitting en logs CSV/JSON |

---

## Aspect Ratios por modelo

| Ratio | NB2 | NB Pro | NB Orig | Imagen 4 |
|-------|-----|--------|---------|----------|
| 1:1 | Yes | Yes | Yes | Yes |
| 16:9 | Yes | Yes | Yes | Yes |
| 9:16 | Yes | Yes | Yes | Yes |
| 4:3 | Yes | Yes | Yes | Yes |
| 3:4 | Yes | Yes | Yes | Yes |
| 2:3 | Yes | Yes | Yes | - |
| 3:2 | Yes | Yes | Yes | - |
| 4:5 | Yes | Yes | Yes | - |
| 5:4 | Yes | Yes | Yes | - |
| 21:9 | Yes | Yes | Yes | - |
| 1:4 | Yes | - | - | - |
| 4:1 | Yes | - | - | - |
| 1:8 | Yes | - | - | - |
| 8:1 | Yes | - | - | - |

## imageSize por modelo

| Size | NB2 | NB Pro | NB Orig |
|------|-----|--------|---------|
| 512px | Yes | Yes | Yes |
| 0.5K | Yes | - | - |
| 1K | Yes | Yes | Yes |
| 2K | Yes | Yes | - |
| 4K | Yes | Yes | - |

> NB Original se auto-downgrade a 1K si se selecciona mayor resolucion.

---

## Requisitos del sistema

- **Python** >= 3.10
- **ComfyUI** (cualquier version reciente)
- **ffmpeg** — necesario para video/audio (se instala automaticamente en Docker)
- **GPU** — recomendada para torchvision video decoding

### Dependencias Python

```
requests>=2.28.0
aiohttp>=3.8.0
Pillow>=9.0.0
opencv-python-headless>=4.8.0
safetensors>=0.4.0
scipy>=1.10.0
```

---

## Changelog

### V2.5.0 (Mar 2026)
- Nano Banana 2 model support
- Dedicated NanoBanana node with 14 aspect ratios + 5 imageSize
- ThinkingConfig fix (thinkingLevel vs thinkingBudget)
- Fixed model strings (gemini-3-flash-preview)
- TextNode: 5 image inputs
- Removed ImageBatchNode
- HTTP 500 retry support
- MIME detection fix (JPEG)
- responseModalities: TEXT+IMAGE

### V2.4.3
- Video black screen fix (H.264 transcoding)
- Audio extraction via ffmpeg (no torchaudio/moviepy)

### V2.4.2
- Nano Banana Pro support with 5 reference image pins
- Size presets with resolution hints
- 4K validation

---

## Comunidad

- [Skool Community](https://www.skool.com/prompt-models-studio) — 2,000+ miembros
- [GitHub Issues](https://github.com/cdanielp/COMFYUI_PROMPTMODELS/issues)
