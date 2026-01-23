"""
🧱 Prompt Constructor - Concatenador inteligente de campos opcionales
Reemplaza el nodo "CLIP Text Encode" positivo
"""
from typing import Dict, Any, Tuple, List

class PromptConstructor:
    """
    Nodo para construir prompts complejos desde campos separados
    Output: CONDITIONING (conectar a sampler positivo)
    """
    
    # CORRECCIÓN 5.1: Lista fija de campos para IS_CHANGED
    CAMPOS_ORDENADOS = [
        "👤 Sujeto",
        "🎨 Estilo",
        "🧍 Pose / Acción",
        "🧥 Ropa / Apariencia",
        "📷 Cámara / Lente",
        "💡 Iluminación",
        "🏞️ Fondo / Entorno",
        "🎭 Emoción / Expresión",
        "✨ Calidad / Detalle",
        "🎚️ Extra",
    ]
    
    @classmethod
    def INPUT_TYPES(cls) -> Dict[str, Any]:
        return {
            "required": {
                "clip": ("CLIP",),
                "🔧 Separador": ([", ", " ", "\n", " | "], {"default": ", "}),
            },
            "optional": {
                "👤 Sujeto": ("STRING", {"default": "", "multiline": False}),
                "🎨 Estilo": ("STRING", {"default": "", "multiline": False}),
                "🧍 Pose / Acción": ("STRING", {"default": "", "multiline": False}),
                "🧥 Ropa / Apariencia": ("STRING", {"default": "", "multiline": False}),
                "📷 Cámara / Lente": ("STRING", {"default": "", "multiline": False}),
                "💡 Iluminación": ("STRING", {"default": "", "multiline": False}),
                "🏞️ Fondo / Entorno": ("STRING", {"default": "", "multiline": False}),
                "🎭 Emoción / Expresión": ("STRING", {"default": "", "multiline": False}),
                "✨ Calidad / Detalle": ("STRING", {"default": "", "multiline": False}),
                "🎚️ Extra": ("STRING", {"default": "", "multiline": True}),
                
                # Opciones avanzadas
                "✂️ Normalizar": ("BOOLEAN", {"default": True}),
                "🚫 Evitar duplicados": ("BOOLEAN", {"default": False}),
                "📌 Prefijo": ("STRING", {"default": "", "multiline": False}),
                "📌 Sufijo": ("STRING", {"default": "", "multiline": False}),
            }
        }
    
    RETURN_TYPES = ("CONDITIONING", "STRING")
    RETURN_NAMES = ("positivo", "prompt_final")
    FUNCTION = "construct"
    CATEGORY = "Baúles/Utilidades"
    
    def _normalize_text(self, text: str) -> str:
        """Normaliza whitespace y limpia el texto"""
        if not text:
            return ""
        
        # Eliminar espacios duplicados
        import re
        text = re.sub(r'\s+', ' ', text)
        
        # Trim
        text = text.strip()
        
        # Eliminar comas/separadores al inicio/final
        text = text.strip(', \n|')
        
        return text
    
    def _remove_duplicates(self, parts: List[str]) -> List[str]:
        """Elimina partes duplicadas manteniendo el orden"""
        seen = set()
        unique_parts = []
        
        for part in parts:
            part_lower = part.lower()
            if part_lower not in seen:
                seen.add(part_lower)
                unique_parts.append(part)
        
        return unique_parts
    
    def construct(self, clip, **kwargs) -> Tuple[Any, str]:
        """
        Construye el prompt final concatenando campos no vacíos
        
        Args:
            clip: CLIP model (obligatorio)
            **kwargs: Campos opcionales del prompt
            
        Returns:
            (CONDITIONING, STRING): Conditioning para sampler + prompt como texto
        """
        separador = kwargs.get("🔧 Separador", ", ")
        normalizar = kwargs.get("✂️ Normalizar", True)
        evitar_duplicados = kwargs.get("🚫 Evitar duplicados", False)
        prefijo = kwargs.get("📌 Prefijo", "")
        sufijo = kwargs.get("📌 Sufijo", "")
        
        # Recolectar partes no vacías
        partes = []
        for campo in self.CAMPOS_ORDENADOS:
            valor = kwargs.get(campo, "")
            if valor and valor.strip():
                if normalizar:
                    valor = self._normalize_text(valor)
                if valor:  # Después de normalizar, verificar que no quedó vacío
                    partes.append(valor)
        
        # Eliminar duplicados si se solicita
        if evitar_duplicados:
            partes = self._remove_duplicates(partes)
        
        # Construir prompt final
        if not partes:
            prompt_final = ""
        else:
            prompt_core = separador.join(partes)
            
            # Aplicar prefijo/sufijo
            if prefijo.strip():
                prompt_final = f"{prefijo.strip()} {prompt_core}"
            else:
                prompt_final = prompt_core
            
            if sufijo.strip():
                prompt_final = f"{prompt_final} {sufijo.strip()}"
        
        # Normalización final
        if normalizar and prompt_final:
            prompt_final = self._normalize_text(prompt_final)
        
        # Validación
        if not prompt_final.strip():
            raise ValueError(
                "❌ Prompt Constructor: El prompt final está vacío.\n"
                "Debes llenar al menos un campo (Sujeto, Estilo, etc.)."
            )
        
        # Encodear con CLIP
        from nodes import CLIPTextEncode
        encoder = CLIPTextEncode()
        conditioning = encoder.encode(clip=clip, text=prompt_final)[0]
        
        return (conditioning, prompt_final)
    
    @classmethod
    def IS_CHANGED(cls, **kwargs) -> str:
        """
        CORRECCIÓN 5.1: Hash basado en lista fija de campos en orden
        """
        import hashlib
        
        # Usar lista fija de claves en orden
        valores = []
        for campo in cls.CAMPOS_ORDENADOS:
            valores.append(str(kwargs.get(campo, "")))
        
        # Añadir opciones de configuración
        valores.append(str(kwargs.get("🔧 Separador", ", ")))
        valores.append(str(kwargs.get("✂️ Normalizar", True)))
        valores.append(str(kwargs.get("🚫 Evitar duplicados", False)))
        valores.append(str(kwargs.get("📌 Prefijo", "")))
        valores.append(str(kwargs.get("📌 Sufijo", "")))
        
        combined = "_".join(valores)
        return hashlib.sha256(combined.encode()).hexdigest()[:16]


# ============================================================================
# Nodo Complementario: Negativo Rápido
# ============================================================================

class NegativeQuick:
    """
    ⛔ Negativo Rápido - Versión simplificada para el prompt negativo
    """
    
    @classmethod
    def INPUT_TYPES(cls) -> Dict[str, Any]:
        return {
            "required": {
                "clip": ("CLIP",),
                "⛔ Negativo": ("STRING", {
                    "default": "low quality, blurry, worst quality",
                    "multiline": True,
                }),
            },
            "optional": {
                "📋 Preset adicional": ("STRING", {
                    "default": "",
                    "multiline": False,
                    "placeholder": "Conectar desde Baúl Negativos"
                }),
            }
        }
    
    RETURN_TYPES = ("CONDITIONING", "STRING")
    RETURN_NAMES = ("negativo", "prompt_negativo")
    FUNCTION = "encode"
    CATEGORY = "Baúles/Utilidades"
    
    def encode(self, clip, **kwargs) -> Tuple[Any, str]:
        """Encodea el prompt negativo"""
        negativo_base = kwargs.get("⛔ Negativo", "")
        preset_adicional = kwargs.get("📋 Preset adicional", "")
        
        # Combinar base + preset
        partes = []
        if negativo_base.strip():
            partes.append(negativo_base.strip())
        if preset_adicional.strip():
            partes.append(preset_adicional.strip())
        
        prompt_negativo = ", ".join(partes)
        
        if not prompt_negativo.strip():
            # Usar un negativo por defecto si está completamente vacío
            prompt_negativo = "low quality, worst quality"
        
        # Encodear con CLIP
        from nodes import CLIPTextEncode
        encoder = CLIPTextEncode()
        conditioning = encoder.encode(clip=clip, text=prompt_negativo)[0]
        
        return (conditioning, prompt_negativo)


# ============================================================================
# Mapeo de Nodos
# ============================================================================

NODE_CLASS_MAPPINGS = {
    "PromptConstructor": PromptConstructor,
    "NegativeQuick": NegativeQuick,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "PromptConstructor": "🧱 Prompt Constructor",
    "NegativeQuick": "⛔ Negativo Rápido",
}