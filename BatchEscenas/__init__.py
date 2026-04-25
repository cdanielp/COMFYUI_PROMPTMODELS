"""
BatchEscenas - Sub-módulo de PROMPTMODELS
Batch secuencial para pipelines de voz+video.
"""
import torch


class PMS_DualPromptListBatch:
    """
    Recibe 2 textareas paralelos (voz + visual) separados por '---'.
    Emite listas: ComfyUI ejecuta el workflow downstream 1 vez por escena.
    Combinar con PMS_VideoBatchConcat para cerrar el batch.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "voice_prompts": ("STRING", {
                    "multiline": True,
                    "default": "Texto narracion 1\n---\nTexto narracion 2\n---\nTexto narracion 3"
                }),
                "visual_prompts": ("STRING", {
                    "multiline": True,
                    "default": "Descripcion visual 1\n---\nDescripcion visual 2\n---\nDescripcion visual 3"
                }),
                "separator": ("STRING", {"default": "---"}),
                "max_scenes": ("INT", {"default": 5, "min": 1, "max": 50}),
            }
        }

    RETURN_TYPES = ("STRING", "STRING", "INT", "STRING")
    RETURN_NAMES = ("voice_prompt", "visual_prompt", "index", "index_str")
    OUTPUT_IS_LIST = (True, True, True, True)
    FUNCTION = "split"
    CATEGORY = "PromptModels/batch"

    def split(self, voice_prompts, visual_prompts, separator, max_scenes):
        voices = [p.strip() for p in voice_prompts.split(separator) if p.strip()]
        visuals = [p.strip() for p in visual_prompts.split(separator) if p.strip()]

        if len(voices) != len(visuals):
            print(f"[PMS_Batch] WARN: voices={len(voices)} visuals={len(visuals)}, usando el menor")

        n = min(len(voices), len(visuals))
        if n > max_scenes:
            print(f"[PMS_Batch] WARN: {n} escenas detectadas, procesando solo {max_scenes} (max_scenes={max_scenes})")
            n = max_scenes

        if n == 0:
            raise ValueError("[PMS_Batch] No hay escenas validas. Revisa separator y prompts.")

        voices = voices[:n]
        visuals = visuals[:n]
        indices = list(range(n))
        idx_strs = [f"{i:03d}" for i in indices]

        print(f"[PMS_Batch] procesando {n} escena(s)")
        return (voices, visuals, indices, idx_strs)


class PMS_VideoBatchConcat:
    """
    Recibe listas de IMAGE y AUDIO (output del batch).
    Concatena en 1 IMAGE batch + 1 AUDIO continuo. Cierre del fan-out.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "images": ("IMAGE",),
                "audio": ("AUDIO",),
                "silence_ms": ("INT", {"default": 0, "min": 0, "max": 5000, "step": 50}),
            }
        }

    RETURN_TYPES = ("IMAGE", "AUDIO", "INT")
    RETURN_NAMES = ("images", "audio", "total_frames")
    INPUT_IS_LIST = True
    FUNCTION = "concat"
    CATEGORY = "PromptModels/batch"

    def concat(self, images, audio, silence_ms):
        silence_ms = silence_ms[0] if isinstance(silence_ms, list) else silence_ms

        if not images or not audio:
            raise ValueError("[PMS_VideoBatchConcat] listas vacias")
        if len(images) != len(audio):
            print(f"[PMS_VideoBatchConcat] WARN: images={len(images)} audio={len(audio)}")

        ref_shape = images[0].shape[1:]
        for i, img in enumerate(images):
            if img.shape[1:] != ref_shape:
                raise ValueError(
                    f"[PMS_VideoBatchConcat] Escena {i}: shape {tuple(img.shape[1:])} "
                    f"!= ref {tuple(ref_shape)}. Todas las escenas deben tener misma H/W/C."
                )
        all_images = torch.cat(images, dim=0)

        sr = audio[0]["sample_rate"]
        for i, a in enumerate(audio):
            if a["sample_rate"] != sr:
                raise ValueError(f"[PMS_VideoBatchConcat] Escena {i}: sample_rate {a['sample_rate']} != {sr}")

        waveforms = [a["waveform"] for a in audio]

        if silence_ms > 0 and len(waveforms) > 1:
            n_samples = int(sr * silence_ms / 1000)
            ref_w = waveforms[0]
            silence = torch.zeros(
                (ref_w.shape[0], ref_w.shape[1], n_samples),
                dtype=ref_w.dtype, device=ref_w.device,
            )
            interleaved = []
            for i, w in enumerate(waveforms):
                interleaved.append(w)
                if i < len(waveforms) - 1:
                    interleaved.append(silence)
            waveforms = interleaved

        full_wav = torch.cat(waveforms, dim=-1)
        merged_audio = {"waveform": full_wav, "sample_rate": sr}
        total_frames = all_images.shape[0]

        print(f"[PMS_VideoBatchConcat] {len(images)} escenas -> {total_frames} frames + {full_wav.shape[-1]/sr:.2f}s audio")
        return (all_images, merged_audio, total_frames)


NODE_CLASS_MAPPINGS = {
    "PMS_DualPromptListBatch": PMS_DualPromptListBatch,
    "PMS_VideoBatchConcat": PMS_VideoBatchConcat,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "PMS_DualPromptListBatch": "Dual Prompt List Batch (PMS)",
    "PMS_VideoBatchConcat": "Video Batch Concat (PMS)",
}

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]
