from comfy_api.latest import io

# ── model lists (exact V1 strings) ────────────────────────────────
_TEXT_MODELS = ["gemini-3.1-pro-preview","gemini-3-flash-preview","gemini-2.5-pro","gemini-2.5-flash"]
_NB_MODELS   = ["gemini-3.1-flash-image-preview","gemini-3-pro-image-preview","gemini-2.5-flash-image"]
_NB_AR       = ["1:1","1:4","1:8","2:3","3:2","3:4","4:1","4:3","4:5","5:4","8:1","9:16","16:9","21:9"]
_NB_SIZES    = ["512px","0.5K","1K","2K","4K"]
_IMG_MODELS  = ["imagen-4.0-generate-001","imagen-4.0-ultra-generate-001","imagen-4.0-fast-generate-001",
                "imagen-3.0-generate-002","imagen-3.0-fast-generate-001"]
_IMG_AR      = ["1:1","16:9","9:16","4:3","3:4"]
_VID_MODELS  = ["veo-3.1-generate-preview","veo-3.1-fast-generate-preview","veo-2.0-generate-001"]
_VID_PRESETS = ["1920x1080 (16:9)","1080x1920 (9:16)","1080x1080 (1:1)","3840x2160 (16:9 4K)","2160x3840 (9:16 4K)"]
_VID_DUR     = ["4","6","8"]
_SAFETY      = ["BLOCK_ONLY_HIGH","BLOCK_MEDIUM_AND_ABOVE","BLOCK_LOW_AND_ABOVE"]
_THINKING    = ["Off","Low","Medium","High"]
_DIAG_MODELS = ["gemini-3.1-pro-preview","gemini-3-flash-preview","gemini-2.5-flash","gemini-2.5-pro"]


def _gemini_key(api_key):
    from ..core.keys import gemini_key
    return gemini_key(api_key)


# ═══════════════ GoogleAI_TextNode ════════════════════════════════
class GoogleAI_TextNode(io.ComfyNode):
    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id="GoogleAI_TextNode",
            display_name="Google AI - Text Generator",
            category="Google AI/Text",
            inputs=[
                io.String.Input("prompt", multiline=True, default="Describe esta imagen en detalle."),
                io.Combo.Input("model", options=_TEXT_MODELS, default="gemini-3.1-pro-preview"),
                io.Combo.Input("thinking_budget", options=_THINKING, default="Off",
                               tooltip="Gemini 3+: thinkingLevel. Gemini 2.5: thinkingBudget."),
                io.String.Input("api_key", optional=True, default=""),
                io.String.Input("system_prompt", optional=True, multiline=True, default=""),
                io.Image.Input("image_1", optional=True, tooltip="Imagen 1 para análisis multimodal."),
                io.Image.Input("image_2", optional=True, tooltip="Imagen 2 (opcional)."),
                io.Image.Input("image_3", optional=True, tooltip="Imagen 3 (opcional)."),
                io.Image.Input("image_4", optional=True, tooltip="Imagen 4 (opcional)."),
                io.Image.Input("image_5", optional=True, tooltip="Imagen 5 (opcional)."),
                io.String.Input("youtube_url", optional=True, default=""),
                io.Int.Input("max_tokens", optional=True, default=4096, min=64, max=65536, step=64),
                io.Float.Input("temperature", optional=True, default=0.7, min=0.0, max=2.0, step=0.05),
            ],
            outputs=[io.String.Output("text")],
            is_deprecated=True,
        )

    @classmethod
    def execute(cls, prompt, model, thinking_budget, api_key="", system_prompt="",
                image_1=None, image_2=None, image_3=None, image_4=None, image_5=None,
                youtube_url="", max_tokens=4096, temperature=0.7) -> io.NodeOutput:
        try:
            from ..ComfyUI_GoogleAI.google_core import GoogleAICore
            key = _gemini_key(api_key)
            extra_parts = []
            for img in [image_1, image_2, image_3, image_4, image_5]:
                if img is not None:
                    b64 = GoogleAICore.tensor_to_base64(img, index=0)
                    extra_parts.append({"inlineData": {"mimeType": "image/png", "data": b64}})
            if youtube_url and youtube_url.strip():
                extra_parts.append({"fileData": {"mimeType": "video/*", "fileUri": youtube_url.strip()}})
            gen_cfg = {"maxOutputTokens": max_tokens, "temperature": temperature}
            tb = thinking_budget if thinking_budget != "Off" else None
            result = GoogleAICore.call_gemini_text(
                api_key=key, prompt=prompt, model=model,
                system_instruction=system_prompt or None, thinking_budget=tb,
                extra_parts=extra_parts or None, generation_config=gen_cfg,
            )
            return io.NodeOutput(result)
        except Exception as e:
            return io.NodeOutput(f"❌ Error: {str(e)}")


# ═══════════════ PMS_GeminiChat (alias) ═══════════════════════════
class PMS_GeminiChat(io.ComfyNode):
    @classmethod
    def define_schema(cls) -> io.Schema:
        s = GoogleAI_TextNode.define_schema()
        return io.Schema(
            node_id="PMS_GeminiChat", display_name="Gemini Chat (PMS)",
            category="Google AI/Text", inputs=s.inputs, outputs=s.outputs,
            is_deprecated=True,
        )

    @classmethod
    def execute(cls, **kw) -> io.NodeOutput:
        return GoogleAI_TextNode.execute(**kw)


# ═══════════════ GoogleAI_TextVisionNode ══════════════════════════
class GoogleAI_TextVisionNode(io.ComfyNode):
    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id="GoogleAI_TextVisionNode",
            display_name="Google AI - Vision Analyzer",
            category="Google AI/Text",
            inputs=[
                io.Image.Input("image_1", tooltip="Imagen principal (obligatoria)."),
                io.String.Input("prompt", multiline=True, default="Describe esta imagen en detalle."),
                io.Combo.Input("model", options=_TEXT_MODELS, default="gemini-3.1-pro-preview"),
                io.String.Input("api_key", optional=True, default=""),
                io.String.Input("system_prompt", optional=True, multiline=True, default=""),
                io.Image.Input("image_2", optional=True, tooltip="Imagen adicional 2 (opcional)."),
                io.Image.Input("image_3", optional=True, tooltip="Imagen adicional 3 (opcional)."),
                io.Image.Input("image_4", optional=True, tooltip="Imagen adicional 4 (opcional)."),
                io.Image.Input("image_5", optional=True, tooltip="Imagen adicional 5 (opcional)."),
            ],
            outputs=[io.String.Output("analysis")],
            is_deprecated=True,
        )

    @classmethod
    def execute(cls, image_1, prompt, model, api_key="", system_prompt="",
                image_2=None, image_3=None, image_4=None, image_5=None) -> io.NodeOutput:
        try:
            from ..ComfyUI_GoogleAI.google_core import GoogleAICore
            key = _gemini_key(api_key)
            extra_parts = []
            for img in [image_1, image_2, image_3, image_4, image_5]:
                if img is not None:
                    b64 = GoogleAICore.tensor_to_base64(img, index=0)
                    extra_parts.append({"inlineData": {"mimeType": "image/png", "data": b64}})
            result = GoogleAICore.call_gemini_text(
                api_key=key, prompt=prompt, model=model,
                system_instruction=system_prompt or None, extra_parts=extra_parts,
            )
            return io.NodeOutput(result)
        except Exception as e:
            return io.NodeOutput(f"❌ Error: {str(e)}")


# ═══════════════ GoogleAI_NanoBananaNode ══════════════════════════
class GoogleAI_NanoBananaNode(io.ComfyNode):
    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id="GoogleAI_NanoBananaNode",
            display_name="Google AI - Nano Banana (NB2/Pro)",
            category="Google AI/Image",
            inputs=[
                io.String.Input("prompt", multiline=True,
                                default="A beautiful cinematic portrait, photorealistic, 8K detail"),
                io.Combo.Input("model", options=_NB_MODELS, default="gemini-3.1-flash-image-preview"),
                io.Combo.Input("aspect_ratio", options=_NB_AR, default="1:1",
                               tooltip="14 ratios oficiales. Extremos (1:4,4:1,1:8,8:1) solo NB2."),
                io.Combo.Input("image_size", options=_NB_SIZES, default="2K",
                               tooltip="512px, 0.5K (solo NB2), 1K, 2K, 4K (NB2/Pro)."),
                io.Int.Input("seed", default=0, min=0, max=0xffffffffffffffff),
                io.Boolean.Input("randomize_seed", default=True),
                io.String.Input("api_key", optional=True, default=""),
                io.String.Input("system_prompt", optional=True, multiline=True,
                                default="You are an expert image composition engine. "
                                        "Use the reference images to understand the visual style, "
                                        "character traits, and composition goals. "
                                        "Generate a new image that matches the described scenario."),
                io.Image.Input("image_1", optional=True, tooltip="Referencia 1."),
                io.Image.Input("image_2", optional=True, tooltip="Referencia 2"),
                io.Image.Input("image_3", optional=True, tooltip="Referencia 3"),
                io.Image.Input("image_4", optional=True, tooltip="Referencia 4"),
                io.Image.Input("image_5", optional=True, tooltip="Referencia 5"),
                io.Combo.Input("safety_threshold", options=_SAFETY, optional=True,
                               default="BLOCK_ONLY_HIGH",
                               tooltip="Nivel de filtro. BLOCK_ONLY_HIGH = menos restrictivo."),
            ],
            outputs=[io.Image.Output("image"), io.String.Output("description")],
            is_deprecated=True,
        )

    @classmethod
    def execute(cls, prompt, model, aspect_ratio, image_size, seed, randomize_seed,
                api_key="", system_prompt="",
                image_1=None, image_2=None, image_3=None, image_4=None, image_5=None,
                safety_threshold="BLOCK_ONLY_HIGH") -> io.NodeOutput:
        try:
            import random
            from ..ComfyUI_GoogleAI.google_core import GoogleAICore, SAFETY_THRESHOLDS
            key = _gemini_key(api_key)
            eff_seed = random.randint(0, 0xffffffffffffffff) if randomize_seed else seed
            refs = []
            for ref in [image_1, image_2, image_3, image_4, image_5]:
                if ref is not None:
                    refs.append(GoogleAICore.compress_image_for_api(ref, 0))
            safety_cfg = [{"category": cat, "threshold": safety_threshold}
                          for cat in ["HARM_CATEGORY_HARASSMENT","HARM_CATEGORY_HATE_SPEECH",
                                      "HARM_CATEGORY_SEXUALLY_EXPLICIT","HARM_CATEGORY_DANGEROUS_CONTENT"]]
            img_bytes, description = GoogleAICore.generate_image_gemini(
                api_key=key, prompt=prompt, model=model,
                system_instruction=system_prompt or None, reference_images_b64=refs or None,
                aspect_ratio=aspect_ratio, image_size=image_size, seed=eff_seed, safety_settings=safety_cfg,
            )
            return io.NodeOutput(GoogleAICore.bytes_to_image_tensor(img_bytes), description)
        except Exception as e:
            from ..ComfyUI_GoogleAI.google_core import GoogleAICore
            return io.NodeOutput(GoogleAICore.create_error_image(str(e)), f"Error: {str(e)}")


# ═══════════════ PMS_NanaBanana (alias) ═══════════════════════════
class PMS_NanaBanana(io.ComfyNode):
    @classmethod
    def define_schema(cls) -> io.Schema:
        s = GoogleAI_NanoBananaNode.define_schema()
        return io.Schema(
            node_id="PMS_NanaBanana", display_name="Nano Banana - Imagen IA (PMS)",
            category="Google AI/Image", inputs=s.inputs, outputs=s.outputs,
            is_deprecated=True,
        )

    @classmethod
    def execute(cls, **kw) -> io.NodeOutput:
        return GoogleAI_NanoBananaNode.execute(**kw)


# ═══════════════ GoogleAI_ImageNode ═══════════════════════════════
class GoogleAI_ImageNode(io.ComfyNode):
    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id="GoogleAI_ImageNode",
            display_name="Google AI - Image Generator (Imagen 4)",
            category="Google AI/Image",
            inputs=[
                io.String.Input("prompt", multiline=True, default="A beautiful cinematic portrait"),
                io.Combo.Input("model", options=_IMG_MODELS, default="imagen-4.0-generate-001"),
                io.Combo.Input("aspect_ratio", options=_IMG_AR, default="1:1"),
                io.Int.Input("seed", default=0, min=0, max=0xffffffffffffffff),
                io.Boolean.Input("randomize_seed", default=True),
                io.String.Input("api_key", optional=True, default=""),
                io.String.Input("negative_prompt", optional=True, multiline=True, default=""),
            ],
            outputs=[io.Image.Output("image")],
            is_deprecated=True,
        )

    @classmethod
    def execute(cls, prompt, model, aspect_ratio, seed, randomize_seed,
                api_key="", negative_prompt="") -> io.NodeOutput:
        try:
            import random
            from ..ComfyUI_GoogleAI.google_core import GoogleAICore
            key = _gemini_key(api_key)
            eff_seed = random.randint(0, 0xffffffffffffffff) if randomize_seed else seed
            imgs = GoogleAICore.generate_image(
                api_key=key, prompt=prompt, model=model,
                negative_prompt=negative_prompt, aspect_ratio=aspect_ratio, seed=eff_seed,
            )
            if not imgs:
                return io.NodeOutput(GoogleAICore.create_error_image("La API no retornó imágenes."))
            return io.NodeOutput(GoogleAICore.bytes_to_image_tensor(imgs[0]))
        except Exception as e:
            from ..ComfyUI_GoogleAI.google_core import GoogleAICore
            return io.NodeOutput(GoogleAICore.create_error_image(str(e)))


# ═══════════════ GoogleAI_VideoGenerator ══════════════════════════
class GoogleAI_VideoGenerator(io.ComfyNode):
    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id="GoogleAI_VideoGenerator",
            display_name="Google AI - Video Generator (Veo 3.1)",
            category="Google AI/Video",
            inputs=[
                io.String.Input("prompt", multiline=True,
                                default="A cinematic drone shot flying over a mountain range at sunrise"),
                io.Combo.Input("model", options=_VID_MODELS, default="veo-3.1-generate-preview"),
                io.Combo.Input("video_preset", options=_VID_PRESETS, default="1920x1080 (16:9)"),
                io.Combo.Input("duration_seconds", options=_VID_DUR, default="6"),
                io.String.Input("api_key", optional=True, default=""),
                io.Image.Input("init_image_or_video", optional=True,
                               tooltip="1 frame=Img2Vid, >1=Extension (ultimo frame)."),
                io.String.Input("negative_prompt", optional=True, multiline=True, default=""),
            ],
            outputs=[io.Image.Output("video_frames"), io.Audio.Output("audio"),
                     io.String.Output("cost_estimate")],
            is_deprecated=True,
        )

    @classmethod
    def execute(cls, prompt, model, video_preset, duration_seconds, api_key="",
                init_image_or_video=None, negative_prompt="") -> io.NodeOutput:
        try:
            from ..core.keys import gemini_key
            from ..ComfyUI_GoogleAI.google_core import GoogleAICore, _make_dummy_audio
            key = gemini_key(api_key)
            duration = int(duration_seconds)
            cost_str = GoogleAICore.estimate_video_cost(duration)
            dummy = _make_dummy_audio()
            init_b64 = None
            if init_image_or_video is not None:
                nf = init_image_or_video.shape[0]
                init_b64 = [GoogleAICore.tensor_to_base64(init_image_or_video, nf - 1 if nf > 1 else 0)]
            full_prompt = prompt + (f"\n\nNegative: {negative_prompt}" if negative_prompt else "")
            video_bytes = GoogleAICore.run_async_in_thread(
                GoogleAICore.generate_video(api_key=key, prompt=full_prompt, model=model,
                                             resolution_preset=video_preset, duration_seconds=duration,
                                             init_images_b64=init_b64))
            video_tensor = GoogleAICore.video_bytes_to_tensor(video_bytes)
            audio = GoogleAICore.video_bytes_to_audio(video_bytes) if model.startswith("veo-3") else dummy
            return io.NodeOutput(video_tensor, audio, cost_str)
        except Exception as e:
            from ..ComfyUI_GoogleAI.google_core import GoogleAICore, _make_dummy_audio
            return io.NodeOutput(GoogleAICore.create_error_image(str(e)), _make_dummy_audio(),
                                 f"Error - {str(e)[:50]}")


# ═══════════════ GoogleAI_VideoInterpolation ══════════════════════
class GoogleAI_VideoInterpolation(io.ComfyNode):
    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id="GoogleAI_VideoInterpolation",
            display_name="Google AI - Video Interpolation",
            category="Google AI/Video",
            inputs=[
                io.Image.Input("first_frame"),
                io.Image.Input("last_frame",
                               tooltip="Se redimensiona al tamaño del first_frame."),
                io.String.Input("prompt", multiline=True,
                                default="A smooth cinematic transition between two scenes"),
                io.Combo.Input("model", options=_VID_MODELS, default="veo-3.1-generate-preview"),
                io.Combo.Input("video_preset", options=_VID_PRESETS, default="1920x1080 (16:9)"),
                io.Combo.Input("duration_seconds", options=_VID_DUR, default="6"),
                io.String.Input("api_key", optional=True, default=""),
            ],
            outputs=[io.Image.Output("video_frames"), io.Audio.Output("audio"),
                     io.String.Output("cost_estimate")],
            is_deprecated=True,
        )

    @classmethod
    def execute(cls, first_frame, last_frame, prompt, model, video_preset,
                duration_seconds, api_key="") -> io.NodeOutput:
        try:
            from ..core.keys import gemini_key
            from ..ComfyUI_GoogleAI.google_core import GoogleAICore, _make_dummy_audio
            key = gemini_key(api_key)
            duration = int(duration_seconds)
            cost_str = GoogleAICore.estimate_video_cost(duration)
            last_r = GoogleAICore.resize_tensor_to_match(last_frame, first_frame)
            first_b64 = GoogleAICore.tensor_to_base64(first_frame, 0)
            last_b64 = GoogleAICore.tensor_to_base64(last_r, 0)
            video_bytes = GoogleAICore.run_async_in_thread(
                GoogleAICore.generate_video(api_key=key, prompt=prompt, model=model,
                                             resolution_preset=video_preset, duration_seconds=duration,
                                             init_images_b64=[first_b64], last_frame_b64=last_b64))
            video_tensor = GoogleAICore.video_bytes_to_tensor(video_bytes)
            audio = GoogleAICore.video_bytes_to_audio(video_bytes) if model.startswith("veo-3") else _make_dummy_audio()
            return io.NodeOutput(video_tensor, audio, cost_str)
        except Exception as e:
            from ..ComfyUI_GoogleAI.google_core import GoogleAICore, _make_dummy_audio
            return io.NodeOutput(GoogleAICore.create_error_image(str(e)), _make_dummy_audio(), f"Error - {str(e)[:50]}")


# ═══════════════ GoogleAI_VideoStoryboard ═════════════════════════
class GoogleAI_VideoStoryboard(io.ComfyNode):
    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id="GoogleAI_VideoStoryboard",
            display_name="Google AI - Video Storyboard",
            category="Google AI/Video",
            inputs=[
                io.String.Input("prompt", multiline=True,
                                default="A stylized animated scene with vibrant colors"),
                io.Combo.Input("model", options=_VID_MODELS, default="veo-3.1-generate-preview"),
                io.Combo.Input("video_preset", options=_VID_PRESETS, default="1920x1080 (16:9)"),
                io.Combo.Input("duration_seconds", options=_VID_DUR, default="8",
                               tooltip="Se fuerza a 8s con referencias."),
                io.String.Input("api_key", optional=True, default=""),
                io.Image.Input("reference_image_1", optional=True),
                io.Image.Input("reference_image_2", optional=True),
                io.Image.Input("reference_image_3", optional=True),
            ],
            outputs=[io.Image.Output("video_frames"), io.Audio.Output("audio"),
                     io.String.Output("cost_estimate")],
            is_deprecated=True,
        )

    @classmethod
    def execute(cls, prompt, model, video_preset, duration_seconds, api_key="",
                reference_image_1=None, reference_image_2=None,
                reference_image_3=None) -> io.NodeOutput:
        try:
            from ..core.keys import gemini_key
            from ..ComfyUI_GoogleAI.google_core import GoogleAICore, _make_dummy_audio
            key = gemini_key(api_key)
            duration = int(duration_seconds)
            refs_b64 = [GoogleAICore.tensor_to_base64(r, 0)
                        for r in [reference_image_1, reference_image_2, reference_image_3]
                        if r is not None]
            if refs_b64 and duration != 8:
                duration = 8
            cost_str = GoogleAICore.estimate_video_cost(duration)
            video_bytes = GoogleAICore.run_async_in_thread(
                GoogleAICore.generate_video(api_key=key, prompt=prompt, model=model,
                                             resolution_preset=video_preset, duration_seconds=duration,
                                             reference_images_b64=refs_b64 or None))
            video_tensor = GoogleAICore.video_bytes_to_tensor(video_bytes)
            audio = GoogleAICore.video_bytes_to_audio(video_bytes) if model.startswith("veo-3") else _make_dummy_audio()
            return io.NodeOutput(video_tensor, audio, cost_str)
        except Exception as e:
            from ..ComfyUI_GoogleAI.google_core import GoogleAICore, _make_dummy_audio
            return io.NodeOutput(GoogleAICore.create_error_image(str(e)), _make_dummy_audio(), f"Error - {str(e)[:50]}")


# ═══════════════ Diagnostic nodes (8-12) ══════════════════════════
def _diag_exec(api_key, model, prompt_text):
    from ..ComfyUI_GoogleAI.google_core import GoogleAICore
    key = _gemini_key(api_key)
    return GoogleAICore.call_gemini_text(api_key=key, prompt=prompt_text, model=model)


class GoogleAI_ModelArchitectureDetector(io.ComfyNode):
    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id="GoogleAI_ModelArchitectureDetector",
            display_name="Google AI - Architecture Detector",
            category="Google AI/Diagnostic",
            inputs=[
                io.String.Input("safetensors_path", default=""),
                io.String.Input("api_key", optional=True, default=""),
                io.Combo.Input("model", options=_DIAG_MODELS, optional=True,
                               default="gemini-3.1-pro-preview"),
            ],
            outputs=[io.String.Output("architecture_report")],
            is_deprecated=True,
        )

    @classmethod
    def execute(cls, safetensors_path, api_key="", model="gemini-3.1-pro-preview") -> io.NodeOutput:
        try:
            import os
            from ..ComfyUI_GoogleAI.google_core import SYSTEM_PROMPT_ARCHITECTURE_DETECTOR
            if not os.path.isfile(safetensors_path):
                return io.NodeOutput(f"❌ Archivo no encontrado: {safetensors_path}")
            from safetensors import safe_open
            with safe_open(safetensors_path, framework="pt", device="cpu") as f:
                keys = list(f.keys())
            sample = keys[:200] + ["... (truncado) ..."] + keys[-50:] if len(keys) > 250 else keys
            prompt = f"Archivo: {os.path.basename(safetensors_path)}\nTotal tensores: {len(keys)}\n\nKeys:\n" + "\n".join(sample)
            return io.NodeOutput(_diag_exec(api_key, model, prompt))
        except Exception as e:
            return io.NodeOutput(f"❌ Error: {str(e)}")


class GoogleAI_TriggerWordExtractor(io.ComfyNode):
    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id="GoogleAI_TriggerWordExtractor",
            display_name="Google AI - Trigger Word Extractor",
            category="Google AI/Diagnostic",
            inputs=[
                io.String.Input("lora_path", default=""),
                io.String.Input("api_key", optional=True, default=""),
                io.Combo.Input("model", options=_DIAG_MODELS, optional=True, default="gemini-2.5-flash"),
            ],
            outputs=[io.String.Output("trigger_words")],
            is_deprecated=True,
        )

    @classmethod
    def execute(cls, lora_path, api_key="", model="gemini-2.5-flash") -> io.NodeOutput:
        try:
            import os, json
            from ..ComfyUI_GoogleAI.google_core import SYSTEM_PROMPT_TRIGGER_EXTRACTOR
            from safetensors import safe_open
            with safe_open(lora_path, framework="pt", device="cpu") as f:
                metadata = f.metadata() or {}
            tag_freq_raw = metadata.get("ss_tag_frequency", "")
            if not tag_freq_raw:
                return io.NodeOutput(f"⚠️ No se encontró ss_tag_frequency.")
            try:
                tag_freq = json.loads(tag_freq_raw) if isinstance(tag_freq_raw, str) else tag_freq_raw
            except Exception:
                tag_freq = tag_freq_raw
            prompt = f"LoRA: {os.path.basename(lora_path)}\n\nss_tag_frequency:\n{json.dumps(tag_freq, indent=2, ensure_ascii=False)[:8000]}"
            return io.NodeOutput(_diag_exec(api_key, model, prompt))
        except Exception as e:
            return io.NodeOutput(f"❌ Error: {str(e)}")


class GoogleAI_WorkflowAnalyzer(io.ComfyNode):
    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id="GoogleAI_WorkflowAnalyzer",
            display_name="Google AI - Workflow Analyzer",
            category="Google AI/Diagnostic",
            inputs=[
                io.String.Input("workflow_json", multiline=True, default="",
                                tooltip="JSON del workflow o ruta al archivo .json."),
                io.String.Input("api_key", optional=True, default=""),
                io.Combo.Input("model", options=_DIAG_MODELS, optional=True,
                               default="gemini-3.1-pro-preview"),
            ],
            outputs=[io.String.Output("analysis_report")],
            is_deprecated=True,
        )

    @classmethod
    def execute(cls, workflow_json, api_key="", model="gemini-3.1-pro-preview") -> io.NodeOutput:
        try:
            import os, json
            if os.path.isfile(workflow_json.strip()):
                with open(workflow_json.strip(), "r", encoding="utf-8") as f:
                    data = json.load(f)
            else:
                data = json.loads(workflow_json)
            class_types = set()
            if isinstance(data, dict):
                for nid, nd in data.items():
                    if isinstance(nd, dict) and "class_type" in nd:
                        class_types.add(nd["class_type"])
                for node in data.get("nodes", []):
                    if isinstance(node, dict):
                        ct = node.get("type", node.get("class_type", ""))
                        if ct:
                            class_types.add(ct)
            if not class_types:
                return io.NodeOutput("⚠️ No se encontraron class_type en el JSON.")
            prompt = f"Nodos ({len(class_types)} tipos):\n\n" + "\n".join(f"- {ct}" for ct in sorted(class_types))
            return io.NodeOutput(_diag_exec(api_key, model, prompt))
        except Exception as e:
            return io.NodeOutput(f"❌ Error: {str(e)}")


class GoogleAI_CompatibilityChecker(io.ComfyNode):
    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id="GoogleAI_CompatibilityChecker",
            display_name="Google AI - Compatibility Checker",
            category="Google AI/Diagnostic",
            inputs=[
                io.String.Input("checkpoint_path", default=""),
                io.String.Input("lora_path", default=""),
                io.String.Input("api_key", optional=True, default=""),
                io.Combo.Input("model", options=_DIAG_MODELS, optional=True, default="gemini-2.5-flash"),
            ],
            outputs=[io.Boolean.Output("is_compatible"), io.String.Output("compatibility_report")],
            is_deprecated=True,
        )

    @classmethod
    def execute(cls, checkpoint_path, lora_path, api_key="", model="gemini-2.5-flash") -> io.NodeOutput:
        try:
            import os, json
            from safetensors import safe_open
            from ..ComfyUI_GoogleAI.google_core import SYSTEM_PROMPT_COMPATIBILITY_CHECKER
            for path, name in [(checkpoint_path, "Checkpoint"), (lora_path, "LoRA")]:
                if not os.path.isfile(path):
                    return io.NodeOutput(False, f"❌ {name} no encontrado: {path}")
            def _info(p):
                d = {"keys": [], "dims": {}}
                with safe_open(p, framework="pt", device="cpu") as f:
                    d["keys"] = list(f.keys())[:150]
                return d
            ci = _info(checkpoint_path)
            li = _info(lora_path)
            prompt = (f"**Checkpoint:** {os.path.basename(checkpoint_path)}\nKeys:\n" +
                      "\n".join(ci["keys"][:100]) + f"\n\n**LoRA:** {os.path.basename(lora_path)}\nKeys:\n" +
                      "\n".join(li["keys"][:100]) + "\n\nResponde empezando con 'COMPATIBLE: Sí' o 'COMPATIBLE: No'.")
            result = _diag_exec(api_key, model, prompt)
            return io.NodeOutput("compatible: sí" in result.lower(), result)
        except Exception as e:
            return io.NodeOutput(False, f"❌ Error: {str(e)}")


class GoogleAI_LoRATrainingAnalyzer(io.ComfyNode):
    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id="GoogleAI_LoRATrainingAnalyzer",
            display_name="Google AI - Training Analyzer",
            category="Google AI/Diagnostic",
            inputs=[
                io.String.Input("training_logs", multiline=True, default="",
                                tooltip="CSV/JSON de loss, o ruta al archivo."),
                io.String.Input("api_key", optional=True, default=""),
                io.Combo.Input("model", options=_DIAG_MODELS, optional=True,
                               default="gemini-3.1-pro-preview"),
            ],
            outputs=[io.String.Output("diagnosis_report")],
            is_deprecated=True,
        )

    @classmethod
    def execute(cls, training_logs, api_key="", model="gemini-3.1-pro-preview") -> io.NodeOutput:
        try:
            import os, json, csv, io as sio
            log_data = training_logs
            if os.path.isfile(training_logs.strip()):
                fp = training_logs.strip()
                with open(fp, encoding="utf-8") as f:
                    raw = f.read()
                log_data = raw[:10000]
            prompt = f"Datos de entrenamiento:\n\n{log_data}\n\nAnaliza overfitting."
            return io.NodeOutput(_diag_exec(api_key, model, prompt))
        except Exception as e:
            return io.NodeOutput(f"❌ Error: {str(e)}")


# ═══════════════ PMS_GeminiTTS ════════════════════════════════════
class PMS_GeminiTTS(io.ComfyNode):
    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id="PMS_GeminiTTS",
            display_name="Gemini Text to Speech (PMS)",
            category="PromptModels/Google",
            inputs=[
                io.String.Input("text", multiline=True,
                                default="Hola, soy Gemini. Encantado de hablar contigo."),
                io.String.Input("voice_name", optional=True, default="Aoede",
                                tooltip="Nombre de voz: Aoede, Charon, Fenrir, Kore, Puck."),
                io.String.Input("language_code", optional=True, default="es-419",
                                tooltip="Código BCP-47. ej: es-419, en-US, fr-FR."),
                io.String.Input("api_key", optional=True, default=""),
            ],
            outputs=[io.Audio.Output("audio")],
            is_deprecated=True,
        )

    @classmethod
    def execute(cls, text, voice_name="Aoede", language_code="es-419",
                api_key="") -> io.NodeOutput:
        try:
            from ..core.keys import gemini_key
            from ..ComfyUI_GoogleAI.google_tts_node import PMS_GeminiTTS as V1
            key = gemini_key(api_key)
            result = V1().sintetizar(text=text, voice_name=voice_name,
                                     language_code=language_code, api_key=key)
            return io.NodeOutput(*result)
        except Exception as e:
            import torch
            silence = {"waveform": torch.zeros((1, 1, 24000)), "sample_rate": 24000}
            return io.NodeOutput(silence)
