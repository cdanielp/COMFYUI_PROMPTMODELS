"""
Titan Maestro - Control Central
Nodo principal: Prompt, Resolución, Latente y Búnker de Ideas.
"""

import torch
import random
import logging
from typing import Tuple, Dict, Any

from .titan_utils import (
    cargar_bunker, 
    guardar_en_bunker, 
    eliminar_de_bunker,
    listar_bunker,
    procesar_aleatoriedad,
    procesar_wildcards_peso,
    limpiar_prompt,
    PRESETS
)

logger = logging.getLogger("TitanSuite")


class Titan_Maestro:
    """
    🏰 Control Central: Prompt, Resolución, Latente y Búnker.
    
    Características:
    - Búnker de Ideas: Guarda y carga prompts favoritos (persistente en cloud)
    - Presets de Resolución: Menú con tamaños optimizados
    - Wildcards: Escribe {opcion1|opcion2} para aleatoriedad
    - Wildcards con peso: {opcion1::2|opcion2::1} para probabilidades
    - Generación de Latente: Listo para samplers
    """
    
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls) -> Dict[str, Any]:
        # Cargar favoritos guardados
        favoritos = listar_bunker()
        if not favoritos:
            favoritos = ["(Vacío - Guarda algo primero)"]
        
        return {
            "required": {
                "prompt_positivo": ("STRING", {
                    "default": "masterpiece, best quality, ", 
                    "multiline": True,
                    "placeholder": "Escribe tu prompt aquí... Usa {a|b|c} para wildcards"
                }),
                "prompt_negativo": ("STRING", {
                    "default": "worst quality, low quality, text, watermark, signature, blurry", 
                    "multiline": True,
                    "placeholder": "Elementos a evitar..."
                }),
                "resolucion": (list(PRESETS.keys()), {
                    "default": "📐 Cuadrado (1024x1024)"
                }),
                "lotes_batch": ("INT", {
                    "default": 1, 
                    "min": 1, 
                    "max": 64,
                    "step": 1,
                    "display": "number"
                }),
                "semilla": ("INT", {
                    "default": 0, 
                    "min": 0, 
                    "max": 0xffffffffffffffff,
                    "step": 1,
                    "display": "number"
                }),
                "modo_wildcard": (["Normal {a|b}", "Con Pesos {a::2|b::1}"], {
                    "default": "Normal {a|b}"
                }),
                "accion_bunker": ([
                    "--- Nada ---", 
                    "💾 GUARDAR este Prompt", 
                    "📖 CARGAR del Menú",
                    "🗑️ ELIMINAR del Menú"
                ],),
                "favoritos": (favoritos,),
            },
            "optional": {
                "nombre_guardar": ("STRING", {
                    "default": "Mi_Prompt_01", 
                    "multiline": False,
                    "placeholder": "Nombre para guardar"
                }),
                "ancho_custom": ("INT", {
                    "default": 0, 
                    "min": 0, 
                    "max": 4096,
                    "step": 8,
                    "display": "number"
                }),
                "alto_custom": ("INT", {
                    "default": 0, 
                    "min": 0, 
                    "max": 4096,
                    "step": 8,
                    "display": "number"
                }),
                "limpiar_prompt": ("BOOLEAN", {
                    "default": True,
                    "label_on": "Limpiar espacios",
                    "label_off": "Sin limpiar"
                }),
            }
        }

    RETURN_TYPES = ("LATENT", "STRING", "STRING", "INT", "INT", "INT")
    RETURN_NAMES = ("Latente", "Positivo", "Negativo", "Ancho", "Alto", "Semilla Usada")
    FUNCTION = "ejecutar"
    CATEGORY = "Titan Suite 🇪🇸"
    
    # Permitir ejecución en output (para debugging)
    OUTPUT_NODE = False

    def ejecutar(
        self, 
        prompt_positivo: str,
        prompt_negativo: str,
        resolucion: str,
        lotes_batch: int,
        semilla: int,
        modo_wildcard: str,
        accion_bunker: str,
        favoritos: str,
        nombre_guardar: str = "Mi_Prompt_01",
        ancho_custom: int = 0,
        alto_custom: int = 0,
        limpiar_prompt_flag: bool = True
    ) -> Tuple:
        """
        Ejecuta el nodo Maestro.
        
        Returns:
            Tuple: (latente, texto_positivo, texto_negativo, ancho, alto, semilla_usada)
        """
        texto = prompt_positivo
        
        # === LÓGICA DEL BÚNKER ===
        if accion_bunker == "💾 GUARDAR este Prompt":
            if texto.strip():
                exito = guardar_en_bunker(nombre_guardar, texto)
                if exito:
                    logger.info(f"💾 Prompt guardado como: {nombre_guardar}")
                else:
                    logger.warning(f"⚠️ No se pudo guardar el prompt")
            else:
                logger.warning("⚠️ Prompt vacío, no se guardó")
                
        elif accion_bunker == "📖 CARGAR del Menú":
            db = cargar_bunker()
            if favoritos in db:
                texto = db[favoritos].get("texto", texto)
                logger.info(f"📖 Cargado: {favoritos}")
            else:
                logger.warning(f"⚠️ '{favoritos}' no encontrado en búnker")
                
        elif accion_bunker == "🗑️ ELIMINAR del Menú":
            if favoritos and favoritos != "(Vacío - Guarda algo primero)":
                eliminar_de_bunker(favoritos)
        
        # === PROCESAR WILDCARDS ===
        # Determinar semilla efectiva
        if semilla == 0:
            seed_efectiva = random.randint(1, 0xffffffffffffffff)
        else:
            seed_efectiva = semilla
        
        # Aplicar wildcards según modo
        if modo_wildcard == "Con Pesos {a::2|b::1}":
            texto_procesado = procesar_wildcards_peso(texto, seed_efectiva)
        else:
            texto_procesado = procesar_aleatoriedad(texto, seed_efectiva)
        
        # Limpiar si está habilitado
        if limpiar_prompt_flag:
            texto_procesado = limpiar_prompt(texto_procesado)
            prompt_negativo = limpiar_prompt(prompt_negativo)
        
        # === DETERMINAR RESOLUCIÓN ===
        # Prioridad: Custom > Preset
        if ancho_custom > 0 and alto_custom > 0:
            # Redondear a múltiplo de 8 (requisito de modelos de difusión)
            ancho = (ancho_custom // 8) * 8
            alto = (alto_custom // 8) * 8
            
            # Validar mínimo razonable (64px)
            ancho = max(64, ancho)
            alto = max(64, alto)
            
            # Validar máximo (evitar OOM)
            ancho = min(4096, ancho)
            alto = min(4096, alto)
            
            if ancho != ancho_custom or alto != alto_custom:
                logger.info(f"📐 Resolución ajustada: {ancho_custom}x{alto_custom} → {ancho}x{alto} (múltiplo de 8)")
            else:
                logger.info(f"📐 Usando resolución custom: {ancho}x{alto}")
        else:
            ancho, alto = PRESETS.get(resolucion, (1024, 1024))
        
        # === GENERAR LATENTE ===
        # SDXL/Flux usan factor 8, SD1.5 también
        latent_height = alto // 8
        latent_width = ancho // 8
        
        latent = torch.zeros(
            [lotes_batch, 4, latent_height, latent_width],
            dtype=torch.float32
        )
        
        logger.info(f"✅ Latente generado: {lotes_batch}x4x{latent_height}x{latent_width}")
        
        return (
            {"samples": latent},
            texto_procesado,
            prompt_negativo,
            ancho,
            alto,
            seed_efectiva
        )


class Titan_Maestro_Lite:
    """
    🏰 Versión ligera del Maestro (sin búnker).
    
    Para quienes solo necesitan resolución + wildcards sin guardar prompts.
    """
    
    @classmethod
    def INPUT_TYPES(cls) -> Dict[str, Any]:
        return {
            "required": {
                "prompt_positivo": ("STRING", {
                    "default": "", 
                    "multiline": True
                }),
                "prompt_negativo": ("STRING", {
                    "default": "worst quality, low quality", 
                    "multiline": True
                }),
                "resolucion": (list(PRESETS.keys()),),
                "batch": ("INT", {"default": 1, "min": 1, "max": 64}),
                "semilla": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff}),
            }
        }

    RETURN_TYPES = ("LATENT", "STRING", "STRING", "INT", "INT")
    RETURN_NAMES = ("Latente", "Positivo", "Negativo", "Ancho", "Alto")
    FUNCTION = "ejecutar"
    CATEGORY = "Titan Suite 🇪🇸"

    def ejecutar(self, prompt_positivo, prompt_negativo, resolucion, batch, semilla):
        seed = semilla if semilla > 0 else random.randint(1, 9999999)
        texto = procesar_aleatoriedad(prompt_positivo, seed)
        ancho, alto = PRESETS.get(resolucion, (1024, 1024))
        latent = torch.zeros([batch, 4, alto // 8, ancho // 8])
        
        return ({"samples": latent}, texto, prompt_negativo, ancho, alto)
