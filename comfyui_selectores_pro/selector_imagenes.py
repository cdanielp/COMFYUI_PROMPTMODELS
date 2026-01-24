"""
Selector de imágenes
====================
Selecciona y combina múltiples imágenes con sus máscaras.
"""

import torch
from typing import Dict, Any, Tuple, List

# Configuración
N_SLOTS: int = 12
CATEGORY: str = "Selectores Pro"


class SelectorDeImagenes:
    """
    Selecciona y combina múltiples imágenes con sus máscaras.
    - 1 slot activo → salida single
    - 2+ slots activos → salida batch concatenado
    """
    
    @classmethod
    def INPUT_TYPES(cls) -> Dict[str, Any]:
        inputs: Dict[str, Any] = {
            "required": {
                "fallback": (["error", "slot1"], {"default": "slot1"}),
                "mode": (["auto", "single_only", "batch_only"], {"default": "auto"}),
            },
            "optional": {}
        }
        
        for i in range(1, N_SLOTS + 1):
            inputs["optional"][f"img{i}"] = ("IMAGE",)
            inputs["optional"][f"mask{i}"] = ("MASK",)
            inputs["required"][f"on{i}"] = ("BOOLEAN", {"default": i == 1})
        
        return inputs
    
    RETURN_TYPES = ("IMAGE", "MASK")
    RETURN_NAMES = ("image", "mask")
    FUNCTION = "execute"
    CATEGORY = CATEGORY
    
    def execute(self, fallback: str, mode: str, **kwargs) -> Tuple[torch.Tensor, torch.Tensor]:
        active_slots: List[Dict[str, Any]] = []
        
        for i in range(1, N_SLOTS + 1):
            if kwargs.get(f"on{i}", False):
                img = kwargs.get(f"img{i}")
                mask = kwargs.get(f"mask{i}")
                
                if img is None:
                    raise ValueError(
                        f"❌ Slot {i} activado pero sin imagen conectada.\n"
                        f"Conecta una imagen o desactiva el slot."
                    )
                
                if mask is None:
                    raise ValueError(
                        f"❌ Slot {i} activado pero sin máscara conectada.\n"
                        f"Conecta una máscara o desactiva el slot."
                    )
                
                active_slots.append({"index": i, "image": img, "mask": mask})
        
        if len(active_slots) == 0:
            if fallback == "error":
                raise ValueError("❌ Ningún slot activado.")
            else:
                img1 = kwargs.get("img1")
                mask1 = kwargs.get("mask1")
                if img1 is None or mask1 is None:
                    raise ValueError("❌ Fallback a slot1 pero no tiene imagen/máscara.")
                return (img1, mask1)
        
        if mode == "single_only" and len(active_slots) > 1:
            slots = [str(s["index"]) for s in active_slots]
            raise ValueError(
                f"❌ Modo single_only con {len(active_slots)} slots activos: {', '.join(slots)}.\n"
                f"Desactiva hasta dejar 1 o cambia el modo."
            )
        
        if len(active_slots) == 1:
            img = active_slots[0]["image"]
            mask = active_slots[0]["mask"]
            
            if mode == "batch_only":
                if img.dim() == 3:
                    img = img.unsqueeze(0)
                if mask.dim() == 2:
                    mask = mask.unsqueeze(0)
            
            return (img, mask)
        
        return self._create_batch(active_slots)
    
    def _create_batch(self, active_slots: List[Dict[str, Any]]) -> Tuple[torch.Tensor, torch.Tensor]:
        images: List[torch.Tensor] = []
        masks: List[torch.Tensor] = []
        
        ref = active_slots[0]
        ref_img = ref["image"]
        ref_mask = ref["mask"]
        
        if ref_img.dim() == 3:
            ref_img = ref_img.unsqueeze(0)
        if ref_mask.dim() == 2:
            ref_mask = ref_mask.unsqueeze(0)
        
        ref_h, ref_w, ref_c = ref_img.shape[1], ref_img.shape[2], ref_img.shape[3]
        ref_mh, ref_mw = ref_mask.shape[1], ref_mask.shape[2]
        
        for slot in active_slots:
            idx = slot["index"]
            img = slot["image"]
            mask = slot["mask"]
            
            if img.dim() == 3:
                img = img.unsqueeze(0)
            if mask.dim() == 2:
                mask = mask.unsqueeze(0)
            
            h, w, c = img.shape[1], img.shape[2], img.shape[3]
            if (h, w, c) != (ref_h, ref_w, ref_c):
                raise ValueError(
                    f"❌ Imagen slot {idx} incompatible.\n"
                    f"   Esperado: {ref_h}x{ref_w}x{ref_c}\n"
                    f"   Recibido: {h}x{w}x{c}"
                )
            
            mh, mw = mask.shape[1], mask.shape[2]
            if (mh, mw) != (ref_mh, ref_mw):
                raise ValueError(
                    f"❌ Máscara slot {idx} incompatible.\n"
                    f"   Esperado: {ref_mh}x{ref_mw}\n"
                    f"   Recibido: {mh}x{mw}"
                )
            
            images.append(img)
            masks.append(mask)
        
        return (torch.cat(images, dim=0), torch.cat(masks, dim=0))
