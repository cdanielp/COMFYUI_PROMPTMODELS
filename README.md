<div align="center">

<img src="prompts models logo.png" alt="Prompt Models Studio" width="200"/>

# 🎨 COMFYUI_PROMPTMODELS

![Version](https://img.shields.io/badge/version-2.0.0-blue.svg)
![ComfyUI](https://img.shields.io/badge/ComfyUI-Custom%20Nodes-green.svg)
![License](https://img.shields.io/badge/license-MIT-purple.svg)
![Python](https://img.shields.io/badge/Python-3.10%2B-yellow.svg)

**Colección de nodos profesionales para ComfyUI**

Desarrollado por [Prompt Models Studio](https://www.skool.com/prompt-models-studio) 🇲🇽

[Instalación](#-instalación) · [Nodos](#-nodos-incluidos) · [Google AI](#-comfyui_googleai-v21) · [Grok AI](#-comfyui_grokai) · [Utilidades](#-utilidades) · [Soporte](#-soporte)

</div>

---

## 🚀 Instalación

### Opción 1: Comfy Registry (Recomendado)
```bash
comfy node install promptmodels
```

### Opción 2: ComfyUI Manager
Busca `PROMPTMODELS` en ComfyUI Manager e instala.

### Opción 3: Manual
```bash
cd ComfyUI/custom_nodes
git clone https://github.com/cdanielp/COMFYUI_PROMPTMODELS.git
pip install -r COMFYUI_PROMPTMODELS/requirements.txt
```

Reinicia ComfyUI.

---

## 📦 Nodos Incluidos

| Carpeta | Categoría | Nodos | Descripción |
|---------|-----------|:-----:|-------------|
| `ComfyUI_GoogleAI` | 🤖 AI APIs | 14 | Suite completa Google AI (Gemini · Imagen 3 · Veo 3.1 · Lyria 3) |
| `ComfyUI_GrokAI` | 🤖 AI APIs | 7 | Suite xAI Grok (Texto · Visión · JSON · Imagen · Diagnóstico) |
| `GETSETNODE_PRO` | 🧠 Memoria | 5 | Sistema de caché Set/Get compatible con rgthree |
| `comfyui_selectores_pro` | 🎛️ Selectores | 4 | Selectores de imagen, prompt, latente y constructor de prompts |
| `DivisorDePrompts` | ✂️ Texto | 1 | Divide texto en hasta 10 prompts independientes |
| `get_last_frame` | 🎬 Video | 2 | Extrae frames específicos de secuencias |
| `text_prompt_blocker` | 🛡️ Seguridad | 1 | Filtro de palabras prohibidas en prompts |

---

## 🔑 API Keys Requeridas

| Suite | Proveedor | Obtener Key |
|-------|-----------|-------------|
| Google AI | Google | [aistudio.google.com/apikey](https://aistudio.google.com/apikey) |
| Grok AI | xAI | [console.x.ai](https://console.x.ai/) |

> Los nodos de Selectores Pro, Memoria, Video y Texto no requieren API keys.

---

## 🤖 ComfyUI_GoogleAI (V2.1)

> **Gemini 3.1 Pro** · **Imagen 3** · **Veo 3.1** · **Lyria 3**

Suite integral que conecta ComfyUI con Google AI mediante arquitectura 100% nativa REST (cero SDKs). API Key configurable globalmente desde los Settings de ComfyUI.

### 🆕 Novedades V2.1
- **Polling asíncrono de video** — ComfyUI no se congela durante los 5-10 min de generación
- **Dependencias headless** — `opencv-python-headless` para RunPod/Colab/servidores sin GUI
- **Sanitización de semillas** — Convierte seeds de 64 bits a 32 bits automáticamente (`safe_seed()`)
- **Error handling por tipo** — Imagen/video → imagen roja · Audio → silencio (evita Type Mismatch)
- **Nodo maestro multimodal** — `GoogleAI_TextNode` acepta hasta 5 imágenes, video, audio, YouTube y documentos
- **Menús desplegables en diagnóstico** — Sin escribir rutas manualmente

### 🔑 Configurar API Key

| Prioridad | Fuente | Cómo |
|:---------:|--------|------|
| 1️⃣ | Campo del nodo | Escribir directo en `api_key` |
| 2️⃣ | Settings UI | ⚙️ > **Google AI API Key (Gemini)** |
| 3️⃣ | Variable de entorno | `export GOOGLE_AI_API_KEY="tu-clave"` |

### 🔤 Texto Multimodal — Gemini 3.1 Pro

#### GoogleAI_TextNode ⭐ Nodo Maestro

| Input | Tipo | Req | Descripción |
|-------|------|:---:|-------------|
| `prompt` | STRING | ✅ | Prompt principal |
| `model` | COMBO | ✅ | gemini-3.1-pro-preview, 2.5-pro, flash, flash-lite |
| `thinking_budget` | COMBO | ✅ | Off / Low (1024 tokens) / High (8192 tokens) |
| `system_prompt` | STRING | ❌ | Instrucción de sistema |
| `image_1`..`image_5` | IMAGE | ❌ | Hasta 5 imágenes simultáneas |
| `video_frames` | IMAGE | ❌ | Frames desde VHS/Load Video (muestrea 8) |
| `video_path` | STRING | ❌ | Ruta local a .mp4/.webm |
| `audio` | AUDIO | ❌ | Audio para transcripción/análisis |
| `youtube_url` | STRING | ❌ | URL de YouTube |
| `max_tokens` | INT | ❌ | 64–65536 (default: 4096) |
| `temperature` | FLOAT | ❌ | 0.0–2.0 (default: 0.7) |
| `seed` | INT | ❌ | 64 bits UI → sanitizado a 32 bits |
| **Output** | `text` STRING | | |

#### GoogleAI_TextVisionNode *(retrocompatibilidad)*
> ⚠️ Migrar a `GoogleAI_TextNode` con `image_1`.

### 🎨 Imagen — Imagen 3

#### GoogleAI_ImageNode

| Input | Tipo | Req | Descripción |
|-------|------|:---:|-------------|
| `prompt` | STRING | ✅ | Descripción de la imagen |
| `model` | COMBO | ✅ | imagen-3.0-generate-002, 001, fast-001 |
| `aspect_ratio` | COMBO | ✅ | 1:1, 16:9, 9:16, 4:3, 3:4 |
| `seed` | INT | ✅ | Sanitizado automáticamente a 32 bits |
| `batch_size` | INT | ✅ | 1–4 imágenes |
| `negative_prompt` | STRING | ❌ | Elementos a evitar |
| `image_1`..`image_5` | IMAGE | ❌ | Referencias para style transfer / edición |
| **Output** | `image` IMAGE (batch) | | |

> **Anti-crash:** errores HTTP 400 retornan imagen roja 512×512 en lugar de detener el workflow.

#### GoogleAI_ImageBatchNode *(retrocompatibilidad)*
> ⚠️ Usar `GoogleAI_ImageNode` con `batch_size` directamente.

### 🎬 Video — Veo 3.1

> ⚡ Salida a **24 FPS** — Configurar VHS Video Combine a 24 FPS.  
> 🔄 **Polling asíncrono** — El workflow sigue ejecutándose durante la generación (5-10 min).  
> ⚠️ **Sin seed manual** — La API de Veo 3.1 no acepta seed (HTTP 400 si se envía).

**Resoluciones:** 1920×1080, 1080×1920, 1080×1080, 3840×2160, 2160×3840  
**Duraciones:** 4, 6, 8 segundos · **Costo:** $0.05 USD/seg

#### GoogleAI_VideoGenerator

| Input | Tipo | Req | Descripción |
|-------|------|:---:|-------------|
| `prompt` | STRING | ✅ | Descripción del video |
| `model` | COMBO | ✅ | veo-3.1, veo-3.0, veo-2.0 |
| `video_preset` | COMBO | ✅ | Resolución (16:9, 9:16, 1:1, 4K) |
| `duration_seconds` | COMBO | ✅ | 4, 6 u 8 segundos |
| `init_image_or_video` | IMAGE | ❌ | 1 frame = Img2Vid · >1 frame = Video Extension |
| `negative_prompt` | STRING | ❌ | Elementos a evitar |
| **Outputs** | `video_frames` IMAGE, `cost_estimate` STRING | | |

#### GoogleAI_VideoInterpolation
Genera video interpolando entre primer y último frame. `last_frame` se redimensiona automáticamente.

| Input | Tipo | Req |
|-------|------|:---:|
| `first_frame` | IMAGE | ✅ |
| `last_frame` | IMAGE | ✅ |
| `prompt` | STRING | ✅ |
| **Outputs** | `video_frames` IMAGE, `cost_estimate` STRING | |

#### GoogleAI_VideoStoryboard
Video estilizado con hasta 3 imágenes de referencia.
> ⚠️ Con imágenes de referencia, la duración se **fuerza a 8 segundos** automáticamente.

### 🎵 Audio — Lyria 3

> SynthID warnings se filtran automáticamente.  
> **Type Mismatch Fallback:** errores HTTP 400 devuelven audio silencioso en vez de crashear.

#### GoogleAI_MusicDirector

| Input | Tipo | Req | Descripción |
|-------|------|:---:|-------------|
| `prompt` | STRING | ✅ | Descripción de la música |
| `vocals` | BOOL | ✅ | True = con voces · False = instrumental |
| `init_image` | IMAGE | ❌ | Referencia contextual (ej: portada de álbum) |
| `video_frames` | IMAGE | ❌ | Para Video-to-Music 🆕 |
| **Output** | `audio` AUDIO (30s) | | |

#### GoogleAI_FoleyGenerator

| Input | Tipo | Req | Descripción |
|-------|------|:---:|-------------|
| `video_frames` | IMAGE | ✅ | Frames del video |
| `prompt` | STRING | ✅ | Guía para los efectos de sonido |
| `max_frames_to_send` | INT | ❌ | 2-16 frames (default: 8) |
| **Output** | `foley_audio` AUDIO | | |

### 🔍 Diagnóstico — Gemini 3.1 Pro

**Subgrupo A — Menús desplegables nativos** (sin escribir rutas):

| Nodo | Entrada | Salida |
|------|---------|--------|
| ArchitectureDetector | `checkpoint` (desplegable) | `architecture_report` STRING |
| TriggerWordExtractor | `lora` (desplegable) | `trigger_words` STRING |
| CompatibilityChecker | `checkpoint` + `lora` (desplegables) | `is_compatible` BOOL + `report` STRING |

**Subgrupo B — Diagnóstico con puerto físico** (`text_or_file_path` con `forceInput: True`):

| Nodo | Entrada Principal | Puerto Físico | Salida |
|------|------------------|---------------|--------|
| WorkflowAnalyzer | `workflow_json` multiline | `text_or_file_path` | `analysis_report` STRING |
| LoRATrainingAnalyzer | `training_logs` multiline | `text_or_file_path` | `diagnosis_report` STRING |

### 📝 Notas Técnicas

| Tipo de Nodo | Error HTTP 400 / Safety | Resultado |
|:------------:|:-----------------------:|:---------:|
| Imagen | `create_error_image()` | Imagen roja 512×512 |
| Video | `create_error_image()` | Imagen roja 512×512 |
| Audio | Audio silencioso | `torch.zeros(1, 1, 48000)` @ 48kHz |
| Texto | String de error | `"❌ Error: ..."` |

**Dependencias:**

| Paquete | Versión | Propósito |
|---------|---------|-----------|
| `requests` | ≥2.28 | HTTP síncrono |
| `aiohttp` | ≥3.8 | HTTP asíncrono (video polling) |
| `opencv-python-headless` | ≥4.8 | Decodificación MP4 → frames |
| `torchaudio` | ≥2.0 | Conversión audio WAV ↔ tensor |
| `safetensors` | ≥0.4 | Lectura de checkpoints/LoRAs |

> 💡 El explicador de errores fue separado al plugin universal [ComfyUI_UniversalErrorExplainer](https://github.com/cdanielp/ComfyUI_UniversalErrorExplainer).

---

## 🤖 ComfyUI_GrokAI

> **Grok 4.1** (Texto · Razonamiento · Visión) · **Grok 2 Image** (Generación · Edición) · **Diagnóstico**

Suite de 7 nodos que conecta ComfyUI con la API de xAI. Cero SDKs — todo via `requests` HTTP puras contra `api.x.ai/v1`.

### 🔑 Configurar API Key

| Prioridad | Fuente | Cómo |
|:---------:|--------|------|
| 1️⃣ | Campo del nodo | Escribir directo en `api_key` |
| 2️⃣ | Variable de entorno | `export XAI_API_KEY="xai-..."` |

### 🧠 Texto, Visión y JSON

#### Grok_Text_Advanced

| Input | Tipo | Req | Descripción |
|-------|------|:---:|-------------|
| `prompt` | STRING | ✅ | Prompt de texto |
| `model` | COMBO | ✅ | grok-4.1-fast-reasoning, etc. |
| `reasoning_effort` | COMBO | ✅ | Off / Low / High |
| `system_prompt` | STRING | ❌ | Instrucción de sistema |
| `temperature` | FLOAT | ❌ | 0.0–2.0 |
| `max_tokens` | INT | ❌ | 64–131072 |
| **Output** | `text` STRING | | |

> `Off` no envía el parámetro reasoning al JSON. `Low`/`High` activan razonamiento extendido de Grok.

#### Grok_Vision_Analyzer
Analiza imágenes. Envía el tensor como base64 automáticamente.

| Input | Tipo | Req | Descripción |
|-------|------|:---:|-------------|
| `image` | IMAGE | ✅ | Imagen a analizar |
| `prompt` | STRING | ✅ | Pregunta sobre la imagen |
| `model` | COMBO | ✅ | Modelo con capacidad visual |
| `detail` | COMBO | ✅ | `low` o `high` |
| **Output** | `analysis` STRING | | |

#### Grok_JSON_Formatter
Fuerza respuesta en JSON estricto via Structured Outputs.

| Input | Tipo | Req | Descripción |
|-------|------|:---:|-------------|
| `prompt` | STRING | ✅ | Lo que quieres generar |
| `json_schema` | STRING | ✅ | Esquema JSON deseado |
| **Output** | `json_string` STRING | | JSON limpio y parseado |

Ejemplo de schema: `{"subject": "string", "style": "string", "mood": "string"}`

### 🎨 Imagen

#### Grok_Image_Generator
Text-to-Image. Anti-crash: errores HTTP retornan imagen roja 512×512.

| Input | Tipo | Req | Descripción |
|-------|------|:---:|-------------|
| `prompt` | STRING | ✅ | Descripción de la imagen |
| `model` | COMBO | ✅ | grok-2-image-1212, grok-2-image |
| `aspect_ratio` | COMBO | ✅ | 1:1, 16:9, 9:16, 4:3, 3:4 |
| `batch_size` | INT | ✅ | 1–4 imágenes |
| **Output** | `images` IMAGE (batch) | | |

#### Grok_Image_Editor
Edición de imágenes con lenguaje natural.

| Input | Tipo | Req | Descripción |
|-------|------|:---:|-------------|
| `image` | IMAGE | ✅ | Imagen base |
| `prompt` | STRING | ✅ | Instrucción de edición |
| **Output** | `edited_image` IMAGE | | |

### 🔧 Diagnóstico

#### Grok_Workflow_Debugger
Analiza un workflow JSON completo. `fun_mode` = responde con sarcasmo pero da la solución real.

| Input | Tipo | Req | Descripción |
|-------|------|:---:|-------------|
| `workflow_json` | STRING | ✅ | JSON del workflow o ruta al archivo |
| `fun_mode` | BOOLEAN | ✅ | True = sarcasmo + solución |
| **Output** | `analysis_report` STRING | | |

#### Grok_Metadata_Reader
Lee un `.safetensors` y Grok identifica arquitectura + trigger words.

| Input | Tipo | Req | Descripción |
|-------|------|:---:|-------------|
| `safetensors_path` | STRING | ✅ | Ruta al archivo |
| **Output** | `metadata_summary` STRING | | |

---

## 🛠️ Utilidades

### 🧠 GETSETNODE_PRO — Sistema de Memoria

Sistema de caché de contexto **100% compatible** con workflows que usan SetNode/GetNode de rgthree-comfy.

**Nodos incluidos:** `SetNode`, `GetNode`, `UnetLoaderGGUF`, `ListCacheNode`, `ClearCacheNode`

---

### 🎛️ comfyui_selectores_pro — Selectores Pro

Suite de 4 nodos para selección múltiple, construcción de prompts y generación de latents.

#### Selector de Imágenes
Selecciona y combina hasta 12 slots de imagen + máscara en batch.

| Input | Descripción |
|-------|-------------|
| `img1`..`img12` | Slots de imagen |
| `mask1`..`mask12` | Máscaras opcionales |
| `on1`..`on12` | Activar/desactivar cada slot |
| `mode` | `auto` |
| `fallback` | `error` |
| **Outputs** | `image` IMAGE, `mask` MASK |

- 1 slot activo → salida single
- 2+ slots → batch concatenado (valida mismo tamaño)

#### Selector de Prompts
Selecciona y combina hasta 12 prompts de texto.

| Input | Descripción |
|-------|-------------|
| `p1`..`p12` | Slots de texto multiline |
| `on1`..`on12` | Activar/desactivar cada slot |
| `join_with` | Separador entre prompts (`\n\n` default) |
| **Output** | `text` STRING |

#### Imagen Latente Pro
Genera un latent vacío con 29 presets predefinidos. **Un solo dropdown, sin cálculos manuales.**

| Categoría | Ratios disponibles |
|-----------|--------------------|
| **Test** (256 base) | 1:1, 4:5, 3:4, 2:3, 9:16, 16:9, 3:2, 2:1, 21:9 |
| **Medio** (512 base) | 1:1, 4:5, 3:4, 2:3, 9:16, 16:9, 3:2, 2:1, 21:9 |
| **Grande** (1024 base) | 1:1, 4:5, 3:4, 2:3, 9:16, 16:9, 3:2, 2:1, 21:9 |
| **Social** | 720×1280 (9:16), 1280×720 (16:9) |

**Output:** `latent` LATENT

#### Prompt Pro
Constructor de prompts por campos con 10 diseños predefinidos. Solo requiere **👤 Sujeto**.

**Diseños:** Retrato Pro · Cinemático · Producto E-commerce · Anime Clean · Concept Art · Arquitectura · Moda Editorial · Interior Design · Vertical Reels (9:16) · Thumbnail YouTube (16:9)

**Campos disponibles:** Sujeto 👤 · Acción 🧍 · Emoción 🎭 · Vestuario 👗 · Fondo 🏞️ · Estilo 🎨 · Paleta 🎨 · Iluminación 💡 · Cámara 📷 · Materiales 🧪 · Composición 🧷 · Detalle 🔎 · Atmósfera 🌫️ · Calidad ✨ · Restricciones 🧯 · Extra ➕

**Opciones globales:** Separador (`, ` `\n` `|`) · Prefijo/Sufijo · Normalizar espacios · Evitar duplicados

---

### ✂️ DivisorDePrompts

Divide texto multilínea en hasta 10 prompts independientes usando párrafos como separador.

**Outputs:** `prompt_01` a `prompt_10` + `count`

---

### 🎬 get_last_frame

Extrae frames específicos de secuencias de video o batches de imágenes.

**Nodos:** `GetLastFrame`, `GetFrameByIndex`

---

### 🛡️ text_prompt_blocker

Nodo de seguridad que analiza y filtra prompts con palabras prohibidas antes de enviarlos a cualquier modelo.

**Modos:** `Hard block` (detiene el workflow) · `Soft block` (devuelve string vacío)

---

## 📋 Requisitos del Sistema

| Componente | Versión mínima |
|------------|---------------|
| ComfyUI | ≥ 0.3.76 |
| Python | ≥ 3.10 |
| PyTorch | ≥ 2.0 |

---

## 📜 Licencia

MIT License — Libre para uso personal y comercial.

---

## 💬 Soporte

- **GitHub Issues:** [Reportar problema](https://github.com/cdanielp/COMFYUI_PROMPTMODELS/issues)
- **Comunidad Skool:** [Prompt Models Studio](https://www.skool.com/prompt-models-studio)

---

<div align="center">

**Hecho con ❤️ en México por [Prompt Models Studio](https://www.skool.com/prompt-models-studio)**

⭐ Si te fue útil, regálanos una estrella en GitHub

</div>
