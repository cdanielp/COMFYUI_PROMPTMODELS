"""
Titan Suite 🇪🇸 para ComfyUI
Nodos esenciales en español para eliminar fricción y evitar errores.

Versión: 1.0.0
Autor: Prompt Models
Compatible: ComfyUI, ComfyDeploy, RunComfy
"""

__version__ = "1.0.0"
__author__ = "Prompt Models"

# === IMPORTAR NODOS ===
from .titan_maestro import Titan_Maestro, Titan_Maestro_Lite
from .titan_inspector import Titan_Inspector, Titan_Inspector_Batch
from .titan_multilora import Titan_MultiLora, Titan_LoRA_Info, Titan_LoRA_Stack

# === MAPEO DE CLASES ===
NODE_CLASS_MAPPINGS = {
    # Maestro (Control Central)
    "Titan_Maestro": Titan_Maestro,
    "Titan_Maestro_Lite": Titan_Maestro_Lite,
    
    # Inspector (Metadatos)
    "Titan_Inspector": Titan_Inspector,
    "Titan_Inspector_Batch": Titan_Inspector_Batch,
    
    # MultiLora (Cargador)
    "Titan_MultiLora": Titan_MultiLora,
    "Titan_LoRA_Info": Titan_LoRA_Info,
    "Titan_LoRA_Stack": Titan_LoRA_Stack,
}

# === NOMBRES PARA MOSTRAR EN UI ===
NODE_DISPLAY_NAME_MAPPINGS = {
    # Maestro
    "Titan_Maestro": "🏰 Titan Maestro (Control Central)",
    "Titan_Maestro_Lite": "🏰 Titan Maestro Lite",
    
    # Inspector
    "Titan_Inspector": "🕵️ Titan Inspector (Metadatos)",
    "Titan_Inspector_Batch": "🕵️ Titan Inspector Batch",
    
    # MultiLora
    "Titan_MultiLora": "🧬 Titan Power LoRA 5x (Blindado)",
    "Titan_LoRA_Info": "🔍 Titan LoRA Info",
    "Titan_LoRA_Stack": "📚 Titan LoRA Stack",
}

# === EXPORTAR ===
__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]

# === MENSAJE DE CARGA ===
def _print_welcome():
    """Imprime mensaje de bienvenida al cargar."""
    print("\n" + "="*50)
    print("  ✅ Titan Suite 🇪🇸 cargada correctamente")
    print(f"  📦 Versión: {__version__}")
    print(f"  🧩 Nodos disponibles: {len(NODE_CLASS_MAPPINGS)}")
    print("="*50 + "\n")

_print_welcome()
