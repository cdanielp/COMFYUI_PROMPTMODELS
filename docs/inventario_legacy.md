# Inventario Legacy — promptmodels v2.x → v3.0.0
> Contrato intocable. 38 nodos en 8 carpetas. Los node_ids, nombres de inputs, tipos, defaults y orden de outputs NO pueden cambiar.

## Posiciones de api_key (20 nodos — índice 1-based sobre lista req+opt unificada)

| node_id | api_key_pos | total_inputs |
|---------|-------------|--------------|
| GoogleAI_TextNode | **#4** | 13 |
| GoogleAI_TextVisionNode | **#4** | 9 |
| GoogleAI_NanoBananaNode | **#7** | 14 |
| GoogleAI_ImageNode | **#6** | 7 |
| GoogleAI_VideoGenerator | **#5** | 7 |
| GoogleAI_VideoInterpolation | **#7** | 7 |
| GoogleAI_VideoStoryboard | **#5** | 8 |
| GoogleAI_ModelArchitectureDetector | **#2** | 3 |
| GoogleAI_TriggerWordExtractor | **#2** | 3 |
| GoogleAI_WorkflowAnalyzer | **#2** | 3 |
| GoogleAI_CompatibilityChecker | **#3** | 4 |
| GoogleAI_LoRATrainingAnalyzer | **#2** | 3 |
| PMS_GeminiChat | **#4** | 13 (alias de GoogleAI_TextNode) |
| PMS_NanaBanana | **#7** | 14 (alias de GoogleAI_NanoBananaNode) |
| PMS_GeminiTTS | **#4** | 4 |
| GrokTextNode | **#5** | 5 |
| PMS_GrokImageGen | **#5** | 5 |
| PMS_GrokVideoGen | **#6** | 6 |
| PMS_GrokTTS | **#4** | 4 |
| PMS_GrokSTT | **#3** | 3 |

---

## Carpeta: ComfyUI_GoogleAI (15 nodos)

### 1. GoogleAI_TextNode
**display_name:** "Google AI - Text Generator"  
**category:** "Google AI/Text"  
**api_key:** sí (optional, posición: último de optional)

| # | nombre | tipo | default | req/opt |
|---|--------|------|---------|---------|
| 1 | prompt | STRING multiline | "Describe esta imagen en detalle." | required |
| 2 | model | COMBO ["gemini-3.1-pro-preview","gemini-3-flash-preview","gemini-2.5-pro","gemini-2.5-flash"] | "gemini-3.1-pro-preview" | required |
| 3 | thinking_budget | COMBO ["Off","Low","Medium","High"] | "Off" | required |
| 4 | api_key | STRING | "" | optional |
| 5 | system_prompt | STRING multiline | "" | optional |
| 6 | image_1 | IMAGE | — | optional |
| 7 | image_2 | IMAGE | — | optional |
| 8 | image_3 | IMAGE | — | optional |
| 9 | image_4 | IMAGE | — | optional |
| 10 | image_5 | IMAGE | — | optional |
| 11 | youtube_url | STRING | "" | optional |
| 12 | max_tokens | INT min=64 max=65536 step=64 | 4096 | optional |
| 13 | temperature | FLOAT min=0.0 max=2.0 step=0.05 | 0.7 | optional |

**outputs:** (STRING,) → ("text",)

---

### 2. GoogleAI_TextVisionNode
**display_name:** "Google AI - Vision Analyzer"  
**category:** "Google AI/Text"  
**api_key:** sí (optional)

| # | nombre | tipo | default | req/opt |
|---|--------|------|---------|---------|
| 1 | image_1 | IMAGE | — | required |
| 2 | prompt | STRING multiline | "Describe esta imagen en detalle." | required |
| 3 | model | COMBO ["gemini-3.1-pro-preview","gemini-3-flash-preview","gemini-2.5-pro","gemini-2.5-flash"] | "gemini-3.1-pro-preview" | required |
| 4 | api_key | STRING | "" | optional |
| 5 | system_prompt | STRING multiline | "" | optional |
| 6 | image_2 | IMAGE | — | optional |
| 7 | image_3 | IMAGE | — | optional |
| 8 | image_4 | IMAGE | — | optional |
| 9 | image_5 | IMAGE | — | optional |

**outputs:** (STRING,) → ("analysis",)

---

### 3. GoogleAI_NanoBananaNode
**display_name:** "Google AI - Nano Banana (NB2/Pro)"  
**category:** "Google AI/Image"  
**api_key:** sí (optional)

| # | nombre | tipo | default | req/opt |
|---|--------|------|---------|---------|
| 1 | prompt | STRING multiline | "A beautiful cinematic portrait..." | required |
| 2 | model | COMBO ["gemini-3.1-flash-image-preview","gemini-3-pro-image-preview","gemini-2.5-flash-image"] | "gemini-3.1-flash-image-preview" | required |
| 3 | aspect_ratio | COMBO [14 values: "1:1","1:4","1:8","2:3","3:2","3:4","4:1","4:3","4:5","5:4","8:1","9:16","16:9","21:9"] | "1:1" | required |
| 4 | image_size | COMBO ["512px","0.5K","1K","2K","4K"] | "2K" | required |
| 5 | seed | INT min=0 max=0xffffffffffffffff | 0 | required |
| 6 | randomize_seed | BOOLEAN | True | required |
| 7 | api_key | STRING | "" | optional |
| 8 | system_prompt | STRING multiline | "You are an expert image composition engine..." | optional |
| 9 | image_1 | IMAGE | — | optional |
| 10 | image_2 | IMAGE | — | optional |
| 11 | image_3 | IMAGE | — | optional |
| 12 | image_4 | IMAGE | — | optional |
| 13 | image_5 | IMAGE | — | optional |
| 14 | safety_threshold | COMBO ["BLOCK_ONLY_HIGH","BLOCK_MEDIUM_AND_ABOVE","BLOCK_LOW_AND_ABOVE"] | "BLOCK_ONLY_HIGH" | optional |

**outputs:** (IMAGE, STRING) → ("image", "description")

---

### 4. GoogleAI_ImageNode
**display_name:** "Google AI - Image Generator (Imagen 4)"  
**category:** "Google AI/Image"  
**api_key:** sí (optional)

| # | nombre | tipo | default | req/opt |
|---|--------|------|---------|---------|
| 1 | prompt | STRING multiline | "A beautiful cinematic portrait" | required |
| 2 | model | COMBO ["imagen-4.0-generate-001","imagen-4.0-ultra-generate-001","imagen-4.0-fast-generate-001","imagen-3.0-generate-002","imagen-3.0-fast-generate-001"] | "imagen-4.0-generate-001" | required |
| 3 | aspect_ratio | COMBO ["1:1","16:9","9:16","4:3","3:4"] | "1:1" | required |
| 4 | seed | INT min=0 max=0xffffffffffffffff | 0 | required |
| 5 | randomize_seed | BOOLEAN | True | required |
| 6 | api_key | STRING | "" | optional |
| 7 | negative_prompt | STRING multiline | "" | optional |

**outputs:** (IMAGE,) → ("image",)

---

### 5. GoogleAI_VideoGenerator
**display_name:** "Google AI - Video Generator (Veo 3.1)"  
**category:** "Google AI/Video"  
**api_key:** sí (optional)

| # | nombre | tipo | default | req/opt |
|---|--------|------|---------|---------|
| 1 | prompt | STRING multiline | "A cinematic drone shot..." | required |
| 2 | model | COMBO ["veo-3.1-generate-preview","veo-3.1-fast-generate-preview","veo-2.0-generate-001"] | "veo-3.1-generate-preview" | required |
| 3 | video_preset | COMBO [5 presets] | "1920x1080 (16:9)" | required |
| 4 | duration_seconds | COMBO ["4","6","8"] | "6" | required |
| 5 | api_key | STRING | "" | optional |
| 6 | init_image_or_video | IMAGE | — | optional |
| 7 | negative_prompt | STRING multiline | "" | optional |

**outputs:** (IMAGE, AUDIO, STRING) → ("video_frames", "audio", "cost_estimate")

---

### 6. GoogleAI_VideoInterpolation
**display_name:** "Google AI - Video Interpolation"  
**category:** "Google AI/Video"  
**api_key:** sí (optional)

| # | nombre | tipo | default | req/opt |
|---|--------|------|---------|---------|
| 1 | first_frame | IMAGE | — | required |
| 2 | last_frame | IMAGE | — | required |
| 3 | prompt | STRING multiline | "A smooth cinematic transition..." | required |
| 4 | model | COMBO ["veo-3.1-generate-preview","veo-3.1-fast-generate-preview","veo-2.0-generate-001"] | "veo-3.1-generate-preview" | required |
| 5 | video_preset | COMBO [5 presets] | "1920x1080 (16:9)" | required |
| 6 | duration_seconds | COMBO ["4","6","8"] | "6" | required |
| 7 | api_key | STRING | "" | optional |

**outputs:** (IMAGE, AUDIO, STRING) → ("video_frames", "audio", "cost_estimate")

---

### 7. GoogleAI_VideoStoryboard
**display_name:** "Google AI - Video Storyboard"  
**category:** "Google AI/Video"  
**api_key:** sí (optional)

| # | nombre | tipo | default | req/opt |
|---|--------|------|---------|---------|
| 1 | prompt | STRING multiline | "A stylized animated scene..." | required |
| 2 | model | COMBO ["veo-3.1-generate-preview","veo-3.1-fast-generate-preview","veo-2.0-generate-001"] | "veo-3.1-generate-preview" | required |
| 3 | video_preset | COMBO [5 presets] | "1920x1080 (16:9)" | required |
| 4 | duration_seconds | COMBO ["4","6","8"] | "8" | required |
| 5 | api_key | STRING | "" | optional |
| 6 | reference_image_1 | IMAGE | — | optional |
| 7 | reference_image_2 | IMAGE | — | optional |
| 8 | reference_image_3 | IMAGE | — | optional |

**outputs:** (IMAGE, AUDIO, STRING) → ("video_frames", "audio", "cost_estimate")

---

### 8. GoogleAI_ModelArchitectureDetector
**display_name:** "Google AI - Architecture Detector"  
**category:** "Google AI/Diagnostic"  
**api_key:** sí (optional)

| # | nombre | tipo | default | req/opt |
|---|--------|------|---------|---------|
| 1 | safetensors_path | STRING | "" | required |
| 2 | api_key | STRING | "" | optional |
| 3 | model | COMBO ["gemini-3.1-pro-preview","gemini-3-flash-preview","gemini-2.5-flash","gemini-2.5-pro"] | "gemini-3.1-pro-preview" | optional |

**outputs:** (STRING,) → ("architecture_report",)

---

### 9. GoogleAI_TriggerWordExtractor
**display_name:** "Google AI - Trigger Word Extractor"  
**category:** "Google AI/Diagnostic"  
**api_key:** sí (optional)

| # | nombre | tipo | default | req/opt |
|---|--------|------|---------|---------|
| 1 | lora_path | STRING | "" | required |
| 2 | api_key | STRING | "" | optional |
| 3 | model | COMBO ["gemini-3.1-pro-preview","gemini-3-flash-preview","gemini-2.5-flash","gemini-2.5-pro"] | "gemini-2.5-flash" | optional |

**outputs:** (STRING,) → ("trigger_words",)

---

### 10. GoogleAI_WorkflowAnalyzer
**display_name:** "Google AI - Workflow Analyzer"  
**category:** "Google AI/Diagnostic"  
**api_key:** sí (optional)

| # | nombre | tipo | default | req/opt |
|---|--------|------|---------|---------|
| 1 | workflow_json | STRING multiline | "" | required |
| 2 | api_key | STRING | "" | optional |
| 3 | model | COMBO ["gemini-3.1-pro-preview","gemini-3-flash-preview","gemini-2.5-flash","gemini-2.5-pro"] | "gemini-3.1-pro-preview" | optional |

**outputs:** (STRING,) → ("analysis_report",)

---

### 11. GoogleAI_CompatibilityChecker
**display_name:** "Google AI - Compatibility Checker"  
**category:** "Google AI/Diagnostic"  
**api_key:** sí (optional)

| # | nombre | tipo | default | req/opt |
|---|--------|------|---------|---------|
| 1 | checkpoint_path | STRING | "" | required |
| 2 | lora_path | STRING | "" | required |
| 3 | api_key | STRING | "" | optional |
| 4 | model | COMBO ["gemini-3.1-pro-preview","gemini-3-flash-preview","gemini-2.5-flash","gemini-2.5-pro"] | "gemini-2.5-flash" | optional |

**outputs:** (BOOLEAN, STRING) → ("is_compatible", "compatibility_report")

---

### 12. GoogleAI_LoRATrainingAnalyzer
**display_name:** "Google AI - Training Analyzer"  
**category:** "Google AI/Diagnostic"  
**api_key:** sí (optional)

| # | nombre | tipo | default | req/opt |
|---|--------|------|---------|---------|
| 1 | training_logs | STRING multiline | "" | required |
| 2 | api_key | STRING | "" | optional |
| 3 | model | COMBO ["gemini-3.1-pro-preview","gemini-3-flash-preview","gemini-2.5-flash","gemini-2.5-pro"] | "gemini-3.1-pro-preview" | optional |

**outputs:** (STRING,) → ("diagnosis_report",)

---

### 13. PMS_GeminiChat
**display_name:** "Gemini Chat (PMS)"  
**category:** "Google AI/Text"  
**api_key:** sí — **ALIAS de GoogleAI_TextNode (misma clase)**  
Inputs/outputs idénticos a GoogleAI_TextNode.

---

### 14. PMS_NanaBanana
**display_name:** "Nano Banana - Imagen IA (PMS)"  
**category:** "Google AI/Image"  
**api_key:** sí — **ALIAS de GoogleAI_NanoBananaNode (misma clase)**  
Inputs/outputs idénticos a GoogleAI_NanoBananaNode.

---

### 15. PMS_GeminiTTS
**display_name:** "Gemini Text to Speech (PMS)"  
**category:** "PromptModels/Google"  
**api_key:** sí (optional)

| # | nombre | tipo | default | req/opt |
|---|--------|------|---------|---------|
| 1 | text | STRING multiline | "Hola, soy Gemini..." | required |
| 2 | voice_name | STRING | "Aoede" | optional |
| 3 | language_code | STRING | "es-419" | optional |
| 4 | api_key | STRING | "" | optional |

**outputs:** (AUDIO,) → ("audio",)

---

## Carpeta: ComfyUI_GrokAI (5 nodos)

### 16. GrokTextNode
**display_name:** "Grok Chat (PMS)"  
**category:** "PromptModels/Grok"  
**api_key:** sí (optional)

| # | nombre | tipo | default | req/opt |
|---|--------|------|---------|---------|
| 1 | prompt | STRING multiline | "Escribe tu mensaje aqui..." | required |
| 2 | model | COMBO ["grok-4.20","grok-4.1","grok-4.1-fast"] | "grok-4.1" | required |
| 3 | system_prompt | STRING multiline | "You are a helpful assistant." | optional |
| 4 | temperature | FLOAT min=0.0 max=2.0 step=0.1 | 0.7 | optional |
| 5 | api_key | STRING | "" | optional |

**outputs:** (STRING,) → ("texto",)

---

### 17. PMS_GrokImageGen
**display_name:** "Grok Image Gen (PMS)"  
**category:** "PromptModels/Grok"  
**api_key:** sí (optional)

| # | nombre | tipo | default | req/opt |
|---|--------|------|---------|---------|
| 1 | prompt | STRING multiline | "A futuristic city in cyberpunk style" | required |
| 2 | aspect_ratio | COMBO ["1:1","2:3","3:2"] | "1:1" | required |
| 3 | n | INT min=1 max=4 step=1 | 1 | required |
| 4 | image_ref | IMAGE | — | optional |
| 5 | api_key | STRING | "" | optional |

**outputs:** (IMAGE, STRING) → ("imagen", "url_o_error")

---

### 18. PMS_GrokVideoGen
**display_name:** "Grok Video Gen (PMS)"  
**category:** "PromptModels/Grok"  
**api_key:** sí (optional)

| # | nombre | tipo | default | req/opt |
|---|--------|------|---------|---------|
| 1 | prompt | STRING multiline | "A cinematic shot of a futuristic neon city." | required |
| 2 | duration | INT min=1 max=15 step=1 | 8 | required |
| 3 | aspect_ratio | COMBO ["16:9","9:16","1:1","4:3"] | "16:9" | required |
| 4 | resolution | COMBO ["720p","1080p"] | "720p" | required |
| 5 | source_image | IMAGE | — | optional |
| 6 | api_key | STRING | "" | optional |

**outputs:** (STRING, STRING) → ("video_url", "status")

---

### 19. PMS_GrokTTS
**display_name:** "Grok Text to Speech (PMS)"  
**category:** "PromptModels/Grok"  
**api_key:** sí (optional)

| # | nombre | tipo | default | req/opt |
|---|--------|------|---------|---------|
| 1 | text | STRING multiline | "Hola, soy Grok..." | required |
| 2 | voice | COMBO ["ara","eve","leo","rex","sal"] | "ara" | required |
| 3 | speed | FLOAT min=0.5 max=2.0 step=0.1 | 1.0 | required |
| 4 | api_key | STRING | "" | optional |

**outputs:** (AUDIO, STRING) → ("audio", "voz_usada")

---

### 20. PMS_GrokSTT
**display_name:** "Grok Speech to Text (PMS)"  
**category:** "PromptModels/Grok"  
**api_key:** sí (optional)

| # | nombre | tipo | default | req/opt |
|---|--------|------|---------|---------|
| 1 | audio | AUDIO | — | required |
| 2 | language | STRING | "es" | optional |
| 3 | api_key | STRING | "" | optional |

**outputs:** (STRING, STRING) → ("transcripcion", "idioma_detectado")

---

## Carpeta: GETSETNODE_PRO (7 nodos)

### 21. PRO_SetNode
**display_name:** "📦 PRO Set Node"  
**category:** "GetSetNode_Pro/utils"  
**api_key:** no

| # | nombre | tipo | default | req/opt |
|---|--------|------|---------|---------|
| — | MODEL/CLIP/VAE/IMAGE/LATENT/etc. | varios tipos opcionales + ANY | — | optional |
| — | hidden: unique_id, prompt, extra_pnginfo | HIDDEN | — | hidden |

**outputs:** (ANY,) → ("*",)  OUTPUT_NODE=True

---

### 22. PRO_GetNode
**display_name:** "📤 PRO Get Node"  
**category:** "GetSetNode_Pro/utils"  
**api_key:** no

| # | nombre | tipo | default | req/opt |
|---|--------|------|---------|---------|
| 1 | name | STRING | "my_variable" | optional |
| — | hidden: unique_id, prompt, extra_pnginfo | HIDDEN | — | hidden |

**outputs:** (ANY,) → ("*",)

---

### 23. PRO_UnetLoaderGGUF
**display_name:** "🧠 PRO Unet Loader GGUF"  
**category:** "GetSetNode_Pro/loaders"  
**api_key:** no

| # | nombre | tipo | default | req/opt |
|---|--------|------|---------|---------|
| 1 | unet_name | COMBO [archivos en unet/diffusion_models/checkpoints] | — | required |

**outputs:** (MODEL,) → ("model",)

---

### 24. PRO_SetNodeNamed
**display_name:** "📦 PRO Set Node (Named)"  
**category:** "GetSetNode_Pro/utils"  
**api_key:** no

| # | nombre | tipo | default | req/opt |
|---|--------|------|---------|---------|
| 1 | value | ANY | — | required |
| 2 | name | STRING | "my_variable" | required |

**outputs:** (ANY,) → ("value",)  OUTPUT_NODE=True

---

### 25. PRO_UnetLoaderGGUFAdvanced
**display_name:** "🧠 PRO Unet Loader GGUF+"  
**category:** "GetSetNode_Pro/loaders"  
**api_key:** no

| # | nombre | tipo | default | req/opt |
|---|--------|------|---------|---------|
| 1 | unet_name | COMBO [archivos] | — | required |
| 2 | dtype | COMBO ["auto","float32","float16","bfloat16"] | "auto" | optional |
| 3 | force_cpu | BOOLEAN | False | optional |

**outputs:** (MODEL, STRING) → ("model", "info")

---

### 26. PRO_ListCacheNode
**display_name:** "📋 PRO List Cache"  
**category:** "GetSetNode_Pro/utils"  
**api_key:** no

| # | nombre | tipo | default | req/opt |
|---|--------|------|---------|---------|
| 1 | trigger | ANY | — | optional |

**outputs:** (STRING,) → ("info",)

---

### 27. PRO_ClearCacheNode
**display_name:** "🗑️ PRO Clear Cache"  
**category:** "GetSetNode_Pro/utils"  
**api_key:** no

| # | nombre | tipo | default | req/opt |
|---|--------|------|---------|---------|
| 1 | confirm | BOOLEAN | False | required |

**outputs:** (STRING,) → ("status",)  OUTPUT_NODE=True

---

## Carpeta: comfyui_selectores_pro (4 nodos)

### 28. SelectorDeImagenes
**display_name:** "Selector de imágenes"  
**category:** "Selectores Pro"  
**api_key:** no

| # | nombre | tipo | default | req/opt |
|---|--------|------|---------|---------|
| 1 | fallback | COMBO ["error","slot1"] | "slot1" | required |
| 2 | mode | COMBO ["auto","single_only","batch_only"] | "auto" | required |
| 3 | on1 | BOOLEAN | True | required |
| 4 | on2 | BOOLEAN | False | required |
| … | on3–on12 | BOOLEAN | False | required |
| — | img1–img12 | IMAGE | — | optional |
| — | mask1–mask12 | MASK | — | optional |

**outputs:** (IMAGE, MASK) → ("image", "mask")

---

### 29. SelectorDePrompts
**display_name:** "Selector de Prompts"  
**category:** "Selectores Pro"  
**api_key:** no

| # | nombre | tipo | default | req/opt |
|---|--------|------|---------|---------|
| 1 | fallback | COMBO ["error","p1"] | "p1" | required |
| 2 | join_with | COMBO ["\\n\\n","\\n","\|",","] | "\\n\\n" | required |
| 3 | mode | COMBO ["auto","single_only","join_only"] | "auto" | required |
| 4 | on1 | BOOLEAN | True | required |
| … | on2–on12 | BOOLEAN | False | required |
| — | p1–p12 | STRING multiline | "" | optional |

**outputs:** (STRING,) → ("text",)

---

### 30. ImagenLatentePro
**display_name:** "Imagen latente Pro"  
**category:** "Selectores Pro"  
**api_key:** no

| # | nombre | tipo | default | req/opt |
|---|--------|------|---------|---------|
| 1 | size_preset | COMBO [28 presets] | "512×512 (1:1) - Medio" | required |
| 2 | batch_size | INT min=1 max=64 | 1 | required |
| 3 | rounding | COMBO ["auto_round","strict"] | "auto_round" | required |

**outputs:** (LATENT,) → ("latent",)

---

### 31. PromptPro
**display_name:** "Prompt Pro"  
**category:** "Selectores Pro"  
**api_key:** no

| # | nombre | tipo | default | req/opt |
|---|--------|------|---------|---------|
| 1 | 📐 Diseño | COMBO [10 diseños] | "Retrato Pro" | required |
| 2 | 👤 Sujeto | STRING | "" | required |
| 3 | 🧍 Acción / Pose | STRING | "" | required |
| 4 | 🎭 Emoción / Expresión | STRING | "" | required |
| 5 | 👗 Vestuario / Props | STRING | "" | required |
| 6 | 🏞️ Fondo / Entorno | STRING | "" | required |
| 7 | 🎨 Estilo | STRING | "" | required |
| 8 | 🎨 Paleta / Colores | STRING | "" | required |
| 9 | 💡 Iluminación | STRING | "" | required |
| 10 | 📷 Cámara / Lente | STRING | "" | required |
| 11 | 🧪 Materiales / Texturas | STRING | "" | required |
| 12 | 🧷 Composición | STRING | "" | required |
| 13 | 🔎 Detalle | STRING | "" | required |
| 14 | 🌫️ Atmósfera | STRING | "" | required |
| 15 | ✨ Calidad | STRING | "" | required |
| 16 | 🧯 Restricciones | STRING | "" | required |
| 17 | ➕ Extra | STRING multiline | "" | required |
| 18 | 🔗 Separador | COMBO [", "," ","\\n"," \| "] | ", " | required |
| 19 | 📌 Prefijo | STRING | "" | required |
| 20 | 📌 Sufijo | STRING | "" | required |
| 21 | 🧹 Normalizar | BOOLEAN | True | required |
| 22 | 🧼 Evitar duplicados | BOOLEAN | False | required |

**outputs:** (STRING,) → ("text",)

---

## Carpeta: BatchEscenas (2 nodos)

### 32. PMS_DualPromptListBatch
**display_name:** "Dual Prompt List Batch (PMS)"  
**category:** "PromptModels/batch"  
**api_key:** no  
**OUTPUT_IS_LIST:** (True, True, True, True)

| # | nombre | tipo | default | req/opt |
|---|--------|------|---------|---------|
| 1 | voice_prompts | STRING multiline | "Texto narracion 1\n---\n..." | required |
| 2 | visual_prompts | STRING multiline | "Descripcion visual 1\n---\n..." | required |
| 3 | separator | STRING | "---" | required |
| 4 | max_scenes | INT min=1 max=50 | 5 | required |

**outputs:** (STRING, STRING, INT, STRING) → ("voice_prompt", "visual_prompt", "index", "index_str")

---

### 33. PMS_VideoBatchConcat
**display_name:** "Video Batch Concat (PMS)"  
**category:** "PromptModels/batch"  
**api_key:** no  
**INPUT_IS_LIST:** True

| # | nombre | tipo | default | req/opt |
|---|--------|------|---------|---------|
| 1 | images | IMAGE | — | required |
| 2 | audio | AUDIO | — | required |
| 3 | silence_ms | INT min=0 max=5000 step=50 | 0 | required |

**outputs:** (IMAGE, AUDIO, INT) → ("images", "audio", "total_frames")

---

## Carpeta: get_last_frame (2 nodos)

### 34. GetLastFrame
**display_name:** "Get Last Frame"  
**category:** "🧩 Utility"  
**api_key:** no

| # | nombre | tipo | default | req/opt |
|---|--------|------|---------|---------|
| 1 | frames | IMAGE | — | required |

**outputs:** (IMAGE,) → ("image",)

---

### 35. GetFrameByIndex
**display_name:** "Get Frame by Index"  
**category:** "🧩 Utility"  
**api_key:** no

| # | nombre | tipo | default | req/opt |
|---|--------|------|---------|---------|
| 1 | frames | IMAGE | — | required |
| 2 | index | INT min=-9999 max=9999 step=1 display="number" | -1 | required |

**outputs:** (IMAGE,) → ("image",)

---

## Carpeta: text_prompt_blocker (2 nodos)

### 36. TextPromptBlocker
**display_name:** "🛡️ Text Prompt Blocker"  
**category:** "Text/Security"  
**api_key:** no

| # | nombre | tipo | default | req/opt |
|---|--------|------|---------|---------|
| 1 | prompt | STRING multiline | "" | required |
| 2 | blocked_words | STRING multiline | "child, kid, baby, infant, underage, young, school, nursery, teen, minor, toddler, preteen" | required |
| 3 | case_sensitive | BOOLEAN | False | optional |
| 4 | hard_block | BOOLEAN | True | optional |
| 5 | detect_contained | BOOLEAN | True | optional |
| 6 | expand_variations | BOOLEAN | True | optional |

**outputs:** (STRING, BOOLEAN, STRING) → ("allowed_output", "is_blocked", "matched_word")

---

### 37. TextPromptBlockerPreview
**display_name:** "🔍 Text Prompt Blocker (Preview)"  
**category:** "Text/Security"  
**api_key:** no  
**OUTPUT_NODE:** True

| # | nombre | tipo | default | req/opt |
|---|--------|------|---------|---------|
| 1 | prompt | STRING multiline | "" | required |
| 2 | blocked_words | STRING multiline | "child, kid, baby, infant, underage, young, school, nursery, teen, minor, toddler, preteen" | required |
| 3 | detect_contained | BOOLEAN | True | optional |
| 4 | expand_variations | BOOLEAN | True | optional |

**outputs:** (STRING, STRING, STRING) → ("original_prompt", "status", "detected_words")

---

## Carpeta: DivisorDePrompts (1 nodo)

### 38. DivisorDePrompts
**display_name:** "DivisorDePrompts (10)"  
**category:** "Prompt Tools"  
**api_key:** no

| # | nombre | tipo | default | req/opt |
|---|--------|------|---------|---------|
| 1 | full_text | STRING multiline | "" | required |
| 2 | trim_mode | BOOLEAN | True | optional |
| 3 | preserve_newlines | BOOLEAN | True | optional |

**outputs:** (STRING×10, INT) → ("prompt_01"…"prompt_10", "count")

---

## Resumen

| Carpeta | Nodos | API key |
|---------|-------|---------|
| ComfyUI_GoogleAI | 15 | 15/15 tienen api_key optional |
| ComfyUI_GrokAI | 5 | 5/5 tienen api_key optional |
| GETSETNODE_PRO | 7 | 0 |
| comfyui_selectores_pro | 4 | 0 |
| BatchEscenas | 2 | 0 |
| get_last_frame | 2 | 0 |
| text_prompt_blocker | 2 | 0 |
| DivisorDePrompts | 1 | 0 |
| **Total** | **38** | **20 con api_key** |
