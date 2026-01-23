# ComfyUI-Baules 🧰

Sistema modular de gestión de assets y prompts para workflows de ComfyUI. Organiza tus imágenes, referencias y presets de texto en "baúles" reutilizables y compartidos.

## Características Principales

- **📦 Baúles de Imágenes (Local)**: Biblioteca global por tipo (imágenes, openpose, depth, lineart) con output `IMAGE`
- **☁️ Baúles Cloud Ref**: Gestión de referencias remotas (URLs, asset IDs) con output `STRING` para integración con External Image
- **📝 Baúles de Prompts**: 8 nodos especializados con presets persistentes (Estilos, Poses, Cámara, Iluminación, etc.)
- **🧱 Prompt Constructor**: Concatenador inteligente de campos opcionales que reemplaza CLIP Text Encode
- **🔒 Sin conflictos**: Diseño sin estado global de selección - cada nodo usa su propia selección del dropdown
- **💾 Persistencia automática**: Catálogos en disco con escritura atómica, sin corrupción de datos

## Instalación

### Método Manual

**Windows:**
```powershell
cd C:\path\to\ComfyUI\custom_nodes
git clone https://github.com/cdanielp/COMFYUI_PROMPTMODELS.git ComfyUI-Baules
```

**Linux/Mac:**
```bash
cd ~/ComfyUI/custom_nodes
git clone https://github.com/cdanielp/COMFYUI_PROMPTMODELS.git ComfyUI-Baules
```

Luego reinicia ComfyUI. Los nodos aparecerán en la categoría **Baúles/**.

## Requisitos

- **ComfyUI** (última versión recomendada)
- **Python 3.10+**
- **Pillow** (normalmente ya incluido con ComfyUI)

No requiere instalación adicional de dependencias.

## Nodos Incluidos

### Baúles de Imágenes (Local)

| Nodo | Output | Uso |
|------|--------|-----|
| 🧰 Baúl Imágenes (Local) | `IMAGE` | Referencias generales, concept art |
| 🧍 Baúl OpenPose (Local) | `IMAGE` | Poses de control para ControlNet |
| 🗺️ Baúl Depth (Local) | `IMAGE` | Mapas de profundidad |
| ✍️ Baúl Lineart (Local) | `IMAGE` | Line art, bocetos |

**Funcionamiento:** Almacenamiento **global por tipo**. Todos los nodos del mismo tipo comparten la misma biblioteca de archivos.

### Baúles de Referencias Cloud

| Nodo | Output | Uso |
|------|--------|-----|
| ☁️🧰 Baúl Imágenes (Cloud) | `STRING` | URLs o asset IDs → External Image |
| ☁️🧍 Baúl OpenPose (Cloud) | `STRING` | Referencias OpenPose remotas |
| ☁️🗺️ Baúl Depth (Cloud) | `STRING` | Referencias Depth remotas |
| ☁️✍️ Baúl Lineart (Cloud) | `STRING` | Referencias Lineart remotas |
| ☁️🧊 Baúl 3D / Referencias (Cloud) | `STRING` | Modelos 3D, renders |

**Funcionamiento:** NO descargan imágenes. Solo gestionan y devuelven referencias como `STRING` para conectar a nodos External Image.

### Baúles de Prompts

| Nodo | Presets por Defecto |
|------|---------------------|
| 🧾 Baúl de Prompts (Base) | Genéricos editables |
| 🎨 Baúl Estilos | Realista, Anime, Óleo |
| 🧍 Baúl Poses | Neutral, Acción, Sentado |
| 📷 Baúl Cámara / Lente | Plano medio, Gran angular, Retrato |
| 💡 Baúl Iluminación | Natural, Estudio, Dramática |
| 🏞️ Baúl Fondo / Entorno | Urbano, Interior, Naturaleza |
| ✨ Baúl Calidad | Alta calidad, Ultra realista |
| ⛔ Baúl Negativos | Defectos, Anatomía, Técnicos |

**Output:** `STRING` - Texto del preset seleccionado

### Utilidades

| Nodo | Función |
|------|---------|
| 🧱 Prompt Constructor | Concatena 10 campos opcionales → `CONDITIONING` |
| ⛔ Negativo Rápido | Prompt negativo simplificado → `CONDITIONING` |

## Cómo Usar - Baúles Locales (Paso a Paso)

### 1. Agregar Imágenes al Baúl

```
1. Añade un nodo "🧰 Baúl Imágenes (Local)" al workflow
2. En "📂 Acción" selecciona "Agregar archivos"
3. En "📎 Rutas a importar" pega las rutas absolutas de tus imágenes:
   
   C:\Users\TuUsuario\Pictures\concept_1.png
   C:\Users\TuUsuario\Pictures\concept_2.png
   
4. Ejecuta el workflow (Queue Prompt)
5. En la consola verás: "✅ 2 archivo(s) agregado(s)"
```

### 2. Seleccionar y Usar

```
1. Cambia "📂 Acción" a "Nada"
2. En el dropdown "🖼️ Selección" elige una imagen:
   
   abc12345 - concept_1
   
3. Conecta el output IMAGE a tu pipeline (ControlNet, Image2Image, etc.)
4. Ejecuta - la imagen seleccionada se cargará
```

### 3. Actualizar Lista

Si agregas más archivos copiando manualmente a la carpeta:
```
ComfyUI/user/baules/imagenes/files/
```

Luego usa "📂 Acción" → "Refrescar lista" para detectarlos.

## Cómo Usar - Baúles Cloud Ref (Paso a Paso)

### 1. Agregar Referencias Remotas

```
1. Añade un nodo "☁️🧰 Baúl Imágenes (Cloud)"
2. En "🔗 Acción" selecciona "Agregar referencia(s)"
3. En "📎 Agregar" pega URLs (una por línea):
   
   https://example.com/image1.png
   https://cdn.site.com/assets/pose_ref.jpg
   s3://bucket/key/image.png
   
4. Ejecuta el workflow
5. Las referencias se guardan en el nodo (persistencia en workflow)
```

### 2. Usar Referencia

```
1. Cambia "🔗 Acción" a "Nada"
2. En "🖼️ Selección" pega la referencia exacta a usar:
   
   https://example.com/image1.png
   
3. Conecta el output STRING a un nodo "External Image" (o equivalente)
4. Ejecuta - el nodo External Image descargará/cargará la imagen
```

**Importante:** Los baúles Cloud NO descargan imágenes. Solo almacenan y devuelven referencias como texto.

## Persistencia y Rutas en Disco

### Estructura de Almacenamiento Local

```
ComfyUI/
└── user/
    └── baules/
        ├── imagenes/
        │   ├── files/          # Archivos originales
        │   │   ├── abc12345.png
        │   │   └── def67890.jpg
        │   ├── thumbs/         # (futuro)
        │   └── index.json      # Catálogo global
        ├── openpose/
        │   ├── files/
        │   └── index.json
        ├── depth/
        │   ├── files/
        │   └── index.json
        └── lineart/
            ├── files/
            └── index.json
```

### Ejemplo de `index.json`

```json
{
  "version": 1,
  "items": [
    {
      "id": "abc12345",
      "name": "concept_art_1",
      "relpath": "files/abc12345.png",
      "tags": ["fantasy", "character"],
      "favorite": false,
      "created_at": 1706054400,
      "meta": {
        "w": 1024,
        "h": 1024,
        "format": "png"
      }
    }
  ]
}
```

**Regla crítica:** NO contiene campo `selected`. La selección es local a cada nodo (via widget).

### Persistencia Cloud Ref

Los baúles Cloud guardan las referencias en el **workflow JSON** (`widget_values`). No se crea almacenamiento en disco.

## Limitaciones / Notas Importantes

### Local vs Cloud

- **Local**: Copia archivos a `user/baules/<tipo>/files/`. Incrementa uso de disco.
- **Cloud**: Solo referencias. Requiere nodo "External Image" o equivalente para descargar.

### Baúl 3D

- **Solo disponible como Cloud Ref** (no como Local)
- Pensado para URLs de modelos 3D, renders, o referencias visuales complejas

### Exportar/Importar Workflows

- **Baúles Local**: Al exportar workflow, las imágenes **NO se incluyen**. Solo las rutas/IDs.
- **Baúles Cloud**: Las referencias **SÍ viajan** con el workflow JSON.
- **Prompts**: Los presets editados **SÍ se exportan** con el workflow.

### Output en Acciones de Gestión

Al ejecutar acciones como "Agregar archivos" o "Limpiar baúl", el nodo retorna una **imagen blank 1x1** para evitar errores. Solo la acción "Nada" carga la imagen real.

## Troubleshooting

### Dropdown Vacío (Solo "(ninguno)")

**Causa:** No hay archivos en el baúl.

**Solución:**
```
1. Acción → "Agregar archivos"
2. Pegar rutas en "📎 Rutas a importar"
3. Ejecutar workflow
4. Refrescar navegador (F5) para actualizar dropdown
```

### Error: "Archivo no encontrado"

**Causa:** El archivo fue eliminado del disco pero sigue en `index.json`.

**Solución:**
```
1. Acción → "Refrescar lista" (detecta archivos huérfanos)
2. O manualmente editar index.json y eliminar la entrada
```

### Permisos de Escritura (Linux/Mac)

**Síntoma:** Error "Permission denied" al agregar archivos.

**Solución:**
```bash
chmod -R 755 ~/ComfyUI/user/baules/
```

### `index.json` Corrupto

**Síntoma:** Error al cargar catálogo, dropdown vacío.

**Solución:**
```
1. Navegar a ComfyUI/user/baules/<tipo>/
2. Renombrar index.json a index.json.bak
3. El nodo creará uno nuevo vacío
4. Volver a agregar archivos
```

### Baúl Cloud: "Referencia no existe"

**Causa:** La referencia en "🖼️ Selección" no está en la lista almacenada.

**Solución:**
```
1. Acción → "Agregar referencia(s)"
2. Volver a pegar la URL/asset ID
3. Ejecutar para guardar
4. Ahora sí pegar en "Selección" y cambiar acción a "Nada"
```

## Roadmap

### v0.2.0 (Próximo)
- [ ] UI de galería visual (reemplazar dropdown por grid de thumbnails)
- [ ] Generación automática de thumbnails 256x256
- [ ] Filtros por tags en dropdown
- [ ] Ordenar por favoritos/fecha
- [ ] Búsqueda por nombre

### v0.3.0 (Futuro)
- [ ] Importar carpeta completa recursivamente
- [ ] Sincronización con Google Drive / Dropbox
- [ ] Exportar baúl completo como ZIP
- [ ] Soporte para videos (preview frames)
- [ ] Integración con ComfyUI Manager para instalar

### Consideraciones
- **No planeado**: Batch de múltiples imágenes en v1 (solo 1 imagen por selección)
- **No planeado**: Procesamiento de imágenes (crop, resize) - usar otros nodos

## Licencia

MIT License - Copyright (c) 2026 Oficial K (cdanielp)

Consulta el archivo [LICENSE](LICENSE) para más detalles.

## Créditos

**Desarrollado por:** [Oficial K](https://github.com/cdanielp)  
**Repositorio:** [COMFYUI_PROMPTMODELS](https://github.com/cdanielp/COMFYUI_PROMPTMODELS)

Basado en la arquitectura interna de ComfyUI. Agradecimientos a:
- Comunidad de ComfyUI
- Comfy Org por la plataforma
- Usuarios que reportaron el bug de estado global que inspiró este diseño

## Soporte

- **Issues:** [GitHub Issues](https://github.com/cdanielp/COMFYUI_PROMPTMODELS/issues)
- **Discusiones:** [GitHub Discussions](https://github.com/cdanielp/COMFYUI_PROMPTMODELS/discussions)

---

**Nota:** Este pack está en desarrollo activo. Reporta bugs o sugerencias en GitHub Issues.
