# ComfyUI-GoogleAI

Custom nodes for ComfyUI that connect to Google AI (Gemini API) for text and image generation.

**Actualizado: Diciembre 2025** - Incluye Gemini 3, Nano Banana Pro, entradas multimodales

## 🚀 Installation

```bash
cd ComfyUI/custom_nodes/
unzip ComfyUI_GoogleAI.zip
pip install -r ComfyUI_GoogleAI/requirements.txt
```

Restart ComfyUI.

## 🔑 API Key

Get your API key from [Google AI Studio](https://aistudio.google.com/apikey)

## 📦 Available Nodes

### 🧠 Google AI Text Generator

Nodo multimodal de generación de texto con soporte para imágenes, audio, video y archivos.

| Input | Type | Description |
|-------|------|-------------|
| **images** | IMAGE (optional) | Imágenes para análisis |
| **audio** | AUDIO (optional) | Audio para transcripción/análisis |
| **video** | IMAGE (optional) | Frames de video |
| **files** | STRING (optional) | Base64 de PDFs u otros archivos |
| api_key | STRING | Your Google AI API key |
| prompt | STRING | Main prompt text |
| model | DROPDOWN | Select from available text models |
| seed | INT | Seed for reproducibility |
| randomize_seed | BOOLEAN | Generate random seed each run |
| system_prompt | STRING | System instructions |
| temperature | FLOAT | Creativity (0.0-2.0) |

**Output:** `text` (STRING)

### 🎨 Google AI Image Generator

Nodo de generación de imagen con presets de tamaño estilo Seedream.

| Input | Type | Description |
|-------|------|-------------|
| **image_1-5** | IMAGE (optional) | Reference images |
| api_key | STRING | Your Google AI API key |
| model | DROPDOWN | Select from available image models |
| prompt | STRING | Image description prompt |
| system_prompt | STRING | Style instructions |
| size_preset | DROPDOWN | Predefined sizes "2048×2048 (1:1) - 2K" |
| seed | INT | Seed for reproducibility |
| randomize_seed | BOOLEAN | Generate random seed |
| response_mode | DROPDOWN | IMAGE+TEXT or IMAGE |

**Output:** `image` (IMAGE)

## 📐 Size Presets

### 1K (~1024px)
- 1024×1024 (1:1)
- 1152×896 (4:3)
- 896×1152 (3:4)
- 1280×720 (16:9)
- 720×1280 (9:16)

### 2K (~2048px)
- 2048×2048 (1:1)
- 2304×1728 (4:3)
- 2560×1440 (16:9)
- 1440×2560 (9:16)

### 4K (~4096px) - Solo Nano Banana Pro
- 4096×4096 (1:1)
- 4608×3456 (4:3)
- 5120×2880 (16:9)

## 🎯 Models

### Text Models
| Model | Description |
|-------|-------------|
| `gemini-3-pro-preview` | Más avanzado |
| `gemini-3-flash-preview` | Pro-level rápido |
| `gemini-2.5-pro` | Razonamiento |
| `gemini-2.5-flash` | Balance |

### Image Models
| Model | Max Res | Description |
|-------|---------|-------------|
| `gemini-3-pro-image-preview` | 4K | Nano Banana Pro |
| `gemini-2.5-flash-image` | 2K | Nano Banana |
| `imagen-3.0-generate-002` | 1K | Imagen 3 |

## 🔗 Resources

- [Google AI Studio](https://aistudio.google.com/)
- [Gemini API Docs](https://ai.google.dev/gemini-api/docs)
- [Image Generation](https://ai.google.dev/gemini-api/docs/image-generation)
