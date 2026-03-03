"""
google_diagnostic_node.py - Nodos de Diagnóstico para ComfyUI (V2.5.0)
=====================================================================
Gemini 3.1 Pro para análisis de modelos, LoRAs, workflows, compatibilidad.

V2.5.0: gemini-3-flash-preview agregado como opcion rapida.
Modelos actualizados a strings estables (Mar 2026).

Autor: Prompt Models Studio | cdanielp
"""

import json
import csv
import io
import os
import logging
from typing import Dict, Any

from .google_core import (
    GoogleAICore, DEFAULT_TEXT_MODEL,
    SYSTEM_PROMPT_ARCHITECTURE_DETECTOR, SYSTEM_PROMPT_TRIGGER_EXTRACTOR,
    SYSTEM_PROMPT_WORKFLOW_ANALYZER, SYSTEM_PROMPT_COMPATIBILITY_CHECKER,
    SYSTEM_PROMPT_TRAINING_ANALYZER,
)

logger = logging.getLogger("ComfyUI_GoogleAI")

# Strings exactos válidos en la API — Feb 2026
DIAG_MODELS = [
    "gemini-3.1-pro-preview",  # Mejor para análisis complejos
    "gemini-3-flash-preview",  # Rápido y económico (V2.5.0)
    "gemini-2.5-flash",        # Antes: gemini-2.5-flash-preview-05-20
    "gemini-2.5-pro",          # Antes: gemini-2.5-pro-preview-06-05
]


class GoogleAI_ModelArchitectureDetector:
    """Extrae keys de un .safetensors y Gemini identifica la arquitectura."""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "safetensors_path": ("STRING", {"default": ""}),
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

    def detect_architecture(self, safetensors_path, api_key="", model="gemini-3.1-pro-preview"):
        try:
            key = GoogleAICore.resolve_api_key(api_key)
            if not os.path.isfile(safetensors_path):
                return (f"❌ Archivo no encontrado: {safetensors_path}",)
            if not safetensors_path.endswith(".safetensors"):
                return ("❌ El archivo debe ser .safetensors",)

            try:
                from safetensors import safe_open
            except ImportError:
                return ("❌ Librería 'safetensors' no instalada.",)

            with safe_open(safetensors_path, framework="pt", device="cpu") as f:
                tensor_keys = list(f.keys())

            if not tensor_keys:
                return ("❌ El archivo no contiene tensores válidos.",)

            if len(tensor_keys) > 250:
                sample = tensor_keys[:200] + ["... (truncado) ..."] + tensor_keys[-50:]
            else:
                sample = tensor_keys

            prompt = (
                f"Archivo: {os.path.basename(safetensors_path)}\n"
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
    """Extrae ss_tag_frequency de un LoRA y formatea trigger words con Gemini."""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {"lora_path": ("STRING", {"default": ""})},
            "optional": {
                "api_key": ("STRING", {"default": ""}),
                "model": (DIAG_MODELS, {"default": "gemini-2.5-flash"}),
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("trigger_words",)
    FUNCTION = "extract_triggers"
    CATEGORY = "Google AI/Diagnostic"

    def extract_triggers(self, lora_path, api_key="", model="gemini-2.5-flash"):
        try:
            key = GoogleAICore.resolve_api_key(api_key)
            if not os.path.isfile(lora_path):
                return (f"❌ Archivo no encontrado: {lora_path}",)

            try:
                from safetensors import safe_open
            except ImportError:
                return ("❌ Librería 'safetensors' no instalada.",)

            with safe_open(lora_path, framework="pt", device="cpu") as f:
                metadata = f.metadata() or {}

            tag_freq_raw = metadata.get("ss_tag_frequency", "")
            if not tag_freq_raw:
                alt = [k for k in metadata if "tag" in k.lower() or "trigger" in k.lower()]
                if alt:
                    tag_freq_raw = metadata[alt[0]]
                else:
                    return (f"⚠️ No se encontró 'ss_tag_frequency'. Keys: {', '.join(list(metadata.keys())[:20])}",)

            if isinstance(tag_freq_raw, str):
                try:
                    tag_freq = json.loads(tag_freq_raw)
                except json.JSONDecodeError:
                    tag_freq = tag_freq_raw
            else:
                tag_freq = tag_freq_raw

            prompt = (
                f"LoRA: {os.path.basename(lora_path)}\n\n"
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


class GoogleAI_WorkflowAnalyzer:
    """Analiza class_type de un workflow JSON y Gemini devuelve repos de GitHub."""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "workflow_json": ("STRING", {
                    "multiline": True, "default": "",
                    "tooltip": "JSON del workflow o ruta al archivo .json.",
                }),
            },
            "optional": {
                "api_key": ("STRING", {"default": ""}),
                "model": (DIAG_MODELS, {"default": "gemini-3.1-pro-preview"}),
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("analysis_report",)
    FUNCTION = "analyze_workflow"
    CATEGORY = "Google AI/Diagnostic"

    def analyze_workflow(self, workflow_json, api_key="", model="gemini-3.1-pro-preview"):
        try:
            key = GoogleAICore.resolve_api_key(api_key)

            if os.path.isfile(workflow_json.strip()):
                with open(workflow_json.strip(), "r", encoding="utf-8") as f:
                    workflow_data = json.load(f)
            else:
                try:
                    workflow_data = json.loads(workflow_json)
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


class GoogleAI_CompatibilityChecker:
    """Verifica compatibilidad checkpoint + LoRA analizando dimensiones de tensores."""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "checkpoint_path": ("STRING", {"default": ""}),
                "lora_path": ("STRING", {"default": ""}),
            },
            "optional": {
                "api_key": ("STRING", {"default": ""}),
                "model": (DIAG_MODELS, {"default": "gemini-2.5-flash"}),
            },
        }

    RETURN_TYPES = ("BOOLEAN", "STRING",)
    RETURN_NAMES = ("is_compatible", "compatibility_report",)
    FUNCTION = "check_compatibility"
    CATEGORY = "Google AI/Diagnostic"

    def check_compatibility(self, checkpoint_path, lora_path,
                            api_key="", model="gemini-2.5-flash"):
        try:
            key = GoogleAICore.resolve_api_key(api_key)
            try:
                from safetensors import safe_open
            except ImportError:
                return (False, "❌ Librería 'safetensors' no instalada.",)

            for path, name in [(checkpoint_path, "Checkpoint"), (lora_path, "LoRA")]:
                if not os.path.isfile(path):
                    return (False, f"❌ {name} no encontrado: {path}",)

            ckpt_info = self._extract_info(checkpoint_path)
            lora_info = self._extract_info(lora_path)

            prompt = (
                f"**Checkpoint:** {os.path.basename(checkpoint_path)}\n"
                f"Keys (100):\n{chr(10).join(ckpt_info['keys'][:100])}\n"
                f"Dims:\n{json.dumps(ckpt_info['dims'], indent=2)}\n\n"
                f"**LoRA:** {os.path.basename(lora_path)}\n"
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


class GoogleAI_LoRATrainingAnalyzer:
    """Analiza logs de entrenamiento (.csv/.json) para detectar overfitting."""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "training_logs": ("STRING", {
                    "multiline": True, "default": "",
                    "tooltip": "CSV/JSON de loss, o ruta al archivo.",
                }),
            },
            "optional": {
                "api_key": ("STRING", {"default": ""}),
                "model": (DIAG_MODELS, {"default": "gemini-3.1-pro-preview"}),
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("diagnosis_report",)
    FUNCTION = "analyze_training"
    CATEGORY = "Google AI/Diagnostic"

    def analyze_training(self, training_logs, api_key="", model="gemini-3.1-pro-preview"):
        try:
            key = GoogleAICore.resolve_api_key(api_key)
            log_data = training_logs

            if os.path.isfile(training_logs.strip()):
                fp = training_logs.strip()
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
                    log_data = json.dumps(json.loads(training_logs), indent=2)[:10000]
                except (json.JSONDecodeError, TypeError):
                    if "," in training_logs and "\n" in training_logs:
                        log_data = self._csv_summary(training_logs)
                    else:
                        log_data = training_logs[:10000]

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
