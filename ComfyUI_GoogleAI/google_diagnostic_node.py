"""
google_diagnostic_node.py - Nodos de Diagnóstico para ComfyUI (V2.1)
=====================================================================
Gemini 3.1 Pro para análisis de modelos, LoRAs, workflows, compatibilidad.

V2.1 Cambios:
  Subgrupo A (ArchitectureDetector, TriggerWordExtractor, CompatibilityChecker):
    - Eliminados inputs STRING manuales para rutas
    - Menús desplegables nativos via folder_paths.get_filename_list()
    - Backend usa folder_paths.get_full_path() para resolver rutas absolutas
  Subgrupo B (WorkflowAnalyzer, LoRATrainingAnalyzer):
    - Mantienen STRING multiline para texto manual
    - Nuevo optional: text_or_file_path con forceInput=True (puerto físico)

Autor: Prompt Models Studio | cdanielp
"""

import json
import csv
import io
import os
import logging
from typing import Dict, Any

import folder_paths

from .google_core import (
    GoogleAICore, DEFAULT_TEXT_MODEL,
    SYSTEM_PROMPT_ARCHITECTURE_DETECTOR, SYSTEM_PROMPT_TRIGGER_EXTRACTOR,
    SYSTEM_PROMPT_WORKFLOW_ANALYZER, SYSTEM_PROMPT_COMPATIBILITY_CHECKER,
    SYSTEM_PROMPT_TRAINING_ANALYZER,
)

logger = logging.getLogger("ComfyUI_GoogleAI")

DIAG_MODELS = ["gemini-3.1-pro-preview", "gemini-2.5-flash-preview-05-20"]


# ============================================================================
# SUBGRUPO A: Menús Desplegables Inteligentes
# ============================================================================

class GoogleAI_ModelArchitectureDetector:
    """
    Extrae keys de un .safetensors y Gemini identifica la arquitectura.
    UI: Menú desplegable nativo de checkpoints.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "checkpoint": (folder_paths.get_filename_list("checkpoints"), {
                    "tooltip": "Selecciona un checkpoint .safetensors del menú.",
                }),
            },
            "optional": {
                "api_key": ("STRING", {"default": ""}),
                "model": (DIAG_MODELS, {"default": "gemini-3.1-pro-preview"}),
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("architecture_report",)
    FUNCTION = "detect_architecture"
    CATEGORY = "Google AI/Diagnostic"

    def detect_architecture(self, checkpoint, api_key="", model="gemini-3.1-pro-preview"):
        try:
            key = GoogleAICore.resolve_api_key(api_key)

            # Resolver ruta absoluta via folder_paths
            full_path = folder_paths.get_full_path("checkpoints", checkpoint)
            if not full_path or not os.path.isfile(full_path):
                return (f"❌ Checkpoint no encontrado: {checkpoint}",)

            if not full_path.endswith(".safetensors"):
                return ("❌ El archivo debe ser .safetensors para analizar la arquitectura.",)

            try:
                from safetensors import safe_open
            except ImportError:
                return ("❌ Librería 'safetensors' no instalada. pip install safetensors",)

            with safe_open(full_path, framework="pt", device="cpu") as f:
                tensor_keys = list(f.keys())

            if not tensor_keys:
                return ("❌ El archivo no contiene tensores válidos.",)

            # Limitar para no exceder contexto de Gemini
            if len(tensor_keys) > 250:
                sample = tensor_keys[:200] + ["... (truncado) ..."] + tensor_keys[-50:]
            else:
                sample = tensor_keys

            prompt = (
                f"Archivo: {checkpoint}\n"
                f"Total tensores: {len(tensor_keys)}\n\nKeys:\n" + "\n".join(sample)
            )
            result = GoogleAICore.call_gemini_text(
                api_key=key, prompt=prompt, model=model,
                system_instruction=SYSTEM_PROMPT_ARCHITECTURE_DETECTOR,
            )
            return (result,)

        except Exception as e:
            logger.error(f"[ArchitectureDetector] Error: {e}")
            return (f"❌ Error: {str(e)}",)


class GoogleAI_TriggerWordExtractor:
    """
    Extrae ss_tag_frequency de un LoRA y formatea trigger words con Gemini.
    UI: Menú desplegable nativo de LoRAs.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "lora": (folder_paths.get_filename_list("loras"), {
                    "tooltip": "Selecciona un LoRA del menú desplegable.",
                }),
            },
            "optional": {
                "api_key": ("STRING", {"default": ""}),
                "model": (DIAG_MODELS, {"default": "gemini-2.5-flash-preview-05-20"}),
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("trigger_words",)
    FUNCTION = "extract_triggers"
    CATEGORY = "Google AI/Diagnostic"

    def extract_triggers(self, lora, api_key="", model="gemini-2.5-flash-preview-05-20"):
        try:
            key = GoogleAICore.resolve_api_key(api_key)

            full_path = folder_paths.get_full_path("loras", lora)
            if not full_path or not os.path.isfile(full_path):
                return (f"❌ LoRA no encontrado: {lora}",)

            try:
                from safetensors import safe_open
            except ImportError:
                return ("❌ Librería 'safetensors' no instalada. pip install safetensors",)

            with safe_open(full_path, framework="pt", device="cpu") as f:
                metadata = f.metadata() or {}

            tag_freq_raw = metadata.get("ss_tag_frequency", "")
            if not tag_freq_raw:
                alt = [k for k in metadata if "tag" in k.lower() or "trigger" in k.lower()]
                if alt:
                    tag_freq_raw = metadata[alt[0]]
                else:
                    return (
                        f"⚠️ No se encontró 'ss_tag_frequency' en {lora}.\n"
                        f"Keys de metadata: {', '.join(list(metadata.keys())[:20])}"
                    ,)

            if isinstance(tag_freq_raw, str):
                try:
                    tag_freq = json.loads(tag_freq_raw)
                except json.JSONDecodeError:
                    tag_freq = tag_freq_raw
            else:
                tag_freq = tag_freq_raw

            prompt = (
                f"LoRA: {lora}\n\n"
                f"ss_tag_frequency:\n{json.dumps(tag_freq, indent=2, ensure_ascii=False)[:8000]}"
            )
            result = GoogleAICore.call_gemini_text(
                api_key=key, prompt=prompt, model=model,
                system_instruction=SYSTEM_PROMPT_TRIGGER_EXTRACTOR,
            )
            return (result,)

        except Exception as e:
            logger.error(f"[TriggerWordExtractor] Error: {e}")
            return (f"❌ Error: {str(e)}",)


class GoogleAI_CompatibilityChecker:
    """
    Verifica compatibilidad checkpoint + LoRA analizando dimensiones de tensores.
    UI: Menús desplegables nativos para ambos.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "checkpoint": (folder_paths.get_filename_list("checkpoints"), {
                    "tooltip": "Selecciona un checkpoint del menú.",
                }),
                "lora": (folder_paths.get_filename_list("loras"), {
                    "tooltip": "Selecciona un LoRA del menú.",
                }),
            },
            "optional": {
                "api_key": ("STRING", {"default": ""}),
                "model": (DIAG_MODELS, {"default": "gemini-2.5-flash-preview-05-20"}),
            },
        }

    RETURN_TYPES = ("BOOLEAN", "STRING",)
    RETURN_NAMES = ("is_compatible", "compatibility_report",)
    FUNCTION = "check_compatibility"
    CATEGORY = "Google AI/Diagnostic"

    def check_compatibility(self, checkpoint, lora,
                            api_key="", model="gemini-2.5-flash-preview-05-20"):
        try:
            key = GoogleAICore.resolve_api_key(api_key)

            try:
                from safetensors import safe_open
            except ImportError:
                return (False, "❌ Librería 'safetensors' no instalada.",)

            # Resolver rutas absolutas
            ckpt_path = folder_paths.get_full_path("checkpoints", checkpoint)
            lora_path = folder_paths.get_full_path("loras", lora)

            for path, name, label in [(ckpt_path, checkpoint, "Checkpoint"), (lora_path, lora, "LoRA")]:
                if not path or not os.path.isfile(path):
                    return (False, f"❌ {label} no encontrado: {name}",)

            ckpt_info = self._extract_info(ckpt_path)
            lora_info = self._extract_info(lora_path)

            prompt = (
                f"**Checkpoint:** {checkpoint}\n"
                f"Keys (100):\n{chr(10).join(ckpt_info['keys'][:100])}\n"
                f"Dims:\n{json.dumps(ckpt_info['dims'], indent=2)}\n\n"
                f"**LoRA:** {lora}\n"
                f"Keys (100):\n{chr(10).join(lora_info['keys'][:100])}\n"
                f"Dims:\n{json.dumps(lora_info['dims'], indent=2)}\n\n"
                "Responde empezando con 'COMPATIBLE: Sí' o 'COMPATIBLE: No'."
            )
            result = GoogleAICore.call_gemini_text(
                api_key=key, prompt=prompt, model=model,
                system_instruction=SYSTEM_PROMPT_COMPATIBILITY_CHECKER,
            )
            is_compat = "compatible: sí" in result.lower()
            return (is_compat, result,)

        except Exception as e:
            logger.error(f"[CompatibilityChecker] Error: {e}")
            return (False, f"❌ Error: {str(e)}",)

    @staticmethod
    def _extract_info(path: str) -> Dict[str, Any]:
        from safetensors import safe_open
        info = {"keys": [], "dims": {}}
        with safe_open(path, framework="pt", device="cpu") as f:
            keys = list(f.keys())
            info["keys"] = keys[:150]
            dim_keys = [
                k for k in keys
                if any(t in k.lower() for t in [
                    "input_blocks.0", "down_blocks.0", "conv_in",
                    "time_embed", "lora_down", "lora_up",
                ])
            ]
            for dk in dim_keys[:20]:
                try:
                    info["dims"][dk] = list(f.get_tensor(dk).shape)
                except Exception:
                    pass
        return info


# ============================================================================
# SUBGRUPO B: Diagnóstico de Texto/Workflow (STRING multiline + forceInput)
# ============================================================================

class GoogleAI_WorkflowAnalyzer:
    """
    Analiza class_type de un workflow JSON y Gemini devuelve repos de GitHub.
    UI: Cuadro de texto manual + puerto físico text_or_file_path (forceInput).
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "workflow_json": ("STRING", {
                    "multiline": True,
                    "default": "",
                    "tooltip": "JSON del workflow o ruta al archivo .json.",
                }),
            },
            "optional": {
                "api_key": ("STRING", {"default": ""}),
                "model": (DIAG_MODELS, {"default": "gemini-3.1-pro-preview"}),
                "text_or_file_path": ("STRING", {
                    "forceInput": True,
                    "tooltip": "Puerto de conexión: recibe texto o ruta de archivo desde otro nodo.",
                }),
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("analysis_report",)
    FUNCTION = "analyze_workflow"
    CATEGORY = "Google AI/Diagnostic"

    def analyze_workflow(self, workflow_json, api_key="",
                         model="gemini-3.1-pro-preview", text_or_file_path=""):
        try:
            key = GoogleAICore.resolve_api_key(api_key)

            # Prioridad: text_or_file_path > workflow_json
            source = text_or_file_path.strip() if text_or_file_path else workflow_json

            if os.path.isfile(source.strip()):
                with open(source.strip(), "r", encoding="utf-8") as f:
                    workflow_data = json.load(f)
            else:
                try:
                    workflow_data = json.loads(source)
                except json.JSONDecodeError:
                    return ("❌ No es un JSON válido ni una ruta existente.",)

            class_types = set()
            if isinstance(workflow_data, dict):
                for nid, ndata in workflow_data.items():
                    if isinstance(ndata, dict) and "class_type" in ndata:
                        class_types.add(ndata["class_type"])
                for node in workflow_data.get("nodes", []):
                    if isinstance(node, dict):
                        ct = node.get("type", node.get("class_type", ""))
                        if ct:
                            class_types.add(ct)

            if not class_types:
                return ("⚠️ No se encontraron 'class_type' en el JSON.",)

            sorted_ct = sorted(class_types)
            prompt = (
                f"Nodos ({len(sorted_ct)} tipos):\n\n"
                + "\n".join(f"- {ct}" for ct in sorted_ct)
            )
            result = GoogleAICore.call_gemini_text(
                api_key=key, prompt=prompt, model=model,
                system_instruction=SYSTEM_PROMPT_WORKFLOW_ANALYZER,
            )
            return (result,)

        except Exception as e:
            logger.error(f"[WorkflowAnalyzer] Error: {e}")
            return (f"❌ Error: {str(e)}",)


class GoogleAI_LoRATrainingAnalyzer:
    """
    Analiza logs de entrenamiento (.csv/.json) para detectar overfitting.
    UI: Cuadro de texto manual + puerto físico text_or_file_path (forceInput).
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "training_logs": ("STRING", {
                    "multiline": True,
                    "default": "",
                    "tooltip": "CSV/JSON de loss de entrenamiento, o ruta al archivo.",
                }),
            },
            "optional": {
                "api_key": ("STRING", {"default": ""}),
                "model": (DIAG_MODELS, {"default": "gemini-3.1-pro-preview"}),
                "text_or_file_path": ("STRING", {
                    "forceInput": True,
                    "tooltip": "Puerto de conexión: recibe datos o ruta desde otro nodo.",
                }),
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("diagnosis_report",)
    FUNCTION = "analyze_training"
    CATEGORY = "Google AI/Diagnostic"

    def analyze_training(self, training_logs, api_key="",
                         model="gemini-3.1-pro-preview", text_or_file_path=""):
        try:
            key = GoogleAICore.resolve_api_key(api_key)

            # Prioridad: text_or_file_path > training_logs
            source = text_or_file_path.strip() if text_or_file_path else training_logs
            log_data = source

            if os.path.isfile(source.strip()):
                fp = source.strip()
                with open(fp, "r", encoding="utf-8") as f:
                    raw = f.read()
                if fp.endswith(".json"):
                    try:
                        log_data = json.dumps(json.loads(raw), indent=2)[:10000]
                    except json.JSONDecodeError:
                        log_data = raw[:10000]
                elif fp.endswith(".csv"):
                    log_data = self._csv_summary(raw)
                else:
                    log_data = raw[:10000]
            else:
                try:
                    log_data = json.dumps(json.loads(source), indent=2)[:10000]
                except (json.JSONDecodeError, TypeError):
                    if "," in source and "\n" in source:
                        log_data = self._csv_summary(source)
                    else:
                        log_data = source[:10000]

            if not log_data.strip():
                return ("❌ No se proporcionaron datos de entrenamiento.",)

            prompt = f"Datos de entrenamiento:\n\n{log_data}\n\nAnaliza overfitting."
            result = GoogleAICore.call_gemini_text(
                api_key=key, prompt=prompt, model=model,
                system_instruction=SYSTEM_PROMPT_TRAINING_ANALYZER,
            )
            return (result,)

        except Exception as e:
            logger.error(f"[LoRATrainingAnalyzer] Error: {e}")
            return (f"❌ Error: {str(e)}",)

    @staticmethod
    def _csv_summary(csv_content: str) -> str:
        try:
            rows = list(csv.DictReader(io.StringIO(csv_content)))
            if not rows:
                return csv_content[:10000]

            total = len(rows)
            idxs = set()
            for i in range(min(10, total)):
                idxs.add(i)
            for pct in range(10, 100, 10):
                idxs.add(min(int(total * pct / 100), total - 1))
            for i in range(max(0, total - 10), total):
                idxs.add(i)

            lines = [f"Total: {total}", f"Columnas: {', '.join(rows[0].keys())}", ""]
            for row in [rows[i] for i in sorted(idxs)]:
                lines.append(str(dict(row)))
            return "\n".join(lines)
        except Exception:
            return csv_content[:10000]
