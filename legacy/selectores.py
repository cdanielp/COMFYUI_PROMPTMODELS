from comfy_api.latest import io

_N = 12  # slots

# ─────────────────────── SelectorDeImagenes ────────────────────────
def _selector_img_inputs():
    # required: fallback, mode, on1-on12 (widget order preserved)
    # optional: img1-img12, mask1-mask12 (link slots after)
    inputs = [
        io.Combo.Input("fallback", options=["error", "slot1"], default="slot1"),
        io.Combo.Input("mode", options=["auto", "single_only", "batch_only"], default="auto"),
    ]
    for i in range(1, _N + 1):
        inputs.append(io.Boolean.Input(f"on{i}", default=(i == 1)))
    for i in range(1, _N + 1):
        inputs.append(io.Image.Input(f"img{i}", optional=True))
        inputs.append(io.Mask.Input(f"mask{i}", optional=True))
    return inputs


class SelectorDeImagenes(io.ComfyNode):
    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id="SelectorDeImagenes",
            display_name="Selector de imágenes",
            category="Selectores Pro",
            inputs=_selector_img_inputs(),
            outputs=[io.Image.Output("image"), io.Mask.Output("mask")],
            is_deprecated=True,
        )

    @classmethod
    def execute(cls, fallback, mode, **kwargs) -> io.NodeOutput:
        import torch
        active = []
        for i in range(1, _N + 1):
            if kwargs.get(f"on{i}", False):
                img = kwargs.get(f"img{i}")
                mask = kwargs.get(f"mask{i}")
                if img is None:
                    raise ValueError(f"Slot {i} activado pero sin imagen conectada.")
                if mask is None:
                    raise ValueError(f"Slot {i} activado pero sin máscara conectada.")
                active.append((i, img, mask))
        if not active:
            if fallback == "error":
                raise ValueError("Ningún slot activado.")
            img1 = kwargs.get("img1")
            mask1 = kwargs.get("mask1")
            if img1 is None or mask1 is None:
                raise ValueError("Fallback a slot1 pero no tiene imagen/máscara.")
            return io.NodeOutput(img1, mask1)
        if mode == "single_only" and len(active) > 1:
            raise ValueError(f"Modo single_only con {len(active)} slots activos.")
        if len(active) == 1:
            _, img, mask = active[0]
            if img.dim() == 3:
                img = img.unsqueeze(0)
            if mask.dim() == 2:
                mask = mask.unsqueeze(0)
            return io.NodeOutput(img, mask)
        images, masks = [], []
        ref_h, ref_w, ref_c = active[0][1].shape[1], active[0][1].shape[2], active[0][1].shape[3]
        for idx, img, mask in active:
            if img.dim() == 3:
                img = img.unsqueeze(0)
            if mask.dim() == 2:
                mask = mask.unsqueeze(0)
            if img.shape[1:] != (ref_h, ref_w, ref_c):
                raise ValueError(f"Imagen slot {idx}: shape incompatible.")
            images.append(img)
            masks.append(mask)
        return io.NodeOutput(torch.cat(images, dim=0), torch.cat(masks, dim=0))


# ─────────────────────── SelectorDePrompts ─────────────────────────
_SEP_OPTS = ["\\n\\n", "\\n", "|", ","]
_SEP_MAP = {"\\n\\n": "\n\n", "\\n": "\n", "|": " | ", ",": ", "}


def _selector_prompts_inputs():
    inputs = [
        io.Combo.Input("fallback", options=["error", "p1"], default="p1"),
        io.Combo.Input("join_with", options=_SEP_OPTS, default="\\n\\n"),
        io.Combo.Input("mode", options=["auto", "single_only", "join_only"], default="auto"),
    ]
    for i in range(1, _N + 1):
        inputs.append(io.Boolean.Input(f"on{i}", default=(i == 1)))
    for i in range(1, _N + 1):
        inputs.append(io.String.Input(f"p{i}", optional=True, multiline=True, default=""))
    return inputs


class SelectorDePrompts(io.ComfyNode):
    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id="SelectorDePrompts",
            display_name="Selector de Prompts",
            category="Selectores Pro",
            inputs=_selector_prompts_inputs(),
            outputs=[io.String.Output("text")],
            is_deprecated=True,
        )

    @classmethod
    def execute(cls, fallback, join_with, mode, **kwargs) -> io.NodeOutput:
        sep = _SEP_MAP.get(join_with, "\n\n")
        active = []
        for i in range(1, _N + 1):
            if kwargs.get(f"on{i}", False):
                txt = (kwargs.get(f"p{i}") or "").strip()
                if txt:
                    active.append((i, txt))
        if not active:
            if fallback == "error":
                raise ValueError("Ningún prompt activo o todos vacíos.")
            return io.NodeOutput((kwargs.get("p1") or "").strip())
        if mode == "single_only" and len(active) > 1:
            raise ValueError(f"Modo single_only con {len(active)} prompts activos.")
        if len(active) == 1:
            return io.NodeOutput(active[0][1])
        return io.NodeOutput(sep.join(t for _, t in active))


# ─────────────────────── ImagenLatentePro ──────────────────────────
_SIZE_PRESETS = {
    "256×256 (1:1) - Test":(256,256),"208×256 (4:5) - Test":(208,256),
    "192×256 (3:4) - Test":(192,256),"168×256 (2:3) - Test":(168,256),
    "144×256 (9:16) - Test":(144,256),"256×144 (16:9) - Test":(256,144),
    "256×168 (3:2) - Test":(256,168),"256×128 (2:1) - Test":(256,128),
    "256×112 (21:9) - Test":(256,112),
    "512×512 (1:1) - Medio":(512,512),"408×512 (4:5) - Medio":(408,512),
    "384×512 (3:4) - Medio":(384,512),"344×512 (2:3) - Medio":(344,512),
    "288×512 (9:16) - Medio":(288,512),"512×288 (16:9) - Medio":(512,288),
    "512×344 (3:2) - Medio":(512,344),"512×256 (2:1) - Medio":(512,256),
    "512×216 (21:9) - Medio":(512,216),
    "1024×1024 (1:1) - Grande":(1024,1024),"816×1024 (4:5) - Grande":(816,1024),
    "768×1024 (3:4) - Grande":(768,1024),"680×1024 (2:3) - Grande":(680,1024),
    "576×1024 (9:16) - Grande":(576,1024),"1024×576 (16:9) - Grande":(1024,576),
    "1024×680 (3:2) - Grande":(1024,680),"1024×512 (2:1) - Grande":(1024,512),
    "1024×440 (21:9) - Grande":(1024,440),
    "720×1280 (9:16) - Social":(720,1280),"1280×720 (16:9) - Social":(1280,720),
}


class ImagenLatentePro(io.ComfyNode):
    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id="ImagenLatentePro",
            display_name="Imagen latente Pro",
            category="Selectores Pro",
            inputs=[
                io.Combo.Input("size_preset", options=list(_SIZE_PRESETS.keys()),
                               default="512×512 (1:1) - Medio"),
                io.Int.Input("batch_size", default=1, min=1, max=64),
                io.Combo.Input("rounding", options=["auto_round", "strict"], default="auto_round"),
            ],
            outputs=[io.Latent.Output("latent")],
            is_deprecated=True,
        )

    @classmethod
    def execute(cls, size_preset, batch_size, rounding) -> io.NodeOutput:
        import torch
        w, h = _SIZE_PRESETS[size_preset]
        if rounding == "auto_round":
            w = ((w + 4) // 8) * 8
            h = ((h + 4) // 8) * 8
        elif (w % 8 != 0 or h % 8 != 0):
            raise ValueError(f"Resolución {w}x{h} no es múltiplo de 8 en modo strict.")
        latent = torch.zeros([batch_size, 4, h // 8, w // 8], dtype=torch.float32)
        return io.NodeOutput({"samples": latent})


# ─────────────────────── PromptPro ─────────────────────────────────
_DESIGNS = ["Retrato Pro","Cinemático","Producto E-commerce","Anime Clean",
            "Concept Art","Arquitectura","Moda Editorial","Interior Design",
            "Vertical Reels (9:16)","Thumbnail YouTube (16:9)"]
_SEP_OPTS_PP = [", ", " ", "\\n", " | "]
_SEP_MAP_PP = {", ": ", ", " ": " ", "\\n": "\n", " | ": " | "}
_DESIGN_ORDERS = {
    "Retrato Pro":[["sujeto"],["emocion","vestuario"],["estilo","paleta"],["iluminacion","camara"],["calidad","detalle"],["restricciones"],["extra"]],
    "Cinemático":[["sujeto","accion"],["emocion","vestuario"],["fondo","atmosfera"],["iluminacion"],["camara","composicion"],["detalle","calidad"],["restricciones"],["extra"]],
    "Producto E-commerce":[["sujeto"],["materiales","paleta"],["fondo"],["iluminacion"],["camara","composicion"],["detalle","calidad"],["restricciones"],["extra"]],
    "Anime Clean":[["sujeto","accion"],["emocion","vestuario"],["estilo"],["fondo","atmosfera"],["paleta","iluminacion"],["detalle","calidad"],["restricciones"],["extra"]],
    "Concept Art":[["sujeto"],["accion","vestuario"],["fondo","atmosfera"],["estilo","paleta"],["iluminacion","composicion"],["materiales","detalle"],["calidad"],["restricciones"],["extra"]],
    "Arquitectura":[["sujeto"],["fondo","atmosfera"],["estilo","materiales"],["iluminacion"],["camara","composicion"],["detalle","calidad"],["restricciones"],["extra"]],
    "Moda Editorial":[["sujeto","accion"],["vestuario"],["emocion"],["fondo","estilo"],["iluminacion","camara"],["composicion","paleta"],["calidad","detalle"],["restricciones"],["extra"]],
    "Interior Design":[["sujeto"],["fondo"],["estilo","materiales"],["paleta","iluminacion"],["atmosfera"],["camara","composicion"],["detalle","calidad"],["restricciones"],["extra"]],
    "Vertical Reels (9:16)":[["sujeto","accion"],["emocion"],["vestuario"],["fondo"],["iluminacion","atmosfera"],["composicion"],["calidad"],["restricciones"],["extra"]],
    "Thumbnail YouTube (16:9)":[["sujeto","accion"],["emocion"],["fondo"],["paleta","iluminacion"],["composicion"],["calidad","detalle"],["restricciones"],["extra"]],
}
# Ordered field keys matching V1 input order
_FIELD_KEYS = ["sujeto","accion","emocion","vestuario","fondo","estilo","paleta",
               "iluminacion","camara","materiales","composicion","detalle","atmosfera",
               "calidad","restricciones","extra"]
_FIELD_DISPLAY = ["👤 Sujeto","🧍 Acción / Pose","🎭 Emoción / Expresión","👗 Vestuario / Props",
                  "🏞️ Fondo / Entorno","🎨 Estilo","🎨 Paleta / Colores","💡 Iluminación",
                  "📷 Cámara / Lente","🧪 Materiales / Texturas","🧷 Composición","🔎 Detalle",
                  "🌫️ Atmósfera","✨ Calidad","🧯 Restricciones","➕ Extra"]


def _prompt_pro_inputs():
    inputs = [io.Combo.Input("diseno", display_name="📐 Diseño", options=_DESIGNS, default="Retrato Pro")]
    for key, disp in zip(_FIELD_KEYS, _FIELD_DISPLAY):
        ml = (key == "extra")
        inputs.append(io.String.Input(key, display_name=disp, default="", multiline=ml))
    inputs += [
        io.Combo.Input("separador", display_name="🔗 Separador", options=_SEP_OPTS_PP, default=", "),
        io.String.Input("prefijo", display_name="📌 Prefijo", default=""),
        io.String.Input("sufijo", display_name="📌 Sufijo", default=""),
        io.Boolean.Input("normalizar", display_name="🧹 Normalizar", default=True),
        io.Boolean.Input("evitar_duplicados", display_name="🧼 Evitar duplicados", default=False),
    ]
    return inputs


class PromptPro(io.ComfyNode):
    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id="PromptPro",
            display_name="Prompt Pro",
            category="Selectores Pro",
            inputs=_prompt_pro_inputs(),
            outputs=[io.String.Output("text")],
            is_deprecated=True,
        )

    @classmethod
    def execute(cls, diseno, sujeto, accion, emocion, vestuario, fondo, estilo, paleta,
                iluminacion, camara, materiales, composicion, detalle, atmosfera, calidad,
                restricciones, extra, separador, prefijo, sufijo, normalizar,
                evitar_duplicados) -> io.NodeOutput:
        import re
        if not sujeto:
            raise ValueError("El campo 👤 Sujeto es obligatorio.")
        sep = _SEP_MAP_PP.get(separador, ", ")
        campos = dict(zip(_FIELD_KEYS, [sujeto, accion, emocion, vestuario, fondo, estilo,
                                         paleta, iluminacion, camara, materiales, composicion,
                                         detalle, atmosfera, calidad, restricciones, extra]))
        grupos = []
        for grupo_keys in _DESIGN_ORDERS.get(diseno, _DESIGN_ORDERS["Retrato Pro"]):
            partes = [campos.get(k, "").strip() for k in grupo_keys if campos.get(k, "").strip()]
            if partes:
                grupos.append(", ".join(partes))
        prompt = sep.join(grupos)
        if prefijo.strip():
            prompt = prefijo.strip() + sep + prompt
        if sufijo.strip():
            prompt = prompt + sep + sufijo.strip()
        if normalizar:
            prompt = re.sub(r' +', ' ', prompt)
            prompt = re.sub(r',+', ',', prompt)
            prompt = re.sub(r',\s*,', ',', prompt)
            prompt = re.sub(r'\s+,', ',', prompt)
            prompt = re.sub(r',(?!\s)', ', ', prompt)
            prompt = prompt.strip().strip(',').strip()
        if evitar_duplicados and sep.strip():
            parts = [p.strip() for p in prompt.split(sep.strip())]
            seen = set()
            unique = []
            for p in parts:
                if p and p.lower() not in seen:
                    seen.add(p.lower())
                    unique.append(p)
            prompt = sep.join(unique)
        return io.NodeOutput(prompt)
