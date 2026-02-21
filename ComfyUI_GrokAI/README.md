# 🧠 ComfyUI_GrokAI — Suite de xAI (Grok) para ComfyUI

> **Grok 4.1** (Texto/Razonamiento/Visión) · **Grok 2 Image** (Generación/Edición) · **Diagnóstico** (Workflows + Modelos)

![Version](https://img.shields.io/badge/Version-1.0.0-blue)
![License](https://img.shields.io/badge/License-MIT-yellow)
![Nodes](https://img.shields.io/badge/Nodos-7-green)

---

## 📑 Tabla de Contenidos

1. [Instalación](#-instalación)
2. [Configurar API Key](#-configurar-api-key)
3. [Nodos: Texto y Visión](#-texto-visión-y-json)
4. [Nodos: Imagen](#-imagen)
5. [Nodos: Diagnóstico](#-diagnóstico)
6. [Notas Técnicas](#-notas-técnicas)

---

## 📦 Instalación

```bash
cd ComfyUI/custom_nodes/
git clone https://github.com/cdanielp/ComfyUI_GrokAI.git
cd ComfyUI_GrokAI
pip install -r requirements.txt
```

Reinicia ComfyUI y los 7 nodos aparecerán en la categoría **Grok AI**.

---

## 🔑 Configurar API Key

Obtén tu API Key en [console.x.ai](https://console.x.ai).

| Prioridad | Fuente | Cómo |
|:---------:|--------|------|
| 1️⃣ | Campo del nodo | Escribir directo en `api_key` |
| 2️⃣ | Variable de entorno | `export XAI_API_KEY="xai-..."` |

Si no hay clave en ninguna fuente, el nodo lanza un error limpio sin crashear.

---

## 🧠 Texto, Visión y JSON

### 🧠 Grok_Text_Advanced

Generación de texto con control de razonamiento.

| Input | Tipo | Req | Descripción |
|-------|------|:---:|-------------|
| `prompt` | STRING | ✅ | Prompt de texto |
| `model` | COMBO | ✅ | grok-4.1-fast-reasoning, etc. |
| `reasoning_effort` | COMBO | ✅ | **Off** = no envía el parámetro. Low/High activan razonamiento |
| `api_key` | STRING | ❌ | Opcional si usas variable de entorno |
| `system_prompt` | STRING | ❌ | Instrucción de sistema |
| `temperature` | FLOAT | ❌ | 0.0-2.0 |
| `max_tokens` | INT | ❌ | 64-131072 |
| **Output** | `text` STRING | | |

### 👁️ Grok_Vision_Analyzer

Analiza imágenes con Grok Vision. Envía tensor como base64 automáticamente.

| Input | Tipo | Req | Descripción |
|-------|------|:---:|-------------|
| `image` | IMAGE | ✅ | Imagen a analizar |
| `prompt` | STRING | ✅ | Pregunta sobre la imagen |
| `model` | COMBO | ✅ | Modelo con capacidad visual |
| `detail` | COMBO | ✅ | `low` o `high` |
| **Output** | `analysis` STRING | | |

### 📋 Grok_JSON_Formatter

Fuerza respuesta en JSON estricto (Structured Outputs). Ideal para parsear prompts.

| Input | Tipo | Req | Descripción |
|-------|------|:---:|-------------|
| `prompt` | STRING | ✅ | Lo que quieres generar |
| `json_schema` | STRING | ✅ | Esquema JSON de la estructura deseada |
| **Output** | `json_string` STRING | | JSON limpio y parseado |

**Ejemplo de json_schema:**
```json
{"subject": "string", "style": "string", "mood": "string"}
```

---

## 🎨 Imagen

### 🎨 Grok_Image_Generator

Generación Text-to-Image. **Anti-crash:** errores HTTP retornan imagen roja 512×512.

| Input | Tipo | Req | Descripción |
|-------|------|:---:|-------------|
| `prompt` | STRING | ✅ | Descripción de la imagen |
| `model` | COMBO | ✅ | grok-2-image-1212, grok-2-image |
| `aspect_ratio` | COMBO | ✅ | 1:1, 16:9, 9:16, 4:3, 3:4 |
| `batch_size` | INT | ✅ | 1-4 imágenes |
| **Output** | `images` IMAGE (batch) | | |

### ✏️ Grok_Image_Editor

Edición de imágenes con lenguaje natural.

| Input | Tipo | Req | Descripción |
|-------|------|:---:|-------------|
| `image` | IMAGE | ✅ | Imagen base a editar |
| `prompt` | STRING | ✅ | Instrucción de edición |
| **Output** | `edited_image` IMAGE | | |

---

## 🔧 Diagnóstico

### 🔧 Grok_Workflow_Debugger

Analiza un workflow JSON. `fun_mode` = Grok responde con sarcasmo pero da la solución.

| Input | Tipo | Req | Descripción |
|-------|------|:---:|-------------|
| `workflow_json` | STRING | ✅ | JSON del workflow o ruta al archivo |
| `fun_mode` | BOOLEAN | ✅ | True = sarcasmo + solución real |
| **Output** | `analysis_report` STRING | | |

### 🔍 Grok_Metadata_Reader

Lee un .safetensors y Grok identifica arquitectura + trigger words.

| Input | Tipo | Req | Descripción |
|-------|------|:---:|-------------|
| `safetensors_path` | STRING | ✅ | Ruta al archivo .safetensors |
| **Output** | `metadata_summary` STRING | | |

---

## 📝 Notas Técnicas

- **Cero SDKs** — Toda la comunicación usa `requests` HTTP puras contra `api.x.ai/v1`
- **Anti-Crash** — Errores HTTP 400 (safety/NSFW) y 429 (rate limit) retornan una **imagen roja de 512×512** con el error impreso, en vez de crashear el workflow
- **Tensores estándar** — `[B, H, W, C]` float `0.0-1.0` (formato PyTorch de ComfyUI)
- **Reasoning effort** — `Off` no envía el parámetro al JSON; `Low`/`High` activan razonamiento de Grok
- **JSON Formatter** — Usa `response_format: json_object` + validación post-respuesta

---

## 📄 Licencia

MIT

---

Desarrollado por **[Prompt Models Studio](https://github.com/cdanielp)** 🇲🇽
