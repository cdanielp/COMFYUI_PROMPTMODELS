"""
Baúles de Prompts - Sistema de presets persistentes
1 clase base + 7 wrappers especializados
"""
import json
from typing import Dict, Any, Tuple, List

class BasePromptChest:
    """Clase base para baúles de prompts (presets)"""
    
    # Sobreescribir en subclases
    CHEST_NAME = "Prompts Base"
    DEFAULT_PRESETS = {
        "Preset 1": "Escribe tu prompt aquí",
        "Preset 2": "Otro preset de ejemplo",
    }
    
    @classmethod
    def INPUT_TYPES(cls) -> Dict[str, Any]:
        return {
            "required": {
                "📝 Preset": (list(cls.DEFAULT_PRESETS.keys()),),
                "✏️ Texto del preset": ("STRING", {
                    "default": list(cls.DEFAULT_PRESETS.values())[0],
                    "multiline": True,
                }),
                "🔧 Acción": ([
                    "Nada",
                    "Nuevo preset",
                    "Duplicar actual",
                    "Borrar preset",
                    "Guardar cambios"
                ],),
            },
            "optional": {
                "📋 Importar lista": ("STRING", {
                    "default": "",
                    "multiline": True,
                    "placeholder": "Formato: nombre1|texto1\nnombre2|texto2"
                }),
            },
            "hidden": {
                "unique_id": "UNIQUE_ID",
                "presets_json": "STRING",  # Storage persistente
            }
        }
    
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("texto",)
    FUNCTION = "execute"
    CATEGORY = "Baúles/Prompts"
    
    def __init__(self):
        self.presets: Dict[str, str] = {}
    
    def _load_presets(self, presets_json: str) -> Dict[str, str]:
        """Carga presets desde JSON del widget oculto"""
        if not presets_json:
            return dict(self.DEFAULT_PRESETS)
        
        try:
            return json.loads(presets_json)
        except Exception:
            return dict(self.DEFAULT_PRESETS)
    
    def _save_presets(self, presets: Dict[str, str]) -> str:
        """Guarda presets como JSON"""
        return json.dumps(presets, ensure_ascii=False, indent=2)
    
    def _parse_import_list(self, text: str) -> Dict[str, str]:
        """Parsea el formato: nombre1|texto1\nnombre2|texto2"""
        if not text.strip():
            return {}
        
        imported = {}
        lines = text.strip().split('\n')
        for line in lines:
            line = line.strip()
            if not line or '|' not in line:
                continue
            
            parts = line.split('|', 1)
            if len(parts) == 2:
                nombre = parts[0].strip()
                texto = parts[1].strip()
                if nombre and texto:
                    imported[nombre] = texto
        
        return imported
    
    def execute(self, **kwargs) -> Tuple[str]:
        """Ejecuta la lógica del baúl de prompts"""
        preset_seleccionado = kwargs.get("📝 Preset", "")
        texto_actual = kwargs.get("✏️ Texto del preset", "")
        accion = kwargs.get("🔧 Acción", "Nada")
        importar_lista = kwargs.get("📋 Importar lista", "")
        presets_json = kwargs.get("presets_json", "")
        
        # Cargar presets existentes
        self.presets = self._load_presets(presets_json)
        
        # Procesar acciones
        if accion == "Nuevo preset":
            nuevo_nombre = f"Nuevo Preset {len(self.presets) + 1}"
            self.presets[nuevo_nombre] = "Texto del nuevo preset"
            raise RuntimeError(
                f"✅ Preset creado: {nuevo_nombre}\n"
                f"Refrescar nodo para verlo en el dropdown."
            )
        
        elif accion == "Duplicar actual":
            if preset_seleccionado and preset_seleccionado in self.presets:
                duplicado_nombre = f"{preset_seleccionado} (copia)"
                self.presets[duplicado_nombre] = self.presets[preset_seleccionado]
                raise RuntimeError(f"✅ Preset duplicado: {duplicado_nombre}")
        
        elif accion == "Borrar preset":
            if preset_seleccionado and preset_seleccionado in self.presets:
                if len(self.presets) > 1:
                    del self.presets[preset_seleccionado]
                    raise RuntimeError(f"✅ Preset borrado: {preset_seleccionado}")
                else:
                    raise ValueError("❌ No puedes borrar el último preset")
        
        elif accion == "Guardar cambios":
            if preset_seleccionado and preset_seleccionado in self.presets:
                self.presets[preset_seleccionado] = texto_actual
                raise RuntimeError(f"✅ Cambios guardados en: {preset_seleccionado}")
        
        # Importar lista masiva
        if importar_lista.strip():
            importados = self._parse_import_list(importar_lista)
            if importados:
                self.presets.update(importados)
                raise RuntimeError(
                    f"✅ Importados {len(importados)} preset(s).\n"
                    f"Refrescar nodo para ver cambios."
                )
        
        # Validación
        if not preset_seleccionado or preset_seleccionado not in self.presets:
            raise ValueError(
                f"❌ Preset seleccionado no válido: {preset_seleccionado}\n"
                f"Presets disponibles: {', '.join(self.presets.keys())}"
            )
        
        # Devolver el texto del preset seleccionado
        texto_final = self.presets.get(preset_seleccionado, "")
        
        return (texto_final,)
    
    @classmethod
    def IS_CHANGED(cls, **kwargs) -> str:
        """Hash basado en presets + selección"""
        preset_seleccionado = kwargs.get("📝 Preset", "")
        presets_json = kwargs.get("presets_json", "")
        
        import hashlib
        combined = f"{presets_json}_{preset_seleccionado}"
        return hashlib.sha256(combined.encode()).hexdigest()[:16]


# ============================================================================
# Nodos Específicos (8 variantes)
# ============================================================================

class PromptChestBase(BasePromptChest):
    """🧾 Baúl de Prompts (Base)"""
    CHEST_NAME = "Prompts Base"
    DEFAULT_PRESETS = {
        "Preset 1": "Escribe tu prompt aquí",
        "Preset 2": "Otro preset de ejemplo",
    }

class StyleChest(BasePromptChest):
    """🎨 Baúl Estilos"""
    CHEST_NAME = "Estilos"
    DEFAULT_PRESETS = {
        "Realista": "photorealistic, highly detailed, 8k uhd",
        "Anime": "anime style, cel shading, vibrant colors",
        "Pintura al óleo": "oil painting, brushstrokes, textured canvas",
    }

class PoseChest(BasePromptChest):
    """🧍 Baúl Poses"""
    CHEST_NAME = "Poses"
    DEFAULT_PRESETS = {
        "Pose neutra": "standing, neutral pose, arms at sides",
        "Pose acción": "dynamic pose, action shot, mid-movement",
        "Sentado": "sitting, relaxed posture, comfortable",
    }

class CameraChest(BasePromptChest):
    """📷 Baúl Cámara / Lente"""
    CHEST_NAME = "Cámara / Lente"
    DEFAULT_PRESETS = {
        "Plano medio": "medium shot, eye level, 50mm lens",
        "Gran angular": "wide angle, 24mm, dramatic perspective",
        "Retrato": "portrait, 85mm, shallow depth of field, bokeh",
    }

class LightingChest(BasePromptChest):
    """💡 Baúl Iluminación"""
    CHEST_NAME = "Iluminación"
    DEFAULT_PRESETS = {
        "Natural": "natural lighting, soft shadows, golden hour",
        "Estudio": "studio lighting, three-point setup, professional",
        "Dramática": "dramatic lighting, high contrast, chiaroscuro",
    }

class EnvironmentChest(BasePromptChest):
    """🏞️ Baúl Fondo / Entorno"""
    CHEST_NAME = "Fondo / Entorno"
    DEFAULT_PRESETS = {
        "Exterior urbano": "urban background, city street, modern architecture",
        "Interior minimalista": "minimalist interior, clean background, white walls",
        "Naturaleza": "outdoor nature scene, forest, natural environment",
    }

class QualityChest(BasePromptChest):
    """✨ Baúl Calidad"""
    CHEST_NAME = "Calidad / Detalle"
    DEFAULT_PRESETS = {
        "Alta calidad": "masterpiece, best quality, highly detailed, sharp focus",
        "Ultra realista": "ultra realistic, photorealistic, 8k uhd, ray tracing",
        "Profesional": "professional photography, high resolution, award winning",
    }

class NegativeChest(BasePromptChest):
    """⛔ Baúl Negativos"""
    CHEST_NAME = "Negativos"
    DEFAULT_PRESETS = {
        "Defectos básicos": "low quality, blurry, pixelated, artifacts",
        "Anatomía": "bad anatomy, extra limbs, deformed hands, missing fingers",
        "Técnicos": "oversaturated, underexposed, noise, compression artifacts",
    }


# ============================================================================
# Mapeo de Nodos
# ============================================================================

NODE_CLASS_MAPPINGS = {
    "PromptChestBase": PromptChestBase,
    "StyleChest": StyleChest,
    "PoseChest": PoseChest,
    "CameraChest": CameraChest,
    "LightingChest": LightingChest,
    "EnvironmentChest": EnvironmentChest,
    "QualityChest": QualityChest,
    "NegativeChest": NegativeChest,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "PromptChestBase": "🧾 Baúl de Prompts (Base)",
    "StyleChest": "🎨 Baúl Estilos",
    "PoseChest": "🧍 Baúl Poses",
    "CameraChest": "📷 Baúl Cámara / Lente",
    "LightingChest": "💡 Baúl Iluminación",
    "EnvironmentChest": "🏞️ Baúl Fondo / Entorno",
    "QualityChest": "✨ Baúl Calidad",
    "NegativeChest": "⛔ Baúl Negativos",
}
