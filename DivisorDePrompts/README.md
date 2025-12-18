# DivisorDePrompts (10)

Custom node para **ComfyUI** que divide texto multilínea en hasta 10 prompts independientes usando párrafos como separador.

![ComfyUI](https://img.shields.io/badge/ComfyUI-Custom%20Node-blue)
![Python](https://img.shields.io/badge/Python-3.10%2B-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

## Instalación

### Opción 1: ComfyUI Manager
Busca `DivisorDePrompts` en ComfyUI Manager e instala.

### Opción 2: Manual
```bash
cd ComfyUI/custom_nodes
git clone https://github.com/TU_USUARIO/DivisorDePrompts.git
# Reinicia ComfyUI
```

## Uso

Pega tus prompts separados por **líneas vacías**:

```
portrait photo, cinematic light, 85mm

product photo, white background, softbox

landscape, golden hour, volumetric fog
```

**Salidas:**
| Output | Valor |
|--------|-------|
| `prompt_01` | portrait photo, cinematic light, 85mm |
| `prompt_02` | product photo, white background, softbox |
| `prompt_03` | landscape, golden hour, volumetric fog |
| `prompt_04-10` | "" (vacío) |
| `count` | 3 |

## Parámetros

| Parámetro | Tipo | Default | Descripción |
|-----------|------|---------|-------------|
| `full_text` | STRING | "" | Texto con prompts separados por líneas vacías |
| `trim_mode` | BOOL | True | Limpia espacios al inicio/fin de cada prompt |
| `preserve_newlines` | BOOL | True | Mantiene saltos de línea dentro de cada prompt |

## Características

- ✅ Detecta párrafos automáticamente (sin sintaxis especial)
- ✅ Soporta Windows/Unix newlines
- ✅ Preserva o colapsa saltos internos
- ✅ Output `count` para lógica condicional
- ✅ Sin dependencias externas
- ✅ Determinista (mismo input → mismo output)

## Casos de Uso

- **Multi-shot prompting**: genera múltiples imágenes desde un solo texto
- **Guiones de prompts**: pega scripts completos y distribuye automáticamente
- **Workflows batch**: conecta cada output a un sampler diferente

## Ejemplo de Workflow

```
[DivisorDePrompts] → prompt_01 → [CLIP Text Encode] → [KSampler] → [Save Image]
                  → prompt_02 → [CLIP Text Encode] → [KSampler] → [Save Image]
                  → prompt_03 → ...
```

## Licencia

MIT License - Úsalo como quieras.

## Créditos

Desarrollado por [Tu Nombre] | [Prompt Models Studio](https://tu-link.com)
