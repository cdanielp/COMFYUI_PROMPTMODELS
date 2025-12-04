# get_last_frame.py
# Nodo personalizado para ComfyUI
# Extrae el último frame (o cualquier frame por índice) de una secuencia de imágenes

class GetLastFrame:
    """
    Toma una lista de imágenes (IMAGE) y devuelve solo la última.
    Ideal para workflows de video (AnimateDiff, VideoHelperSuite) o batch processing.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "frames": ("IMAGE",),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)
    FUNCTION = "get_last_frame"
    CATEGORY = "🧩 Utility"

    def get_last_frame(self, frames):
        if frames is None or len(frames) == 0:
            raise ValueError("El input 'frames' está vacío. No se puede seleccionar el último elemento.")
        
        # frames es un tensor de shape [batch, height, width, channels]
        # Seleccionamos el último frame y mantenemos las dimensiones
        last_frame = frames[-1:, :, :, :]
        return (last_frame,)


class GetFrameByIndex:
    """
    Versión extendida: permite seleccionar cualquier frame por índice.
    Índice -1 = último frame, 0 = primero, etc.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "frames": ("IMAGE",),
                "index": ("INT", {
                    "default": -1,
                    "min": -9999,
                    "max": 9999,
                    "step": 1,
                    "display": "number"
                }),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)
    FUNCTION = "get_frame_by_index"
    CATEGORY = "🧩 Utility"

    def get_frame_by_index(self, frames, index):
        if frames is None or len(frames) == 0:
            raise ValueError("El input 'frames' está vacío.")
        
        total_frames = len(frames)
        
        # Validar índice y hacer fallback si está fuera de rango
        if index >= total_frames:
            index = total_frames - 1  # último frame
        elif index < -total_frames:
            index = 0  # primer frame
        
        # Seleccionar frame manteniendo dimensiones [1, H, W, C]
        selected_frame = frames[index:index+1, :, :, :] if index >= 0 else frames[index:, :, :, :][:1]
        return (selected_frame,)


# Registro de nodos para ComfyUI
NODE_CLASS_MAPPINGS = {
    "GetLastFrame": GetLastFrame,
    "GetFrameByIndex": GetFrameByIndex,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "GetLastFrame": "Get Last Frame",
    "GetFrameByIndex": "Get Frame by Index",
}
