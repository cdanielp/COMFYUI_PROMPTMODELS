# ============================================================
#  PROMPTMODELS STUDIO — v3.0.0 (rama v3-migration)
# ============================================================
import logging

log = logging.getLogger("promptmodels")

try:
    from comfy_api.latest import io, ComfyExtension
except ImportError:
    log.error(
        "[promptmodels] promptmodels 3.x requiere ComfyUI >= 0.26.0. "
        "Actualiza ComfyUI o instala promptmodels@2.x"
    )
    raise

try:
    from .legacy import ALL_LEGACY_NODES
except Exception as _e:
    log.error("[promptmodels] Error cargando legacy nodes: %s", _e)
    ALL_LEGACY_NODES = []

try:
    from .nodes import ALL_NEW_NODES
except Exception as _e:
    log.error("[promptmodels] Error cargando new nodes: %s", _e)
    ALL_NEW_NODES = []

WEB_DIRECTORY = "./ComfyUI_GoogleAI/web"


class PromptModelsExtension(ComfyExtension):
    async def get_node_list(self):
        return list(ALL_LEGACY_NODES) + list(ALL_NEW_NODES)

    async def on_load(self):
        log.info(
            "[promptmodels] %d legacy + %d new nodes cargados.",
            len(ALL_LEGACY_NODES), len(ALL_NEW_NODES),
        )


def comfy_entrypoint():
    return PromptModelsExtension()
