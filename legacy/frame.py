from comfy_api.latest import io


class GetLastFrame(io.ComfyNode):
    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id="GetLastFrame",
            display_name="Get Last Frame",
            category="🧩 Utility",
            inputs=[io.Image.Input("frames")],
            outputs=[io.Image.Output("image")],
            is_deprecated=True,
        )

    @classmethod
    def execute(cls, frames) -> io.NodeOutput:
        if frames is None or len(frames) == 0:
            raise ValueError("El input 'frames' está vacío.")
        return io.NodeOutput(frames[-1:, :, :, :])


class GetFrameByIndex(io.ComfyNode):
    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id="GetFrameByIndex",
            display_name="Get Frame by Index",
            category="🧩 Utility",
            inputs=[
                io.Image.Input("frames"),
                io.Int.Input("index", default=-1, min=-9999, max=9999, step=1),
            ],
            outputs=[io.Image.Output("image")],
            is_deprecated=True,
        )

    @classmethod
    def execute(cls, frames, index=-1) -> io.NodeOutput:
        if frames is None or len(frames) == 0:
            raise ValueError("El input 'frames' está vacío.")
        total = len(frames)
        if index >= total:
            index = total - 1
        elif index < -total:
            index = 0
        selected = frames[index:index+1, :, :, :] if index >= 0 else frames[index:, :, :, :][:1]
        return io.NodeOutput(selected)
