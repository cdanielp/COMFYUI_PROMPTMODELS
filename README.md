# ComfyUI-GoogleAI

Custom nodes for ComfyUI that connect to Google AI (Gemini API) for text and image generation.

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

### 🧠 Google AI Text (Simple)
Simplified text generation without system prompt.

### 🎨 Google AI Image Generator
Full-featured image generation with reference images support.

| Input | Type | Description |
|-------|------|-------------|
| api_key | STRING | Your Google AI API key |
| model | DROPDOWN | Select from available image models |
| prompt | STRING | Image description prompt |
| system_prompt | STRING (optional) | Style/behavior instructions |
| resolution | DROPDOWN | 1K or 2K |
| aspect_ratio | DROPDOWN | 1:1, 3:4, 4:3, 9:16, 16:9 |
| custom_model | STRING (optional) | Override model selection |
| image_1-5 | IMAGE (optional) | Reference images for context |

**Outputs:** 
- `IMAGE` (generated image tensor)
- `STRING` (status message)

### 🎨 Google AI Image (Simple)
Simplified image generation with just prompt and aspect ratio.

## 🎯 Available Models

### Text Models
- `gemini-2.5-pro-preview-06-05`
- `gemini-2.5-flash-preview-05-20`
- `gemini-2.0-flash`
- `gemini-2.0-flash-lite`
- `gemini-1.5-pro`
- `gemini-1.5-flash`
- `gemini-1.5-flash-8b`

### Image Models
- `gemini-2.0-flash-preview-image-generation`
- `imagen-3.0-generate-002`
- `imagen-3.0-generate-001`

Use the `custom_model` input to use models not in the dropdown.

## 💡 Usage Examples

### Text Generation
```
Model: gemini-2.5-flash-preview-05-20
Prompt: "Explain quantum computing in simple terms"
System Prompt: "You are a patient teacher explaining complex topics to beginners"
```

### Image Generation
```
Model: gemini-2.0-flash-preview-image-generation
Prompt: "A futuristic cyberpunk samurai standing in Tokyo at night, neon lights, rain"
Resolution: 2K
Aspect Ratio: 16:9
```

## ⚠️ Error Handling

- Red image output = generation failed (check status output for details)
- Common errors:
  - Invalid API key
  - Model not available for your account
  - Rate limiting
  - Content policy violations

## 🔧 Troubleshooting

1. **"No candidates returned"**: The model couldn't generate content. Try a different prompt.
2. **"Model returned text only"**: Image model returned text instead of image. Try gemini-2.0-flash-preview-image-generation.
3. **Rate limits**: Wait a few seconds between requests or upgrade your API tier.

## 📝 Notes

- Image tensors are in ComfyUI format: `[B, H, W, C]` with values 0-1
- Reference images are sent as base64 PNG to the API
- System prompts use Gemini's `systemInstruction` field for proper handling

## 🔗 Resources

- [Google AI Studio](https://aistudio.google.com/)
- [Gemini API Documentation](https://ai.google.dev/gemini-api/docs)
- [Available Models](https://ai.google.dev/gemini-api/docs/models/gemini)
