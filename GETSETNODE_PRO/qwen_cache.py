"""
QwenCache - Sistema de memoria global para ComfyUI
Compatible con rgthree-comfy SetNode/GetNode
"""

import time
import threading
from typing import Any, Dict, Optional, Tuple

# ============================================================================
# TIPOS SOPORTADOS POR COMFYUI
# ============================================================================
COMFY_TYPES = [
    "MODEL", "CLIP", "VAE", "LATENT", "IMAGE", "MASK",
    "CONDITIONING", "CONTROL_NET", "STYLE_MODEL", "GLIGEN",
    "UPSCALE_MODEL", "CLIP_VISION", "CLIP_VISION_OUTPUT",
    "SAMPLER", "SIGMAS", "NOISE", "GUIDER", "STRING", "INT", "FLOAT"
]


def detect_comfy_type(value: Any) -> str:
    """
    Detecta el tipo ComfyUI de un valor basándose en su estructura.
    
    Args:
        value: El valor a analizar
        
    Returns:
        String con el tipo ComfyUI detectado
    """
    if value is None:
        return "*"
    
    type_name = type(value).__name__
    module = type(value).__module__ if hasattr(type(value), '__module__') else ""
    
    # Detección por nombre de clase
    class_mappings = {
        "ModelPatcher": "MODEL",
        "CLIP": "CLIP", 
        "VAE": "VAE",
        "ControlNet": "CONTROL_NET",
        "T2IAdapter": "CONTROL_NET",
        "StyleModel": "STYLE_MODEL",
        "CLIPVisionModel": "CLIP_VISION",
    }
    
    for class_name, comfy_type in class_mappings.items():
        if class_name in type_name:
            return comfy_type
    
    # Detección por estructura de diccionario
    if isinstance(value, dict):
        if "samples" in value:
            return "LATENT"
        if "cond" in value or len(value) > 0 and isinstance(list(value.values())[0], tuple):
            return "CONDITIONING"
    
    # Detección por lista de condiciones
    if isinstance(value, list) and len(value) > 0:
        first = value[0]
        if isinstance(first, (list, tuple)) and len(first) >= 2:
            return "CONDITIONING"
    
    # Detección por tensor
    try:
        import torch
        if isinstance(value, torch.Tensor):
            # 4D con shape típico de imagen (B, C, H, W)
            if value.dim() == 4:
                if value.shape[1] in (1, 3, 4):  # Grayscale, RGB, RGBA
                    return "IMAGE"
                return "LATENT"
            # 3D podría ser máscara
            if value.dim() == 3:
                return "MASK"
    except ImportError:
        pass
    
    # Tipos primitivos
    if isinstance(value, str):
        return "STRING"
    if isinstance(value, int):
        return "INT"
    if isinstance(value, float):
        return "FLOAT"
    
    return "*"


# ============================================================================
# CACHE SINGLETON
# ============================================================================
class QwenCache:
    """
    Singleton thread-safe para almacenar variables entre nodos.
    """
    _instance: Optional['QwenCache'] = None
    _lock = threading.Lock()
    _initialized = False

    def __new__(cls) -> 'QwenCache':
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not QwenCache._initialized:
            with QwenCache._lock:
                if not QwenCache._initialized:
                    self._data: Dict[str, dict] = {}
                    self._data_lock = threading.RLock()
                    QwenCache._initialized = True

    def set(self, name: str, value: Any, dtype: str = None) -> str:
        """
        Almacena un valor. Detecta el tipo automáticamente si no se proporciona.
        
        Returns:
            El tipo detectado/asignado
        """
        if dtype is None or dtype == "*":
            dtype = detect_comfy_type(value)
        
        with self._data_lock:
            self._data[name] = {
                "value": value,
                "type": dtype,
                "time": time.time()
            }
        return dtype

    def get(self, name: str) -> Optional[Any]:
        """Recupera un valor por nombre."""
        with self._data_lock:
            entry = self._data.get(name)
            return entry["value"] if entry else None

    def get_with_type(self, name: str) -> Tuple[Optional[Any], str]:
        """Recupera valor y tipo."""
        with self._data_lock:
            entry = self._data.get(name)
            if entry:
                return entry["value"], entry["type"]
            return None, "*"

    def get_type(self, name: str) -> str:
        """Obtiene el tipo de un valor."""
        with self._data_lock:
            entry = self._data.get(name)
            return entry["type"] if entry else "*"

    def exists(self, name: str) -> bool:
        """Verifica si existe un valor."""
        with self._data_lock:
            return name in self._data

    def list_all(self) -> Dict[str, str]:
        """Lista todas las variables con sus tipos."""
        with self._data_lock:
            return {k: v["type"] for k, v in self._data.items()}

    def list_names(self) -> list:
        """Lista nombres de variables."""
        with self._data_lock:
            return list(self._data.keys())

    def remove(self, name: str) -> bool:
        """Elimina una variable."""
        with self._data_lock:
            if name in self._data:
                del self._data[name]
                return True
            return False

    def clear(self) -> None:
        """Limpia toda la caché."""
        with self._data_lock:
            self._data.clear()


# Instancia global
_cache = QwenCache()

def get_cache() -> QwenCache:
    """Obtiene la instancia del caché."""
    return _cache
