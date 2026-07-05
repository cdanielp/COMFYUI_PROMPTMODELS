from comfy_api.latest import io

# ─────────────────── PRO_SetNode ───────────────────────────────────
def _set_node_inputs():
    # Orden exacto V1: MODEL,CLIP,VAE,CONTROL_NET,CLIP_VISION,STYLE_MODEL,
    # UPSCALE_MODEL,LATENT,IMAGE,MASK,CONDITIONING,SAMPLER,SIGMAS,NOISE,GUIDER,*
    return [
        io.Model.Input("MODEL", optional=True),
        io.Clip.Input("CLIP", optional=True),
        io.Vae.Input("VAE", optional=True),
        io.ControlNet.Input("CONTROL_NET", optional=True),
        io.ClipVision.Input("CLIP_VISION", optional=True),
        io.StyleModel.Input("STYLE_MODEL", optional=True),
        io.UpscaleModel.Input("UPSCALE_MODEL", optional=True),
        io.Latent.Input("LATENT", optional=True),
        io.Image.Input("IMAGE", optional=True),
        io.Mask.Input("MASK", optional=True),
        io.Conditioning.Input("CONDITIONING", optional=True),
        io.Sampler.Input("SAMPLER", optional=True),
        io.Sigmas.Input("SIGMAS", optional=True),
        io.Noise.Input("NOISE", optional=True),
        io.Guider.Input("GUIDER", optional=True),
        io.AnyType.Input("star", optional=True),
    ]


class PRO_SetNode(io.ComfyNode):
    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id="PRO_SetNode",
            display_name="📦 PRO Set Node",
            category="GetSetNode_Pro/utils",
            inputs=_set_node_inputs(),
            hidden=[io.Hidden.unique_id, io.Hidden.prompt, io.Hidden.extra_pnginfo],
            outputs=[io.AnyType.Output("star")],
            is_output_node=True,
            is_deprecated=True,
        )

    @classmethod
    def execute(cls, unique_id=None, prompt=None, extra_pnginfo=None,
                MODEL=None, CLIP=None, VAE=None, CONTROL_NET=None, CLIP_VISION=None,
                STYLE_MODEL=None, UPSCALE_MODEL=None, LATENT=None, IMAGE=None,
                MASK=None, CONDITIONING=None, SAMPLER=None, SIGMAS=None, NOISE=None,
                GUIDER=None, star=None) -> io.NodeOutput:
        try:
            from ..GETSETNODE_PRO.setget_nodes import PRO_SetNode as V1
            instance = V1()
            kwargs = {"unique_id": unique_id, "prompt": prompt, "extra_pnginfo": extra_pnginfo}
            for name, val in [("MODEL",MODEL),("CLIP",CLIP),("VAE",VAE),
                               ("CONTROL_NET",CONTROL_NET),("CLIP_VISION",CLIP_VISION),
                               ("STYLE_MODEL",STYLE_MODEL),("UPSCALE_MODEL",UPSCALE_MODEL),
                               ("LATENT",LATENT),("IMAGE",IMAGE),("MASK",MASK),
                               ("CONDITIONING",CONDITIONING),("SAMPLER",SAMPLER),
                               ("SIGMAS",SIGMAS),("NOISE",NOISE),("GUIDER",GUIDER),
                               ("*",star)]:
                if val is not None:
                    kwargs[name] = val
            result = instance.set_value(**kwargs)
            return io.NodeOutput(*result)
        except Exception as e:
            return io.NodeOutput(None)


# ─────────────────── PRO_GetNode ───────────────────────────────────
class PRO_GetNode(io.ComfyNode):
    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id="PRO_GetNode",
            display_name="📤 PRO Get Node",
            category="GetSetNode_Pro/utils",
            inputs=[io.String.Input("name", optional=True, default="my_variable")],
            hidden=[io.Hidden.unique_id, io.Hidden.prompt, io.Hidden.extra_pnginfo],
            outputs=[io.AnyType.Output("star")],
            is_deprecated=True,
        )

    @classmethod
    def execute(cls, name="my_variable", unique_id=None, prompt=None,
                extra_pnginfo=None) -> io.NodeOutput:
        from ..GETSETNODE_PRO.setget_nodes import PRO_GetNode as V1
        instance = V1()
        result = instance.get_value(name=name, unique_id=unique_id,
                                    prompt=prompt, extra_pnginfo=extra_pnginfo)
        return io.NodeOutput(*result)


# ─────────────────── PRO_SetNodeNamed ──────────────────────────────
class PRO_SetNodeNamed(io.ComfyNode):
    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id="PRO_SetNodeNamed",
            display_name="📦 PRO Set Node (Named)",
            category="GetSetNode_Pro/utils",
            inputs=[
                io.AnyType.Input("value"),
                io.String.Input("name", default="my_variable"),
            ],
            outputs=[io.AnyType.Output("value")],
            is_output_node=True,
            is_deprecated=True,
        )

    @classmethod
    def execute(cls, value, name) -> io.NodeOutput:
        from ..GETSETNODE_PRO.setget_nodes import PRO_SetNodeNamed as V1
        instance = V1()
        result = instance.set_value(value=value, name=name)
        return io.NodeOutput(*result)


# ─────────────────── PRO_ListCacheNode ─────────────────────────────
class PRO_ListCacheNode(io.ComfyNode):
    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id="PRO_ListCacheNode",
            display_name="📋 PRO List Cache",
            category="GetSetNode_Pro/utils",
            inputs=[io.AnyType.Input("trigger", optional=True)],
            outputs=[io.String.Output("info")],
            is_deprecated=True,
        )

    @classmethod
    def execute(cls, trigger=None) -> io.NodeOutput:
        from ..GETSETNODE_PRO.setget_nodes import PRO_ListCacheNode as V1
        result = V1().list_cache(trigger=trigger)
        return io.NodeOutput(*result)


# ─────────────────── PRO_ClearCacheNode ────────────────────────────
class PRO_ClearCacheNode(io.ComfyNode):
    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id="PRO_ClearCacheNode",
            display_name="🗑️ PRO Clear Cache",
            category="GetSetNode_Pro/utils",
            inputs=[io.Boolean.Input("confirm", default=False)],
            outputs=[io.String.Output("status")],
            is_output_node=True,
            is_deprecated=True,
        )

    @classmethod
    def execute(cls, confirm=False) -> io.NodeOutput:
        from ..GETSETNODE_PRO.setget_nodes import PRO_ClearCacheNode as V1
        result = V1().clear_cache(confirm=confirm)
        return io.NodeOutput(*result)


# ─────────────────── PRO_UnetLoaderGGUF ────────────────────────────
class PRO_UnetLoaderGGUF(io.ComfyNode):
    @classmethod
    def define_schema(cls) -> io.Schema:
        try:
            from ..GETSETNODE_PRO.unet_loader_gguf import get_unet_files
            opts = get_unet_files()
        except Exception:
            opts = ["none"]
        return io.Schema(
            node_id="PRO_UnetLoaderGGUF",
            display_name="🧠 PRO Unet Loader GGUF",
            category="GetSetNode_Pro/loaders",
            inputs=[io.Combo.Input("unet_name", options=opts,
                                   tooltip="Modelo GGUF")],
            outputs=[io.Model.Output("model")],
            is_deprecated=True,
        )

    @classmethod
    def execute(cls, unet_name) -> io.NodeOutput:
        from ..GETSETNODE_PRO.unet_loader_gguf import PRO_UnetLoaderGGUF as V1
        result = V1().load_unet(unet_name)
        return io.NodeOutput(*result)


# ─────────────────── PRO_UnetLoaderGGUFAdvanced ────────────────────
class PRO_UnetLoaderGGUFAdvanced(io.ComfyNode):
    @classmethod
    def define_schema(cls) -> io.Schema:
        try:
            from ..GETSETNODE_PRO.unet_loader_gguf import get_unet_files
            opts = get_unet_files()
        except Exception:
            opts = ["none"]
        return io.Schema(
            node_id="PRO_UnetLoaderGGUFAdvanced",
            display_name="🧠 PRO Unet Loader GGUF+",
            category="GetSetNode_Pro/loaders",
            inputs=[
                io.Combo.Input("unet_name", options=opts),
                io.Combo.Input("dtype", options=["auto","float32","float16","bfloat16"],
                               optional=True, default="auto"),
                io.Boolean.Input("force_cpu", optional=True, default=False),
            ],
            outputs=[
                io.Model.Output("model"),
                io.String.Output("info"),
            ],
            is_deprecated=True,
        )

    @classmethod
    def execute(cls, unet_name, dtype="auto", force_cpu=False) -> io.NodeOutput:
        from ..GETSETNODE_PRO.unet_loader_gguf import PRO_UnetLoaderGGUFAdvanced as V1
        result = V1().load_unet_advanced(unet_name, dtype=dtype, force_cpu=force_cpu)
        return io.NodeOutput(*result)
