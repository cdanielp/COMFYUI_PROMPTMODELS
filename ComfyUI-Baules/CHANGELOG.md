# Changelog

Todos los cambios notables de este proyecto serán documentados en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/)
y este proyecto adhiere a [Semantic Versioning](https://semver.org/lang/es/).

## [0.1.0] - 2026-01-23

### Agregado
- **Baúles de Imágenes (Local)**: 4 nodos especializados (Imágenes, OpenPose, Depth, Lineart)
  - Almacenamiento global por tipo con dropdown dinámico
  - Output `IMAGE` para conexión directa al pipeline
  - Acciones: Agregar archivos, Eliminar, Limpiar baúl, Guardar metadata

- **Baúles Cloud Ref**: 5 nodos para referencias remotas (incluye 3D)
  - Output `STRING` para integración con nodos tipo *External Image*
  - Persistencia de referencias en el workflow (widget values)

- **Baúles de Prompts**: 8 nodos especializados
  - Presets persistentes por nodo (Base, Estilos, Poses, Cámara, Iluminación, Entorno, Calidad, Negativos)
  - Importación masiva con formato `nombre|texto`

- **🧱 Prompt Constructor**
  - Campos opcionales para construir prompt final
  - Output `CONDITIONING` directo para sampler

- **⛔ Negativo Rápido**
  - Prompt negativo simplificado
  - Compatible con presets del Baúl Negativos

### Técnico
- Catálogo `index.json` **sin** estado global de selección
- Persistencia local en `ComfyUI/user/baules/<tipo>/`
- Guardado atómico de catálogos (`.tmp` + `os.replace`)
- Hash de catálogo para invalidación de caché (`IS_CHANGED`)

## [Unreleased]
- UI de galería visual (thumbnails)
- Filtros/búsqueda por tags
- Ordenar por favoritos/fecha
