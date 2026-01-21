"""
Titan MultiLora - Cargador de LoRAs Blindado
Carga hasta 5 LoRAs con protección anti-crash y detección de triggers.
"""

import os
import json
import logging
from typing import Tuple, Dict, Any, List, Optional

import comfy.sd
import comfy.utils
import folder_paths

logger = logging.getLogger("TitanSuite")

# Intentar importar safetensors para lectura avanzada de metadata
try:
    from safetensors import safe_open
    HAS_SAFETENSORS = True
except ImportError:
    HAS_SAFETENSORS = False
    logger.warning("safetensors no disponible - trigger detection limitada")


def extraer_triggers(lora_path: str) -> Tuple[str, Dict[str, Any]]:
    """
    Extrae trigger words y metadata de un archivo LoRA.
    
    Args:
        lora_path: Ruta completa al archivo .safetensors
        
    Returns:
        Tuple: (triggers_string, metadata_dict)
    """
    if not HAS_SAFETENSORS:
        return "", {}
    
    if not lora_path.endswith('.safetensors'):
        return "", {}
    
    triggers = []
    metadata = {}
    
    try:
        with safe_open(lora_path, framework="pt", device="cpu") as f:
            meta = f.metadata()
            if not meta:
                return "", {}
            
            metadata = dict(meta)
            
            # Método 1: trainedWords (CivitAI format)
            if "ss_training_comment" in meta:
                try:
                    comment = json.loads(meta["ss_training_comment"])
                    if "activation text" in comment:
                        triggers.append(comment["activation text"])
                except:
                    pass
            
            if "trainedWords" in meta:
                try:
                    words = json.loads(meta["trainedWords"])
                    if isinstance(words, list):
                        triggers.extend([w for w in words if w])
                    elif isinstance(words, str):
                        triggers.append(words)
                except json.JSONDecodeError:
                    # A veces es string directo
                    triggers.append(meta["trainedWords"])
            
            # Método 2: modelspec.trigger_phrase (kohya format)
            if "modelspec.trigger_phrase" in meta:
                phrase = meta["modelspec.trigger_phrase"]
                if phrase and phrase not in triggers:
                    triggers.append(phrase)
            
            # Método 3: ss_tag_frequency (tags más frecuentes del training)
            if not triggers and "ss_tag_frequency" in meta:
                try:
                    tag_freq = json.loads(meta["ss_tag_frequency"])
                    top_tags = []
                    
                    for bucket_name, bucket_tags in tag_freq.items():
                        if isinstance(bucket_tags, dict):
                            # Ordenar por frecuencia
                            sorted_tags = sorted(
                                bucket_tags.items(), 
                                key=lambda x: x[1], 
                                reverse=True
                            )
                            # Tomar top 3 de cada bucket
                            top_tags.extend([t[0] for t in sorted_tags[:3]])
                    
                    # Eliminar tags genéricos
                    generic = {'1girl', '1boy', 'solo', 'simple background', 'white background'}
                    top_tags = [t for t in top_tags if t.lower() not in generic]
                    triggers.extend(top_tags[:5])
                    
                except Exception as e:
                    logger.debug(f"Error parseando ss_tag_frequency: {e}")
            
            # Método 4: ss_dataset_dirs (nombre del concepto)
            if not triggers and "ss_dataset_dirs" in meta:
                try:
                    dirs = json.loads(meta["ss_dataset_dirs"])
                    for dir_info in dirs.values():
                        if "n_repeats" in dir_info:
                            # El nombre del directorio suele ser el concepto
                            dir_name = list(dirs.keys())[0]
                            # Limpiar formato "5_conceptname"
                            clean = dir_name.split("_", 1)[-1] if "_" in dir_name else dir_name
                            if clean:
                                triggers.append(clean)
                except:
                    pass
                    
    except Exception as e:
        logger.debug(f"Error extrayendo triggers de {lora_path}: {e}")
        return "", {}
    
    # Limpiar y formatear triggers
    if triggers:
        # Eliminar duplicados manteniendo orden
        seen = set()
        clean_triggers = []
        for t in triggers:
            t_clean = t.replace(",", "").strip()
            t_lower = t_clean.lower()
            if t_clean and t_lower not in seen:
                seen.add(t_lower)
                clean_triggers.append(t_clean)
        
        return ", ".join(clean_triggers[:5]), metadata
    
    return "", metadata


def obtener_info_lora(lora_path: str) -> Dict[str, Any]:
    """
    Obtiene información detallada de un LoRA.
    """
    info = {
        "nombre": os.path.basename(lora_path),
        "tamaño_mb": 0,
        "triggers": "",
        "base_model": "desconocido",
        "resolution": ""
    }
    
    try:
        info["tamaño_mb"] = round(os.path.getsize(lora_path) / (1024 * 1024), 1)
    except:
        pass
    
    triggers, meta = extraer_triggers(lora_path)
    info["triggers"] = triggers
    
    if meta:
        # Detectar modelo base
        if "ss_base_model_version" in meta:
            info["base_model"] = meta["ss_base_model_version"]
        elif "ss_sd_model_name" in meta:
            info["base_model"] = meta["ss_sd_model_name"]
        
        # Resolución de entrenamiento
        if "ss_resolution" in meta:
            info["resolution"] = meta["ss_resolution"]
    
    return info


class Titan_MultiLora:
    """
    🧬 Cargador de 5 LoRAs con Escudo Anti-Crash.
    
    Características:
    - Anti-Crash: LoRAs incompatibles son ignorados sin detener el flujo
    - Trigger Words: Muestra las palabras clave ocultas
    - 5 Ranuras: Con interruptores On/Off individuales
    - Fuerza dual: Control separado para modelo y CLIP
    - Reporte detallado: Estado de cada LoRA cargado
    """
    
    @classmethod
    def INPUT_TYPES(cls) -> Dict[str, Any]:
        loras = ["None"] + folder_paths.get_filename_list("loras")
        
        inputs = {
            "required": {
                "modelo": ("MODEL",),
                "clip": ("CLIP",),
            }
        }
        
        # Generar 5 slots dinámicamente
        for i in range(1, 6):
            inputs["required"].update({
                f"lora_{i}": (loras, {"default": "None"}),
                f"on_{i}": ("BOOLEAN", {
                    "default": True, 
                    "label_on": "🟢 ON", 
                    "label_off": "🔴 OFF"
                }),
                f"fuerza_modelo_{i}": ("FLOAT", {
                    "default": 1.0, 
                    "min": -2.0, 
                    "max": 2.0, 
                    "step": 0.05,
                    "display": "slider"
                }),
                f"fuerza_clip_{i}": ("FLOAT", {
                    "default": 1.0, 
                    "min": -2.0, 
                    "max": 2.0, 
                    "step": 0.05,
                    "display": "slider"
                }),
            })
        
        inputs["optional"] = {
            "mostrar_detalles": ("BOOLEAN", {
                "default": True,
                "label_on": "Detalles completos",
                "label_off": "Resumen"
            })
        }
        
        return inputs

    RETURN_TYPES = ("MODEL", "CLIP", "STRING", "STRING")
    RETURN_NAMES = ("Modelo", "CLIP", "Reporte", "Triggers Combinados")
    FUNCTION = "procesar"
    CATEGORY = "Titan Suite 🇪🇸"

    def procesar(
        self, 
        modelo, 
        clip,
        mostrar_detalles: bool = True,
        **kwargs
    ) -> Tuple[Any, Any, str, str]:
        """
        Procesa y carga los LoRAs seleccionados.
        """
        modelo_actual = modelo
        clip_actual = clip
        reporte = []
        triggers_totales = []
        loras_cargados = 0
        
        for i in range(1, 6):
            nombre = kwargs.get(f"lora_{i}", "None")
            activo = kwargs.get(f"on_{i}", True)
            fuerza_modelo = kwargs.get(f"fuerza_modelo_{i}", 1.0)
            fuerza_clip = kwargs.get(f"fuerza_clip_{i}", 1.0)
            
            # Saltar si es None
            if nombre == "None" or not nombre:
                continue
            
            # Saltar si está desactivado
            if not activo:
                reporte.append(f"Slot {i}: 🔴 SKIP - {nombre}")
                continue
            
            # Obtener ruta completa
            ruta = folder_paths.get_full_path("loras", nombre)
            
            if not ruta or not os.path.exists(ruta):
                reporte.append(f"Slot {i}: ⚠️ NO ENCONTRADO - {nombre}")
                continue
            
            # Extraer información
            info = obtener_info_lora(ruta)
            
            if info["triggers"]:
                triggers_totales.append(info["triggers"])
            
            # === CARGA SEGURA (ANTI-CRASH) ===
            try:
                lora_data = comfy.utils.load_torch_file(ruta, safe_load=True)
                
                modelo_actual, clip_actual = comfy.sd.load_lora_for_models(
                    modelo_actual, 
                    clip_actual, 
                    lora_data, 
                    fuerza_modelo, 
                    fuerza_clip
                )
                
                loras_cargados += 1
                
                # Construir reporte
                if mostrar_detalles:
                    linea = f"Slot {i}: ✅ {nombre}"
                    if fuerza_modelo != 1.0 or fuerza_clip != 1.0:
                        linea += f" [M:{fuerza_modelo:.2f} C:{fuerza_clip:.2f}]"
                    if info["triggers"]:
                        linea += f"\n         🏷️ Triggers: {info['triggers']}"
                    if info["tamaño_mb"]:
                        linea += f" ({info['tamaño_mb']}MB)"
                else:
                    linea = f"Slot {i}: ✅ {nombre}"
                
                reporte.append(linea)
                logger.info(f"✅ LoRA cargado: {nombre}")
                
            except RuntimeError as e:
                error_str = str(e)
                if "size mismatch" in error_str.lower():
                    reporte.append(f"Slot {i}: 🛡️ INCOMPATIBLE (ignorado) - {nombre}")
                    reporte.append(f"         ⚠️ Modelo base diferente")
                else:
                    reporte.append(f"Slot {i}: 🛡️ ERROR (ignorado) - {nombre}")
                logger.warning(f"LoRA ignorado por error: {nombre} - {e}")
                
            except Exception as e:
                reporte.append(f"Slot {i}: 🛡️ ERROR (ignorado) - {nombre}")
                logger.warning(f"LoRA ignorado por excepción: {nombre} - {e}")
        
        # Resumen final
        if not reporte:
            texto_reporte = "ℹ️ Sin LoRAs seleccionados"
        else:
            header = f"═══ Titan LoRA Report ═══\n📦 {loras_cargados} LoRA(s) cargados\n"
            texto_reporte = header + "\n".join(reporte)
        
        # Combinar triggers
        texto_triggers = ", ".join(triggers_totales) if triggers_totales else ""
        
        return (modelo_actual, clip_actual, texto_reporte, texto_triggers)


class Titan_LoRA_Info:
    """
    🔍 Inspector de LoRAs - Muestra información detallada sin cargar.
    
    Útil para ver triggers y metadata antes de usar un LoRA.
    """
    
    @classmethod
    def INPUT_TYPES(cls) -> Dict[str, Any]:
        loras = folder_paths.get_filename_list("loras")
        return {
            "required": {
                "lora": (loras,),
            }
        }

    RETURN_TYPES = ("STRING", "STRING", "STRING")
    RETURN_NAMES = ("Triggers", "Info Completa", "Modelo Base")
    FUNCTION = "inspeccionar"
    CATEGORY = "Titan Suite 🇪🇸"

    def inspeccionar(self, lora: str) -> Tuple[str, str, str]:
        """
        Inspecciona un LoRA sin cargarlo.
        """
        ruta = folder_paths.get_full_path("loras", lora)
        
        if not ruta or not os.path.exists(ruta):
            return ("", f"❌ LoRA no encontrado: {lora}", "")
        
        info = obtener_info_lora(ruta)
        
        # Construir info detallada
        detalles = [
            f"📄 Nombre: {info['nombre']}",
            f"📦 Tamaño: {info['tamaño_mb']} MB",
            f"🤖 Modelo Base: {info['base_model']}",
        ]
        
        if info["resolution"]:
            detalles.append(f"📐 Resolución: {info['resolution']}")
        
        if info["triggers"]:
            detalles.append(f"🏷️ Triggers: {info['triggers']}")
        else:
            detalles.append("🏷️ Triggers: No detectados")
        
        return (
            info["triggers"],
            "\n".join(detalles),
            info["base_model"]
        )


class Titan_LoRA_Stack:
    """
    📚 LoRA Stack - Combina múltiples nodos LoRA en uno.
    
    Entrada: Stack previo (opcional)
    Salida: Stack actualizado para pasar a otro nodo
    """
    
    @classmethod
    def INPUT_TYPES(cls) -> Dict[str, Any]:
        loras = ["None"] + folder_paths.get_filename_list("loras")
        return {
            "required": {
                "lora": (loras,),
                "fuerza_modelo": ("FLOAT", {"default": 1.0, "min": -2.0, "max": 2.0, "step": 0.05}),
                "fuerza_clip": ("FLOAT", {"default": 1.0, "min": -2.0, "max": 2.0, "step": 0.05}),
            },
            "optional": {
                "stack_previo": ("LORA_STACK",),
            }
        }

    RETURN_TYPES = ("LORA_STACK", "STRING")
    RETURN_NAMES = ("Stack", "Triggers")
    FUNCTION = "apilar"
    CATEGORY = "Titan Suite 🇪🇸"

    def apilar(
        self, 
        lora: str, 
        fuerza_modelo: float,
        fuerza_clip: float,
        stack_previo: Optional[List] = None
    ) -> Tuple[List, str]:
        """
        Añade un LoRA al stack.
        """
        stack = list(stack_previo) if stack_previo else []
        triggers = ""
        
        if lora != "None":
            stack.append({
                "nombre": lora,
                "fuerza_modelo": fuerza_modelo,
                "fuerza_clip": fuerza_clip
            })
            
            # Obtener triggers
            ruta = folder_paths.get_full_path("loras", lora)
            if ruta:
                triggers, _ = extraer_triggers(ruta)
        
        return (stack, triggers)
