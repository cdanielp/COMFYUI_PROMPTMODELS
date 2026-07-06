# PromptModels Studio — ComfyUI Custom Nodes

**v3.0.0** · Requiere ComfyUI ≥ 0.26.0

Nodos de IA para ComfyUI: NVIDIA NIM, Google Gemini y Grok. Sin SDKs externos — solo REST nativo con `requests` y `Pillow`.

---

## Nodos activos en v3.0.0

### Nuevos — v3 (sin deprecar)

| Nodo | Categoría | API | Descripción |
|------|-----------|-----|-------------|
| **PMS_NimbusText** | PromptModels/NVIDIA (NIMbus) | NVIDIA NIM | Chat con modelos de texto: Nemotron, DeepSeek V4 |
| **PMS_NimbusVision** | PromptModels/NVIDIA (NIMbus) | NVIDIA NIM | Análisis de imagen multimodal (VL models) |
| **PMS_GeminiChatV3** | PromptModels/Google | Gemini API | Chat Gemini con thinking budget (Gemini 3+ / 2.5) |

### Legacy (38 nodos, marcados como deprecados)

> Funcionan igual que en v2. Se mantienen para compatibilidad con workflows existentes.

| Categoría | Nodos |
|-----------|-------|
| **Google AI / Text** | GoogleAI_TextNode, GoogleAI_TextVisionNode, PMS_GeminiChat |
| **Google AI / Image** | GoogleAI_NanoBananaNode, PMS_NanaBanana, GoogleAI_ImageNode |
| **Google AI / Video** | GoogleAI_VideoGenerator, GoogleAI_VideoInterpolation, GoogleAI_VideoStoryboard |
| **Google AI / Diagnostic** | GoogleAI_ModelArchitectureDetector, GoogleAI_TriggerWordExtractor, GoogleAI_WorkflowAnalyzer, GoogleAI_CompatibilityChecker, GoogleAI_LoRATrainingAnalyzer |
| **Google AI / TTS** | PMS_GeminiTTS |
| **PromptModels / Grok** | GrokTextNode, PMS_GrokImageGen, PMS_GrokVideoGen, PMS_GrokTTS, PMS_GrokSTT |
| **GetSetNode Pro** | PRO_SetNode, PRO_GetNode, PRO_UnetLoaderGGUF, PRO_SetNodeNamed, PRO_UnetLoaderGGUFAdvanced, PRO_ListCacheNode, PRO_ClearCacheNode |
| **Selectores Pro** | SelectorDeImagenes, SelectorDePrompts, ImagenLatentePro, PromptPro |
| **PromptModels / Batch** | PMS_DualPromptListBatch, PMS_VideoBatchConcat |
| **Utility** | GetLastFrame, GetFrameByIndex |
| **Text / Security** | TextPromptBlocker, TextPromptBlockerPreview |
| **Prompt Tools** | DivisorDePrompts (10) |

---

## Instalacion

1. Copia esta carpeta en `ComfyUI/custom_nodes/COMFYUI_PROMPTMODELS/`
2. Crea un archivo `.env` en la raiz del paquete con tus API keys:

```env
NVIDIA_API_KEY=nvapi-...
GEMINI_API_KEY=AI...
XAI_API_KEY=xai-...
```

3. Reinicia ComfyUI.

Las keys tambien se pueden pegar directamente en el input `api_key` de cada nodo (ver advertencia abajo).

---

## Protege tu API key

> **Advertencia importante:** si pegas una API key directamente en el campo `api_key` de un nodo, esa key queda expuesta en dos lugares:
>
> - **El JSON del workflow** — el archivo `.json` que guardas o compartes contiene el valor en texto plano.
> - **Los metadatos PNG** — cuando guardas una imagen desde ComfyUI, el workflow completo (con la key) se embebe en los metadatos del PNG.
>
> **Recomendacion:** usa siempre el archivo `.env` o una variable de entorno del sistema (`NVIDIA_API_KEY`, `GEMINI_API_KEY`, `XAI_API_KEY`). Asi el campo `api_key` del nodo queda vacio y la key nunca viaja en tus archivos.

---

## Variables de entorno

| Variable | Proveedor |
|----------|-----------|
| `NVIDIA_API_KEY` | NVIDIA NIM (NIMbus) |
| `GEMINI_API_KEY` | Google Gemini |
| `XAI_API_KEY` | Grok / xAI |

Prioridad de resolucion: `input del nodo` > `variable de entorno` > `.env`.

---

## Que viene en v3.1.0

- **Nano Banana Gen + Edit** — generacion y edicion de imagenes con Gemini (`/v1beta/interactions`). Requiere cuenta Gemini con billing activo.
- **Grok completo** — PMS_GrokChat, PMS_GrokImageGenV3, PMS_GrokImageEdit (codigo listo, activacion pendiente de key).
- **Video** — nodos de video Veo y Grok en API v3.
- **Voz** — TTS/STT actualizados a v3.

---

## Requisitos

- ComfyUI >= 0.26.0
- Python >= 3.10
- `requests`
- `Pillow`
