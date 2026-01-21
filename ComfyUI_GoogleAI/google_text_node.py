# google_text_node.py
import random
import traceback
from .google_core import GoogleAICore

# =============================================================================
# MODELOS DE TEXTO - Actualizado & Experimental (Labs)
# =============================================================================
TEXT_MODELS = [
    # --- Production Ready ---
    "gemini-2.0-flash",              # El estándar actual (Rápido/Multimodal)
    "gemini-1.5-pro",                # Ventana de contexto gigante
    
    # --- Google Labs / Experimental ---
    "gemini-2.0-flash-thinking-exp-1219", # MODELO QUE "PIENSA" (Chain of Thought)
    "gemini-exp-1206",                    # La versión experimental más potente hoy
    "learnlm-1.5-pro-experimental",       # Optimizado para explicar/enseñar
    "gemini-1.5-flash",                   # Versión anterior estable
]

class GoogleAI_ModelSelector:
    """
    🔀 ROUTER INTELIGENTE
    Analiza tu petición y decide cuál es el mejor modelo (Costo vs Calidad).
    """
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "api_key": ("STRING", {"default": "", "multiline": False}),
                "user_prompt": ("STRING", {"default": "", "multiline": True}),
                "strategy": (["Best Quality (Slow)", "Balanced", "Speed/Cost (Fast)"],),
            }
        }

    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("selected_model", "reasoning")
    FUNCTION = "select_model"
    CATEGORY = "GoogleAI/Logic"

    def select_model(self, api_key, user_prompt, strategy):
        # Usamos Flash para tomar la decisión (es el "cerebro" barato del router)
        decision_model = "gemini-2.0-flash" 
        
        if not api_key.strip():
            return ("gemini-2.0-flash", "Error: No API Key")

        # Prompt de Sistema para ingeniería de decisión
        sys_prompt = (
            f"You are a Model Router. User Strategy: {strategy}. "
            "Analyze the prompt complexity.\n"
            "- If complex/reasoning needed -> Select 'gemini-2.0-flash-thinking-exp-1219'\n"
            "- If simple/fast task -> Select 'gemini-2.0-flash'\n"
            "- If creative/high quality -> Select 'gemini-exp-1206'\n"
            "Return ONLY the exact model name."
        )

        try:
            client = GoogleAICore(api_key.strip(), decision_model)
            # Temperatura 0 para decisiones lógicas
            result = client.generate_text(prompt=f"Task: {user_prompt}", system_prompt=sys_prompt, temperature=0.0)
            
            # Limpieza básica de la respuesta
            if "candidates" in result and result["candidates"]:
                selected = result["candidates"][0]["content"]["parts"][0]["text"].strip()
            else:
                selected = "gemini-2.0-flash"

            # Validación de seguridad (fallback)
            found = False
            for m in TEXT_MODELS:
                if m in selected:
                    selected = m
                    found = True
                    break
            
            if not found: 
                selected = "gemini-2.0-flash"
                
            return (selected, f"Strategy: {strategy} -> Router Chose: {selected}")

        except Exception as e:
            print(f"[GoogleAI Router] ⚠️ Error: {e}")
            return ("gemini-2.0-flash", f"Router Error: {str(e)}")


class GoogleAI_TextNode:
    """
    🧠 NODO GENERADOR PRO
    Incluye: Manejo de errores seguro, soporte Thinking y Labs.
    """
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "api_key": ("STRING", {"default": "", "multiline": False}),
                "prompt": ("STRING", {"default": "", "multiline": True}),
                "model": (TEXT_MODELS, {"default": "gemini-2.0-flash"}),
                "seed": ("INT", {"default": 0, "min": 0, "max": 2147483647}),
                "randomize_seed": ("BOOLEAN", {"default": True}),
                "temperature": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 2.0, "step": 0.1}),
            },
            "optional": {
                "images": ("IMAGE",), # Renombrado para compatibilidad general, pero acepta tu lógica
                "audio": ("AUDIO",),
                "video": ("IMAGE",),
                "files": ("DOCUMENT",),
                "custom_model": ("STRING", {"default": "", "multiline": False, "forceInput": True}),
                "system_prompt": ("STRING", {"default": "", "multiline": True}),
                # Mantenemos compatibilidad con tus inputs antiguos por si acaso
                "image_1": ("IMAGE",),
                "image_2": ("IMAGE",),
                "image_3": ("IMAGE",),
                "image_4": ("IMAGE",),
                "image_5": ("IMAGE",),
            }
        }

    # SALIDAS SEGURAS: Texto, Mensaje de Estado, Booleano de Éxito
    RETURN_TYPES = ("STRING", "STRING", "BOOLEAN")
    RETURN_NAMES = ("content", "status", "is_success")
    FUNCTION = "generate_text"
    CATEGORY = "GoogleAI"

    def generate_text(self, api_key, prompt, model, seed, randomize_seed, temperature, 
                      images=None, audio=None, video=None, files=None, custom_model="", system_prompt="",
                      image_1=None, image_2=None, image_3=None, image_4=None, image_5=None):
        
        # 1. Prioridad al Router (custom_model) sobre la lista desplegable
        active_model = custom_model.strip() if custom_model.strip() else model
        
        # 2. Gestión de Semilla (Seed)
        MAX_SEED = 2147483647
        if seed > MAX_SEED: seed = seed % (MAX_SEED + 1)
        seed_used = random.randint(1, MAX_SEED) if (randomize_seed or seed == 0) else seed

        # 3. Validación Inicial
        if not api_key.strip():
            return ("", "❌ Error: API Key missing", False)

        try:
            # --- PREPARACIÓN DE MEDIOS (Restaurando tu lógica original) ---
            image_data = []
            
            # Soporte para lista de imágenes (input nuevo)
            if images is not None:
                if len(images.shape) == 4:
                    for i in range(images.shape[0]):
                        image_data.append(GoogleAICore.tensor_to_base64(images[i:i+1]))
                else:
                    image_data.append(GoogleAICore.tensor_to_base64(images))
            
            # Soporte para imágenes individuales (inputs legacy 1-5)
            for img in [image_1, image_2, image_3, image_4, image_5]:
                if img is not None:
                    image_data.append(GoogleAICore.tensor_to_base64(img))

            # Audio
            audio_data = []
            if audio is not None:
                if isinstance(audio, dict):
                    waveform = audio.get("waveform")
                    sample_rate = audio.get("sample_rate", 44100)
                    if waveform is not None:
                        b64 = GoogleAICore.audio_to_base64(waveform, sample_rate)
                        audio_data.append({"data": b64, "mime_type": "audio/wav"})

            # Video
            video_data = []
            if video is not None:
                if len(video.shape) == 4:
                    num_frames = min(video.shape[0], 8)  # Limitamos frames para no saturar
                    step = max(1, video.shape[0] // num_frames)
                    for i in range(0, video.shape[0], step)[:num_frames]:
                        b64 = GoogleAICore.tensor_to_base64(video[i:i+1])
                        video_data.append({"data": b64, "mime_type": "image/png"})

            # Archivos
            file_data = []
            if files is not None:
                 if isinstance(files, dict) and "data" in files:
                     file_data.append({"data": files.get("data"), "mime_type": files.get("mime_type", "application/pdf")})
                 elif isinstance(files, str):
                     file_data.append({"data": files, "mime_type": "application/pdf"})

            print(f"[GoogleAI] 🚀 Generando con: {active_model} | Seed: {seed_used}")

            # 4. LLAMADA A LA API
            client = GoogleAICore(api_key.strip(), active_model)
            result = client.generate_text(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=temperature,
                images=image_data if image_data else None,
                audio_data=audio_data if audio_data else None,
                video_data=video_data if video_data else None,
                file_data=file_data if file_data else None,
                seed=seed_used
            )

            # 5. MANEJO DE RESPUESTA Y ERRORES DE API
            if "error" in result:
                err = result.get("error", {}).get("message", "Unknown API Error")
                print(f"[GoogleAI] ❌ API Error: {err}")
                return ("", f"API Error: {err}", False) # <--- NO ROMPE EL FLUJO

            # 6. EXTRACCIÓN EXITOSA
            if "candidates" in result and result["candidates"]:
                final_text = result["candidates"][0]["content"]["parts"][0]["text"]
                return (final_text, "Success", True)
            else:
                return ("", "No content returned", False)

        except Exception as e:
            # 7. MANEJO DE CRASHES (Python Errors)
            tb = traceback.format_exc()
            print(f"[GoogleAI] 💥 System Error: {tb}")
            return ("", f"System Error: {str(e)}", False) # <--- NO ROMPE EL FLUJO

class GoogleAI_TextNode_Simple:
    """
    Versión simple mantenida para compatibilidad
    """
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "api_key": ("STRING", {"default": "", "multiline": False}),
                "model": (TEXT_MODELS, {"default": "gemini-2.0-flash"}),
                "prompt": ("STRING", {"default": "", "multiline": True}),
            }
        }
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("text",)
    FUNCTION = "generate_text"
    CATEGORY = "GoogleAI"

    def generate_text(self, api_key, model, prompt):
        # Lógica simple directa
        if not api_key: return ("No API Key",)
        try:
            client = GoogleAICore(api_key.strip(), model)
            res = client.generate_text(prompt)
            if "candidates" in res:
                return (res["candidates"][0]["content"]["parts"][0]["text"],)
            return ("Error in generation",)
        except Exception as e:
            return (f"Error: {e}",)

# =============================================================================
# NODE MAPPINGS
# =============================================================================
NODE_CLASS_MAPPINGS = {
    "GoogleAI_TextNode": GoogleAI_TextNode,
    "GoogleAI_TextNode_Simple": GoogleAI_TextNode_Simple,
    "GoogleAI_ModelSelector": GoogleAI_ModelSelector, # <--- Nuevo Router
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "GoogleAI_TextNode": "🧠 Google AI Generator (Pro)",
    "GoogleAI_TextNode_Simple": "🧠 Google AI Text (Simple)",
    "GoogleAI_ModelSelector": "🔀 Google AI Smart Router",
}
