import os
import folder_paths
from nodes import LoadImage

"""
Baules (Chests) - Implementación Local
Este archivo contiene la lógica para cargar imágenes desde el directorio 'input'
clasificándolas en diferentes nodos para mejor organización.
"""

class BaseChestLocal(LoadImage):
    """
    Clase base que hereda de LoadImage. 
    Permite cargar imágenes subidas o existentes en la carpeta 'input'.
    """
    @classmethod
    def INPUT_TYPES(s):
        input_dir = folder_paths.get_input_directory()
        files = [f for f in os.listdir(input_dir) if os.path.isfile(os.path.join(input_dir, f))]
        # Filtrar extensiones de imagen válidas
        files = [f for f in files if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp', '.bmp', '.tiff'))]
        return {
            "required": {
                "image": (sorted(files), {"image_upload": True})
            }
        }

    CATEGORY = "Baules/Local"
    RETURN_TYPES = ("IMAGE", "MASK")
    FUNCTION = "load_image"

# ============================================================================
# IMPLEMENTACIONES ESPECÍFICAS
# ============================================================================

class ImageChestLocal(BaseChestLocal):
    """Baúl para imágenes generales"""
    CATEGORY = "Baules/Local"
    
class OpenPoseChestLocal(BaseChestLocal):
    """Baúl específico para referencias de OpenPose"""
    CATEGORY = "Baules/Local/ControlNet"

class DepthChestLocal(BaseChestLocal):
    """Baúl específico para mapas de profundidad"""
    CATEGORY = "Baules/Local/ControlNet"

class LineartChestLocal(BaseChestLocal):
    """Baúl específico para Lineart/Bocetos"""
    CATEGORY = "Baules/Local/ControlNet"
