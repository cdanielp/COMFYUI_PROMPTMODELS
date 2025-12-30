# google_text_node.py
import random
from .google_core import GoogleAICore

# =============================================================================
# MODELOS DE TEXTO - Actualizado Diciembre 2025
# =============================================================================
TEXT_MODELS = [
    # Gemini 3 Series (Diciembre 2025)
    "gemini-3-pro-preview",          # Más avanzado, razonamiento complejo
    "gemini-3-flash-preview",        # Pro-level a velocidad Flash
    
    # Gemini 2.5 Series
    "gemini-2.5-pro",                # Razonamiento y código
    "gemini-2.5-flash",              # Balance velocidad/calidad
    "gemini-2.5-flash-lite",         # Ultra rápido y económico
    
    # Gemini 2.0 Series
    "gemini-2.0-flash",              # General purpose
]


class GoogleAI_TextNode:
    """
    Nodo completo de generación de texto usando Gemini API
    Incluye: entradas multimodales (imágenes, audio, video, archivos), system prompt, temperatura, seed
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "api_key": ("STRING", {"default": "", "multiline": False}),
                "prompt": ("STRING", {"default": "", "multiline": True}),
                "model": (TEXT_MODELS, {"default": "gemini-3-pro-preview"}),
                "seed": ("INT", {"default": 42, "min": 0, "max": 2147483647}),
                "randomize_seed": ("BOOLEAN", {"default": True}),
                "system_prompt": ("STRING", {
                    "default": "",
                    "multiline": True
                }),
            },
            "optional": {
                "images": ("IMAGE",),
                "audio": ("AUDIO",),
                "video": ("IMAGE",),  # Video frames como secuencia de imágenes
                "files": ("STRING", {"multiline": True}),  # Base64 de archivos
                "custom_model": ("STRING", {"default": "", "multiline": False}),
                "temperature": ("FLOAT", {
                    "default": 1.0,
                    "min": 0.0,
                    "max": 2.0,
                    "step": 0.1
                }),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("text",)
    FUNCTION = "generate_text"
    CATEGORY = "GoogleAI"

    def generate_text(self, api_key, prompt, model, seed, randomize_seed, system_prompt,
                      images=None, audio=None, video=None, files=None,
                      custom_model="", temperature=1.0):
        
        # Usar modelo personalizado si se proporciona
        active_model = custom_model.strip() if custom_model.strip() else model

        if not api_key.strip():
            return ("❌ Error: API key is required",)

        if not prompt.strip():
            return ("❌ Error: Prompt is required",)

        # Manejar seed
        if randomize_seed or seed == 0:
            seed_used = random.randint(1, 2147483647)
        else:
            seed_used = seed

        # Convertir imágenes a base64
        image_data = []
        if images is not None:
            try:
                # Si es batch de imágenes
                if len(images.shape) == 4:
                    for i in range(images.shape[0]):
                        b64 = GoogleAICore.tensor_to_base64(images[i:i+1])
                        image_data.append(b64)
                        print(f"[GoogleAI] ✅ Imagen {i+1} convertida")
                else:
                    b64 = GoogleAICore.tensor_to_base64(images)
                    image_data.append(b64)
                    print(f"[GoogleAI] ✅ Imagen convertida")
            except Exception as e:
                print(f"[GoogleAI] ⚠️ Error convirtiendo imagen: {e}")

        # Convertir audio a base64
        audio_data = []
        if audio is not None:
            try:
                # ComfyUI audio format: {"waveform": tensor, "sample_rate": int}
                if isinstance(audio, dict):
                    waveform = audio.get("waveform")
                    sample_rate = audio.get("sample_rate", 44100)
                    if waveform is not None:
                        b64 = GoogleAICore.audio_to_base64(waveform, sample_rate)
                        audio_data.append({"data": b64, "mime_type": "audio/wav"})
                        print(f"[GoogleAI] ✅ Audio convertido")
            except Exception as e:
                print(f"[GoogleAI] ⚠️ Error convirtiendo audio: {e}")

        # Video frames (secuencia de imágenes)
        video_data = []
        if video is not None:
            try:
                # Tomar algunos frames del video
                if len(video.shape) == 4:
                    num_frames = min(video.shape[0], 8)  # Máximo 8 frames
                    step = max(1, video.shape[0] // num_frames)
                    for i in range(0, video.shape[0], step)[:num_frames]:
                        b64 = GoogleAICore.tensor_to_base64(video[i:i+1])
                        video_data.append({"data": b64, "mime_type": "image/png"})
                    print(f"[GoogleAI] ✅ {len(video_data)} frames de video convertidos")
            except Exception as e:
                print(f"[GoogleAI] ⚠️ Error convirtiendo video: {e}")

        # Archivos (espera base64 directo o path)
        file_data = []
        if files is not None and files.strip():
            try:
                # Asumir que es base64 directo o lista separada por líneas
                for line in files.strip().split('\n'):
                    if line.strip():
                        file_data.append({"data": line.strip(), "mime_type": "application/pdf"})
                print(f"[GoogleAI] ✅ {len(file_data)} archivo(s) agregados")
            except Exception as e:
                print(f"[GoogleAI] ⚠️ Error procesando archivos: {e}")

        # Info de debug
        print(f"[GoogleAI] 🧠 Modelo: {active_model}")
        print(f"[GoogleAI] 🌡️ Temperatura: {temperature}")
        print(f"[GoogleAI] 🎲 Seed: {seed_used}")
        print(f"[GoogleAI] 🖼️ Imágenes: {len(image_data)}")
        print(f"[GoogleAI] 🔊 Audio: {len(audio_data)}")
        print(f"[GoogleAI] 🎬 Video frames: {len(video_data)}")
        print(f"[GoogleAI] 📄 Archivos: {len(file_data)}")

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

        try:
            # Verificar errores de API
            if "error" in result:
                error_msg = result.get("error", {}).get("message", str(result))
                print(f"[GoogleAI] ❌ API Error: {error_msg}")
                return (f"❌ API Error: {error_msg}",)

            text = result["candidates"][0]["content"]["parts"][0]["text"]
            print(f"[GoogleAI] ✅ Texto generado ({len(text)} chars) | Seed: {seed_used}")
            return (text,)
        except KeyError:
            error_msg = result.get("error", {}).get("message", str(result))
            print(f"[GoogleAI] ❌ Error: {error_msg}")
            return (f"❌ Error: {error_msg}",)
        except Exception as e:
            print(f"[GoogleAI] ❌ Error: {str(e)}")
            return (f"❌ Error: {str(e)}",)


class GoogleAI_TextNode_Simple:
    """
    Versión simplificada del nodo de texto (solo prompt y modelo)
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "api_key": ("STRING", {"default": "", "multiline": False}),
                "model": (TEXT_MODELS, {"default": "gemini-3-flash-preview"}),
                "prompt": ("STRING", {"default": "", "multiline": True}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("text",)
    FUNCTION = "generate_text"
    CATEGORY = "GoogleAI"

    def generate_text(self, api_key, model, prompt):
        if not api_key.strip():
            return ("❌ Error: API key is required",)

        if not prompt.strip():
            return ("❌ Error: Prompt is required",)

        print(f"[GoogleAI] 🧠 Modelo: {model}")

        client = GoogleAICore(api_key.strip(), model)
        result = client.generate_text(prompt)

        try:
            if "error" in result:
                error_msg = result.get("error", {}).get("message", str(result))
                print(f"[GoogleAI] ❌ API Error: {error_msg}")
                return (f"❌ API Error: {error_msg}",)

            text = result["candidates"][0]["content"]["parts"][0]["text"]
            print(f"[GoogleAI] ✅ Texto generado ({len(text)} chars)")
            return (text,)
        except KeyError:
            error_msg = result.get("error", {}).get("message", str(result))
            print(f"[GoogleAI] ❌ Error: {error_msg}")
            return (f"❌ Error: {error_msg}",)
        except Exception as e:
            print(f"[GoogleAI] ❌ Error: {str(e)}")
            return (f"❌ Error: {str(e)}",)


# =============================================================================
# NODE MAPPINGS
# =============================================================================
NODE_CLASS_MAPPINGS = {
    "GoogleAI_TextNode": GoogleAI_TextNode,
    "GoogleAI_TextNode_Simple": GoogleAI_TextNode_Simple,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "GoogleAI_TextNode": "🧠 Google AI Text Generator",
    "GoogleAI_TextNode_Simple": "🧠 Google AI Text (Simple)",
}
