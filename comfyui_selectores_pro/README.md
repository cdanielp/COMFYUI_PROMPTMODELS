# ComfyUI Selectores Pro

Paquete de nodos personalizados para ComfyUI que incluye selectores múltiples, generación de latents y construcción de prompts.

## Instalación

Copiar la carpeta a:
```
ComfyUI/custom_nodes/comfyui_selectores_pro/
```
Reiniciar ComfyUI. Los nodos aparecen en la categoría **Selectores Pro**.

## Estructura del paquete

```
comfyui_selectores_pro/
├── __init__.py           # Registro de nodos
├── selector_imagenes.py  # Nodo Selector de imágenes
├── selector_prompts.py   # Nodo Selector de Prompts
├── imagen_latente.py     # Nodo Imagen latente Pro
├── prompt_pro.py         # Nodo Prompt Pro
└── README.md
```

## Nodos

### 1. Selector de imágenes

Selecciona y combina hasta 12 slots de imagen + máscara.

**Entradas:**
- `fallback`: `error` | `slot1`
- `mode`: `auto` | `single_only` | `batch_only`
- `img1..img12`: IMAGE
- `mask1..mask12`: MASK
- `on1..on12`: BOOLEAN

**Salidas:** `image` (IMAGE), `mask` (MASK)

---

### 2. Selector de Prompts

Selecciona y combina hasta 12 prompts de texto.

**Entradas:**
- `fallback`: `error` | `p1`
- `join_with`: `\n\n` | `\n` | `|` | `,`
- `mode`: `auto` | `single_only` | `join_only`
- `p1..p12`: STRING (multiline)
- `on1..on12`: BOOLEAN

**Salidas:** `text` (STRING)

---

### 3. Imagen latente Pro

Genera un latent vacío usando presets de ratio y tamaño.

**Entradas:**
- `ratio`: `1:1` | `9:16` | `16:9`
- `size`: `256` | `320` | `384` | `448` | `512` | `640` | `768` | `896` | `1024`
- `batch_size`: INT (1-64)
- `rounding`: `auto_round` | `strict`

**Salidas:** `latent` (LATENT)

---

### 4. Prompt Pro

Constructor de prompts por campos con diseños predefinidos. Solo requiere el campo **👤 Sujeto**, todo lo demás es opcional.

**Diseños disponibles:**
- Retrato Pro
- Cinemático
- Producto E-commerce
- Anime Clean
- Concept Art
- Arquitectura
- Moda Editorial
- Interior Design
- Vertical Reels (9:16)
- Thumbnail YouTube (16:9)

**Campos:**
| Campo | Obligatorio |
|-------|-------------|
| 👤 Sujeto | ✅ Sí |
| 🧍 Acción / Pose | No |
| 🎭 Emoción / Expresión | No |
| 👗 Vestuario / Props | No |
| 🏞️ Fondo / Entorno | No |
| 🎨 Estilo | No |
| 🎨 Paleta / Colores | No |
| 💡 Iluminación | No |
| 📷 Cámara / Lente | No |
| 🧪 Materiales / Texturas | No |
| 🧷 Composición | No |
| 🔎 Detalle | No |
| 🌫️ Atmósfera | No |
| ✨ Calidad | No |
| 🧯 Restricciones | No |
| ➕ Extra | No |

**Opciones:**
- `🔗 Separador`: `, ` | ` ` | `\n` | ` | `
- `📌 Prefijo` / `📌 Sufijo`: STRING opcional
- `🧹 Normalizar`: Limpia espacios y comas
- `🧼 Evitar duplicados`: Elimina frases repetidas

**Salidas:** `text` (STRING)

---

## Reglas de Batch (Selector de imágenes)

- Todas las imágenes activas deben tener el mismo tamaño (H, W, C)
- Todas las máscaras activas deben tener el mismo tamaño (H, W)
- Mismatch → error indicando el slot problemático

## Requisitos

- ComfyUI
- Python 3.10+
- PyTorch (incluido en ComfyUI)

Sin dependencias externas.
