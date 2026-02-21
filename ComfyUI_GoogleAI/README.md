# 🚀 ComfyUI_GoogleAI V2.1 — Suite Integral de Google AI

> **Gemini 3.1 Pro** (Texto Multimodal + Diagnóstico) · **Imagen 3** (Imágenes) · **Veo 3.1** (Video Async) · **Lyria 3** (Audio)

![Version](https://img.shields.io/badge/Version-2.1.0-blue)
![Nodes](https://img.shields.io/badge/Nodos-14-green)
![Async](https://img.shields.io/badge/Video-Async_Polling-purple)

---

## 📑 Tabla de Contenidos

1. [Qué Hay de Nuevo en V2.1](#-qué-hay-de-nuevo-en-v21)
2. [Instalación](#-instalación)
3. [Configurar API Key](#-configurar-api-key)
4. [Nodos: Texto Multimodal](#-texto-multimodal--gemini-31-pro)
5. [Nodos: Imagen](#-imagen--imagen-3)
6. [Nodos: Video](#-video--veo-31)
7. [Nodos: Audio](#-audio--lyria-3)
8. [Nodos: Diagnóstico](#-diagnóstico--gemini-31-pro)
9. [Notas Técnicas](#-notas-técnicas)

---

## 🆕 Qué Hay de Nuevo en V2.1

### 🛠️ Core y Servidor
- **Dependencias Headless**: `opencv-python-headless` reemplaza a `opencv-python` → obligatorio para RunPod/Colab/servidores Linux sin GUI.
- **Polling Asíncrono de Video**: `generate_video()` es ahora `async def` con `aiohttp` + `asyncio.sleep()`. ComfyUI no se congela durante los 5-10 minutos de generación de video.
- **Sanitización de Semillas**: Método `GoogleAICore.safe_seed()` convierte semillas de 64 bits (generadas por otros nodos) a 32 bits (`seed % 2147483648`) para evitar crashes con APIs de Google.
- **Error Handling Estricto**: HTTP 400 en imagen/video → imagen roja con texto de error. HTTP 400 en audio → audio silencioso (evita Type Mismatch crash).

### 🧠 Texto Multimodal
- `GoogleAI_TextNode` ahora es el **nodo maestro multimodal**: acepta hasta 5 imágenes, video (frames o ruta), audio, documentos, YouTube y seed.
- `GoogleAI_TextVisionNode` se mantiene por retrocompatibilidad.

### 🎨 Imagen
- `seed` acepta 64 bits en la UI (sanitizado a 32 bits internamente).
- `batch_size` integrado directamente (1-4 imágenes).
- 5 puertos `image_1`..`image_5` de referencia opcionales.
- `negative_prompt` restaurado como opcional.

### 🎬 Video
- **Cascada Async**: Todas las funciones `FUNCTION` de video son `async def` + `await`.
- **Sin seed manual**: La API de Veo 3.1 no lo soporta (enviar seed causa HTTP 400).
- 3 puertos de imagen de referencia en Storyboard.

### 🎵 Audio
- `MusicDirector` ahora tiene puerto `video_frames` para **Video-to-Music**.
- **Type Mismatch Fallback**: Errores devuelven audio silencioso (`torch.zeros(1, 1, 48000)`) en vez de imagen roja.

### 🩺 Diagnóstico
- **Subgrupo A** (ArchitectureDetector, TriggerWordExtractor, CompatibilityChecker): Menús desplegables nativos via `folder_paths.get_filename_list()`.
- **Subgrupo B** (WorkflowAnalyzer, LoRATrainingAnalyzer): Nuevo puerto `text_or_file_path` con `forceInput: True` para conexión física desde otros nodos.

---

## 📦 Instalación

```bash
cd ComfyUI/custom_nodes/
git clone https://github.com/cdanielp/COMFYUI_PROMPTMODELS.git ComfyUI_GoogleAI
cd ComfyUI_GoogleAI
pip install -r requirements.txt
```

### Dependencias
| Paquete | Versión | Propósito |
|---------|---------|-----------|
| `requests` | ≥2.28 | HTTP síncrono (texto, imagen, audio) |
| `aiohttp` | ≥3.8 | HTTP asíncrono (video polling) |
| `opencv-python-headless` | ≥4.8 | Decodificación MP4 → frames (servidores sin GUI) |
| `torchaudio` | ≥2.0 | Conversión audio WAV ↔ tensor |
| `safetensors` | ≥0.4 | Lectura de checkpoints/LoRAs para diagnóstico |

> 💡 **Explicador de Errores:** Fue separado al plugin universal [ComfyUI_UniversalErrorExplainer](https://github.com/cdanielp/ComfyUI_UniversalErrorExplainer). Compatible con Gemini, OpenAI, Anthropic y Ollama.

---

## 🔑 Configurar API Key

La API Key se busca en este orden de prioridad:

| Prioridad | Fuente | Cómo |
|:---------:|--------|------|
| 1️⃣ | Campo del nodo | Escribir directo en `api_key` de cualquier nodo |
| 2️⃣ | Settings (UI) | ⚙️ > **Google AI API Key (Gemini)** |
| 3️⃣ | Variable de entorno | `export GOOGLE_AI_API_KEY="tu-clave-aquí"` |

El frontend JS inyecta automáticamente la clave de Settings en todos los nodos GoogleAI_ que tengan el campo vacío al ejecutar el workflow.

---

## 🔤 Texto Multimodal — Gemini 3.1 Pro

### GoogleAI_TextNode ⭐ Nodo Maestro Multimodal
Un solo nodo para texto, visión, análisis de video, audio y documentos.

| Input | Tipo | Req | Descripción |
|-------|------|:---:|-------------|
| `prompt` | STRING | ✅ | Prompt principal de texto |
| `model` | COMBO | ✅ | gemini-3.1-pro-preview, gemini-2.5-pro, flash, flash-lite |
| `thinking_budget` | COMBO | ✅ | Off / Low (1024 tokens) / High (8192 tokens) |
| `api_key` | STRING | ❌ | Opcional si configuraste Settings o variable de entorno |
| `system_prompt` | STRING | ❌ | Instrucción de sistema para guiar comportamiento |
| `image_1`..`image_5` | IMAGE | ❌ | Hasta 5 imágenes de análisis simultáneo |
| `video_frames` | IMAGE | ❌ | Frames [B,H,W,C] desde Load Video / VHS (muestrea 8 frames) |
| `video_path` | STRING | ❌ | Ruta local a .mp4/.webm para análisis directo |
| `audio` | AUDIO | ❌ | Diccionario de audio ComfyUI para transcripción/análisis |
| `files` | * | ❌ | Cualquier dato serializable como contexto textual |
| `youtube_url` | STRING | ❌ | URL de YouTube para análisis de video online |
| `max_tokens` | INT | ❌ | 64 – 65536 (default: 4096) |
| `temperature` | FLOAT | ❌ | 0.0 – 2.0 (default: 0.7) |
| `seed` | INT | ❌ | 64 bits en UI → sanitizado a 32 bits internamente |
| **Output** | `text` STRING | | Respuesta de Gemini |

**Ejemplos de uso:**
- Solo texto: Escribe un prompt, ejecuta.
- Análisis de imagen: Conecta image_1 + "Describe esta imagen".
- Comparación: Conecta 3 imágenes + "Compara estas tres fotos".
- Video-to-Text: Conecta video_frames de un nodo VHS + "Describe la acción".
- Audio + texto: Conecta audio + "Transcribe este audio al español".

### GoogleAI_TextVisionNode (Retrocompatibilidad)
| Input | Tipo | Req |
|-------|------|:---:|
| `image` | IMAGE | ✅ |
| `prompt` | STRING | ✅ |
| **Output** | `analysis` STRING | |

> ⚠️ Se recomienda migrar a `GoogleAI_TextNode` con `image_1`.

---

## 🎨 Imagen — Imagen 3

### GoogleAI_ImageNode
Genera imágenes con seed reproducible, batch y hasta 5 referencias.
Error HTTP 400 (violación de seguridad) → retorna imagen roja 512×512, **no crashea**.

| Input | Tipo | Req | Descripción |
|-------|------|:---:|-------------|
| `prompt` | STRING | ✅ | Descripción de la imagen a generar |
| `model` | COMBO | ✅ | imagen-3.0-generate-002, 001, fast-001 |
| `aspect_ratio` | COMBO | ✅ | 1:1, 16:9, 9:16, 4:3, 3:4 |
| `seed` | INT | ✅ | 0 – 0xFFFFFFFFFFFFFFFF (sanitizado a 32 bits con `safe_seed()`) |
| `batch_size` | INT | ✅ | 1 – 4 imágenes por ejecución |
| `api_key` | STRING | ❌ | Opcional si usas Settings |
| `negative_prompt` | STRING | ❌ | Elementos a evitar en la generación |
| `image_1`..`image_5` | IMAGE | ❌ | Imágenes de referencia para style transfer, edit, etc. |
| **Output** | `image` IMAGE | | Tensor [B, H, W, C] (B=batch_size) |

**Sobre la sanitización de seeds:** Muchos nodos de ComfyUI generan semillas de 64 bits (`max: 0xFFFFFFFFFFFFFFFF`). La API de Google requiere int32 (máx 2147483647). `safe_seed()` aplica `seed % 2147483648` automáticamente → nunca crashea por overflow.

### GoogleAI_ImageBatchNode (Retrocompatibilidad)
| Input | Tipo | Req |
|-------|------|:---:|
| `batch_size` | INT (1-4) | ✅ |
| **Output** | `images` IMAGE (batch) | |

> ⚠️ Se recomienda usar `GoogleAI_ImageNode` con `batch_size` directamente.

---

## 🎬 Video — Veo 3.1

> ⚡ **FPS de salida: 24.** Configura VHS Video Combine a **24 FPS**.
>
> 🔄 **Polling asíncrono:** El event loop de ComfyUI NO se bloquea durante la generación (5-10 min).

**Resoluciones:** 1920×1080, 1080×1920, 1080×1080, 3840×2160, 2160×3840
**Duraciones:** 4, 6, 8 segundos | **Costo:** $0.05 USD/segundo

> ⚠️ **Sin seed manual.** La API de Veo 3.1 no soporta el parámetro seed. Enviarlo causa HTTP 400.

### GoogleAI_VideoGenerator
1 frame → Image-to-Video | >1 frame → Video Extension (último frame)

| Input | Tipo | Req | Descripción |
|-------|------|:---:|-------------|
| `prompt` | STRING | ✅ | Descripción del video |
| `model` | COMBO | ✅ | veo-3.1, veo-3.0, veo-2.0 |
| `video_preset` | COMBO | ✅ | Resolución (16:9, 9:16, 1:1, 4K) |
| `duration_seconds` | COMBO | ✅ | 4, 6, u 8 segundos |
| `api_key` | STRING | ❌ | Opcional |
| `init_image_or_video` | IMAGE | ❌ | 1 frame=Img2Vid, >1=Extension (último frame) |
| `negative_prompt` | STRING | ❌ | Elementos a evitar |
| **Outputs** | `video_frames` IMAGE, `cost_estimate` STRING | |

**Flujo interno:**
1. `generate_video()` envía POST a `predictLongRunning` → recibe `operation_name`
2. Loop `await asyncio.sleep(15)` + GET polling cada 15s hasta `done: true`
3. Descarga video (inlineData o videoUri) → OpenCV extrae frames → tensor [B,H,W,C]

### GoogleAI_VideoInterpolation
Genera video interpolando entre dos frames. `last_frame` se redimensiona automáticamente.

| Input | Tipo | Req |
|-------|------|:---:|
| `first_frame` | IMAGE | ✅ |
| `last_frame` | IMAGE | ✅ |
| `prompt` | STRING | ✅ |
| **Outputs** | `video_frames` IMAGE, `cost_estimate` STRING | |

### GoogleAI_VideoStoryboard
Video estilizado con imágenes de referencia.

| Input | Tipo | Req | Descripción |
|-------|------|:---:|-------------|
| `prompt` | STRING | ✅ | Descripción de la escena |
| `reference_image_1` | IMAGE | ❌ | Referencia visual 1 |
| `reference_image_2` | IMAGE | ❌ | Referencia visual 2 |
| `reference_image_3` | IMAGE | ❌ | Referencia visual 3 |
| **Outputs** | `video_frames` IMAGE, `cost_estimate` STRING | |

> ⚠️ **Restricción API:** Cuando se usan imágenes de referencia, la duración se **forza a 8 segundos** automáticamente.

---

## 🎵 Audio — Lyria 3

SynthID warnings se filtran automáticamente sin afectar la generación.

> ⚠️ **Type Mismatch Fallback:** Si la API bloquea el prompt (HTTP 400/safety), los nodos de audio devuelven **audio silencioso** (`torch.zeros(1, 1, 48000)`) en vez de imagen roja. Esto evita que ComfyUI crashee por incompatibilidad de tipos.

### GoogleAI_MusicDirector
| Input | Tipo | Req | Descripción |
|-------|------|:---:|-------------|
| `prompt` | STRING | ✅ | Descripción de la música deseada |
| `vocals` | BOOL | ✅ | True=voces y canto, False=instrumental |
| `api_key` | STRING | ❌ | Opcional |
| `model` | COMBO | ❌ | lyria-3 |
| `init_image` | IMAGE | ❌ | Imagen de referencia contextual (ej: portada de álbum) |
| `video_frames` | IMAGE | ❌ | Frames de video [B,H,W,C] para Video-to-Music 🆕 |
| **Output** | `audio` AUDIO (30s) | | |

**Video-to-Music:** Conecta la salida `video_frames` de un VideoGenerator al puerto `video_frames` del MusicDirector. Lyria 3 analiza los frames y genera música sincronizada con el contenido visual. Se muestrean máximo 8 frames espaciados para no exceder el contexto.

### GoogleAI_FoleyGenerator
| Input | Tipo | Req | Descripción |
|-------|------|:---:|-------------|
| `video_frames` | IMAGE | ✅ | Tensor 4D de frames de video |
| `prompt` | STRING | ✅ | Guía para los efectos de sonido |
| `max_frames_to_send` | INT | ❌ | 2-16 frames a enviar (default: 8) |
| **Output** | `foley_audio` AUDIO | | Duración estimada automáticamente |

---

## 🔍 Diagnóstico — Gemini 3.1 Pro

### Subgrupo A: Menús Desplegables Inteligentes 🆕

Estos nodos ahora usan `folder_paths.get_filename_list()` para crear menús desplegables nativos en la UI de ComfyUI. **Ya no necesitas escribir rutas manualmente.**

| Nodo | Entrada UI | Salida |
|------|-----------|--------|
| **ArchitectureDetector** | `checkpoint` (menú desplegable de checkpoints) | `architecture_report` STRING |
| **TriggerWordExtractor** | `lora` (menú desplegable de LoRAs) | `trigger_words` STRING |
| **CompatibilityChecker** | `checkpoint` + `lora` (menús desplegables) | `is_compatible` BOOL + `report` STRING |

**Cómo funciona:** El backend usa `folder_paths.get_full_path()` para resolver la ruta absoluta del archivo seleccionado, leer sus tensores con `safetensors`, y enviar las keys a Gemini para análisis.

### Subgrupo B: Diagnóstico de Texto/Workflow

Estos nodos mantienen el cuadro de texto manual y añaden un **puerto físico de conexión** `text_or_file_path` (con `forceInput: True`) para recibir datos desde otros nodos.

| Nodo | Entrada Principal | Puerto Físico 🆕 | Salida |
|------|-------------------|-------------------|--------|
| **WorkflowAnalyzer** | `workflow_json` (STRING multiline) | `text_or_file_path` (STRING, forceInput) | `analysis_report` STRING |
| **LoRATrainingAnalyzer** | `training_logs` (STRING multiline) | `text_or_file_path` (STRING, forceInput) | `diagnosis_report` STRING |

**Prioridad de fuentes:** Si `text_or_file_path` tiene contenido, toma prioridad sobre el campo principal. Esto permite encadenar nodos: un nodo "Load Text" → `text_or_file_path` del analizador.

---

## 📝 Notas Técnicas

### Arquitectura
- **Cero SDKs** — Todo usa `requests` HTTP puras. Video usa `aiohttp` para polling asíncrono.
- **Tensores estándar** — `[B, H, W, C]` float `0.0-1.0` para todas las imágenes/video.
- **Video 24 FPS** — Estándar de Veo 3.1. Configurar en VHS Video Combine.

### Manejo de Errores por Tipo
| Tipo de Nodo | Error HTTP 400 / Safety | Resultado |
|:------------:|:-----------------------:|:---------:|
| **Imagen** | `create_error_image()` | Imagen roja 512×512 con texto |
| **Video** | `create_error_image()` | Imagen roja 512×512 con texto |
| **Audio** | Audio silencioso | `torch.zeros(1, 1, 48000)` @ 48kHz |
| **Texto** | String de error | `"❌ Error: ..."` |

### Sanitización de Seeds
```
Input (64 bits): 18446744073709551615
safe_seed():    18446744073709551615 % 2147483648 = 2147483647
Output (32 bits): 2147483647
```

### Cascada Async (Video)
```
google_video_node.py          →  google_core.py
async def generate_video()    →  await GoogleAICore.generate_video()
async def interpolate()       →  await GoogleAICore.generate_video()
async def generate_storyboard() → await GoogleAICore.generate_video()
```
ComfyUI soporta nodos asíncronos nativamente. El event loop no se bloquea.

### Retrocompatibilidad
Las siguientes clases se mantienen por retrocompatibilidad con workflows existentes:
- `GoogleAI_TextVisionNode` → usar `GoogleAI_TextNode` con `image_1`
- `GoogleAI_ImageBatchNode` → usar `GoogleAI_ImageNode` con `batch_size`

---

## 📋 Endpoint de Salud

```bash
curl http://localhost:8188/google-ai/health
```
```json
{
    "status": "ok",
    "version": "2.1.0",
    "nodes": 14,
    "suites": ["text", "image", "video", "audio", "diagnostic"],
    "video_polling": "async (aiohttp)",
    "seed_sanitization": "64→32 bits"
}
```

---

Desarrollado por **[Prompt Models Studio](https://github.com/cdanielp)** 🇲🇽
