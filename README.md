<div align="center">

<img src="prompts models logo.png" alt="Prompt Models Studio" width="200"/>

# 🎨 COMFYUI_PROMPTMODELS

![Version](https://img.shields.io/badge/version-1.1.0-blue.svg)
![ComfyUI](https://img.shields.io/badge/ComfyUI-Custom%20Nodes-green.svg)
![License](https://img.shields.io/badge/license-MIT-purple.svg)
![Python](https://img.shields.io/badge/Python-3.10%2B-yellow.svg)

**Colección de nodos profesionales para ComfyUI**

Desarrollado por [Prompt Models Studio](https://www.skool.com/prompt-models-studio) 🇲🇽

[Instalación](#-instalación) • [Nodos](#-nodos-incluidos) • [Documentación](#-documentación) • [Soporte](#-soporte)

</div>

---

## 🚀 Instalación

### Opción 1: Comfy Registry (Recomendado)
```bash
comfy node install promptmodels
```

### Opción 2: ComfyUI Manager

Busca `PROMPTMODELS` en ComfyUI Manager e instala.

### Opción 3: Manual
```bash
cd ComfyUI/custom_nodes
git clone https://github.com/cdanielp/COMFYUI_PROMPTMODELS.git
pip install -r COMFYUI_PROMPTMODELS/requirements.txt
```

Reinicia ComfyUI.

---

## 📦 Nodos Incluidos

| Nodo | Categoría | Descripción |
|------|-----------|-------------|
| **Google AI Text Generator** | 🤖 AI APIs | Generación de texto con Gemini (multimodal) |
| **Google AI Image Generator** | 🤖 AI APIs | Generación de imágenes con Gemini/Imagen 3 |
| **Grok Text Generator** | 🤖 AI APIs | Generación de texto con xAI Grok |
| **Grok Image Generator** | 🤖 AI APIs | Generación de imágenes con Grok |
| **SetNode / GetNode** | 🧠 Memoria | Sistema de caché compatible con rgthree |
| **DivisorDePrompts** | ✂️ Texto | Divide texto en hasta 10 prompts |
| **Get Last Frame** | 🎬 Video | Extrae frames de secuencias |
| **Text Prompt Blocker** | 🛡️ Seguridad | Filtro de palabras prohibidas |
| **Selector de imágenes** | 🎛️ Selectores Pro | Combina múltiples imágenes+máscaras en batch |
| **Selector de Prompts** | 🎛️ Selectores Pro | Combina múltiples prompts con separadores |
| **Imagen latente Pro** | 🎛️ Selectores Pro | Genera latents con presets de tamaño |
| **Prompt Pro** | 🎛️ Selectores Pro | Constructor de prompts por campos |

---

## 📖 Documentación

### 🤖 ComfyUI_GoogleAI

Conecta ComfyUI con Google AI (Gemini API) para generación de texto e imágenes.

**Características:**
- Soporte multimodal (imágenes, audio, video, PDFs)
- Modelos: Gemini 3, Gemini 2.5, Imagen 3
- Presets de resolución hasta 4K
- Sistema de semillas para reproducibilidad

**Requisitos:** API Key de [Google AI Studio](https://aistudio.google.com/apikey)

---

### 🤖 ComfyUI_Grok

Conecta ComfyUI con xAI API (Grok) para generación de texto e imágenes.

**Características:**
- Generación de texto con Grok 4
- Generación de imágenes con estilos
- 12 estilos artísticos incluidos
- Control de temperatura y tokens

**Requisitos:** API Key de [xAI Console](https://console.x.ai/)

---

### 🧠 ComfyUI_WJSetGetPlus

Sistema de memoria de contexto. **100% compatible** con workflows que usan SetNode/GetNode de rgthree-comfy.

**Nodos:** SetNode, GetNode, UnetLoaderGGUF, ListCacheNode, ClearCacheNode

---

### 🎛️ Selectores Pro

Suite de nodos para selección múltiple, generación de latents y construcción de prompts profesionales.

#### Selector de imágenes

Selecciona y combina hasta 12 slots de imagen + máscara.

| Entrada | Opciones |
|---------|----------|
| `fallback` | `error` \| `slot1` |
| `mode` | `auto` \| `single_only` \| `batch_only` |
| `img1..img12` | IMAGE |
| `mask1..mask12` | MASK |
| `on1..on12` | BOOLEAN |

**Salidas:** `image` (IMAGE), `mask` (MASK)

**Comportamiento:**
- 1 slot activo → salida single
- 2+ slots activos → salida batch concatenado
- Valida que todas las imágenes tengan el mismo tamaño

---

#### Selector de Prompts

Selecciona y combina hasta 12 prompts de texto.

| Entrada | Opciones |
|---------|----------|
| `fallback` | `error` \| `p1` |
| `join_with` | `\n\n` \| `\n` \| `\|` \| `,` |
| `mode` | `auto` \| `single_only` \| `join_only` |
| `p1..p12` | STRING (multiline) |
| `on1..on12` | BOOLEAN |

**Salidas:** `text` (STRING)

---

#### Imagen latente Pro

Genera un latent vacío con presets predefinidos. **Un solo dropdown, sin cálculos.**

| Entrada | Opciones |
|---------|----------|
| `size_preset` | 29 presets (Test, Medio, Grande, Social) |
| `batch_size` | INT (1-64) |
| `rounding` | `auto_round` \| `strict` |

**Salidas:** `latent` (LATENT)

**Presets incluidos:**

| Categoría | Ratios disponibles |
|-----------|-------------------|
| **Test** (256 base) | 1:1, 4:5, 3:4, 2:3, 9:16, 16:9, 3:2, 2:1, 21:9 |
| **Medio** (512 base) | 1:1, 4:5, 3:4, 2:3, 9:16, 16:9, 3:2, 2:1, 21:9 |
| **Grande** (1024 base) | 1:1, 4:5, 3:4, 2:3, 9:16, 16:9, 3:2, 2:1, 21:9 |
| **Social** | 720×1280 (9:16), 1280×720 (16:9) |

---

#### Prompt Pro

Constructor de prompts por campos con 10 diseños predefinidos. Solo requiere **👤 Sujeto**, todo lo demás es opcional.

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

**Campos disponibles:**

| Campo | Emoji | Obligatorio |
|-------|-------|-------------|
| Sujeto | 👤 | ✅ Sí |
| Acción / Pose | 🧍 | No |
| Emoción / Expresión | 🎭 | No |
| Vestuario / Props | 👗 | No |
| Fondo / Entorno | 🏞️ | No |
| Estilo | 🎨 | No |
| Paleta / Colores | 🎨 | No |
| Iluminación | 💡 | No |
| Cámara / Lente | 📷 | No |
| Materiales / Texturas | 🧪 | No |
| Composición | 🧷 | No |
| Detalle | 🔎 | No |
| Atmósfera | 🌫️ | No |
| Calidad | ✨ | No |
| Restricciones | 🧯 | No |
| Extra | ➕ | No |

**Opciones globales:**
- `🔗 Separador`: `, ` | ` ` | `\n` | ` | `
- `📌 Prefijo` / `📌 Sufijo`: Texto adicional
- `🧹 Normalizar`: Limpia espacios y comas duplicadas
- `🧼 Evitar duplicados`: Elimina frases repetidas

**Salidas:** `text` (STRING)

---

### ✂️ DivisorDePrompts

Divide texto multilínea en hasta 10 prompts independientes usando párrafos como separador.

**Salidas:** `prompt_01` a `prompt_10` + `count`

---

### 🎬 get_last_frame

Extrae frames específicos de secuencias de video o batches.

**Nodos:** GetLastFrame, GetFrameByIndex

---

### 🛡️ text_prompt_blocker

Nodo de seguridad que analiza y filtra prompts con palabras prohibidas.

**Modos:** Hard block (detiene workflow) o Soft block (string vacío)

---

## 🔑 API Keys Requeridas

| Nodo | Proveedor | Obtener Key |
|------|-----------|-------------|
| Google AI | Google | [aistudio.google.com/apikey](https://aistudio.google.com/apikey) |
| Grok | xAI | [console.x.ai](https://console.x.ai/) |

> **Nota:** Los nodos de Selectores Pro no requieren API keys.

---

## 📋 Requisitos

| Componente | Versión |
|------------|---------|
| ComfyUI | >= 0.3.76 |
| Python | >= 3.10 |
| PyTorch | >= 2.0 |

---

## 📜 Licencia

MIT License - Libre para uso personal y comercial.

---

## 💬 Soporte

- **GitHub Issues:** [Reportar problema](https://github.com/cdanielp/COMFYUI_PROMPTMODELS/issues)
- **Comunidad:** [Prompt Models Studio en Skool](https://www.skool.com/prompt-models-studio)

---

<div align="center">

**Hecho con ❤️ en México por [Prompt Models Studio](https://www.skool.com/prompt-models-studio)**

⭐ Si te fue útil, regálanos una estrella en GitHub

</div>
