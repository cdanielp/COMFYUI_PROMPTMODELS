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
    Nodo multimodal de generación de texto usando Gemini API
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
                "temperature": ("FLOAT", {
                    "default": 1.0,
                    "min": 0.0,
                    "max": 2.0,
                    "step": 0.1
                }),
            },
            "optional": {
                "custom_model": ("STRING", {"default": "", "multiline": False}),
                "image_1": ("IMAGE",),
                "image_2": ("IMAGE",),
                "image_3": ("IMAGE",),
                "image_4": ("IMAGE",),
                "image_5": ("IMAGE",),
                "audio": ("AUDIO",),
                "video": ("IMAGE",),
                "files": ("DOCUMENT",),  # Para PDFs y documentos
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("text",)
    FUNCTION = "generate_text"
    CATEGORY = "GoogleAI"

    def generate_text(self, api_key, prompt, model, seed, randomize_seed, system_prompt, temperature,
                      custom_model="",
                      image_1=None, image_2=None, image_3=None, image_4=None, image_5=None,
                      audio=None, video=None, files=None):
        
        # Usar modelo personalizado si se proporciona
        active_model = custom_model.strip() if custom_model.strip() else model

        if not api_key.strip():
            return ("❌ Error: API key is required",)

        if not prompt.strip():
            return ("❌ Error: Prompt is required",)

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

        # Convertir imágenes a base64 (5 entradas individuales)
        image_data = []
        for idx, img in enumerate([image_1, image_2, image_3, image_4, image_5], 1):
            if img is not None:
                try:
                    b64 = GoogleAICore.tensor_to_base64(img)
                    image_data.append(b64)
                    print(f"[GoogleAI] ✅ Imagen {idx} convertida")
                except Exception as e:
                    print(f"[GoogleAI] ⚠️ Error en imagen {idx}: {e}")

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

        # Archivos/Documentos
        file_data = []
        if files is not None:
            try:
                # Manejar diferentes formatos de entrada de documentos
                if isinstance(files, dict):
                    # Formato dict con data y mime_type
                    if "data" in files:
                        file_data.append({
                            "data": files.get("data", ""),
                            "mime_type": files.get("mime_type", "application/pdf")
                        })
                elif isinstance(files, str) and files.strip():
                    # Base64 string directo
                    file_data.append({"data": files.strip(), "mime_type": "application/pdf"})
                elif isinstance(files, list):
                    # Lista de archivos
                    for f in files:
                        if isinstance(f, dict) and "data" in f:
                            file_data.append({
                                "data": f.get("data", ""),
                                "mime_type": f.get("mime_type", "application/pdf")
                            })
                        elif isinstance(f, str) and f.strip():
                            file_data.append({"data": f.strip(), "mime_type": "application/pdf"})
                if file_data:
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
