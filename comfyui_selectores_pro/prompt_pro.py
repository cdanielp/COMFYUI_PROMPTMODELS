"""
Prompt Pro
==========
Constructor de prompts por campos con diseños predefinidos.
"""

import re
from typing import Dict, Any, Tuple, List

# Configuración
CATEGORY: str = "Selectores Pro"


class PromptPro:
    """
    Constructor de prompts por campos con diseños predefinidos.
    Solo requiere el campo 👤 Sujeto, todo lo demás es opcional.
    Ensambla automáticamente el prompt final según el diseño elegido.
    """
    
    # Diseños disponibles
    DESIGNS = [
        "Retrato Pro",
        "Cinemático",
        "Producto E-commerce",
        "Anime Clean",
        "Concept Art",
        "Arquitectura",
        "Moda Editorial",
        "Interior Design",
        "Vertical Reels (9:16)",
        "Thumbnail YouTube (16:9)",
    ]
    
    # Separadores disponibles
    SEPARATORS = [", ", " ", "\\n", " | "]
    
    # Mapeo de separadores
    SEPARATOR_MAP = {
        ", ": ", ",
        " ": " ",
        "\\n": "\n",
        " | ": " | ",
    }
    
    @classmethod
    def INPUT_TYPES(cls) -> Dict[str, Any]:
        return {
            "required": {
                "📐 Diseño": (cls.DESIGNS, {"default": "Retrato Pro"}),
                "👤 Sujeto": ("STRING", {"default": "", "placeholder": "Obligatorio"}),
                "🧍 Acción / Pose": ("STRING", {"default": ""}),
                "🎭 Emoción / Expresión": ("STRING", {"default": ""}),
                "👗 Vestuario / Props": ("STRING", {"default": ""}),
                "🏞️ Fondo / Entorno": ("STRING", {"default": ""}),
                "🎨 Estilo": ("STRING", {"default": ""}),
                "🎨 Paleta / Colores": ("STRING", {"default": ""}),
                "💡 Iluminación": ("STRING", {"default": ""}),
                "📷 Cámara / Lente": ("STRING", {"default": ""}),
                "🧪 Materiales / Texturas": ("STRING", {"default": ""}),
                "🧷 Composición": ("STRING", {"default": ""}),
                "🔎 Detalle": ("STRING", {"default": ""}),
                "🌫️ Atmósfera": ("STRING", {"default": ""}),
                "✨ Calidad": ("STRING", {"default": ""}),
                "🧯 Restricciones": ("STRING", {"default": ""}),
                "➕ Extra": ("STRING", {"default": "", "multiline": True}),
                "🔗 Separador": (cls.SEPARATORS, {"default": ", "}),
                "📌 Prefijo": ("STRING", {"default": ""}),
                "📌 Sufijo": ("STRING", {"default": ""}),
                "🧹 Normalizar": ("BOOLEAN", {"default": True}),
                "🧼 Evitar duplicados": ("BOOLEAN", {"default": False}),
            }
        }
    
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("text",)
    FUNCTION = "execute"
    CATEGORY = CATEGORY
    
    # Mapeo de nombres de UI a claves internas
    UI_TO_KEY = {
        "👤 Sujeto": "sujeto",
        "🧍 Acción / Pose": "accion",
        "🎭 Emoción / Expresión": "emocion",
        "👗 Vestuario / Props": "vestuario",
        "🏞️ Fondo / Entorno": "fondo",
        "🎨 Estilo": "estilo",
        "🎨 Paleta / Colores": "paleta",
        "💡 Iluminación": "iluminacion",
        "📷 Cámara / Lente": "camara",
        "🧪 Materiales / Texturas": "materiales",
        "🧷 Composición": "composicion",
        "🔎 Detalle": "detalle",
        "🌫️ Atmósfera": "atmosfera",
        "✨ Calidad": "calidad",
        "🧯 Restricciones": "restricciones",
        "➕ Extra": "extra",
    }
    
    # Orden de campos por diseño
    DESIGN_ORDERS = {
        "Retrato Pro": [
            ["sujeto"],
            ["emocion", "vestuario"],
            ["estilo", "paleta"],
            ["iluminacion", "camara"],
            ["calidad", "detalle"],
            ["restricciones"],
            ["extra"],
        ],
        "Cinemático": [
            ["sujeto", "accion"],
            ["emocion", "vestuario"],
            ["fondo", "atmosfera"],
            ["iluminacion"],
            ["camara", "composicion"],
            ["detalle", "calidad"],
            ["restricciones"],
            ["extra"],
        ],
        "Producto E-commerce": [
            ["sujeto"],
            ["materiales", "paleta"],
            ["fondo"],
            ["iluminacion"],
            ["camara", "composicion"],
            ["detalle", "calidad"],
            ["restricciones"],
            ["extra"],
        ],
        "Anime Clean": [
            ["sujeto", "accion"],
            ["emocion", "vestuario"],
            ["estilo"],
            ["fondo", "atmosfera"],
            ["paleta", "iluminacion"],
            ["detalle", "calidad"],
            ["restricciones"],
            ["extra"],
        ],
        "Concept Art": [
            ["sujeto"],
            ["accion", "vestuario"],
            ["fondo", "atmosfera"],
            ["estilo", "paleta"],
            ["iluminacion", "composicion"],
            ["materiales", "detalle"],
            ["calidad"],
            ["restricciones"],
            ["extra"],
        ],
        "Arquitectura": [
            ["sujeto"],
            ["fondo", "atmosfera"],
            ["estilo", "materiales"],
            ["iluminacion"],
            ["camara", "composicion"],
            ["detalle", "calidad"],
            ["restricciones"],
            ["extra"],
        ],
        "Moda Editorial": [
            ["sujeto", "accion"],
            ["vestuario"],
            ["emocion"],
            ["fondo", "estilo"],
            ["iluminacion", "camara"],
            ["composicion", "paleta"],
            ["calidad", "detalle"],
            ["restricciones"],
            ["extra"],
        ],
        "Interior Design": [
            ["sujeto"],
            ["fondo"],
            ["estilo", "materiales"],
            ["paleta", "iluminacion"],
            ["atmosfera"],
            ["camara", "composicion"],
            ["detalle", "calidad"],
            ["restricciones"],
            ["extra"],
        ],
        "Vertical Reels (9:16)": [
            ["sujeto", "accion"],
            ["emocion"],
            ["vestuario"],
            ["fondo"],
            ["iluminacion", "atmosfera"],
            ["composicion"],
            ["calidad"],
            ["restricciones"],
            ["extra"],
        ],
        "Thumbnail YouTube (16:9)": [
            ["sujeto", "accion"],
            ["emocion"],
            ["fondo"],
            ["paleta", "iluminacion"],
            ["composicion"],
            ["calidad", "detalle"],
            ["restricciones"],
            ["extra"],
        ],
    }
    
    def execute(self, **kwargs) -> Tuple[str]:
        # Extraer parámetros de configuración
        diseno = kwargs.get("📐 Diseño", "Retrato Pro")
        separador_key = kwargs.get("🔗 Separador", ", ")
        prefijo = kwargs.get("📌 Prefijo", "") or ""
        sufijo = kwargs.get("📌 Sufijo", "") or ""
        normalizar = kwargs.get("🧹 Normalizar", True)
        evitar_duplicados = kwargs.get("🧼 Evitar duplicados", False)
        
        # Obtener separador real
        separador = self.SEPARATOR_MAP.get(separador_key, ", ")
        
        # Extraer valores de campos
        campos: Dict[str, str] = {}
        for ui_name, key in self.UI_TO_KEY.items():
            value = kwargs.get(ui_name, "") or ""
            campos[key] = value.strip()
        
        # Validar campo obligatorio
        if not campos["sujeto"]:
            raise ValueError("❌ Prompt Pro: el campo 👤 Sujeto es obligatorio.")
        
        # Obtener orden del diseño
        orden = self.DESIGN_ORDERS.get(diseno, self.DESIGN_ORDERS["Retrato Pro"])
        
        # Construir grupos de texto
        grupos: List[str] = []
        
        for grupo_keys in orden:
            partes: List[str] = []
            for key in grupo_keys:
                if campos.get(key):
                    partes.append(campos[key])
            
            if partes:
                grupos.append(", ".join(partes))
        
        # Unir grupos con separador
        prompt = separador.join(grupos)
        
        # Aplicar prefijo
        if prefijo.strip():
            prompt = prefijo.strip() + separador + prompt
        
        # Aplicar sufijo
        if sufijo.strip():
            prompt = prompt + separador + sufijo.strip()
        
        # Normalizar si está activado
        if normalizar:
            prompt = self._normalize(prompt)
        
        # Evitar duplicados si está activado
        if evitar_duplicados:
            prompt = self._remove_duplicates(prompt, separador)
        
        return (prompt,)
    
    @staticmethod
    def _normalize(text: str) -> str:
        """Limpia espacios dobles, comas repetidas, saltos raros."""
        text = re.sub(r' +', ' ', text)
        text = re.sub(r',+', ',', text)
        text = re.sub(r',\s*,', ',', text)
        text = re.sub(r'\s+,', ',', text)
        text = re.sub(r',(?!\s)', ', ', text)
        text = re.sub(r'\n+', '\n', text)
        text = '\n'.join(line.strip() for line in text.split('\n'))
        text = text.strip().strip(',').strip()
        return text
    
    @staticmethod
    def _remove_duplicates(text: str, separator: str) -> str:
        """Elimina frases repetidas simples."""
        if separator.strip():
            parts = [p.strip() for p in text.split(separator.strip())]
        else:
            parts = [p.strip() for p in text.split(',')]
        
        seen = set()
        unique_parts: List[str] = []
        for part in parts:
            part_lower = part.lower()
            if part and part_lower not in seen:
                seen.add(part_lower)
                unique_parts.append(part)
        
        sep = separator if separator.strip() else ", "
        return sep.join(unique_parts)
