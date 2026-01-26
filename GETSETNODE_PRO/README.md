# GETSETNODE_PRO

Sistema de memoria de contexto para ComfyUI con soporte para carga de modelos GGUF.

## 🎯 Características

- **Sistema de caché thread-safe** para compartir datos entre nodos
- **Detección automática de tipos** ComfyUI (MODEL, CLIP, VAE, IMAGE, etc.)
- **Compatible con workflows existentes** que usan SetNode/GetNode de rgthree-comfy
- **Cargador GGUF integrado** con soporte para múltiples formatos

## 📦 Instalación

```bash
cd ComfyUI/custom_nodes
git clone https://github.com/tu-usuario/GETSETNODE_PRO
```

### Dependencias opcionales

```bash
# Para soporte completo de GGUF
pip install gguf>=0.6.0

# O instalar ComfyUI-GGUF
git clone https://github.com/city96/ComfyUI-GGUF
```

## 🧩 Nodos Disponibles

### Memoria y Contexto

| Nodo | Display Name | Descripción |
|------|--------------|-------------|
| `PRO_SetNode` | 📦 PRO Set Node | Almacena cualquier valor con nombre auto-detectado |
| `PRO_GetNode` | 📤 PRO Get Node | Recupera un valor almacenado por nombre |
| `PRO_SetNodeNamed` | 📦 PRO Set Node (Named) | SetNode con input explícito para el nombre |
| `PRO_ListCacheNode` | 📋 PRO List Cache | Debug: muestra todas las variables en caché |
| `PRO_ClearCacheNode` | 🗑️ PRO Clear Cache | Limpia la caché entre ejecuciones |

### Cargadores de Modelos

| Nodo | Display Name | Descripción |
|------|--------------|-------------|
| `PRO_UnetLoaderGGUF` | 🧠 PRO Unet Loader GGUF | Carga modelos UNET (.gguf, .safetensors, .ckpt) |
| `PRO_UnetLoaderGGUFAdvanced` | 🧠 PRO Unet Loader GGUF+ | Loader con opciones de dtype y CPU |

## 💡 Uso Básico

### Set/Get Pattern

```
[CLIPLoader] ─CLIP─▶ [PRO_SetNode: "MY_CLIP"] ─▶ ...
                              ↓
                  (almacena en caché global)
                              ↓
      ... ─▶ [PRO_GetNode: "MY_CLIP"] ─CLIP─▶ [CLIPEncode]
```

### Nombrar Variables

Hay 3 formas de asignar nombre a una variable:

1. **Por título del nodo**: Renombra el nodo a `Set_NOMBRE` o `PRO_Set_NOMBRE`
2. **Por widget**: En `PRO_SetNodeNamed` usa el input `name`
3. **Por widgets_values**: El primer valor del widget se usa como nombre

### Ejemplo con GetNode

```
PRO_GetNode con name="MY_CLIP" 
   ↓
Busca "MY_CLIP" en caché
   ↓
Retorna el valor con su tipo original
```

## ⚠️ Orden de Ejecución

**IMPORTANTE**: El `SetNode` debe ejecutarse **ANTES** que el `GetNode`.

ComfyUI ejecuta nodos en orden topológico. Asegúrate de que existe una conexión que garantice el orden correcto, o usa el output del SetNode como trigger.

## 🔧 API del Caché

```python
from GETSETNODE_PRO import get_cache

cache = get_cache()

# Almacenar (detecta tipo automáticamente)
cache.set("my_model", model_value)
cache.set("my_clip", clip_value, "CLIP")  # tipo explícito

# Recuperar
value = cache.get("my_var")
value, dtype = cache.get_with_type("my_var")
dtype = cache.get_type("my_var")

# Verificar
exists = cache.exists("my_var")  # True/False

# Listar
cache.list_all()    # {"my_var": "MODEL", "clip": "CLIP"}
cache.list_names()  # ["my_var", "clip"]

# Limpiar
cache.remove("my_var")  # elimina una variable
cache.clear()           # limpia todo
```

## 📋 Tipos Soportados

El sistema detecta automáticamente estos tipos de ComfyUI:

| Categoría | Tipos |
|-----------|-------|
| Modelos | MODEL, CLIP, VAE, CONTROL_NET, STYLE_MODEL, UPSCALE_MODEL |
| Datos | LATENT, IMAGE, MASK, CONDITIONING |
| Vision | CLIP_VISION, CLIP_VISION_OUTPUT |
| Samplers | SAMPLER, SIGMAS, NOISE, GUIDER |
| Primitivos | STRING, INT, FLOAT |

## 🧠 UnetLoaderGGUF

### Formatos soportados
- `.gguf` - Modelos cuantizados (requiere gguf o ComfyUI-GGUF)
- `.safetensors` - SafeTensors
- `.ckpt` / `.pt` / `.pth` - Checkpoints PyTorch
- `.bin` - Binarios PyTorch

### Carpetas escaneadas
- `ComfyUI/models/unet/`
- `ComfyUI/models/diffusion_models/`
- `ComfyUI/models/checkpoints/`

### Versión Avanzada

`PRO_UnetLoaderGGUFAdvanced` añade:
- **dtype**: auto, float32, float16, bfloat16
- **force_cpu**: Forzar carga en CPU

## 🛠 Solución de Problemas

### "Variable 'X' not found"
1. Verifica que SetNode se ejecute antes que GetNode
2. Revisa que el nombre sea exactamente igual (case-sensitive)
3. Usa `PRO_ListCacheNode` para ver variables disponibles

### "Requires ComfyUI-GGUF"
```bash
cd ComfyUI/custom_nodes
git clone https://github.com/city96/ComfyUI-GGUF
pip install gguf
```

### Nodos no aparecen en el menú
1. Reinicia ComfyUI completamente
2. Revisa la consola por errores de importación
3. Busca en la categoría `GetSetNode_Pro`

### Verificar instalación
En la consola de ComfyUI deberías ver:
```
✓ GETSETNODE_PRO v1.0.0 loaded
```

## 📋 Requisitos

| Componente | Versión |
|------------|---------|
| ComfyUI | >= 0.3.76 |
| Python | >= 3.10 |
| PyTorch | >= 2.0 |
| gguf (opcional) | >= 0.6.0 |
| safetensors | >= 0.4.0 |

## 📁 Estructura del Paquete

```
GETSETNODE_PRO/
├── __init__.py          # Registro de nodos
├── setget_nodes.py      # PRO_SetNode, PRO_GetNode, utilidades
├── qwen_cache.py        # Sistema de caché singleton
├── unet_loader_gguf.py  # Cargadores de modelos
├── requirements.txt     # Dependencias
└── README.md
```

## 📄 Licencia

MIT License

---

**v1.0.0** | Creado por Prompt Models Studio
