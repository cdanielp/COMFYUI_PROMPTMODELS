<div align="center">

<img src="prompts models logo.png" alt="Prompt Models Studio" width="200"/>

# COMFYUI_PROMPTMODELS

![Version](https://img.shields.io/badge/version-2.0.1-purple) ![ComfyUI](https://img.shields.io/badge/ComfyUI-custom--nodes-blue) ![License](https://img.shields.io/badge/license-MIT-green) ![Nodos](https://img.shields.io/badge/nodos-38-brightgreen)

Suite de nodos para ComfyUI con integracion REST nativa (sin SDKs) a Google AI y xAI (Grok), mas utilidades de workflow.

</div>

---

## Que hay en v2.0.1

**38 nodos en total** repartidos en 7 carpetas. Los nodos legacy `GoogleAI_*` que se removieron en v2.0.0 fueron **restaurados** — los workflows viejos vuelven a cargar sin errores.

| Carpeta | Nodos | Estado |
|---|---|---|
| ComfyUI_GoogleAI | 15 | Legacy v2.5.0 + PMS_* nuevos |
| ComfyUI_GrokAI | 5 | Rewrite 2026 (Chat + Image + Video + TTS + STT) |
| GETSETNODE_PRO | 2 | PRO_SetNode + PRO_GetNode |
| comfyui_selectores_pro | 4 | Selectores avanzados |
| DivisorDePrompts | 1 | Split de prompts multi-escena |
| get_last_frame | 1 | Extrae ultimo frame de video |
| text_prompt_blocker | 1 | Filtro de keywords |
| BatchEscenas | 1+ | Batch de escenas para video |

---

## Suite ComfyUI_GoogleAI (15 nodos)

### API activa con clase PMS_* (3)
| Nodo | Categoria | Descripcion |
|---|---|---|
| **Gemini Chat (PMS)** | PromptModels/Google | Alias de `GoogleAI_TextNode`. Chat o vision con Gemini 3.x / 2.5. ThinkingConfig auto. |
| **Nano Banana - Imagen IA (PMS)** | PromptModels/Google | Alias de `GoogleAI_NanoBananaNode`. Genera imagenes con NB2/Pro/Original. |
| **Gemini Text to Speech (PMS)** | PromptModels/Google | Voz sintetica con gemini-3.1-flash-tts-preview. Salida tensor AUDIO. |

### Legacy v2.5.0 restaurados (12)

**Texto / Vision**
| Class ID | Display |
|---|---|
| `GoogleAI_TextNode` | Google AI - Text Generator (5 imagenes, YouTube, thinking config) |
| `GoogleAI_TextVisionNode` | Google AI - Vision Analyzer (1 obligatoria + 4 opcionales) |

**Imagen**
| Class ID | Display | API |
|---|---|---|
| `GoogleAI_NanoBananaNode` | Google AI - Nano Banana (NB2/Pro) | generateContent — 14 aspect ratios, 5 imageSize, 5 pines de referencia |
| `GoogleAI_ImageNode` | Google AI - Image Generator (Imagen 4) | generateImages — Imagen 4 Standard/Ultra/Fast + Imagen 3 fallback |

**Video (Veo 3.1)**
| Class ID | Display |
|---|---|
| `GoogleAI_VideoGenerator` | Google AI - Video Generator (Veo 3.1) |
| `GoogleAI_VideoInterpolation` | Google AI - Video Interpolation |
| `GoogleAI_VideoStoryboard` | Google AI - Video Storyboard (hasta 3 referencias) |

**Diagnostico (Gemini-powered)**
| Class ID | Display |
|---|---|
| `GoogleAI_ModelArchitectureDetector` | Google AI - Architecture Detector |
| `GoogleAI_TriggerWordExtractor` | Google AI - Trigger Word Extractor |
| `GoogleAI_WorkflowAnalyzer` | Google AI - Workflow Analyzer |
| `GoogleAI_CompatibilityChecker` | Google AI - Compatibility Checker |
| `GoogleAI_LoRATrainingAnalyzer` | Google AI - Training Analyzer |

### Modelos soportados

**Texto:** `gemini-3.1-pro-preview`, `gemini-3-flash-preview`, `gemini-2.5-pro`, `gemini-2.5-flash`
**Imagen NB:** `gemini-3.1-flash-image-preview` (NB2), `gemini-3-pro-image-preview` (NB Pro), `gemini-2.5-flash-image` (NB Original)
**Imagen Imagen:** `imagen-4.0-generate-001`, `imagen-4.0-ultra-generate-001`, `imagen-4.0-fast-generate-001`, `imagen-3.0-generate-002`, `imagen-3.0-fast-generate-001`
**Video:** `veo-3.1-generate-preview`, `veo-3.1-fast-generate-preview`, `veo-2.0-generate-001`

---

## Suite ComfyUI_GrokAI (5 nodos)

| Nodo | Categoria | Descripcion |
|---|---|---|
| **Grok Chat (PMS)** | PromptModels/Grok | Chat con grok-4.20 / 4.1 / 4.1-fast. Fix parsing de content como lista. |
| **Grok Image Gen (PMS)** | PromptModels/Grok | Text-to-image y image-to-image con grok-imagine-image. Anti-crash. |
| **Grok Video Gen (PMS)** | PromptModels/Grok | Video async con grok-imagine-video. Polling 5s / timeout 300s. |
| **Grok Text to Speech (PMS)** | PromptModels/Grok | Voces ara/eve/leo/rex/sal. Speech tags: [laugh] [sigh] [whisper]. |
| **Grok Speech to Text (PMS)** | PromptModels/Grok | Transcripcion. Entrada tensor AUDIO de ComfyUI. |

---

## Otras utilidades

**GETSETNODE_PRO** — Set/Get nodes con prefijo `PRO_` para evitar colision con KJNodes / rgthree-comfy / ComfyUI core (fix de issue KJNodes #545).

**comfyui_selectores_pro** — 4 selectores avanzados para workflows complejos.

**DivisorDePrompts** — Divide un prompt en multiples escenas para batch processing.

**get_last_frame** — Extrae el ultimo frame de un tensor de video. Util para video extension.

**text_prompt_blocker** — Filtra keywords prohibidas de prompts.

**BatchEscenas** — Procesamiento por lote de escenas para video.

---

## Instalacion

### Opcion 1 — ComfyUI Manager (recomendada)
Busca `promptmodels` en ComfyUI Manager e instala.

### Opcion 2 — Comfy Registry
comfy node install promptmodels

### Opcion 3 — Manual
```bash
cd ComfyUI/custom_nodes
git clone https://github.com/cdanielp/COMFYUI_PROMPTMODELS.git
cd COMFYUI_PROMPTMODELS
pip install -r ComfyUI_GoogleAI/requirements.txt
```

Reinicia ComfyUI.

---

## Configuracion de API Keys

### Opcion 1 — Variables de entorno (recomendada)
```bash
# Linux / macOS
export GOOGLE_AI_API_KEY="AIza..."
export XAI_API_KEY="xai-..."
```
```powershell
# Windows PowerShell
$env:GOOGLE_AI_API_KEY = "AIza..."
$env:XAI_API_KEY = "xai-..."
```

### Opcion 2 — Pin api_key directo en el nodo
Cada nodo tiene un input opcional `api_key`. Si lo dejas vacio toma la variable de entorno.

### Donde obtener las keys
- **Google AI:** https://aistudio.google.com/apikey
- **xAI Grok:** https://console.x.ai/

---

## Compatibilidad de workflows

| Workflow viene de | v2.0.1 |
|---|---|
| v1.x (class IDs `GoogleAI_*`, `Grok*`) | Carga sin cambios |
| v2.0.0 (class IDs `PMS_*`) | Carga sin cambios |
| Mixto | Carga sin cambios |

Los aliases `PMS_GeminiChat = GoogleAI_TextNode` y `PMS_NanaBanana = GoogleAI_NanoBananaNode` apuntan a la misma clase Python — no hay codigo duplicado.

---

## Changelog

### v2.0.1 (Apr 2026)
- **Restaurados 12 nodos legacy GoogleAI_** que se eliminaron por error en v2.0.0
- 3 nodos PMS_* mantenidos como aliases o nodos nuevos
- Total: 15 nodos en ComfyUI_GoogleAI (antes 3)
- Workflows v1.x y v2.0 ambos cargan sin error

### v2.0.0 (Apr 2026)
- Rewrite de Suite GrokAI (Chat + Image + Video + TTS + STT)
- Fix GETSETNODE_PRO: prefijo PRO_ para evitar colision con KJNodes
- Eliminacion accidental de nodos GoogleAI legacy (corregido en v2.0.1)

### v1.5.0 (Apr 2026)
- BatchEscenas module agregado

### v1.4.0 (Mar 2026)
- ComfyUI_GrokAI primera version

### v1.3.x (Feb-Mar 2026)
- Suite GoogleAI completa con Nano Banana 2, Imagen 4, Veo 3.1

---

## Soporte y comunidad

- **Skool:** https://www.skool.com/prompt-models-studio
- **Issues:** https://github.com/cdanielp/COMFYUI_PROMPTMODELS/issues
- **Autor:** Carlos Daniel Penagos | [@cdanielp](https://github.com/cdanielp)

## Licencia

MIT