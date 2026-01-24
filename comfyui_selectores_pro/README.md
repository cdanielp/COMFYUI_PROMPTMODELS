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

Genera un latent vacío usando presets de tamaño predefinidos. Un solo dropdown, sin cálculos.

**Entradas:**
- `size_preset`: Dropdown con todos los presets
- `batch_size`: INT (1-64)
- `rounding`: `auto_round` | `strict`

**Salidas:** `latent` (LATENT)

**Presets disponibles:**

| Categoría | Presets |
|-----------|---------|
| **Test** | 256×256 (1:1), 208×256 (4:5), 192×256 (3:4), 168×256 (2:3), 144×256 (9:16), 256×144 (16:9), 256×168 (3:2), 256×128 (2:1), 256×112 (21:9) |
| **Medio** | 512×512 (1:1), 408×512 (4:5), 384×512 (3:4), 344×512 (2:3), 288×512 (9:16), 512×288 (16:9), 512×344 (3:2), 512×256 (2:1), 512×216 (21:9) |
| **Grande** | 1024×1024 (1:1), 816×1024 (4:5), 768×1024 (3:4), 680×1024 (2:3), 576×1024 (9:16), 1024×576 (16:9), 1024×680 (3:2), 1024×512 (2:1), 1024×440 (21:9) |
| **Social** | 720×1280 (9:16), 1280×720 (16:9) |

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
