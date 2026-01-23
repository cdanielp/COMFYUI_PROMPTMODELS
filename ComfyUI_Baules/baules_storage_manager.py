"""
Storage Manager Local - Sistema de persistencia GLOBAL por tipo de baúl
CORRECCIÓN CRÍTICA: Storage compartido entre todos los nodos del mismo tipo
"""
import os
import json
import uuid
import hashlib
import time
import shutil
from typing import Dict, List, Optional, Any
from pathlib import Path


class StorageManagerLocal:
    """
    Gestiona almacenamiento GLOBAL por tipo de baúl.
    
    CORRECCIÓN 1: Eliminado unique_id del path.
    Estructura: COMFYUI_ROOT/user/baules/<tipo>/
    """
    
    # Extensiones de imagen soportadas
    IMAGE_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.webp', '.bmp', '.tiff', '.tif'}
    
    def __init__(self, comfy_root: str, chest_type: str):
        """
        Args:
            comfy_root: Ruta raíz de ComfyUI
            chest_type: Tipo de baúl (imagenes, openpose, depth, lineart)
        """
        self.chest_type = chest_type
        
        # CORRECCIÓN 1: Rutas GLOBALES por tipo (sin unique_id)
        self.base_path = Path(comfy_root) / "user" / "baules" / chest_type
        self.files_path = self.base_path / "files"
        self.thumbs_path = self.base_path / "thumbs"
        self.index_path = self.base_path / "index.json"
        
        # Crear directorios si no existen
        self._ensure_directories()
    
    def _ensure_directories(self):
        """Crea la estructura de directorios necesaria"""
        self.files_path.mkdir(parents=True, exist_ok=True)
        self.thumbs_path.mkdir(parents=True, exist_ok=True)
    
    def _load_catalog(self) -> Dict[str, Any]:
        """Carga el catálogo desde index.json"""
        if not self.index_path.exists():
            return {"version": 1, "items": []}
        
        try:
            with open(self.index_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"⚠️ Error cargando catálogo {self.index_path}: {e}")
            return {"version": 1, "items": []}
    
    def _save_catalog(self, catalog: Dict[str, Any]):
        """
        CORRECCIÓN 6: Guarda el catálogo con escritura atómica
        """
        try:
            # Escribir a archivo temporal primero
            tmp_path = self.index_path.with_suffix('.json.tmp')
            
            with open(tmp_path, 'w', encoding='utf-8') as f:
                json.dump(catalog, f, indent=2, ensure_ascii=False)
            
            # CORRECCIÓN 6: Reemplazar atómicamente
            os.replace(tmp_path, self.index_path)
            
        except IOError as e:
            raise RuntimeError(f"Error guardando catálogo: {e}")
    
    def get_items_list(self) -> List[Dict[str, Any]]:
        """Obtiene la lista de items del catálogo"""
        catalog = self._load_catalog()
        return catalog.get("items", [])
    
    def get_item_by_id(self, item_id: str) -> Optional[Dict[str, Any]]:
        """Obtiene un item específico por ID"""
        items = self.get_items_list()
        for item in items:
            if item.get("id") == item_id:
                return item
        return None
    
    def add_file(self, source_path: str, name: Optional[str] = None, 
                 tags: List[str] = None, favorite: bool = False) -> str:
        """
        Añade un archivo al baúl
        
        Args:
            source_path: Ruta al archivo original
            name: Nombre personalizado (opcional)
            tags: Lista de tags
            favorite: Marcar como favorito
            
        Returns:
            item_id del nuevo item
        """
        source = Path(source_path)
        if not source.exists():
            raise FileNotFoundError(f"Archivo no encontrado: {source_path}")
        
        # Generar ID único
        item_id = str(uuid.uuid4())[:8]  # ID corto
        
        # Nombre final
        final_name = name if name else source.stem
        
        # Copiar archivo a files/
        dest_filename = f"{item_id}{source.suffix}"
        dest_path = self.files_path / dest_filename
        
        shutil.copy2(source, dest_path)
        
        # CORRECCIÓN 5: Metadata solo para imágenes
        ext = source.suffix.lower()
        meta = {}
        
        if ext in self.IMAGE_EXTENSIONS:
            try:
                from PIL import Image
                with Image.open(dest_path) as img:
                    meta = {
                        "w": img.width,
                        "h": img.height,
                        "format": img.format.lower() if img.format else "unknown"
                    }
            except Exception as e:
                print(f"⚠️ No se pudo leer metadata de imagen {dest_filename}: {e}")
                meta = {"w": None, "h": None, "format": ext[1:]}
        else:
            # CORRECCIÓN 5: Archivo no-imagen, metadata básica
            meta = {
                "w": None,
                "h": None,
                "format": ext[1:] if ext else "unknown"
            }
        
        # Crear item en catálogo
        catalog = self._load_catalog()
        new_item = {
            "id": item_id,
            "name": final_name,
            "relpath": f"files/{dest_filename}",
            "tags": tags or [],
            "favorite": favorite,
            "created_at": int(time.time()),
            "meta": meta
        }
        
        catalog["items"].append(new_item)
        self._save_catalog(catalog)
        
        return item_id
    
    def delete_item(self, item_id: str) -> bool:
        """Elimina un item del baúl"""
        catalog = self._load_catalog()
        items = catalog.get("items", [])
        
        # Buscar item
        item_to_delete = None
        for i, item in enumerate(items):
            if item.get("id") == item_id:
                item_to_delete = items.pop(i)
                break
        
        if not item_to_delete:
            return False
        
        # Eliminar archivo físico
        file_path = self.base_path / item_to_delete.get("relpath", "")
        if file_path.exists():
            try:
                file_path.unlink()
            except Exception as e:
                print(f"⚠️ Error eliminando archivo {file_path}: {e}")
        
        # Guardar catálogo actualizado
        self._save_catalog(catalog)
        return True
    
    def clear_chest(self):
        """Limpia completamente el baúl"""
        catalog = self._load_catalog()
        
        # Eliminar todos los archivos de files/
        if self.files_path.exists():
            for file in self.files_path.iterdir():
                if file.is_file():
                    try:
                        file.unlink()
                    except Exception as e:
                        print(f"⚠️ Error eliminando {file}: {e}")
        
        # Limpiar también thumbs/
        if self.thumbs_path.exists():
            for thumb in self.thumbs_path.iterdir():
                if thumb.is_file():
                    try:
                        thumb.unlink()
                    except Exception as e:
                        print(f"⚠️ Error eliminando thumb {thumb}: {e}")
        
        # Resetear catálogo
        catalog["items"] = []
        self._save_catalog(catalog)
    
    def get_file_path(self, item_id: str) -> Optional[Path]:
        """Obtiene la ruta física del archivo de un item"""
        item = self.get_item_by_id(item_id)
        if not item:
            return None
        
        relpath = item.get("relpath")
        if not relpath:
            return None
        
        file_path = self.base_path / relpath
        return file_path if file_path.exists() else None
    
    def update_item_metadata(self, item_id: str, **kwargs):
        """Actualiza metadata de un item (name, tags, favorite)"""
        catalog = self._load_catalog()
        items = catalog.get("items", [])
        
        for item in items:
            if item.get("id") == item_id:
                for key, value in kwargs.items():
                    if key in ["name", "tags", "favorite"]:
                        item[key] = value
                break
        
        self._save_catalog(catalog)
    
    def get_catalog_hash(self) -> str:
        """
        CORRECCIÓN 7: Genera hash del catálogo GLOBAL para IS_CHANGED
        """
        catalog = self._load_catalog()
        catalog_str = json.dumps(catalog, sort_keys=True)
        return hashlib.sha256(catalog_str.encode()).hexdigest()[:16]
