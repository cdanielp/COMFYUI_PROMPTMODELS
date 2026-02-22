<div align="center">

<img src="prompts models logo.png" alt="Prompt Models Studio" width="200"/>

# 🎨 COMFYUI_PROMPTMODELS

![Version](https://img.shields.io/badge/version-1.3.1-blue.svg)
![ComfyUI](https://img.shields.io/badge/ComfyUI-Custom%20Nodes-green.svg)
![License](https://img.shields.io/badge/license-MIT-purple.svg)
![Python](https://img.shields.io/badge/Python-3.10%2B-yellow.svg)

**Colección de nodos profesionales para ComfyUI**

Desarrollado por [Prompt Models Studio](https://www.skool.com/prompt-models-studio) 🇲🇽

[Instalación](#-instalación) · [Nodos](#-nodos-incluidos) · [Google AI](#-comfyui_googleai-v243) · [Grok AI](#-comfyui_grokai) · [Utilidades](#-utilidades) · [Soporte](#-soporte)

</div>

---

> ### ⚠️ AVISO — NODOS EN PRUEBAS
> **ComfyUI_GoogleAI V2.4.3** está en fase de pruebas activa. Es posible que encuentres nodos rojos, desconexiones o comportamientos inesperados al actualizar desde versiones anteriores.
>
> **Si algo falla:**
> 1. No te espantes — es normal durante esta fase
> 2. Elimina el nodo rojo y vuelve a agregarlo desde el menú
> 3. Consulta el README detallado dentro de `ComfyUI_GoogleAI/README.md` para instrucciones de cada nodo
> 4. Reporta el problema en [GitHub Issues](https://github.com/cdanielp/COMFYUI_PROMPTMODELS/issues)
>
> **Cambios que pueden causar nodos rojos:**
> - Los nodos de audio Lyria 3 (`MusicDirector`, `FoleyGenerator`) fueron **eliminados** — Google no tiene API pública
> - Los nodos de video ahora tienen una salida `AUDIO` adicional — reconecta los nodos downstream
> - Los nodos de imagen cambiaron de Imagen 3 a Nano Banana + Imagen 4 — revisa los modelos disponibles

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
cd COMFYUI_PROMPTMODELS
pip install -r requirements.txt
```

> 💡 **Docker/ComfyDeploy:** El archivo `install.py` dentro de `ComfyUI_GoogleAI/` instala ffmpeg automáticamente. Si usas un Dockerfile personalizado, agrega: `RUN apt-get update && apt-get install -y ffmpeg`

Reinicia ComfyUI.

---

## 📦 Nodos Incluidos

| Carpeta | Categoría | Nodos | Descripción |
|---------|-----------|:-----:|-------------|
| `ComfyUI_GoogleAI` | 🤖 AI APIs | 12 | Suite Google AI — Gemini 3.1 Pro · Nano Banana · Imagen 4 · Veo 3.1 + Audio |
| `ComfyUI_GrokAI` | 🤖 AI APIs | 7 | Suite xAI Grok — Texto · Visión · JSON · Imagen · Diagnóstico |
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

## 🤖 ComfyUI_GoogleAI (V2.4.3)

> **Gemini 3.1 Pro** · **Nano Banana Pro/Flash** · **Imagen 4** · **Veo 3.1 + Audio**

Suite integral que conecta ComfyUI con Google AI mediante arquitectura 100% nativa REST (cero SDKs). 12 nodos organizados en 4 suites: Texto, Imagen, Video y Diagnóstico.

> 📖 **Documentación completa de cada nodo:** [`ComfyUI_GoogleAI/README.md`](ComfyUI_GoogleAI/README.md)

### ❌ Removido en V2.4.3

| Qué | Por qué |
|-----|---------|
| `GoogleAI_MusicDirector` | `lyria-3` no tiene API pública (Feb 2026) |
| `GoogleAI_FoleyGenerator` | `lyria-3` no tiene API pública (Feb 2026) |
| Dependencia `torchaudio` | Reemplazado por extracción de audio via ffmpeg directo |

> Si tenías estos nodos conectados, aparecerán en rojo. Elimínalos del workflow.

### 🆕 Novedades V2.4.3

| Cambio | Detalle |
|--------|---------|
| 🔧 **Video negro resuelto** | Transcodificación automática HEVC/VP9 → H.264 via ffmpeg |
| 🔊 **Audio funcional** | Extracción via ffmpeg directo (sin torchaudio ni moviepy) |
| 📦 **install.py** | Instala ffmpeg + scipy automáticamente en Docker/ComfyDeploy |
| 🩺 **Diagnóstico automático** | Reporta `min/max/mean` del tensor de video en consola |
| 🎨 **Nano Banana Pro/Flash** | Nuevos modelos de imagen multimodal con hasta 14 referencias y 4K |
| 🖼️ **Imagen 4** | Soporte para Imagen 4 Standard, Ultra y Fast |
| 📐 **Size Presets** | Mapeo inteligente `size_preset → aspectRatio + resolution_hint` (1K/2K/4K) |
| 🔒 **Validación 4K** | Downgrade automático a 2K en modelos que no soportan 4K |
| 🔊 **Audio en todos los nodos de video** | Salida `AUDIO` nativa de Veo 3.1 en los 3 nodos de video |

### Resumen de Nodos (12)

| Suite | Nodo | Función |
|-------|------|---------|
| 🔤 Texto | `GoogleAI_TextNode` | Generación de texto con Gemini 3.1 Pro |
| 🔤 Texto | `GoogleAI_TextVisionNode` | Análisis de imágenes con Gemini Vision |
| 🎨 Imagen | `GoogleAI_ImageNode` | Nano Banana Pro/Flash + Imagen 4 (5 refs, 4K) |
| 🎨 Imagen | `GoogleAI_ImageBatchNode` | Batch de imágenes (Imagen 4) |
| 🎬 Video | `GoogleAI_VideoGenerator` | Text/Image to Video (Veo 3.1) + Audio |
| 🎬 Video | `GoogleAI_VideoInterpolation` | Interpolación entre 2 frames + Audio |
| 🎬 Video | `GoogleAI_VideoStoryboard` | Video con 3 refs de estilo + Audio |
| 🔍 Diag | `GoogleAI_ModelArchitectureDetector` | Identifica arquitectura de .safetensors |
| 🔍 Diag | `GoogleAI_TriggerWordExtractor` | Extrae trigger words de LoRA |
| 🔍 Diag | `GoogleAI_WorkflowAnalyzer` | Analiza workflow y lista repos necesarios |
| 🔍 Diag | `GoogleAI_CompatibilityChecker` | Verifica compatibilidad checkpoint + LoRA |
| 🔍 Diag | `GoogleAI_LoRATrainingAnalyzer` | Detecta overfitting en logs de entrenamiento |

### Dependencias

| Paquete | Propósito |
|---------|-----------|
| `requests` ≥2.28 | HTTP síncrono (texto, imagen) |
| `aiohttp` ≥3.8 | HTTP asíncrono (video polling) |
| `opencv-python` ≥4.8 | Decodificación de frames (fallback) |
| `safetensors` ≥0.4 | Lectura de checkpoints/LoRAs |
| `scipy` ≥1.10 | Lectura WAV optimizada (audio) |
| **ffmpeg** (sistema) | Transcodificación video + extracción audio |

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

#### Grok_Metadata_Reader
Lee un `.safetensors` y Grok identifica arquitectura + trigger words.

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

#### Selector de Prompts
Selecciona y combina hasta 12 prompts de texto.

#### Imagen Latente Pro
Genera un latent vacío con 29 presets predefinidos. Un solo dropdown, sin cálculos manuales.

| Categoría | Ratios disponibles |
|-----------|--------------------|
| **Test** (256 base) | 1:1, 4:5, 3:4, 2:3, 9:16, 16:9, 3:2, 2:1, 21:9 |
| **Medio** (512 base) | 1:1, 4:5, 3:4, 2:3, 9:16, 16:9, 3:2, 2:1, 21:9 |
| **Grande** (1024 base) | 1:1, 4:5, 3:4, 2:3, 9:16, 16:9, 3:2, 2:1, 21:9 |
| **Social** | 720×1280 (9:16), 1280×720 (16:9) |

#### Prompt Pro
Constructor de prompts por campos con 10 diseños predefinidos. Solo requiere **👤 Sujeto**.

**Diseños:** Retrato Pro · Cinemático · Producto E-commerce · Anime Clean · Concept Art · Arquitectura · Moda Editorial · Interior Design · Vertical Reels (9:16) · Thumbnail YouTube (16:9)

---

### ✂️ DivisorDePrompts

Divide texto multilínea en hasta 10 prompts independientes usando párrafos como separador.

---

### 🎬 get_last_frame

Extrae frames específicos de secuencias de video o batches de imágenes.

**Nodos:** `GetLastFrame`, `GetFrameByIndex`

---

### 🛡️ text_prompt_blocker

Nodo de seguridad que filtra prompts con palabras prohibidas.

**Modos:** `Hard block` (detiene el workflow) · `Soft block` (devuelve string vacío)

---

## 📋 Requisitos del Sistema

| Componente | Versión mínima |
|------------|---------------|
| ComfyUI | ≥ 0.3.76 |
| Python | ≥ 3.10 |
| PyTorch | ≥ 2.0 |
| ffmpeg | Requerido para video/audio Google AI |

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
