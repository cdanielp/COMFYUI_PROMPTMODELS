import re
from comfy_api.latest import io

_KNOWN_EXPANSIONS = {
    "child": ["children","childish","childhood","childlike","childs"],
    "kid": ["kids","kiddo","kiddos","kiddie","kiddies"],
    "baby": ["babies","babyish","babys"],
    "teen": ["teens","teenage","teenager","teenagers","teeny"],
    "young": ["younger","youngest","youngster","youngsters","youngs"],
    "infant": ["infants","infantile","infancy"],
    "minor": ["minors"],
    "school": ["schools","schooler","schoolers","schooling"],
    "nursery": ["nurseries"],
    "underage": ["underaged"],
    "preteen": ["preteens"],
    "toddler": ["toddlers"],
    "boy": ["boys","boyish"],
    "girl": ["girls","girlish"],
}
_DEFAULT_BLOCKED = "child, kid, baby, infant, underage, young, school, nursery, teen, minor, toddler, preteen"


def _build_word_set(blocked_words, expand):
    words = set()
    for word in blocked_words.split(","):
        word = word.strip().lower()
        if not word:
            continue
        words.add(word)
        if expand and word in _KNOWN_EXPANSIONS:
            words.update(_KNOWN_EXPANSIONS[word])
        if expand:
            for suffix in ["s", "es", "ish", "like", "hood", "ness"]:
                words.add(f"{word}{suffix}")
    return words


class TextPromptBlocker(io.ComfyNode):
    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id="TextPromptBlocker",
            display_name="🛡️ Text Prompt Blocker",
            category="Text/Security",
            inputs=[
                io.String.Input("prompt", multiline=True, default=""),
                io.String.Input("blocked_words", multiline=True, default=_DEFAULT_BLOCKED),
                io.Boolean.Input("case_sensitive", optional=True, default=False),
                io.Boolean.Input("hard_block", optional=True, default=True,
                                 label_on="Bloqueo Duro (Excepción)", label_off="Filtrado Suave (String vacío)"),
                io.Boolean.Input("detect_contained", optional=True, default=True,
                                 label_on="Detectar en palabras compuestas", label_off="Solo palabras exactas"),
                io.Boolean.Input("expand_variations", optional=True, default=True,
                                 label_on="Expandir variaciones automáticamente", label_off="Solo palabras exactas de la lista"),
            ],
            outputs=[
                io.String.Output("allowed_output"),
                io.Boolean.Output("is_blocked"),
                io.String.Output("matched_word"),
            ],
            is_deprecated=True,
        )

    @classmethod
    def execute(cls, prompt, blocked_words, case_sensitive=False, hard_block=True,
                detect_contained=True, expand_variations=True) -> io.NodeOutput:
        if not prompt or not prompt.strip():
            return io.NodeOutput(prompt, False, "")
        if not blocked_words or not blocked_words.strip():
            return io.NodeOutput(prompt, False, "")
        word_set = _build_word_set(blocked_words, expand_variations)
        matched = None
        if detect_contained:
            text_lower = prompt.lower()
            for word in sorted(word_set, key=len, reverse=True):
                if word in text_lower:
                    matched = word
                    break
        else:
            check = prompt if case_sensitive else prompt.lower()
            for word in word_set:
                cw = word if case_sensitive else word.lower()
                if re.search(rf"\b{re.escape(cw)}\b", check, 0 if case_sensitive else re.IGNORECASE):
                    matched = word
                    break
        if matched:
            if hard_block:
                raise Exception(f"🚫 PROMPT BLOQUEADO — Palabra detectada: '{matched}'")
            return io.NodeOutput("", True, matched)
        return io.NodeOutput(prompt, False, "")


class TextPromptBlockerPreview(io.ComfyNode):
    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id="TextPromptBlockerPreview",
            display_name="🔍 Text Prompt Blocker (Preview)",
            category="Text/Security",
            inputs=[
                io.String.Input("prompt", multiline=True, default=""),
                io.String.Input("blocked_words", multiline=True, default=_DEFAULT_BLOCKED),
                io.Boolean.Input("detect_contained", optional=True, default=True),
                io.Boolean.Input("expand_variations", optional=True, default=True),
            ],
            outputs=[
                io.String.Output("original_prompt"),
                io.String.Output("status"),
                io.String.Output("detected_words"),
            ],
            is_output_node=True,
            is_deprecated=True,
        )

    @classmethod
    def execute(cls, prompt, blocked_words, detect_contained=True, expand_variations=True) -> io.NodeOutput:
        word_set = _build_word_set(blocked_words, expand_variations)
        found = []
        lower = prompt.lower()
        if detect_contained:
            for word in sorted(word_set, key=len, reverse=True):
                if word in lower:
                    found.append(word)
        else:
            for word in word_set:
                if re.search(rf"\b{re.escape(word)}\b", lower):
                    found.append(word)
        found = list(dict.fromkeys(found))
        if found:
            status = f"⚠️ DETECTADO: {len(found)} palabra(s) prohibida(s)"
            detected = ", ".join(found[:10]) + (f"... (+{len(found)-10} más)" if len(found) > 10 else "")
        else:
            status = "✅ LIMPIO: No se detectaron palabras prohibidas"
            detected = ""
        return io.NodeOutput(prompt, status, detected)
