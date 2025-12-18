"""
DivisorDePrompts (10) - Custom Node para ComfyUI
Divide texto multilínea en hasta 10 prompts independientes usando párrafos como separador.
"""

import re

class DivisorDePrompts:
    """
    Divide un texto largo en hasta 10 prompts separados por líneas vacías.
    Cada párrafo se convierte en un output STRING independiente.
    """
    
    def __init__(self):
        pass
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "full_text": ("STRING", {
                    "multiline": True,
                    "default": "",
                    "placeholder": "Pega tus prompts aquí, separados por líneas vacías..."
                }),
            },
            "optional": {
                "trim_mode": ("BOOLEAN", {
                    "default": True,
                    "label_on": "Limpiar espacios",
                    "label_off": "Mantener espacios"
                }),
                "preserve_newlines": ("BOOLEAN", {
                    "default": True,
                    "label_on": "Mantener saltos internos",
                    "label_off": "Colapsar a una línea"
                }),
            }
        }
    
    RETURN_TYPES = ("STRING", "STRING", "STRING", "STRING", "STRING", 
                    "STRING", "STRING", "STRING", "STRING", "STRING", "INT")
    
    RETURN_NAMES = ("prompt_01", "prompt_02", "prompt_03", "prompt_04", "prompt_05",
                    "prompt_06", "prompt_07", "prompt_08", "prompt_09", "prompt_10", "count")
    
    FUNCTION = "split_prompts"
    CATEGORY = "Prompt Tools"
    
    def split_prompts(self, full_text, trim_mode=True, preserve_newlines=True):
        """
        Divide el texto en prompts usando líneas vacías como separador.
        
        Args:
            full_text: Texto multilínea con prompts separados por párrafos
            trim_mode: Si True, limpia espacios al inicio/fin de cada prompt
            preserve_newlines: Si True, mantiene saltos de línea internos
            
        Returns:
            Tuple de 10 strings + count (INT)
        """
        
        # Inicializar outputs vacíos
        outputs = [""] * 10
        
        # Si entrada vacía, retornar todo vacío
        if not full_text or not full_text.strip():
            return tuple(outputs) + (0,)
        
        # Normalizar saltos de línea (Windows → Unix)
        text = full_text.replace("\r\n", "\n").replace("\r", "\n")
        
        # Dividir por párrafos (1+ líneas vacías)
        # Patrón: una o más líneas que contienen solo espacios/tabs
        pattern = r'\n(?:[ \t]*\n)+'
        blocks = re.split(pattern, text)
        
        # Procesar cada bloque
        prompts = []
        for block in blocks:
            # Limpiar espacios si trim_mode está activo
            if trim_mode:
                block = block.strip()
            
            # Saltar bloques vacíos
            if not block:
                continue
            
            # Colapsar newlines internos si preserve_newlines está desactivado
            if not preserve_newlines:
                # Reemplazar saltos por espacio y colapsar múltiples espacios
                block = re.sub(r'\s+', ' ', block).strip()
            
            prompts.append(block)
        
        # Tomar máximo 10 prompts
        prompts = prompts[:10]
        
        # Rellenar outputs
        for i, prompt in enumerate(prompts):
            outputs[i] = prompt
        
        # Retornar 10 strings + count
        return tuple(outputs) + (len(prompts),)


# Registro del nodo en ComfyUI
NODE_CLASS_MAPPINGS = {
    "DivisorDePrompts": DivisorDePrompts
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "DivisorDePrompts": "DivisorDePrompts (10)"
}
