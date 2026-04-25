# BatchEscenas

Sub-módulo de PROMPTMODELS. Procesamiento secuencial de batches para pipelines de **voz + video**. Permite generar N escenas (narración + visual) en cadena con un solo workflow, sin duplicar nodos.

## Nodos

### Dual Prompt List Batch (PMS)
2 textareas paralelos separados por `---`. Emite listas — ComfyUI ejecuta el workflow downstream 1 vez por escena.

**Inputs:**
- `voice_prompts` (textarea): textos de narración separados por `---`
- `visual_prompts` (textarea): descripciones visuales separadas por `---`
- `separator` (default `---`)
- `max_scenes` (default 5)

**Outputs:** `voice_prompt`, `visual_prompt`, `index`, `index_str` (`000`, `001`...)

### Video Batch Concat (PMS)
Cierre del batch. Recibe las N listas de IMAGE y AUDIO y concatena en 1 IMAGE batch + 1 AUDIO continuo.

**Inputs:**
- `images` (IMAGE list)
- `audio` (AUDIO list)
- `silence_ms` (default 0): silencio opcional entre escenas

**Outputs:** `images`, `audio`, `total_frames`

## Flujo de uso

1. Pega N escenas en `voice_prompts` y `visual_prompts` separadas por `---`
2. `voice_prompt` → TTS (ej. Qwen3VoiceClone)
3. `visual_prompt` → CLIPTextEncode
4. Salidas IMAGE y AUDIO → `Video Batch Concat (PMS)`
5. Salida del concat → un solo `VHS_VideoCombine` final

## Reemplazo de DivisorDePrompts

Para pipelines de voz+video con múltiples escenas, este sub-módulo reemplaza el flujo basado en `DivisorDePrompts` + N copias de TTS/Video Combine. Reduce ~30 nodos duplicados a ~8 nodos lineales.
