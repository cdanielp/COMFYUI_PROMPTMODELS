"""
Titan Inspector - Extractor de Metadatos
Recupera la receta (Prompt, Seed, etc.) de imágenes generadas por AI.

Soporta múltiples formatos:
- Automatic1111 / Forge / reForge
- ComfyUI (workflow embebido)
- NovelAI
- InvokeAI
- Metadatos EXIF genéricos
"""

import os
import re
import json
import logging
from typing import Tuple, Dict, Any, Optional
from PIL import Image
from PIL.ExifTags import TAGS

logger = logging.getLogger("TitanSuite")

# Intentar importar folder_paths de ComfyUI
try:
    import folder_paths
    HAS_FOLDER_PATHS = True
except ImportError:
    HAS_FOLDER_PATHS = False
    logger.warning("folder_paths no disponible")


def buscar_archivo(ruta: str) -> str:
    """
    Busca un archivo en múltiples ubicaciones.
    
    Args:
        ruta: Ruta original o nombre del archivo
        
    Returns:
        Ruta completa si existe, ruta original si no se encuentra
    """
    # Limpiar comillas y espacios
    ruta = ruta.replace('"', '').replace("'", "").strip()
    
    # Si ya existe, retornar
    if os.path.exists(ruta):
        return ruta
    
    if not HAS_FOLDER_PATHS:
        return ruta
    
    # Lista de carpetas a buscar
    carpetas = [
        folder_paths.get_input_directory(),
        folder_paths.get_output_directory(),
    ]
    
    # Agregar temp si existe
    try:
        carpetas.append(folder_paths.get_temp_directory())
    except:
        pass
    
    # Buscar en cada carpeta
    for carpeta in carpetas:
        if not carpeta:
            continue
            
        # Ruta directa
        ruta_test = os.path.join(carpeta, ruta)
        if os.path.exists(ruta_test):
            return ruta_test
        
        # Solo nombre de archivo
        nombre = os.path.basename(ruta)
        ruta_test = os.path.join(carpeta, nombre)
        if os.path.exists(ruta_test):
            return ruta_test
    
    return ruta


def extraer_metadatos_a1111(info: str) -> Dict[str, Any]:
    """
    Extrae metadatos del formato Automatic1111.
    
    Formato típico:
    prompt positivo
    Negative prompt: prompt negativo
    Steps: 20, Sampler: DPM++ 2M, CFG scale: 7, Seed: 12345, Size: 1024x1024, Model: sdxl_base
    """
    resultado = {
        "positivo": "",
        "negativo": "",
        "semilla": -1,  # -1 = no encontrada (evita confusión con 0=aleatorio)
        "steps": 0,
        "cfg": 0.0,
        "sampler": "",
        "modelo": "",
        "ancho": 0,
        "alto": 0
    }
    
    if not info:
        return resultado
    
    # Separar positivo y negativo
    if "Negative prompt:" in info:
        partes = info.split("Negative prompt:", 1)
        resultado["positivo"] = partes[0].strip()
        resto = partes[1]
        
        # Buscar donde empiezan los parámetros
        # Generalmente después de "Steps:" o similar
        params_markers = ["Steps:", "Seed:", "Size:", "Model:"]
        neg_end = len(resto)
        
        for marker in params_markers:
            if marker in resto:
                idx = resto.index(marker)
                if idx < neg_end:
                    neg_end = idx
        
        resultado["negativo"] = resto[:neg_end].strip()
        params_str = resto[neg_end:]
    else:
        # Sin negativo, buscar donde empiezan params
        if "Steps:" in info:
            partes = info.split("Steps:", 1)
            resultado["positivo"] = partes[0].strip()
            params_str = "Steps:" + partes[1]
        else:
            resultado["positivo"] = info
            params_str = ""
    
    # Extraer parámetros individuales
    patrones = {
        "semilla": r"Seed:\s*(\d+)",
        "steps": r"Steps:\s*(\d+)",
        "cfg": r"CFG scale:\s*([\d.]+)",
        "sampler": r"Sampler:\s*([^,]+)",
        "modelo": r"Model:\s*([^,]+)",
        "size": r"Size:\s*(\d+)x(\d+)"
    }
    
    for key, patron in patrones.items():
        match = re.search(patron, params_str, re.IGNORECASE)
        if match:
            if key == "size":
                resultado["ancho"] = int(match.group(1))
                resultado["alto"] = int(match.group(2))
            elif key in ["semilla", "steps"]:
                resultado[key] = int(match.group(1))
            elif key == "cfg":
                resultado[key] = float(match.group(1))
            else:
                resultado[key] = match.group(1).strip()
    
    return resultado


def extraer_metadatos_comfyui(info: str) -> Dict[str, Any]:
    """
    Extrae metadatos del formato ComfyUI (JSON workflow).
    """
    resultado = {
        "positivo": "",
        "negativo": "",
        "semilla": -1,  # -1 = no encontrada
        "workflow": None
    }
    
    try:
        data = json.loads(info)
        resultado["workflow"] = data
        
        # Buscar en nodos de tipo "KSampler" o similar
        if "nodes" in data:
            for node in data["nodes"]:
                node_type = node.get("type", "")
                widgets = node.get("widgets_values", [])
                
                # Buscar seed en KSampler
                if "KSampler" in node_type and widgets:
                    for i, val in enumerate(widgets):
                        if isinstance(val, int) and val > 1000:
                            resultado["semilla"] = val
                            break
                
                # Buscar prompts en CLIP Text Encode
                if "CLIPTextEncode" in node_type and widgets:
                    texto = str(widgets[0]) if widgets else ""
                    if not resultado["positivo"]:
                        resultado["positivo"] = texto
                    elif "negative" in node.get("title", "").lower():
                        resultado["negativo"] = texto
        
        # Formato prompt (si existe)
        if "prompt" in data:
            prompt_data = data["prompt"]
            for node_id, node_data in prompt_data.items():
                inputs = node_data.get("inputs", {})
                class_type = node_data.get("class_type", "")
                
                if "seed" in inputs:
                    resultado["semilla"] = inputs["seed"]
                
                if class_type == "CLIPTextEncode":
                    texto = inputs.get("text", "")
                    if not resultado["positivo"]:
                        resultado["positivo"] = texto
                        
    except json.JSONDecodeError:
        pass
    except Exception as e:
        logger.debug(f"Error extrayendo ComfyUI metadata: {e}")
    
    return resultado


def extraer_metadatos_novelai(info: Dict) -> Dict[str, Any]:
    """
    Extrae metadatos del formato NovelAI.
    """
    resultado = {
        "positivo": "",
        "negativo": "",
        "semilla": -1  # -1 = no encontrada
    }
    
    if "Comment" in info:
        try:
            comment = json.loads(info["Comment"])
            resultado["positivo"] = comment.get("prompt", "")
            resultado["negativo"] = comment.get("uc", "")
            resultado["semilla"] = comment.get("seed", 0)
        except:
            pass
    
    if "Description" in info:
        resultado["positivo"] = info["Description"]
    
    return resultado


class Titan_Inspector:
    """
    🕵️ Extractor de Metadatos de Imágenes AI.
    
    Recupera la receta (Prompt, Seed) de imágenes generadas.
    Compatible con A1111, ComfyUI, NovelAI y más.
    """
    
    @classmethod
    def INPUT_TYPES(cls) -> Dict[str, Any]:
        return {
            "required": {
                "ruta_imagen": ("STRING", {
                    "default": "", 
                    "multiline": False,
                    "placeholder": "Arrastra imagen o escribe ruta..."
                })
            },
            "optional": {
                "imagen": ("IMAGE",),  # Para recibir imagen de otro nodo
                "mostrar_raw": ("BOOLEAN", {
                    "default": False,
                    "label_on": "Mostrar datos crudos",
                    "label_off": "Solo procesado"
                })
            }
        }

    RETURN_TYPES = ("STRING", "STRING", "INT", "INT", "INT", "STRING")
    RETURN_NAMES = ("Positivo", "Negativo", "Semilla", "Ancho", "Alto", "Info Completa")
    FUNCTION = "inspeccionar"
    CATEGORY = "Titan Suite 🇪🇸"
    
    # Constante para indicar semilla no encontrada
    SEED_NOT_FOUND = -1

    def inspeccionar(
        self, 
        ruta_imagen: str,
        imagen=None,
        mostrar_raw: bool = False
    ) -> Tuple[str, str, int, int, int, str]:
        """
        Inspecciona una imagen y extrae sus metadatos.
        
        Nota: Si la semilla no se encuentra, retorna -1 (no 0, para evitar
        que otros nodos interpreten 0 como "aleatorio").
        """
        # Buscar archivo
        ruta = buscar_archivo(ruta_imagen)
        
        if not os.path.exists(ruta):
            return (
                f"❌ Archivo no encontrado: {ruta_imagen}",
                "",
                self.SEED_NOT_FOUND, 0, 0,
                "Archivo no encontrado"
            )
        
        try:
            with Image.open(ruta) as img:
                ancho, alto = img.size
                info_dict = dict(img.info) if img.info else {}
                
                # Inicializar resultados
                # Nota: semilla = -1 indica "no encontrada" (evita confusión con 0=aleatorio)
                positivo = ""
                negativo = ""
                semilla = -1
                info_completa = []
                
                # === INTENTAR FORMATO A1111 (más común) ===
                if "parameters" in info_dict:
                    datos = extraer_metadatos_a1111(info_dict["parameters"])
                    positivo = datos["positivo"]
                    negativo = datos["negativo"]
                    semilla = datos["semilla"]
                    
                    # Actualizar dimensiones si están en metadata
                    if datos["ancho"] > 0:
                        ancho = datos["ancho"]
                        alto = datos["alto"]
                    
                    info_completa.append("📷 Formato: A1111/Forge")
                    if datos["modelo"]:
                        info_completa.append(f"🤖 Modelo: {datos['modelo']}")
                    if datos["sampler"]:
                        info_completa.append(f"🎲 Sampler: {datos['sampler']}")
                    if datos["steps"]:
                        info_completa.append(f"👟 Steps: {datos['steps']}")
                    if datos["cfg"]:
                        info_completa.append(f"⚖️ CFG: {datos['cfg']}")
                
                # === INTENTAR FORMATO COMFYUI ===
                elif "prompt" in info_dict or "workflow" in info_dict:
                    raw_data = info_dict.get("prompt") or info_dict.get("workflow", "{}")
                    datos = extraer_metadatos_comfyui(raw_data)
                    positivo = datos["positivo"]
                    negativo = datos["negativo"]
                    semilla = datos["semilla"]
                    info_completa.append("📷 Formato: ComfyUI")
                    
                    if mostrar_raw and datos["workflow"]:
                        info_completa.append(f"\n📋 Workflow:\n{json.dumps(datos['workflow'], indent=2)[:1000]}...")
                
                # === INTENTAR FORMATO NOVELAI ===
                elif "Comment" in info_dict or "Software" in info_dict:
                    if "NovelAI" in str(info_dict.get("Software", "")):
                        datos = extraer_metadatos_novelai(info_dict)
                        positivo = datos["positivo"]
                        negativo = datos["negativo"]
                        semilla = datos["semilla"]
                        info_completa.append("📷 Formato: NovelAI")
                
                # === INTENTAR EXIF GENÉRICO ===
                if not positivo:
                    exif = img.getexif()
                    if exif:
                        for tag_id, value in exif.items():
                            tag = TAGS.get(tag_id, tag_id)
                            if tag == "ImageDescription":
                                positivo = str(value)
                            elif tag == "UserComment":
                                if not positivo:
                                    positivo = str(value)
                        
                        if positivo:
                            info_completa.append("📷 Formato: EXIF genérico")
                
                # === FALLBACK ===
                if not positivo:
                    positivo = "Sin metadatos de prompt encontrados"
                    info_completa.append("⚠️ No se encontraron metadatos de generación")
                    
                    if mostrar_raw and info_dict:
                        info_completa.append(f"\n📋 Datos raw disponibles:\n{list(info_dict.keys())}")
                
                # Añadir info de dimensiones
                info_completa.append(f"📐 Dimensiones: {ancho}x{alto}")
                
                # Compilar info completa
                texto_info = "\n".join(info_completa)
                
                logger.info(f"🕵️ Inspeccionado: {os.path.basename(ruta)} - {ancho}x{alto}")
                
                return (
                    positivo,
                    negativo,
                    semilla,
                    ancho,
                    alto,
                    texto_info
                )
                
        except Exception as e:
            error_msg = f"❌ Error leyendo imagen: {str(e)}"
            logger.error(error_msg)
            return (error_msg, "", -1, 512, 512, str(e))


class Titan_Inspector_Batch:
    """
    🕵️ Inspector de múltiples imágenes (batch).
    
    Procesa una carpeta completa y extrae metadatos.
    """
    
    @classmethod
    def INPUT_TYPES(cls) -> Dict[str, Any]:
        return {
            "required": {
                "carpeta": ("STRING", {
                    "default": "", 
                    "multiline": False,
                    "placeholder": "Ruta a carpeta con imágenes..."
                }),
                "extensiones": ("STRING", {
                    "default": "png,jpg,jpeg,webp",
                    "multiline": False
                }),
                "limite": ("INT", {
                    "default": 10,
                    "min": 1,
                    "max": 100
                })
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("Reporte",)
    FUNCTION = "inspeccionar_carpeta"
    CATEGORY = "Titan Suite 🇪🇸"

    def inspeccionar_carpeta(
        self, 
        carpeta: str,
        extensiones: str,
        limite: int
    ) -> Tuple[str]:
        """
        Inspecciona múltiples imágenes en una carpeta.
        """
        if not os.path.isdir(carpeta):
            return (f"❌ Carpeta no encontrada: {carpeta}",)
        
        exts = [e.strip().lower() for e in extensiones.split(",")]
        archivos = []
        
        for f in os.listdir(carpeta):
            ext = os.path.splitext(f)[1].lower().replace(".", "")
            if ext in exts:
                archivos.append(os.path.join(carpeta, f))
        
        archivos = archivos[:limite]
        
        if not archivos:
            return (f"⚠️ No se encontraron imágenes en: {carpeta}",)
        
        inspector = Titan_Inspector()
        reportes = []
        
        for archivo in archivos:
            resultado = inspector.inspeccionar(archivo)
            nombre = os.path.basename(archivo)
            reportes.append(f"📄 {nombre}")
            reportes.append(f"   Seed: {resultado[2]} | {resultado[3]}x{resultado[4]}")
            if resultado[0] and "Sin metadatos" not in resultado[0]:
                prompt_corto = resultado[0][:80] + "..." if len(resultado[0]) > 80 else resultado[0]
                reportes.append(f"   Prompt: {prompt_corto}")
            reportes.append("")
        
        return ("\n".join(reportes),)
