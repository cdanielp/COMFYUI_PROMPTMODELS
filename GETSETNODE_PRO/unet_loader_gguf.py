"""
PRO_UnetLoaderGGUF - Cargador de modelos GGUF
"""

import os
import torch
from typing import Tuple, Any, List, Optional

try:
    import folder_paths
    FOLDER_PATHS_AVAILABLE = True
except ImportError:
    FOLDER_PATHS_AVAILABLE = False

GGUF_AVAILABLE = False
try:
    from gguf import load_gguf_sd, GGUFModelPatcher
    GGUF_AVAILABLE = True
    GGUF_BACKEND = "city96"
except ImportError:
    try:
        import gguf as gguf_lib
        GGUF_AVAILABLE = True
        GGUF_BACKEND = "gguf-py"
    except ImportError:
        GGUF_BACKEND = None

def get_unet_files() -> List[str]:
    if not FOLDER_PATHS_AVAILABLE:
        return ["(folder_paths not available)"]
    files = []
    extensions = (".gguf", ".safetensors", ".ckpt", ".pt", ".pth", ".bin")
    folder_names = ["unet", "diffusion_models", "checkpoints"]
    for folder_name in folder_names:
        try:
            paths = folder_paths.get_folder_paths(folder_name)
            for base_path in paths:
                if not os.path.exists(base_path): continue
                for root, dirs, filenames in os.walk(base_path):
                    for filename in filenames:
                        if filename.lower().endswith(extensions):
                            rel_path = os.path.relpath(os.path.join(root, filename), base_path)
                            if rel_path not in files: files.append(rel_path)
        except: pass
    return sorted(set(files)) if files else ["none"]

class PRO_UnetLoaderGGUF:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "unet_name": (get_unet_files(), {"tooltip": "Modelo GGUF"}),
            },
        }

    RETURN_TYPES = ("MODEL",)
    RETURN_NAMES = ("model",)
    FUNCTION = "load_unet"
    CATEGORY = "GetSetNode_Pro/loaders"

    def load_unet(self, unet_name: str) -> Tuple[Any]:
        model_path = self._find_model(unet_name)
        if model_path is None:
            raise FileNotFoundError(f"[PRO_UnetLoader] Not found: {unet_name}")
        
        ext = os.path.splitext(model_path)[1].lower()
        if ext == ".gguf":
            model = self._load_gguf(model_path)
        elif ext == ".safetensors":
            model = self._load_safetensors(model_path)
        elif ext in (".ckpt", ".pt", ".pth"):
            model = self._load_checkpoint(model_path)
        elif ext == ".bin":
            model = self._load_bin(model_path)
        else:
            raise ValueError(f"Unsupported: {ext}")
        return (model,)

    def _find_model(self, filename: str) -> Optional[str]:
        if not FOLDER_PATHS_AVAILABLE: return filename if os.path.exists(filename) else None
        folder_names = ["unet", "diffusion_models", "checkpoints"]
        for folder_name in folder_names:
            try:
                paths = folder_paths.get_folder_paths(folder_name)
                for base_path in paths:
                    full_path = os.path.join(base_path, filename)
                    if os.path.exists(full_path): return full_path
            except: pass
        return filename if os.path.exists(filename) else None

    def _load_gguf(self, path: str) -> Any:
        if not GGUF_AVAILABLE: raise ImportError("Requires ComfyUI-GGUF")
        if GGUF_BACKEND == "city96":
            sd = load_gguf_sd(path)
            return GGUFModelPatcher.from_state_dict(sd)
        else:
            import gguf as gguf_lib
            reader = gguf_lib.GGUFReader(path)
            state_dict = {}
            for tensor in reader.tensors:
                state_dict[tensor.name] = torch.from_numpy(tensor.data.copy())
            return state_dict

    def _load_safetensors(self, path: str) -> dict:
        from safetensors.torch import load_file
        return load_file(path, device="cuda" if torch.cuda.is_available() else "cpu")

    def _load_checkpoint(self, path: str) -> dict:
        data = torch.load(path, map_location="cuda" if torch.cuda.is_available() else "cpu", weights_only=False)
        if isinstance(data, dict):
            if "state_dict" in data: data = data["state_dict"]
            elif "model" in data: data = data["model"]
            elif "unet" in data: data = data["unet"]
        return data

    def _load_bin(self, path: str) -> dict:
        return torch.load(path, map_location="cuda" if torch.cuda.is_available() else "cpu", weights_only=False)

class PRO_UnetLoaderGGUFAdvanced(PRO_UnetLoaderGGUF):
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {"unet_name": (get_unet_files(), {})},
            "optional": {
                "dtype": (["auto", "float32", "float16", "bfloat16"], {"default": "auto"}),
                "force_cpu": ("BOOLEAN", {"default": False}),
            }
        }

    RETURN_TYPES = ("MODEL", "STRING")
    RETURN_NAMES = ("model", "info")
    FUNCTION = "load_unet_advanced"
    CATEGORY = "GetSetNode_Pro/loaders"

    def load_unet_advanced(self, unet_name: str, dtype: str = "auto", force_cpu: bool = False) -> Tuple[Any, str]:
        model, _ = self.load_unet(unet_name)[0], ""
        if dtype != "auto" and isinstance(model, dict):
            dt_map = {"float32": torch.float32, "float16": torch.float16, "bfloat16": torch.bfloat16}
            target = dt_map.get(dtype)
            if target:
                model = {k: v.to(target) if hasattr(v, 'to') and v.is_floating_point() else v for k, v in model.items()}
        if force_cpu and isinstance(model, dict):
            model = {k: v.cpu() if hasattr(v, 'cpu') else v for k, v in model.items()}
        return (model, f"Loaded {unet_name}")