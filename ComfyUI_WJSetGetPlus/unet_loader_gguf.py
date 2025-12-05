"""
UnetLoaderGGUF - Cargador de modelos GGUF para ComfyUI
Compatible con ComfyUI-GGUF de city96 y modelos safetensors/ckpt

IMPORTANTE: Para modelos .gguf, requiere ComfyUI-GGUF instalado:
  git clone https://github.com/city96/ComfyUI-GGUF custom_nodes/ComfyUI-GGUF
"""

import os
import torch
from typing import Tuple, Any, List, Optional

# Importar folder_paths de ComfyUI
try:
    import folder_paths
    FOLDER_PATHS_AVAILABLE = True
except ImportError:
    FOLDER_PATHS_AVAILABLE = False
    print("[UnetLoaderGGUF] Warning: folder_paths not available (not in ComfyUI?)")

# Intentar importar ComfyUI-GGUF
GGUF_AVAILABLE = False
try:
    # ComfyUI-GGUF de city96
    from gguf import load_gguf_sd, GGUFModelPatcher
    GGUF_AVAILABLE = True
    GGUF_BACKEND = "city96"
except ImportError:
    try:
        # Alternativa: solo gguf sin el patcher
        import gguf as gguf_lib
        GGUF_AVAILABLE = True
        GGUF_BACKEND = "gguf-py"
    except ImportError:
        GGUF_BACKEND = None


def get_unet_files() -> List[str]:
    """
    Obtiene lista de archivos de modelo UNET disponibles.
    Busca en las carpetas estándar de ComfyUI.
    """
    if not FOLDER_PATHS_AVAILABLE:
        return ["(folder_paths not available)"]
    
    files = []
    extensions = (".gguf", ".safetensors", ".ckpt", ".pt", ".pth", ".bin")
    
    # Carpetas donde buscar
    folder_names = ["unet", "diffusion_models", "checkpoints"]
    
    for folder_name in folder_names:
        try:
            paths = folder_paths.get_folder_paths(folder_name)
            for base_path in paths:
                if not os.path.exists(base_path):
                    continue
                for root, dirs, filenames in os.walk(base_path):
                    for filename in filenames:
                        if filename.lower().endswith(extensions):
                            # Ruta relativa al folder base
                            rel_path = os.path.relpath(os.path.join(root, filename), base_path)
                            if rel_path not in files:
                                files.append(rel_path)
        except:
            pass
    
    return sorted(set(files)) if files else ["none"]


class UnetLoaderGGUF:
    """
    Carga modelos de difusión UNET en formato GGUF (cuantizados).
    También soporta .safetensors y .ckpt como fallback.
    
    Los modelos GGUF usan cuantización (Q4, Q5, Q6, Q8) para reducir
    el uso de VRAM manteniendo buena calidad.
    
    Requiere: ComfyUI-GGUF para archivos .gguf
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        unet_files = get_unet_files()
        
        return {
            "required": {
                "unet_name": (unet_files, {
                    "tooltip": "Modelo GGUF o safetensors a cargar"
                }),
            },
        }

    RETURN_TYPES = ("MODEL",)
    RETURN_NAMES = ("model",)
    FUNCTION = "load_unet"
    CATEGORY = "loaders"
    DESCRIPTION = "Carga modelos UNET cuantizados en formato GGUF"

    def load_unet(self, unet_name: str) -> Tuple[Any]:
        """
        Carga el modelo UNET especificado.
        
        Args:
            unet_name: Nombre del archivo del modelo
            
        Returns:
            Tuple con el modelo cargado (ModelPatcher o state_dict)
        """
        # Encontrar la ruta completa
        model_path = self._find_model(unet_name)
        
        if model_path is None:
            raise FileNotFoundError(
                f"[UnetLoaderGGUF] Model not found: {unet_name}\n"
                f"Place it in: ComfyUI/models/unet/ or ComfyUI/models/diffusion_models/"
            )
        
        ext = os.path.splitext(model_path)[1].lower()
        print(f"[UnetLoaderGGUF] Loading: {os.path.basename(model_path)}")
        
        # Cargar según extensión
        if ext == ".gguf":
            model = self._load_gguf(model_path)
        elif ext == ".safetensors":
            model = self._load_safetensors(model_path)
        elif ext in (".ckpt", ".pt", ".pth"):
            model = self._load_checkpoint(model_path)
        elif ext == ".bin":
            model = self._load_bin(model_path)
        else:
            raise ValueError(f"[UnetLoaderGGUF] Unsupported format: {ext}")
        
        print(f"[UnetLoaderGGUF] ✓ Model loaded successfully")
        return (model,)

    def _find_model(self, filename: str) -> Optional[str]:
        """Busca el modelo en las carpetas de ComfyUI."""
        if not FOLDER_PATHS_AVAILABLE:
            # Fallback: asumir ruta directa
            if os.path.exists(filename):
                return filename
            return None
        
        folder_names = ["unet", "diffusion_models", "checkpoints"]
        
        for folder_name in folder_names:
            try:
                paths = folder_paths.get_folder_paths(folder_name)
                for base_path in paths:
                    full_path = os.path.join(base_path, filename)
                    if os.path.exists(full_path):
                        return full_path
            except:
                pass
        
        # Último intento: ruta absoluta
        if os.path.exists(filename):
            return filename
        
        return None

    def _load_gguf(self, path: str) -> Any:
        """Carga un modelo GGUF usando ComfyUI-GGUF."""
        if not GGUF_AVAILABLE:
            raise ImportError(
                "[UnetLoaderGGUF] GGUF support requires ComfyUI-GGUF!\n"
                "Install it:\n"
                "  cd ComfyUI/custom_nodes\n"
                "  git clone https://github.com/city96/ComfyUI-GGUF\n"
                "  pip install gguf"
            )
        
        if GGUF_BACKEND == "city96":
            # Usar el cargador oficial de city96
            sd = load_gguf_sd(path)
            model = GGUFModelPatcher.from_state_dict(sd)
            return model
        else:
            # Fallback: cargar como state_dict raw
            import gguf as gguf_lib
            reader = gguf_lib.GGUFReader(path)
            state_dict = {}
            for tensor in reader.tensors:
                state_dict[tensor.name] = torch.from_numpy(tensor.data.copy())
            return state_dict

    def _load_safetensors(self, path: str) -> dict:
        """Carga un modelo safetensors."""
        try:
            from safetensors.torch import load_file
        except ImportError:
            raise ImportError(
                "[UnetLoaderGGUF] safetensors not installed!\n"
                "Run: pip install safetensors"
            )
        
        device = "cuda" if torch.cuda.is_available() else "cpu"
        state_dict = load_file(path, device=device)
        print(f"[UnetLoaderGGUF] Loaded {len(state_dict)} tensors from safetensors")
        return state_dict

    def _load_checkpoint(self, path: str) -> dict:
        """Carga un checkpoint PyTorch."""
        device = "cuda" if torch.cuda.is_available() else "cpu"
        
        # Cargar con weights_only=False para compatibilidad
        data = torch.load(path, map_location=device, weights_only=False)
        
        # Extraer state_dict si está envuelto
        if isinstance(data, dict):
            if "state_dict" in data:
                data = data["state_dict"]
            elif "model" in data:
                data = data["model"]
            elif "unet" in data:
                data = data["unet"]
        
        print(f"[UnetLoaderGGUF] Loaded checkpoint")
        return data

    def _load_bin(self, path: str) -> dict:
        """Carga un archivo .bin (formato HuggingFace)."""
        device = "cuda" if torch.cuda.is_available() else "cpu"
        # weights_only=False para compatibilidad con PyTorch < 2.2
        state_dict = torch.load(path, map_location=device, weights_only=False)
        print(f"[UnetLoaderGGUF] Loaded .bin with {len(state_dict)} tensors")
        return state_dict


class UnetLoaderGGUFAdvanced(UnetLoaderGGUF):
    """
    Versión avanzada con opciones de dispositivo y dtype.
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        unet_files = get_unet_files()
        
        return {
            "required": {
                "unet_name": (unet_files, {}),
            },
            "optional": {
                "dtype": (["auto", "float32", "float16", "bfloat16"], {"default": "auto"}),
                "force_cpu": ("BOOLEAN", {"default": False}),
            }
        }

    RETURN_TYPES = ("MODEL", "STRING")
    RETURN_NAMES = ("model", "info")
    FUNCTION = "load_unet_advanced"
    CATEGORY = "loaders"

    def load_unet_advanced(self, unet_name: str, dtype: str = "auto", 
                           force_cpu: bool = False) -> Tuple[Any, str]:
        """Carga con opciones avanzadas."""
        # Cargar modelo base
        model_tuple = self.load_unet(unet_name)
        model = model_tuple[0]
        
        # Aplicar dtype si es state_dict
        if dtype != "auto" and isinstance(model, dict):
            dtype_map = {
                "float32": torch.float32,
                "float16": torch.float16,
                "bfloat16": torch.bfloat16
            }
            target_dtype = dtype_map.get(dtype)
            if target_dtype:
                model = {
                    k: v.to(target_dtype) if hasattr(v, 'to') and v.is_floating_point() else v
                    for k, v in model.items()
                }
        
        # Mover a CPU si se requiere
        if force_cpu and isinstance(model, dict):
            model = {k: v.cpu() if hasattr(v, 'cpu') else v for k, v in model.items()}
        
        # Info
        device = "cpu" if force_cpu else ("cuda" if torch.cuda.is_available() else "cpu")
        info = f"Model: {unet_name}, Device: {device}, Dtype: {dtype}"
        
        return (model, info)
