# ComfyUI_WJSetGetPlus

Sistema de memoria de contexto para ComfyUI. **100% compatible con workflows JSON existentes** que usan nodos SetNode/GetNode de rgthree-comfy.

## 🎯 Compatibilidad Verificada

Este paquete fue diseñado específicamente para ser compatible con:
- **Qwen X ZIMG Refiner Dataset Maker.json** ✓
- Workflows que usan `SetNode`, `GetNode` de rgthree
- Workflows que usan `UnetLoaderGGUF` de ComfyUI-GGUF

## 📦 Instalación

```bash
cd ComfyUI/custom_nodes
git clone https://github.com/tu-usuario/ComfyUI_WJSetGetPlus

# Para soporte GGUF completo (opcional)
git clone https://github.com/city96/ComfyUI-GGUF
pip install gguf
```

O descomprime el ZIP directamente en `custom_nodes/`.

## 🧩 Nodos Incluidos

### 📦 SetNode
Almacena cualquier valor con un nombre. **Compatible con rgthree.**

- **Input**: Cualquier tipo (MODEL, CLIP, VAE, IMAGE, LATENT, etc.)
- **Widget**: `name` - Nombre de la variable
- **Output**: Passthrough del mismo valor

### 📤 GetNode
Recupera un valor almacenado. **Compatible con rgthree.**

- **Widget**: `name` - Nombre de la variable a recuperar
- **Output**: El valor almacenado con su tipo original

### 🧠 UnetLoaderGGUF
Carga modelos UNET cuantizados. **Compatible con ComfyUI-GGUF.**

- **Widget**: Lista de modelos `.gguf`, `.safetensors`, `.ckpt`
- **Output**: MODEL

### Nodos Extra

| Nodo | Descripción |
|------|-------------|
| SetNodeNamed | SetNode con widget explícito para nombre |
| UnetLoaderGGUFAdvanced | Loader con opciones de dtype y CPU |
| ListCacheNode | Debug: ver variables almacenadas |
| ClearCacheNode | Limpiar caché entre ejecuciones |

## 💡 Cómo Funciona

```
[CLIPLoader] ─CLIP─→ [SetNode: "MY_CLIP"] ─→ ...
                                ↓
                    (almacena en caché global)
                                ↓
        ... ─→ [GetNode: "MY_CLIP"] ─CLIP─→ [CLIPEncode]
```

El `SetNode` captura el tipo del input automáticamente y lo almacena con el nombre especificado. El `GetNode` recupera el valor con su tipo correcto.

## ⚠️ Orden de Ejecución

**IMPORTANTE**: El `SetNode` debe ejecutarse ANTES que el `GetNode`.

ComfyUI ejecuta nodos en orden topológico. Asegúrate de que existe una dependencia (conexión) que garantice el orden correcto.

## 🔧 API del Caché

```python
from ComfyUI_WJSetGetPlus import get_cache

cache = get_cache()

# Almacenar
cache.set("my_var", value, "MODEL")

# Recuperar
value = cache.get("my_var")
value, dtype = cache.get_with_type("my_var")

# Verificar
cache.exists("my_var")  # True/False

# Listar
cache.list_all()    # {"my_var": "MODEL", ...}
cache.list_names()  # ["my_var", ...]

# Limpiar
cache.clear()
```

## 📋 Tipos Soportados

El sistema detecta automáticamente estos tipos de ComfyUI:

- MODEL, CLIP, VAE, LATENT, IMAGE, MASK
- CONDITIONING, CONTROL_NET, STYLE_MODEL
- CLIP_VISION, SAMPLER, SIGMAS
- STRING, INT, FLOAT

## 🐛 Solución de Problemas

### "Variable 'X' not found"
1. Verifica que SetNode se ejecute antes que GetNode
2. Revisa que el nombre sea exactamente igual (case-sensitive)
3. Usa `ListCacheNode` para ver variables disponibles

### "GGUF support requires ComfyUI-GGUF"
```bash
cd ComfyUI/custom_nodes
git clone https://github.com/city96/ComfyUI-GGUF
pip install gguf
```

### Nodos no aparecen en el menú
1. Reinicia ComfyUI
2. Revisa la consola por errores de importación
3. Verifica que el paquete esté en `custom_nodes/`

## 📋 Requisitos

| Componente | Versión |
|------------|---------|
| ComfyUI | >= 0.3.76 |
| Python | >= 3.10 |
| PyTorch | >= 2.0 |
| gguf (opcional) | >= 0.6.0 |

## 📄 Licencia

MIT License
