"""
Titan Utils - El Cerebro Compartido
Base de datos, funciones comunes y configuración central.
Compatible con ComfyUI local y cloud (ComfyDeploy, RunComfy).
"""

import os
import json
import random
import re
import time
import logging
from typing import Dict, Tuple, Optional, Any

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TitanSuite")

# --- VERSIÓN ---
TITAN_VERSION = "1.0.0"

# --- CONFIGURACIÓN DE RUTAS (CLOUD COMPATIBLE) ---
def _get_safe_db_path() -> str:
    """Obtiene la ruta segura para la base de datos, priorizando carpeta persistente."""
    try:
        import folder_paths
        carpeta_segura = folder_paths.get_input_directory()
        return os.path.join(carpeta_segura, "titan_vault.json")
    except ImportError:
        logger.warning("folder_paths no disponible, usando carpeta local")
        return os.path.join(os.path.dirname(__file__), "titan_vault.json")
    except Exception as e:
        logger.warning(f"Error obteniendo carpeta segura: {e}")
        return os.path.join(os.path.dirname(__file__), "titan_vault.json")

DB_FILE = _get_safe_db_path()

# --- PRESETS DE RESOLUCIÓN ---
# Formato: "Nombre descriptivo": (ancho, alto)
PRESETS: Dict[str, Tuple[int, int]] = {
    # SDXL / Flux Optimizados
    "📐 Cuadrado (1024x1024)": (1024, 1024),
    "📱 Retrato Vertical (832x1216)": (832, 1216),
    "🖼️ Paisaje Horizontal (1216x832)": (1216, 832),
    
    # Redes Sociales
    "📲 TikTok/Reels (720x1280)": (720, 1280),
    "🎬 YouTube 720p (1280x720)": (1280, 720),
    "📺 YouTube 1080p (1920x1080)": (1920, 1080),
    "📸 Instagram Post (1080x1080)": (1080, 1080),
    "📖 Instagram Story (1080x1920)": (1080, 1920),
    
    # Cinematográficos
    "🎞️ Cinematic 2.35:1 (1536x640)": (1536, 640),
    "🎥 Cinematic 16:9 (1344x768)": (1344, 768),
    "🎬 Anamórfico (1536x640)": (1536, 640),
    
    # Clásicos
    "🖼️ SD 1.5 Cuadrado (512x512)": (512, 512),
    "📷 SD 1.5 Retrato (512x768)": (512, 768),
    "🌅 SD 1.5 Paisaje (768x512)": (768, 512),
    
    # Alta Resolución
    "🔷 2K Cuadrado (1536x1536)": (1536, 1536),
    "🔶 2K Retrato (1024x1536)": (1024, 1536),
    "🔷 2K Paisaje (1536x1024)": (1536, 1024),
}

# --- FUNCIONES DE BASE DE DATOS ---
def cargar_bunker() -> Dict[str, Any]:
    """
    Carga la base de datos del búnker de forma segura.
    
    Returns:
        Diccionario con los prompts guardados o dict vacío si hay error.
    """
    if not os.path.exists(DB_FILE):
        logger.debug(f"Archivo de búnker no existe: {DB_FILE}")
        return {}
    
    try:
        with open(DB_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            logger.debug(f"Búnker cargado: {len(data)} entradas")
            return data
    except json.JSONDecodeError as e:
        logger.error(f"Error de JSON en búnker: {e}")
        # Crear backup del archivo corrupto
        backup_path = DB_FILE + f".backup_{int(time.time())}"
        try:
            os.rename(DB_FILE, backup_path)
            logger.info(f"Archivo corrupto respaldado en: {backup_path}")
        except:
            pass
        return {}
    except Exception as e:
        logger.error(f"Error cargando búnker: {e}")
        return {}


def _obtener_rutas_fallback() -> list:
    """
    Obtiene lista de rutas posibles para guardar, en orden de prioridad.
    """
    rutas = []
    
    try:
        import folder_paths
        # Prioridad 1: input (persistente en cloud)
        rutas.append(os.path.join(folder_paths.get_input_directory(), "titan_vault.json"))
        # Prioridad 2: output (también persistente)
        rutas.append(os.path.join(folder_paths.get_output_directory(), "titan_vault.json"))
    except:
        pass
    
    # Prioridad 3: carpeta local del nodo (siempre disponible)
    rutas.append(os.path.join(os.path.dirname(__file__), "titan_vault.json"))
    
    return rutas


def guardar_en_bunker(nombre: str, texto: str, categoria: str = "general") -> bool:
    """
    Guarda un prompt en el búnker con fallback automático de rutas.
    
    Args:
        nombre: Identificador único del prompt
        texto: Contenido del prompt
        categoria: Categoría opcional para organización
        
    Returns:
        True si se guardó correctamente, False si hubo error
    """
    global DB_FILE
    
    if not nombre or not nombre.strip():
        logger.warning("Nombre vacío, no se puede guardar")
        return False
    
    # Sanitizar nombre
    nombre = nombre.strip()[:100]  # Limitar a 100 caracteres
    
    db = cargar_bunker()
    db[nombre] = {
        "texto": texto,
        "categoria": categoria,
        "fecha": time.time(),
        "fecha_legible": time.strftime("%Y-%m-%d %H:%M:%S"),
        "version": TITAN_VERSION
    }
    
    # Intentar guardar en múltiples rutas (fallback)
    rutas_intentar = _obtener_rutas_fallback()
    
    for ruta in rutas_intentar:
        try:
            # Asegurar que el directorio existe
            directorio = os.path.dirname(ruta)
            if directorio:
                os.makedirs(directorio, exist_ok=True)
            
            with open(ruta, 'w', encoding='utf-8') as f:
                json.dump(db, f, indent=2, ensure_ascii=False)
            
            # Actualizar DB_FILE global si cambió la ruta exitosa
            if ruta != DB_FILE:
                logger.info(f"📁 Ruta de búnker actualizada a: {ruta}")
                DB_FILE = ruta
            
            logger.info(f"💾 Guardado '{nombre}' en: {ruta}")
            return True
            
        except PermissionError:
            logger.warning(f"Sin permisos en: {ruta}, intentando siguiente...")
            continue
        except OSError as e:
            logger.warning(f"Error OS en {ruta}: {e}, intentando siguiente...")
            continue
        except Exception as e:
            logger.warning(f"Error en {ruta}: {e}, intentando siguiente...")
            continue
    
    logger.error("❌ No se pudo guardar en ninguna ruta disponible")
    return False


def eliminar_de_bunker(nombre: str) -> bool:
    """
    Elimina un prompt del búnker.
    
    Args:
        nombre: Identificador del prompt a eliminar
        
    Returns:
        True si se eliminó, False si no existía o hubo error
    """
    db = cargar_bunker()
    if nombre not in db:
        logger.warning(f"'{nombre}' no existe en el búnker")
        return False
    
    del db[nombre]
    
    try:
        with open(DB_FILE, 'w', encoding='utf-8') as f:
            json.dump(db, f, indent=2, ensure_ascii=False)
        logger.info(f"🗑️ Eliminado '{nombre}' del búnker")
        return True
    except Exception as e:
        logger.error(f"Error eliminando del búnker: {e}")
        return False


def listar_bunker() -> list:
    """
    Lista todos los nombres de prompts guardados.
    
    Returns:
        Lista de nombres ordenados por fecha (más reciente primero)
    """
    db = cargar_bunker()
    if not db:
        return []
    
    # Ordenar por fecha descendente
    items = sorted(db.items(), key=lambda x: x[1].get("fecha", 0), reverse=True)
    return [nombre for nombre, _ in items]


# --- MOTOR DE ALEATORIEDAD (WILDCARDS) ---
def procesar_aleatoriedad(texto: str, semilla: int) -> str:
    """
    Procesa wildcards tipo {opcion1|opcion2|opcion3} en el texto.
    Soporta anidación hasta 10 niveles de profundidad.
    
    Args:
        texto: Texto con wildcards
        semilla: Semilla para reproducibilidad
        
    Returns:
        Texto con wildcards resueltos
        
    Example:
        >>> procesar_aleatoriedad("{rojo|azul} {gato|perro}", 42)
        "azul perro"
    """
    if not texto:
        return ""
    
    random.seed(semilla)
    
    def reemplazar(match):
        opciones = match.group(1).split('|')
        # Filtrar opciones vacías
        opciones = [op.strip() for op in opciones if op.strip()]
        if not opciones:
            return ""
        return random.choice(opciones)
    
    resultado = texto
    ciclos = 0
    max_ciclos = 10  # Prevenir loops infinitos
    
    while '{' in resultado and '}' in resultado and ciclos < max_ciclos:
        nuevo_resultado = re.sub(r'\{([^{}]*)\}', reemplazar, resultado)
        if nuevo_resultado == resultado:
            # No hubo cambios, evitar loop
            break
        resultado = nuevo_resultado
        ciclos += 1
    
    if ciclos >= max_ciclos:
        logger.warning("Se alcanzó el límite de ciclos de wildcard")
    
    return resultado


def procesar_wildcards_peso(texto: str, semilla: int) -> str:
    """
    Versión avanzada que soporta pesos: {opcion1::2|opcion2::1}
    El número después de :: indica el peso relativo.
    
    Args:
        texto: Texto con wildcards pesados
        semilla: Semilla para reproducibilidad
        
    Returns:
        Texto con wildcards resueltos considerando pesos
    """
    if not texto:
        return ""
    
    random.seed(semilla)
    
    def reemplazar_pesado(match):
        opciones_raw = match.group(1).split('|')
        opciones = []
        pesos = []
        
        for op in opciones_raw:
            op = op.strip()
            if not op:
                continue
            
            if '::' in op:
                partes = op.rsplit('::', 1)
                try:
                    peso = float(partes[1])
                except ValueError:
                    peso = 1.0
                opciones.append(partes[0].strip())
                pesos.append(max(0.1, peso))  # Peso mínimo 0.1
            else:
                opciones.append(op)
                pesos.append(1.0)
        
        if not opciones:
            return ""
        
        return random.choices(opciones, weights=pesos, k=1)[0]
    
    resultado = texto
    ciclos = 0
    
    while '{' in resultado and '}' in resultado and ciclos < 10:
        nuevo = re.sub(r'\{([^{}]*)\}', reemplazar_pesado, resultado)
        if nuevo == resultado:
            break
        resultado = nuevo
        ciclos += 1
    
    return resultado


# --- UTILIDADES ADICIONALES ---
def limpiar_prompt(texto: str) -> str:
    """
    Limpia y normaliza un prompt.
    - Elimina espacios múltiples
    - Normaliza comas
    - Elimina líneas vacías extras
    """
    if not texto:
        return ""
    
    # Normalizar saltos de línea
    texto = texto.replace('\r\n', '\n').replace('\r', '\n')
    
    # Eliminar espacios múltiples
    texto = re.sub(r' +', ' ', texto)
    
    # Normalizar comas (espacio después, no antes)
    texto = re.sub(r'\s*,\s*', ', ', texto)
    
    # Eliminar líneas vacías múltiples
    texto = re.sub(r'\n\s*\n', '\n', texto)
    
    return texto.strip()


def obtener_info_sistema() -> Dict[str, Any]:
    """Retorna información del sistema para debugging."""
    info = {
        "titan_version": TITAN_VERSION,
        "db_path": DB_FILE,
        "db_existe": os.path.exists(DB_FILE),
        "presets_count": len(PRESETS),
    }
    
    try:
        import torch
        info["torch_version"] = torch.__version__
        info["cuda_disponible"] = torch.cuda.is_available()
        if torch.cuda.is_available():
            info["gpu_nombre"] = torch.cuda.get_device_name(0)
    except:
        pass
    
    return info
