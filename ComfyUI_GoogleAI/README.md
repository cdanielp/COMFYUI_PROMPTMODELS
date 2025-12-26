# ComfyUI-GoogleAI

Custom nodes for ComfyUI that connect to Google AI (Gemini API) for text and image generation.

**Actualizado: Diciembre 2025** - Incluye Gemini 3 y Nano Banana Pro

## 🚀 Installation

1. Navigate to your ComfyUI custom nodes folder:
```bash
cd ComfyUI/custom_nodes/
```

2. Clone or copy this folder:
```bash
git clone https://github.com/YOUR_USERNAME/ComfyUI-GoogleAI.git
# OR just copy the ComfyUI-GoogleAI folder here
```

3. Install dependencies:
```bash
cd ComfyUI-GoogleAI
pip install -r requirements.txt
```

4. Restart ComfyUI

## 🔑 API Key

Get your API key from [Google AI Studio](https://aistudio.google.com/apikey)

## 📦 Available Nodes

### 🧠 Google AI Text Generator
Full-featured text generation with system prompt support.

| Input | Type | Description |
|-------|------|-------------|
| api_key | STRING | Your Google AI API key |
| model | DROPDOWN | Select from available text models |
| prompt | STRING | Main prompt text |
| system_prompt | STRING (optional) | System instructions for behavior/style |
| custom_model | STRING (optional) | Override model selection with custom model ID |

**Output:** `STRING` (generated text)

### 🎨 Google AI Image Generator (Nano Banana)
Full-featured image generation with reference images support.

| Input | Type | Description |
|-------|------|-------------|
| api_key | STRING | Your Google AI API key |
| model | DROPDOWN | Select from available image models |
| prompt | STRING | Image description prompt |
| system_prompt | STRING | Style/behavior instructions (editable inside node) |
| resolution | DROPDOWN | 1K, 2K, or 4K (4K only Nano Banana Pro) |
| aspect_ratio | DROPDOWN | 1:1, 3:4, 4:3, 9:16, 16:9, 3:2, 2:3, 21:9 |
| custom_model | STRING (optional) | Override model selection |
| image_1-5 | IMAGE (optional) | Reference images for context |

**Outputs:** 
- `IMAGE` (generated image tensor)
- `STRING` (status message)

## 🎯 Available Models (Diciembre 2025)

### Text Models
| Model | Description |
|-------|-------------|
| `gemini-3-pro-preview` | Más avanzado, razonamiento complejo |
| `gemini-3-flash-preview` | Pro-level a velocidad Flash |
| `gemini-2.5-pro` | Razonamiento y código |
| `gemini-2.5-flash` | Balance velocidad/calidad |
| `gemini-2.5-flash-lite` | Ultra rápido y económico |
| `gemini-2.0-flash` | General purpose |

### Image Models (Nano Banana)
| Model | Alias | Max Resolution | Description |
|-------|-------|----------------|-------------|
| `gemini-3-pro-image-preview` | Nano Banana Pro | 4K | El más potente, 14 imgs referencia |
| `gemini-2.5-flash-image` | Nano Banana | 1K | Rápido y eficiente |
| `imagen-3.0-generate-002` | Imagen 3 | 1K | Fotorrealista |
| `imagen-3.0-generate-001` | Imagen 3 | 1K | Fotorrealista |

## 💡 Usage Examples

### Text Generation
```
Model: gemini-3-flash-preview
Prompt: "Explain quantum computing in simple terms"
System Prompt: "You are a patient teacher explaining complex topics to beginners"
```

### Image Generation (Nano Banana Pro)
```
Model: gemini-3-pro-image-preview
Prompt: "A futuristic cyberpunk samurai standing in Tokyo at night, neon lights, rain"
Resolution: 4K
Aspect Ratio: 16:9
```

## ⚠️ Notes

- **4K resolution** only available with `gemini-3-pro-image-preview` (Nano Banana Pro)
- **Nano Banana Pro** supports up to 14 reference images and character consistency
- All generated images include SynthID watermark
- Image tensors are in ComfyUI format: `[B, H, W, C]` with values 0-1

## 🔗 Resources

- [Google AI Studio](https://aistudio.google.com/)
- [Gemini API Documentation](https://ai.google.dev/gemini-api/docs)
- [Nano Banana Documentation](https://ai.google.dev/gemini-api/docs/nanobanana)
- [Image Generation Guide](https://ai.google.dev/gemini-api/docs/image-generation)
