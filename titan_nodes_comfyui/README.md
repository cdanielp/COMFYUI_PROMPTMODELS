# 🏰 Titan Suite para ComfyUI

<div align="center">

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![ComfyUI](https://img.shields.io/badge/ComfyUI-compatible-green.svg)
![Cloud](https://img.shields.io/badge/Cloud-Native-orange.svg)
![License](https://img.shields.io/badge/license-MIT-purple.svg)

**Nodos esenciales en español para eliminar fricción y evitar errores.**

*Compatible con ComfyUI local, ComfyDeploy y RunComfy*

</div>

---

## 📦 Nodos Incluidos

| Nodo | Descripción |
|------|-------------|
| 🏰 **Titan Maestro** | Control central: prompts, resolución, latente y búnker |
| 🏰 **Titan Maestro Lite** | Versión simplificada sin búnker |
| 🕵️ **Titan Inspector** | Extractor de metadatos de imágenes AI |
| 🕵️ **Titan Inspector Batch** | Inspección masiva de carpetas |
| 🧬 **Titan Power LoRA 5x** | Cargador blindado de 5 LoRAs |
| 🔍 **Titan LoRA Info** | Inspector de metadata de LoRAs |
| 📚 **Titan LoRA Stack** | Sistema de apilamiento de LoRAs |

---

## 🏰 Titan Maestro (Control Central)

**Reemplaza 4+ nodos estándar en uno solo.**

### Características

- **Búnker de Ideas**: Guarda y recupera prompts favoritos (persiste en la nube)
- **Presets de Resolución**: Menú con 17 tamaños optimizados
- **Wildcards**: Escribe `{gato|perro|pájaro}` y el nodo elegirá uno al azar
- **Wildcards con Peso**: Usa `{opción::2|otra::1}` para probabilidades
- **Resolución Custom**: Overridea el preset con valores personalizados
- **Semilla Inteligente**: 0 = aleatorio, cualquier otro = fijo

### Presets de Resolución Incluidos

| Categoría | Presets |
|-----------|---------|
| **SDXL/Flux** | Cuadrado 1024, Retrato 832x1216, Paisaje 1216x832 |
| **Redes Sociales** | TikTok, YouTube 720p/1080p, Instagram Post/Story |
| **Cinematic** | 2.35:1, 16:9, Anamórfico |
| **SD 1.5** | 512x512, 512x768, 768x512 |
| **Alta Res** | 2K en todas las orientaciones |

### Ejemplo de Wildcards

```
a {beautiful|gorgeous|stunning} {woman|girl} with {red|blue|green} hair
```

Con peso:

```
{realistic photo::3|anime style::1|oil painting::1}
```

### Salidas

| Salida | Descripción |
|--------|-------------|
| `Latente` | Tensor listo para el sampler |
| `Positivo` | Prompt procesado con wildcards resueltos |
| `Negativo` | Prompt negativo limpio |
| `Ancho/Alto` | Dimensiones según preset o custom |
| `Semilla Usada` | Semilla efectiva (útil para reproducir) |

---

## 🧬 Titan Power LoRA 5x (Blindado)

**El cargador de LoRAs más robusto.**

### Características

- **🛡️ Anti-Crash**: LoRAs incompatibles son ignorados automáticamente sin detener el flujo
- **🏷️ Trigger Words**: Detecta y muestra las palabras clave de cada LoRA
- **5️⃣ Ranuras**: Con interruptores On/Off individuales
- **⚖️ Fuerza Dual**: Control separado para Modelo y CLIP
- **📊 Reporte**: Estado detallado de cada LoRA

### Detección de Triggers

Soporta múltiples formatos de metadata:
- CivitAI (`trainedWords`)
- Kohya (`modelspec.trigger_phrase`)
- Tag frequency (`ss_tag_frequency`)
- Dataset dirs (`ss_dataset_dirs`)

### Salidas

| Salida | Descripción |
|--------|-------------|
| `Modelo` | Modelo con LoRAs aplicados |
| `CLIP` | CLIP con LoRAs aplicados |
| `Reporte` | Estado de cada slot |
| `Triggers Combinados` | Todos los triggers unidos |

---

## 🕵️ Titan Inspector (Metadatos)

**Recupera la receta de cualquier imagen AI.**

### Formatos Soportados

- ✅ Automatic1111 / Forge / reForge
- ✅ ComfyUI (workflow embebido)
- ✅ NovelAI
- ✅ InvokeAI
- ✅ EXIF genérico

### Información Extraída

- Prompt positivo completo
- Prompt negativo
- Semilla (Seed)
- Dimensiones originales
- Modelo, Sampler, Steps, CFG (cuando disponible)

### Búsqueda Inteligente

El inspector busca automáticamente en:
1. Ruta exacta proporcionada
2. Carpeta `input/`
3. Carpeta `output/`

---

## ☁️ Instalación

### ComfyDeploy / RunComfy (Cloud)

1. Sube la carpeta `titan_nodes_comfyui` a `custom_nodes/`
2. Reinicia la máquina
3. Los nodos aparecerán en la categoría **"Titan Suite 🇪🇸"**

> 💾 Tus prompts guardados persisten en `input/titan_vault.json`

### Instalación Local

```bash
# Navegar a custom_nodes
cd ComfyUI/custom_nodes

# Clonar repositorio
git clone https://github.com/tu-usuario/titan_nodes_comfyui.git

# Instalar dependencias
pip install -r titan_nodes_comfyui/requirements.txt

# Reiniciar ComfyUI
```

### Instalación Manual

1. Descarga el ZIP del repositorio
2. Extrae en `ComfyUI/custom_nodes/`
3. Ejecuta:
   ```bash
   pip install safetensors Pillow torch
   ```
4. Reinicia ComfyUI

---

## 🔧 Troubleshooting

### "LoRA incompatible ignorado"

Esto es **comportamiento esperado**. El escudo anti-crash detectó que el LoRA es para un modelo base diferente (ej: SD1.5 vs SDXL).

### "Sin metadatos encontrados"

La imagen fue guardada sin metadata o en formato no soportado. Prueba con una imagen generada directamente desde A1111 o ComfyUI.

### "folder_paths no disponible"

Estás ejecutando fuera de ComfyUI. Los nodos usan rutas relativas como fallback.

### Los triggers no aparecen

Algunos LoRAs no incluyen metadata de triggers. Revisa CivitAI para encontrar los triggers manualmente.

### La semilla muestra -1

Cuando el Inspector no puede recuperar la semilla original, retorna `-1` (no `0`) para evitar confusión, ya que `0` suele significar "aleatorio" en muchos nodos.

---

## ⚠️ Limitaciones Conocidas

### Menú de Favoritos (Búnker)

Cuando guardas un nuevo prompt con `💾 GUARDAR`, el archivo JSON se actualiza correctamente, pero **el menú desplegable no se refresca automáticamente** en la interfaz.

**Solución:** Presiona `F5` o recarga la página del navegador para ver el nuevo favorito en el menú.

> Esto es una limitación de cómo ComfyUI maneja los widgets estáticos. Una futura versión podría incluir un script JS para auto-refresh.

### LORA_STACK (Tipo Personalizado)

El nodo `Titan LoRA Stack` retorna un tipo de dato personalizado `LORA_STACK`. Este output:

- ✅ Se puede conectar a otro `Titan LoRA Stack` (para apilar)
- ❌ **NO** se puede conectar directamente a un `KSampler`
- ❌ **NO** es compatible con nodos estándar de ComfyUI

Para usar el stack, necesitas un nodo que procese ese tipo de dato (o usar directamente `Titan Power LoRA 5x`).

### Resolución Custom

Los valores de `ancho_custom` y `alto_custom` se ajustan automáticamente:
- Se redondean al múltiplo de 8 más cercano (requisito de modelos de difusión)
- Mínimo: 64px
- Máximo: 4096px

---

## 📝 Changelog

### v1.0.0
- 🎉 Lanzamiento inicial
- 🏰 Titan Maestro con Búnker y Wildcards
- 🧬 MultiLora 5x con Anti-Crash
- 🕵️ Inspector con soporte multi-formato
- 🔍 LoRA Info para inspección sin carga
- 📚 LoRA Stack para workflows modulares

---

## 🤝 Contribuir

¿Encontraste un bug? ¿Tienes una idea? ¡Abre un Issue o PR!

---

## 📜 Licencia

MIT License - Usa libremente en proyectos personales y comerciales.

---

<div align="center">

**Hecho con ❤️ por Prompt Models**

*¿Te fue útil? ⭐ el repo!*

</div>
