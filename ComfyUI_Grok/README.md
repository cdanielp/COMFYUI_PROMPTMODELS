# ComfyUI-Grok

Custom nodes for ComfyUI that connect to xAI API (Grok) for text and image generation.

**Actualizado: Diciembre 2025**

## 🚀 Installation

1. Navigate to your ComfyUI custom nodes folder:
```bash
cd ComfyUI/custom_nodes/
```

2. Copy this folder:
```bash
# As standalone
git clone https://github.com/YOUR_USERNAME/ComfyUI-Grok.git

# Or as part of COMFYUI_PROMPTMODELS
# Copy to COMFYUI_PROMPTMODELS/ComfyUI_Grok/
```

3. Install dependencies:
```bash
cd ComfyUI-Grok
pip install -r requirements.txt
```

4. Restart ComfyUI

## 🔑 API Key

Get your API key from [xAI Console](https://console.x.ai/)

You can set it via:
- **Node field**: Enter directly in the `api_key` field
- **Environment variable**: `export XAI_API_KEY="your_key"`

## 📦 Available Nodes

### 🧠 Grok Text Generator
Full-featured text generation with system prompt and parameters.

| Input | Type | Description |
|-------|------|-------------|
| api_key | STRING | Your xAI API key |
| model | DROPDOWN | Select from available text models |
| prompt | STRING | Main prompt text |
| system_prompt | STRING | System instructions (editable inside node) |
| temperature | FLOAT | Creativity (0.0 - 2.0) |
| max_tokens | INT | Max output length (32 - 8192) |
| custom_model | STRING | Override model selection |

**Outputs:** 
- `text` (STRING) - Generated text
- `status` (STRING) - Status message

### 🎨 Grok Image Generator
Full-featured image generation with style and resolution options.

| Input | Type | Description |
|-------|------|-------------|
| api_key | STRING | Your xAI API key |
| model | DROPDOWN | Select from available image models |
| prompt | STRING | Image description |
| system_prompt | STRING | Style instructions (editable inside node) |
| resolution | DROPDOWN | 512x512 to 2048x2048 |
| aspect_ratio | DROPDOWN | 1:1, 3:4, 4:3, 9:16, 16:9, etc. |
| style | DROPDOWN | Realistic, Cinematic, Anime, etc. |
| n_images | INT | Number of images (1-4) |
| custom_model | STRING | Override model selection |

**Outputs:** 
- `image` (IMAGE) - Generated image tensor
- `status` (STRING) - Status message

## 🎯 Available Models (Diciembre 2025)

### Text Models
| Model | Description |
|-------|-------------|
| `grok-4` | Most advanced |
| `grok-4.1-fast` | Fast inference |
| `grok-3-mini` | Lightweight |
| `grok-2` | Stable |
| `grok-2-mini` | Cost-effective |

### Image Models
| Model | Description |
|-------|-------------|
| `grok-2-image` | Full quality |
| `grok-2-image-lite` | Fast/economical |

## 💡 Usage Examples

### Text Generation
```
Model: grok-4
Prompt: "Explain quantum computing in simple terms"
System Prompt: "You are a patient teacher"
Temperature: 0.7
Max Tokens: 2048
```

### Image Generation
```
Model: grok-2-image
Prompt: "A space cat in an astronaut suit floating over Saturn"
Style: Cinematic
Resolution: 1024x1024
Aspect Ratio: 16:9
```

## 🎨 Available Styles

- None (no style modifier)
- Realistic
- Artistic
- Cinematic
- Cartoon
- Concept Art
- Anime
- Oil Painting
- Watercolor
- Digital Art
- Photography
- 3D Render

## ⚠️ Error Handling

- Red image output = generation failed (check status output)
- Common errors:
  - Invalid API key
  - Rate limiting
  - Content policy violations
  - Model not available

## 🔗 Resources

- [xAI API Documentation](https://docs.x.ai/)
- [xAI Console](https://console.x.ai/)
- [Grok Models](https://x.ai/grok)

## 📝 Notes

- Image tensors are in ComfyUI format: `[B, H, W, C]` with values 0-1
- Temperature affects creativity (higher = more creative)
- System prompt guides the model's behavior and output style
