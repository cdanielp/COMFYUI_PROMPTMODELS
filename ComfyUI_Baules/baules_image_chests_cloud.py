"""
Baúles de Imágenes (Cloud Ref) - Output STRING
5 nodos para referencias remotas (URLs, asset_ids, S3 keys)
Compatible con ComfyDeploy/RunningHub → External Image
"""
from typing import Dict, Any, Tuple, List
import json

class BaseImageChestCloudRef:
    """Clase base para baúles de referencias cloud"""
    
    # Sobreescribir en subclases
    CHEST_TYPE = "imagenes"
    DISPLAY_NAME = "🧰 Baúl Imágenes (Cloud Ref)"
    
    @classmethod
    def INPUT_TYPES(cls) -> Dict[str, Any]:
        return {
            "required": {
                "🔗 Acción": ([
                    "Nada",
                    "Agregar referencia(s)",
                    "Eliminar seleccionado",
                    "Limpiar lista"
                ],),
                "🖼️ Selección": ("STRING", {
                    "default": "",
                    "multiline": False,
                    "placeholder": "Pega aquí la referencia a usar"
                }),
            },
            "optional": {
                "📎 Agregar": ("STRING", {
                    "default": "",
                    "multiline": True,
                    "placeholder": "Pega URL o múltiples referencias (una por línea)"
                }),
            },
            "hidden": {
                "unique_id": "UNIQUE_ID",
                "referencias_internas": ("STRING", {"default": ""}),
            }
        }
    
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("referencia",)
    FUNCTION = "execute"
    CATEGORY = "Baúles/Cloud Ref"
    
    def __init__(self):
        self.referencias: List[str] = []
        self.referencias_json_actualizado = ""
    
    def _parse_referencias_input(self, text: str) -> List[str]:
        """Parsea el input de referencias (multilinea o separado por comas)"""
        if not text.strip():
            return []
        
        # Soporta múltiples formatos: líneas, comas, espacios
        lines = text.strip().split('\n')
        refs = []
        for line in lines:
            line = line.strip()
            if not line:
                continue
            # Si la línea tiene comas, dividir
            if ',' in line:
                refs.extend([r.strip() for r in line.split(',') if r.strip()])
            else:
                refs.append(line)
        
        return refs
    
    def _load_referencias(self, referencias_json: str) -> List[str]:
        """Carga las referencias desde el storage del widget"""
        if not referencias_json or not referencias_json.strip():
            return []
        
        try:
            return json.loads(referencias_json)
        except Exception:
            return []
    
    def _save_referencias(self, refs: List[str]) -> str:
        """Guarda las referencias como JSON string"""
        return json.dumps(refs, ensure_ascii=False)
    
    def execute(self, **kwargs) -> Tuple[str]:
        """
        Ejecuta la lógica del nodo
        
        Regla: NO descarga imágenes, solo devuelve STRING
        """
        accion = kwargs.get("🔗 Acción", "Nada")
        seleccion = kwargs.get("🖼️ Selección", "")
        agregar_input = kwargs.get("📎 Agregar", "")
        referencias_json = kwargs.get("referencias_internas", "")
        
        # Cargar referencias existentes
        self.referencias = self._load_referencias(referencias_json)
        modificado = False
        
        # Procesar acciones
        if accion == "Agregar referencia(s)":
            nuevas_refs = self._parse_referencias_input(agregar_input)
            if nuevas_refs:
                # Añadir solo las que no existen
                agregadas = 0
                for ref in nuevas_refs:
                    if ref not in self.referencias:
                        self.referencias.append(ref)
                        agregadas += 1
                
                # CORRECCIÓN 1.1: Guardar persistencia
                self.referencias_json_actualizado = self._save_referencias(self.referencias)
                modificado = True
                
                # Mensaje informativo
                mensaje = (
                    f"✅ Se añadieron {agregadas} referencia(s) nuevas.\n"
                    f"Total en lista: {len(self.referencias)}.\n"
                    f"Lista actualizada:\n" + "\n".join(f"  - {r[:60]}..." for r in self.referencias[-5:])
                )
                print(mensaje)
        
        elif accion == "Eliminar seleccionado":
            if seleccion and seleccion in self.referencias:
                self.referencias.remove(seleccion)
                # CORRECCIÓN 1.1: Guardar persistencia
                self.referencias_json_actualizado = self._save_referencias(self.referencias)
                modificado = True
                print(f"✅ Referencia eliminada: {seleccion[:50]}...")
        
        elif accion == "Limpiar lista":
            self.referencias.clear()
            # CORRECCIÓN 1.1: Guardar persistencia
            self.referencias_json_actualizado = self._save_referencias(self.referencias)
            modificado = True
            print("✅ Lista de referencias limpiada.")
        
        # CORRECCIÓN 1.2: Validación con STRING input
        if not seleccion or not seleccion.strip():
            raise ValueError(
                f"❌ {self.DISPLAY_NAME}: Debes pegar una referencia en '🖼️ Selección'.\n"
                f"Usa 'Agregar referencia(s)' primero para poblar la lista,\n"
                f"luego copia una referencia al campo de selección."
            )
        
        seleccion = seleccion.strip()
        
        if seleccion not in self.referencias:
            raise ValueError(
                f"❌ Referencia '{seleccion[:50]}...' no existe en la lista.\n"
                f"Referencias disponibles: {len(self.referencias)}\n"
                f"Primeras: {', '.join(r[:30] for r in self.referencias[:3])}"
            )
        
        # Devolver la referencia como STRING
        return (seleccion,)
    
    @classmethod
    def IS_CHANGED(cls, **kwargs) -> str:
        """Hash basado en la selección actual"""
        seleccion = kwargs.get("🖼️ Selección", "")
        referencias_json = kwargs.get("referencias_internas", "")
        
        import hashlib
        combined = f"{referencias_json}_{seleccion}"
        return hashlib.sha256(combined.encode()).hexdigest()[:16]


# ============================================================================
# Nodos Específicos (5 tipos cloud ref)
# ============================================================================

class ImageChestCloudRef(BaseImageChestCloudRef):
    """🧰 Baúl Imágenes (Cloud Ref)"""
    CHEST_TYPE = "imagenes"
    DISPLAY_NAME = "🧰 Baúl Imágenes (Cloud Ref)"

class OpenPoseChestCloudRef(BaseImageChestCloudRef):
    """🧍 Baúl OpenPose (Cloud Ref)"""
    CHEST_TYPE = "openpose"
    DISPLAY_NAME = "🧍 Baúl OpenPose (Cloud Ref)"

class DepthChestCloudRef(BaseImageChestCloudRef):
    """🗺️ Baúl Depth (Cloud Ref)"""
    CHEST_TYPE = "depth"
    DISPLAY_NAME = "🗺️ Baúl Depth (Cloud Ref)"

class LineartChestCloudRef(BaseImageChestCloudRef):
    """✍️ Baúl Lineart (Cloud Ref)"""
    CHEST_TYPE = "lineart"
    DISPLAY_NAME = "✍️ Baúl Lineart (Cloud Ref)"

class Chest3DCloudRef(BaseImageChestCloudRef):
    """🧊 Baúl 3D / Referencias (Cloud Ref)"""
    CHEST_TYPE = "3d"
    DISPLAY_NAME = "🧊 Baúl 3D / Referencias (Cloud Ref)"


# ============================================================================
# Mapeo de Nodos
# ============================================================================

NODE_CLASS_MAPPINGS = {
    "ImageChestCloudRef": ImageChestCloudRef,
    "OpenPoseChestCloudRef": OpenPoseChestCloudRef,
    "DepthChestCloudRef": DepthChestCloudRef,
    "LineartChestCloudRef": LineartChestCloudRef,
    "Chest3DCloudRef": Chest3DCloudRef,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "ImageChestCloudRef": "🧰 Baúl Imágenes (Cloud Ref)",
    "OpenPoseChestCloudRef": "🧍 Baúl OpenPose (Cloud Ref)",
    "DepthChestCloudRef": "🗺️ Baúl Depth (Cloud Ref)",
    "LineartChestCloudRef": "✍️ Baúl Lineart (Cloud Ref)",
    "Chest3DCloudRef": "🧊 Baúl 3D / Referencias (Cloud Ref)",
}