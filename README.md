<div align="center">

<img src="prompts models logo.png" alt="Prompt Models Studio" width="200"/>

# COMFYUI_PROMPTMODELS

![Version](https://img.shields.io/badge/version-2.0.0-purple) ![ComfyUI](https://img.shields.io/badge/ComfyUI-custom--nodes-blue) ![License](https://img.shields.io/badge/license-MIT-green)

Suite de nodos para ComfyUI con integracion REST nativa (sin SDKs) a Google AI y xAI (Grok).

</div>

---

## Nodos API activos (v2.0.0)

| Nodo | Categoria | Descripcion |
|---|---|---|
| **Gemini Chat (PMS)** | PromptModels/Google | Chat o vision con Gemini 3.x / 2.5. Imagen opcional. ThinkingConfig auto. |
| **Nano Banana - Imagen IA (PMS)** | PromptModels/Google | Genera imagenes con Gemini via generateContent. Hasta 3 referencias. |
| **Gemini Text to Speech (PMS)** | PromptModels/Google | Voz sintetica con gemini-3.1-flash-tts-preview. Salida tensor AUDIO. |
| **Grok Chat (PMS)** | PromptModels/Grok | Chat con grok-4.20 / 4.1 / 4.1-fast. Fix parsing de content lista. |
| **Grok Image Gen (PMS)** | PromptModels/Grok | Text-to-image y image-to-image con grok-imagine-image. Anti-crash. |
| **Grok Video Gen (PMS)** | PromptModels/Grok | Video async con grok-imagine-video. Output URL MP4. Polling 5s / timeout 300s. |
| **Grok Text to Speech (PMS)** | PromptModels/Grok | TTS con xAI. Voces: ara/eve/leo/rex/sal. Speech tags: [laugh] [sigh] [whisper]. |
| **Grok Speech to Text (PMS)** | PromptModels/Grok | Transcripcion de audio con xAI. Entrada tensor AUDIO de ComfyUI. |

---

## Breaking changes v2.0.0

Los siguientes nodos fueron **eliminados**. Los workflows que los contengan necesitan actualizacion.

| Nodo eliminado | Razon |
|---|---|
| `GoogleAI_VideoGenerator` / `VideoInterpolation` / `VideoStoryboard` | API Veo requiere Vertex AI, no AI Studio |
| `GoogleAI_ImageNode` (Imagen 4 / Imagen 3) | Endpoint `generateImages` en pausa; Nano Banana cubre el caso de uso |
| `GoogleAI_TextVisionNode` | Fusionado en **Gemini Chat** con pin `image` opcional |
| Suite diagnostico Google (5 nodos) | Eliminada en v2.0.0 |
| `GrokImageNode` / `Grok_Image_Master` | Fusionados en **Grok Image Gen** |
| `Grok_Video_Forge` / `Grok_Video_Editor` / `Grok_Video_Extension` | Reemplazados por **Grok Video Gen** |
| Suite diagnostico Grok / `Grok_Prompt_Architect` | Eliminados en v2.0.0 |

### Fix GETSETNODE_PRO
Los nodos `PRO_SetNode` / `PRO_GetNode` usan prefijo `PRO_` para evitar colision con `SetNode` / `GetNode` de KJNodes, rgthree-comfy y ComfyUI core (issue KJNodes #545).

---

## Configuracion de API Keys

### Opcion 1 — Variables de entorno (recomendada)
```bash
# Linux / macOS
export GOOGLE_AI_API_KEY="AIza..."
export XAI_API_KEY="xai-..."

# Windows PowerShell
$env:GOOGLE_AI_API_KEY = "AIza..."
$env:XAI_API_KEY = "xai-..."
```

### Opcion 2 — ComfyUI Settings
En el menu de configuracion (icono Settings) buscar los campos:
- `GOOGLE_AI_API_KEY` para los nodos de Google
- `XAI_API_KEY` para los nodos de Grok

### Opcion 3 — Pin `api_key` en el nodo
Escribir la key directamente en el campo `api_key` del nodo.

---

## Grok Video Gen — uso con VHS

El nodo **Grok Video Gen** devuelve la **URL** del MP4 generado (string).
Para usar el video en el pipeline conectar la URL a:
- **VHS Load Video From URL** (VideoHelperSuite)

---

## Links

- Registry: [registry.comfy.org/publishers/promptmodelsstudio](https://registry.comfy.org/publishers/promptmodelsstudio)
- Issues: [github.com/cdanielp/COMFYUI_PROMPTMODELS/issues](https://github.com/cdanielp/COMFYUI_PROMPTMODELS/issues)
- Google AI Studio: [aistudio.google.com](https://aistudio.google.com)
- xAI Console: [console.x.ai](https://console.x.ai)
