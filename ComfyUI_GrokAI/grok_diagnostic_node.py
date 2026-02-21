"""
grok_diagnostic_node.py - Nodos de Diagnóstico para ComfyUI
==============================================================
Suite 3: Grok_Workflow_Debugger, Grok_Metadata_Reader

Autor: Prompt Models Studio | cdanielp
"""

import json
import os
import logging
from .grok_core import (
    GrokCore,
    TEXT_MODELS,
    SYSTEM_PROMPT_WORKFLOW_DEBUGGER,
    SYSTEM_PROMPT_WORKFLOW_DEBUGGER_FUN,
    SYSTEM_PROMPT_METADATA_READER,
)

logger = logging.getLogger("ComfyUI_GrokAI")


class Grok_Workflow_Debugger:
    """
    Analiza un workflow JSON de ComfyUI con Grok.

    Extrae los class_type de todos los nodos y Grok devuelve:
    - Repositorios de GitHub para cada custom node
    - Advertencias sobre forks conflictivos
    - Pasos de solución

    fun_mode = True → Grok responde con sarcasmo pero da solución real.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "workflow_json": ("STRING", {
                    "multiline": True,
                    "default": "",
                    "tooltip": "Pega el JSON del workflow o la ruta al archivo .json.",
                }),
                "fun_mode": ("BOOLEAN", {
                    "default": False,
                    "tooltip": "True = Grok explica con sarcasmo e ironía (pero da solución real).",
                }),
            },
            "optional": {
                "api_key": ("STRING", {"default": ""}),
                "model": (TEXT_MODELS, {"default": "grok-4.1-fast-reasoning"}),
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("analysis_report",)
    FUNCTION = "debug_workflow"
    CATEGORY = "Grok AI/Diagnostic"
    DESCRIPTION = "Analiza un workflow de ComfyUI. fun_mode = sarcasmo + solución real."

    def debug_workflow(self, workflow_json, fun_mode,
                       api_key="", model="grok-4.1-fast-reasoning"):
        try:
            key = GrokCore.resolve_api_key(api_key)

            # Cargar JSON: archivo o string directo
            workflow_data = None
            if os.path.isfile(workflow_json.strip()):
                with open(workflow_json.strip(), "r", encoding="utf-8") as f:
                    workflow_data = json.load(f)
            else:
                try:
                    workflow_data = json.loads(workflow_json)
                except json.JSONDecodeError:
                    return ("❌ No es un JSON válido ni una ruta de archivo existente.",)

            # Extraer class_types únicos
            class_types = set()
            if isinstance(workflow_data, dict):
                # API format: {"node_id": {"class_type": "..."}}
                for nid, ndata in workflow_data.items():
                    if isinstance(ndata, dict) and "class_type" in ndata:
                        class_types.add(ndata["class_type"])
                # UI format: {"nodes": [{"type": "..."}]}
                for node in workflow_data.get("nodes", []):
                    if isinstance(node, dict):
                        ct = node.get("type", node.get("class_type", ""))
                        if ct:
                            class_types.add(ct)

            if not class_types:
                return ("⚠️ No se encontraron 'class_type' en el JSON.",)

            sorted_ct = sorted(class_types)
            logger.info(f"[Workflow_Debugger] {len(sorted_ct)} tipos de nodo encontrados.")

            # Elegir system prompt según fun_mode
            sys_prompt = (
                SYSTEM_PROMPT_WORKFLOW_DEBUGGER_FUN if fun_mode
                else SYSTEM_PROMPT_WORKFLOW_DEBUGGER
            )

            prompt = (
                f"Workflow de ComfyUI con {len(sorted_ct)} tipos de nodo:\n\n"
                + "\n".join(f"- {ct}" for ct in sorted_ct)
            )

            result = GrokCore.chat_text(
                api_key=key,
                prompt=prompt,
                model=model,
                system_prompt=sys_prompt,
            )
            return (result,)

        except Exception as e:
            logger.error(f"[Workflow_Debugger] Error: {e}")
            return (f"❌ Error: {str(e)}",)


class Grok_Metadata_Reader:
    """
    Extrae los keys y metadata de un .safetensors y usa Grok
    para explicar la arquitectura y trigger words.

    Usa la librería nativa safetensors (safe_open).
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "safetensors_path": ("STRING", {
                    "default": "",
                    "tooltip": "Ruta completa al archivo .safetensors.",
                }),
            },
            "optional": {
                "api_key": ("STRING", {"default": ""}),
                "model": (TEXT_MODELS, {"default": "grok-4.1-fast-reasoning"}),
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("metadata_summary",)
    FUNCTION = "read_metadata"
    CATEGORY = "Grok AI/Diagnostic"
    DESCRIPTION = "Lee un .safetensors y Grok identifica arquitectura y trigger words."

    def read_metadata(self, safetensors_path, api_key="",
                      model="grok-4.1-fast-reasoning"):
        try:
            key = GrokCore.resolve_api_key(api_key)

            if not os.path.isfile(safetensors_path):
                return (f"❌ Archivo no encontrado: {safetensors_path}",)
            if not safetensors_path.endswith(".safetensors"):
                return ("❌ El archivo debe ser .safetensors",)

            try:
                from safetensors import safe_open
            except ImportError:
                return ("❌ Librería 'safetensors' no instalada. Ejecuta: pip install safetensors",)

            # Extraer keys y metadata
            tensor_keys = []
            metadata = {}
            with safe_open(safetensors_path, framework="pt", device="cpu") as f:
                tensor_keys = list(f.keys())
                metadata = f.metadata() or {}

            if not tensor_keys:
                return ("❌ El archivo no contiene tensores válidos.",)

            # Limitar keys para no exceder contexto
            if len(tensor_keys) > 250:
                sample_keys = tensor_keys[:200] + ["... (truncado) ..."] + tensor_keys[-50:]
            else:
                sample_keys = tensor_keys

            # Construir prompt con toda la info disponible
            sections = [
                f"Archivo: {os.path.basename(safetensors_path)}",
                f"Total de tensores: {len(tensor_keys)}",
                "",
                "Keys del modelo (muestra):",
                "\n".join(sample_keys[:100]),
            ]

            # Incluir metadata si existe
            if metadata:
                sections.append("\nMetadata del archivo:")
                for mk, mv in list(metadata.items())[:30]:
                    # Truncar valores largos
                    val_str = str(mv)[:500]
                    sections.append(f"  {mk}: {val_str}")

                # Si hay ss_tag_frequency, incluirlo destacado
                tag_freq = metadata.get("ss_tag_frequency", "")
                if tag_freq:
                    sections.append("\n📌 ss_tag_frequency encontrado:")
                    sections.append(str(tag_freq)[:3000])

            prompt = "\n".join(sections)

            result = GrokCore.chat_text(
                api_key=key,
                prompt=prompt,
                model=model,
                system_prompt=SYSTEM_PROMPT_METADATA_READER,
            )
            return (result,)

        except Exception as e:
            logger.error(f"[Metadata_Reader] Error: {e}")
            return (f"❌ Error: {str(e)}",)
