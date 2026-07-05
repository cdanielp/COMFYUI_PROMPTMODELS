import re
from comfy_api.latest import io


class DivisorDePrompts(io.ComfyNode):
    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id="DivisorDePrompts",
            display_name="DivisorDePrompts (10)",
            category="Prompt Tools",
            inputs=[
                io.String.Input("full_text", multiline=True, default="",
                                tooltip="Pega tus prompts aquí, separados por líneas vacías..."),
                io.Boolean.Input("trim_mode", optional=True, default=True,
                                 label_on="Limpiar espacios", label_off="Mantener espacios"),
                io.Boolean.Input("preserve_newlines", optional=True, default=True,
                                 label_on="Mantener saltos internos", label_off="Colapsar a una línea"),
            ],
            outputs=[
                io.String.Output("prompt_01"), io.String.Output("prompt_02"),
                io.String.Output("prompt_03"), io.String.Output("prompt_04"),
                io.String.Output("prompt_05"), io.String.Output("prompt_06"),
                io.String.Output("prompt_07"), io.String.Output("prompt_08"),
                io.String.Output("prompt_09"), io.String.Output("prompt_10"),
                io.Int.Output("count"),
            ],
            is_deprecated=True,
        )

    @classmethod
    def execute(cls, full_text, trim_mode=True, preserve_newlines=True) -> io.NodeOutput:
        outputs = [""] * 10
        if not full_text or not full_text.strip():
            return io.NodeOutput(*outputs, 0)
        text = full_text.replace("\r\n", "\n").replace("\r", "\n")
        blocks = re.split(r'\n(?:[ \t]*\n)+', text)
        prompts = []
        for block in blocks:
            if trim_mode:
                block = block.strip()
            if not block:
                continue
            if not preserve_newlines:
                block = re.sub(r'\s+', ' ', block).strip()
            prompts.append(block)
        prompts = prompts[:10]
        for i, p in enumerate(prompts):
            outputs[i] = p
        return io.NodeOutput(*outputs, len(prompts))
