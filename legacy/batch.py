from comfy_api.latest import io


class PMS_DualPromptListBatch(io.ComfyNode):
    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id="PMS_DualPromptListBatch",
            display_name="Dual Prompt List Batch (PMS)",
            category="PromptModels/batch",
            inputs=[
                io.String.Input("voice_prompts", multiline=True,
                                default="Texto narracion 1\n---\nTexto narracion 2\n---\nTexto narracion 3"),
                io.String.Input("visual_prompts", multiline=True,
                                default="Descripcion visual 1\n---\nDescripcion visual 2\n---\nDescripcion visual 3"),
                io.String.Input("separator", default="---"),
                io.Int.Input("max_scenes", default=5, min=1, max=50),
            ],
            outputs=[
                io.String.Output("voice_prompt", is_output_list=True),
                io.String.Output("visual_prompt", is_output_list=True),
                io.Int.Output("index", is_output_list=True),
                io.String.Output("index_str", is_output_list=True),
            ],
            is_deprecated=True,
        )

    @classmethod
    def execute(cls, voice_prompts, visual_prompts, separator, max_scenes) -> io.NodeOutput:
        voices = [p.strip() for p in voice_prompts.split(separator) if p.strip()]
        visuals = [p.strip() for p in visual_prompts.split(separator) if p.strip()]
        n = min(len(voices), len(visuals), max_scenes)
        if n == 0:
            raise ValueError("[PMS_Batch] No hay escenas válidas. Revisa separator y prompts.")
        voices = voices[:n]
        visuals = visuals[:n]
        indices = list(range(n))
        idx_strs = [f"{i:03d}" for i in indices]
        return io.NodeOutput(voices, visuals, indices, idx_strs)


class PMS_VideoBatchConcat(io.ComfyNode):
    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id="PMS_VideoBatchConcat",
            display_name="Video Batch Concat (PMS)",
            category="PromptModels/batch",
            inputs=[
                io.Image.Input("images"),
                io.Audio.Input("audio"),
                io.Int.Input("silence_ms", default=0, min=0, max=5000, step=50),
            ],
            outputs=[
                io.Image.Output("images"),
                io.Audio.Output("audio"),
                io.Int.Output("total_frames"),
            ],
            is_input_list=True,
            is_deprecated=True,
        )

    @classmethod
    def execute(cls, images, audio, silence_ms) -> io.NodeOutput:
        import torch
        silence_ms = silence_ms[0] if isinstance(silence_ms, list) else silence_ms
        if not images or not audio:
            raise ValueError("[PMS_VideoBatchConcat] listas vacías")
        ref_shape = images[0].shape[1:]
        for i, img in enumerate(images):
            if img.shape[1:] != ref_shape:
                raise ValueError(f"[PMS_VideoBatchConcat] Escena {i}: shape incompatible")
        all_images = torch.cat(images, dim=0)
        sr = audio[0]["sample_rate"]
        waveforms = [a["waveform"] for a in audio]
        if silence_ms > 0 and len(waveforms) > 1:
            n_samples = int(sr * silence_ms / 1000)
            ref_w = waveforms[0]
            silence = torch.zeros((ref_w.shape[0], ref_w.shape[1], n_samples),
                                  dtype=ref_w.dtype, device=ref_w.device)
            interleaved = []
            for i, w in enumerate(waveforms):
                interleaved.append(w)
                if i < len(waveforms) - 1:
                    interleaved.append(silence)
            waveforms = interleaved
        full_wav = torch.cat(waveforms, dim=-1)
        merged_audio = {"waveform": full_wav, "sample_rate": sr}
        return io.NodeOutput(all_images, merged_audio, all_images.shape[0])
