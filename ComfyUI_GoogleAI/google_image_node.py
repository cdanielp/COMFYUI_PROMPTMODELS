# google_image_node.py
import torch
import numpy as np
import random
from .google_core import GoogleAICore

# =============================================================================
# MODELOS DE IMAGEN - Actualizado Diciembre 2025
# =============================================================================
IMAGE_MODELS = [
    # Nano Banana Pro (Gemini 3 Pro Image) - Hasta 4K, 14 imgs referencia
    "gemini-3-pro-image-preview",
    
    # Nano Banana (Gemini 2.5 Flash Image) - Rápido, 1024px
    "gemini-2.5-flash-image",
    
    # Imagen 3 Series
    "imagen-3.0-generate-002",
    "imagen-3.0-generate-001",
]

# =============================================================================
# PRESETS DE TAMAÑO (estilo Seedream/ByteDance)
# =============================================================================
SIZE_PRESETS = {
    # --- 1K (~1024px base) ---
    "1024×1024 (1:1) - 1K": ("1:1", "1K"),
    "1152×896 (4:3) - 1K": ("4:3", "1K"),
    "896×1152 (3:4) - 1K": ("3:4", "1K"),
    "1280×720 (16:9) - 1K": ("16:9", "1K"),
    "720×1280 (9:16) - 1K": ("9:16", "1K"),
    "1216×832 (3:2) - 1K": ("3:2", "1K"),
    "832×1216 (2:3) - 1K": ("2:3", "1K"),
    "1024×576 (21:9) - 1K": ("21:9", "1K"),
    "1088×896 (5:4) - 1K": ("5:4", "1K"),
    "896×1088 (4:5) - 1K": ("4:5", "1K"),
    
    # --- 2K (~2048px base) ---
    "2048×2048 (1:1) - 2K": ("1:1", "2K"),
    "2304×1728 (4:3) - 2K": ("4:3", "2K"),
    "1728×2304 (3:4) - 2K": ("3:4", "2K"),
    "2560×1440 (16:9) - 2K": ("16:9", "2K"),
    "1440×2560 (9:16) - 2K": ("9:16", "2K"),
    "2432×1664 (3:2) - 2K": ("3:2", "2K"),
    "1664×2432 (2:3) - 2K": ("2:3", "2K"),
    "2048×896 (21:9) - 2K": ("21:9", "2K"),
    "2176×1792 (5:4) - 2K": ("5:4", "2K"),
    "1792×2176 (4:5) - 2K": ("4:5", "2K"),
    
    # --- 4K (~4096px base) - Solo Nano Banana Pro ---
    "4096×4096 (1:1) - 4K": ("1:1", "4K"),
    "4608×3456 (4:3) - 4K": ("4:3", "4K"),
    "3456×4608 (3:4) - 4K": ("3:4", "4K"),
    "5120×2880 (16:9) - 4K": ("16:9", "4K"),
    "2880×5120 (9:16) - 4K": ("9:16", "4K"),
    "4864×3328 (3:2) - 4K": ("3:2", "4K"),
    "3328×4864 (2:3) - 4K": ("2:3", "4K"),
    "4096×1792 (21:9) - 4K": ("21:9", "4K"),
    "4352×3584 (5:4) - 4K": ("5:4", "4K"),
    "3584×4352 (4:5) - 4K": ("4:5", "4K"),
}

SIZE_PRESET_LIST = list(SIZE_PRESETS.keys())

# Aspect ratios disponibles para modo manual
ASPECT_RATIOS = ["1:1", "4:3", "3:4", "16:9", "9:16", "3:2", "2:3", "21:9", "5:4", "4:5"]

# Resoluciones disponibles
RESOLUTIONS = ["1K", "2K", "4K"]

# Response modalities options
RESPONSE_MODES = ["IMAGE+TEXT", "IMAGE"]

# Modo de tamaño
SIZE_MODES = ["preset", "manual"]


def calculate_aspect_ratio(width: int, height: int) -> str:
    """
    Calcula el aspect ratio más cercano basado en width y height
    """
    ratio = width / height
    
    # Mapeo de ratios
    ratio_map = {
        1.0: "1:1",
        4/3: "4:3",
        3/4: "3:4",
        16/9: "16:9",
        9/16: "9:16",
        3/2: "3:2",
        2/3: "2:3",
        21/9: "21:9",
        5/4: "5:4",
        4/5: "4:5",
    }
    
    # Encontrar el ratio más cercano
    closest_ratio = min(ratio_map.keys(), key=lambda x: abs(x - ratio))
    return ratio_map[closest_ratio]


def calculate_resolution(width: int, height: int) -> str:
    """
    Calcula la resolución basada en el lado más largo
    """
    max_side = max(width, height)
    
    if max_side <= 1280:
        return "1K"
    elif max_side <= 2560:
        return "2K"
    else:
        return "4K"


class GoogleAI_ImageNode:
    """
    Nodo completo de generación de imagen con Google AI (Nano Banana)
    Incluye: modo preset/manual, seed, 5 imágenes de referencia, system prompt
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "api_key": ("STRING", {"default": "", "multiline": False}),
                "model": (IMAGE_MODELS, {"default": "gemini-2.5-flash-image"}),
                "prompt": ("STRING", {"default": "", "multiline": True}),
                "system_prompt": ("STRING", {
                    "default": "You are an expert image-generation engine. You must ALWAYS produce an image.\nInterpret all user input—regardless of format, intent, or abstraction—as literal visual directives for image composition.\nIf a prompt is conversational or lacks specific visual details, you must creatively invent a concrete visual scenario that depicts the concept.\nPrioritize generating the visual representation above any text, formatting, or conversational requests.",
                    "multiline": True
                }),
                "size_mode": (SIZE_MODES, {"default": "preset"}),
                "size_preset": (SIZE_PRESET_LIST, {"default": "2048×2048 (1:1) - 2K"}),
                "width": ("INT", {"default": 1024, "min": 512, "max": 5120, "step": 64}),
                "height": ("INT", {"default": 1024, "min": 512, "max": 5120, "step": 64}),
                "seed": ("INT", {"default": 0, "min": 0, "max": 2147483647}),
                "randomize_seed": ("BOOLEAN", {"default": True}),
                "response_mode": (RESPONSE_MODES, {"default": "IMAGE+TEXT"}),
            },
            "optional": {
                "custom_model": ("STRING", {"default": "", "multiline": False}),
                "image_1": ("IMAGE",),
                "image_2": ("IMAGE",),
                "image_3": ("IMAGE",),
                "image_4": ("IMAGE",),
                "image_5": ("IMAGE",),
            },
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)
    FUNCTION = "generate_image"
    CATEGORY = "GoogleAI"

    def generate_image(self, api_key, model, prompt, system_prompt,
                       size_mode, size_preset, width, height,
                       seed, randomize_seed, response_mode,
                       custom_model="",
                       image_1=None, image_2=None, image_3=None,
                       image_4=None, image_5=None):

        # Usar modelo personalizado si se proporciona
        active_model = custom_model.strip() if custom_model.strip() else model

        if not api_key.strip():
            return self._error_image("❌ Error: API key is required")

        if not prompt.strip():
            return self._error_image("❌ Error: Prompt is required")

        # Determinar aspect_ratio e image_size según el modo
        if size_mode == "preset":
            aspect_ratio, image_size = SIZE_PRESETS.get(size_preset, ("1:1", "1K"))
            print(f"[GoogleAI] 📐 Modo: PRESET -> {size_preset}")
        else:
            # Modo manual: calcular aspect ratio y resolución desde width/height
            aspect_ratio = calculate_aspect_ratio(width, height)
            image_size = calculate_resolution(width, height)
            print(f"[GoogleAI] 📐 Modo: MANUAL -> {width}×{height} -> {aspect_ratio}, {image_size}")

        # Validar 4K solo para Nano Banana Pro
        if image_size == "4K" and "gemini-3-pro" not in active_model:
            print(f"[GoogleAI] ⚠️ 4K solo disponible con gemini-3-pro-image-preview, usando 2K")
            image_size = "2K"

        # Manejar seed - Normalizar si excede el límite de 32-bit
        # (ComfyDeploy puede inyectar seeds de 64-bit que exceden 2147483647)
        MAX_SEED = 2147483647
        if seed > MAX_SEED:
            seed = seed % (MAX_SEED + 1)
            print(f"[GoogleAI] ⚠️ Seed normalizado de valor excedido a: {seed}")
        
        if randomize_seed or seed == 0:
            seed_used = random.randint(1, MAX_SEED)
        else:
            seed_used = seed

        # Convertir response_mode a lista
        if response_mode == "IMAGE+TEXT":
            modalities = ["TEXT", "IMAGE"]
        else:
            modalities = ["IMAGE"]

        # Convertir imágenes de entrada a base64
        image_data = []
        for idx, img in enumerate([image_1, image_2, image_3, image_4, image_5], 1):
            if img is not None:
                try:
                    b64 = GoogleAICore.tensor_to_base64(img)
                    image_data.append(b64)
                    print(f"[GoogleAI] ✅ Imagen {idx} convertida")
                except Exception as e:
                    print(f"[GoogleAI] ⚠️ Error en imagen {idx}: {e}")

        # Info de debug
        print(f"[GoogleAI] 🎨 Modelo: {active_model}")
        print(f"[GoogleAI] 📐 Aspect Ratio: {aspect_ratio}, Resolución: {image_size}")
        print(f"[GoogleAI] 🎲 Seed: {seed_used}")
        print(f"[GoogleAI] 🖼️ Imágenes de referencia: {len(image_data)}")

        # Llamar a la API
        client = GoogleAICore(api_key.strip(), active_model)
        result = client.generate_image(
            prompt=prompt,
            system_prompt=system_prompt,
            images=image_data if image_data else None,
            aspect_ratio=aspect_ratio,
            image_size=image_size,
            seed=seed_used,
            response_modalities=modalities
        )

        # Procesar respuesta
        try:
            # Verificar errores de API
            if "error" in result:
                error_msg = result.get("error", {}).get("message", str(result))
                return self._error_image(f"❌ API Error: {error_msg}")

            candidates = result.get("candidates", [])
            if not candidates:
                return self._error_image("❌ No candidates returned")

            parts = candidates[0].get("content", {}).get("parts", [])

            # Buscar parte con imagen
            for part in parts:
                if "inlineData" in part:
                    b64_data = part["inlineData"]["data"]
                    tensor = GoogleAICore.base64_to_tensor(b64_data)
                    print(f"[GoogleAI] ✅ Imagen generada | Seed: {seed_used}")
                    return (tensor,)

            # Si no hay imagen, puede haber solo texto
            for part in parts:
                if "text" in part:
                    print(f"[GoogleAI] ⚠️ Solo texto: {part['text'][:200]}")
                    return self._error_image("⚠️ Model returned text only")

            return self._error_image("❌ No image in response")

        except Exception as e:
            return self._error_image(f"❌ Error: {str(e)}")

    def _error_image(self, message: str):
        """
        Genera imagen de error roja con mensaje
        """
        print(f"[GoogleAI] {message}")
        error_tensor = torch.zeros(1, 512, 512, 3)
        error_tensor[:, :, :, 0] = 0.8  # Rojo
        return (error_tensor,)


class GoogleAI_ImageNode_Simple:
    """
    Versión simplificada del nodo de imagen (sin imágenes de referencia)
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "api_key": ("STRING", {"default": "", "multiline": False}),
                "model": (IMAGE_MODELS, {"default": "gemini-2.5-flash-image"}),
                "prompt": ("STRING", {"default": "", "multiline": True}),
                "size_preset": (SIZE_PRESET_LIST, {"default": "1024×1024 (1:1) - 1K"}),
            },
            "optional": {
                "seed": ("INT", {"default": 0, "min": 0, "max": 2147483647}),
            },
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)
    FUNCTION = "generate_image"
    CATEGORY = "GoogleAI"

    def generate_image(self, api_key, model, prompt, size_preset, seed=0):
        if not api_key.strip():
            return self._error_image("❌ Error: API key is required")

        if not prompt.strip():
            return self._error_image("❌ Error: Prompt is required")

        # Obtener aspect_ratio e image_size del preset
        aspect_ratio, image_size = SIZE_PRESETS.get(size_preset, ("1:1", "1K"))

        # Normalizar seed si excede el límite de 32-bit
        MAX_SEED = 2147483647
        if seed > MAX_SEED:
            seed = seed % (MAX_SEED + 1)
            print(f"[GoogleAI] ⚠️ Seed normalizado de valor excedido a: {seed}")
        
        # Seed aleatorio si es 0
        seed_used = seed if seed != 0 else random.randint(1, MAX_SEED)

        print(f"[GoogleAI] 🎨 Modelo: {model}")
        print(f"[GoogleAI] 📐 Preset: {size_preset}")
        print(f"[GoogleAI] 🎲 Seed: {seed_used}")

        client = GoogleAICore(api_key.strip(), model)
        result = client.generate_image(
            prompt=prompt,
            aspect_ratio=aspect_ratio,
            image_size=image_size,
            seed=seed_used
        )

        try:
            if "error" in result:
                error_msg = result.get("error", {}).get("message", str(result))
                return self._error_image(f"❌ API Error: {error_msg}")

            candidates = result.get("candidates", [])
            if not candidates:
                return self._error_image("❌ No candidates returned")

            parts = candidates[0].get("content", {}).get("parts", [])

            for part in parts:
                if "inlineData" in part:
                    b64_data = part["inlineData"]["data"]
                    tensor = GoogleAICore.base64_to_tensor(b64_data)
                    print(f"[GoogleAI] ✅ Imagen generada | Seed: {seed_used}")
                    return (tensor,)

            for part in parts:
                if "text" in part:
                    print(f"[GoogleAI] ⚠️ Solo texto: {part['text'][:200]}")
                    return self._error_image("⚠️ Model returned text only")

            return self._error_image("❌ No image in response")

        except Exception as e:
            return self._error_image(f"❌ Error: {str(e)}")

    def _error_image(self, message: str):
        print(f"[GoogleAI] {message}")
        error_tensor = torch.zeros(1, 512, 512, 3)
        error_tensor[:, :, :, 0] = 0.8
        return (error_tensor,)


# =============================================================================
# NODE MAPPINGS
# =============================================================================
NODE_CLASS_MAPPINGS = {
    "GoogleAI_ImageNode": GoogleAI_ImageNode,
    "GoogleAI_ImageNode_Simple": GoogleAI_ImageNode_Simple,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "GoogleAI_ImageNode": "🎨 Google AI Image Generator",
    "GoogleAI_ImageNode_Simple": "🎨 Google AI Image (Simple)",
}
