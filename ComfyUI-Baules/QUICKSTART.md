# ComfyUI-Baules - Guía Rápida

## Instalación (2 minutos)

```bash
cd ComfyUI/custom_nodes
git clone https://github.com/cdanielp/COMFYUI_PROMPTMODELS.git ComfyUI-Baules
```

Reinicia ComfyUI. Busca la categoría **Baúles/** en el menú de nodos.

---

## Uso Básico - Imágenes Locales

### 1. Agregar Imágenes
1. Añade nodo: `🧰 Baúl Imágenes (Local)`
2. `📂 Acción` → "Agregar archivos"
3. `📎 Rutas a importar` → Pega rutas absolutas (una por línea):
   ```
   C:\Users\Tu\Pictures\ref1.png
   /home/user/images/ref2.jpg
   ```
4. `Queue Prompt` → Verás "✅ X archivo(s) agregado(s)" en consola

### 2. Usar Imagen
1. Cambia `📂 Acción` a "Nada"
2. En dropdown `🖼️ Selección` elige una imagen
3. Conecta output `IMAGE` a tu pipeline (ControlNet, IP-Adapter, etc.)
4. `Queue Prompt` → Imagen cargada

---

## Uso Básico - Referencias Cloud

### 1. Agregar Referencias
1. Añade nodo: `☁️🧰 Baúl Imágenes (Cloud)`
2. `🔗 Acción` → "Agregar referencia(s)"
3. `📎 Agregar` → Pega URLs (una por línea):
   ```
   https://example.com/pose_ref.png
   s3://bucket/image.jpg
   ```
4. `Queue Prompt` → Referencias guardadas

### 2. Usar Referencia
1. Cambia `🔗 Acción` a "Nada"
2. `🖼️ Selección` → Pega la URL exacta a usar
3. Conecta output `STRING` a nodo "External Image"
4. `Queue Prompt` → External Image descarga la imagen

---

## Prompt Constructor

1. Añade: `🧱 Prompt Constructor`
2. Conecta input `CLIP` desde tu checkpoint
3. Llena campos opcionales:
   - `👤 Sujeto`: "woman with long hair"
   - `🎨 Estilo`: "photorealistic, 8k uhd"
   - `✨ Calidad`: "masterpiece, best quality"
4. Conecta output `positivo` al sampler
5. `Queue Prompt` → Prompt concatenado automáticamente

---

## Guardar Workflow

Archivo → Save → Los baúles locales NO exportan imágenes (solo IDs).  
Los baúles Cloud y Prompts SÍ exportan sus datos con el workflow.

**¿Dudas?** Lee el [README completo](README.md) o reporta en [Issues](https://github.com/cdanielp/COMFYUI_PROMPTMODELS/issues).
