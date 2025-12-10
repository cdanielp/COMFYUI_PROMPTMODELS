# 🛡️ TextPromptBlocker - Custom Node para ComfyUI

Nodo de seguridad que analiza prompts y bloquea/filtra contenido que contiene palabras prohibidas o sus variaciones.

---

## 📦 Instalación

1. Descarga la carpeta `text_prompt_blocker`
2. Cópiala a: `ComfyUI/custom_nodes/`
3. Reinicia ComfyUI
4. Los nodos aparecerán en: **Text → Security**

```
ComfyUI/
└── custom_nodes/
    └── text_prompt_blocker/
        ├── __init__.py
        └── text_prompt_blocker.py
```

---

## 🧩 Nodos Incluidos

### 1. 🛡️ Text Prompt Blocker (Principal)

**Entradas:**
| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `prompt` | STRING | El texto a validar |
| `blocked_words` | STRING | Lista de palabras prohibidas (separadas por coma) |
| `case_sensitive` | BOOLEAN | Respetar mayúsculas/minúsculas (default: False) |
| `hard_block` | BOOLEAN | True = Excepción (detiene workflow), False = String vacío |
| `detect_contained` | BOOLEAN | True = Detecta "child" en "grandchild" |
| `expand_variations` | BOOLEAN | True = Añade automáticamente plurales y variaciones |

**Salidas:**
| Salida | Tipo | Descripción |
|--------|------|-------------|
| `allowed_output` | STRING | El prompt original si pasa el filtro, vacío si no |
| `is_blocked` | BOOLEAN | True si se detectó palabra prohibida |
| `matched_word` | STRING | La palabra que activó el filtro |

---

### 2. 🔍 Text Prompt Blocker (Preview)

Versión para **testing** que NO bloquea, solo muestra qué detectaría.

**Salidas:**
| Salida | Tipo | Descripción |
|--------|------|-------------|
| `original_prompt` | STRING | El prompt sin modificar |
| `status` | STRING | Mensaje de estado (✅ LIMPIO o ⚠️ DETECTADO) |
| `detected_words` | STRING | Lista de todas las palabras encontradas |

---

## ⚙️ Modos de Operación

### Bloqueo Duro (`hard_block: True`)
- Lanza una **excepción** que detiene completamente el workflow
- Muestra mensaje de error con la palabra detectada
- **Recomendado para producción**

### Filtrado Suave (`hard_block: False`)
- Retorna string **vacío** en `allowed_output`
- `is_blocked` será `True`
- El workflow continúa pero sin el prompt
- **Útil para flujos con lógica condicional**

---

## 🎯 Ejemplos de Detección

Con la configuración por defecto (`detect_contained: True`, `expand_variations: True`):

| Prompt | Resultado | Palabra Detectada |
|--------|-----------|-------------------|
| `"adult woman smiling"` | ✅ Permitido | - |
| `"child sitting on chair"` | 🚫 Bloqueado | child |
| `"children playing"` | 🚫 Bloqueado | children |
| `"childish drawing style"` | 🚫 Bloqueado | childish |
| `"grandchild portrait"` | 🚫 Bloqueado | child |
| `"schoolgirl uniform"` | 🚫 Bloqueado | school, girl |
| `"teenage fashion"` | 🚫 Bloqueado | teenage |
| `"young woman"` | 🚫 Bloqueado | young |
| `"elderly woman"` | ✅ Permitido | - |

---

## 📝 Lista de Palabras por Defecto

```
child, kid, baby, infant, underage, young, school, nursery, teen, minor, toddler, preteen
```

### Expansiones Automáticas Incluidas:

- **child** → children, childish, childhood, childlike
- **kid** → kids, kiddo, kiddos, kiddie, kiddies
- **baby** → babies, babyish
- **teen** → teens, teenage, teenager, teenagers
- **young** → younger, youngest, youngster, youngsters
- **infant** → infants, infantile, infancy
- **school** → schools, schooler, schoolers, schooling
- **boy** → boys, boyish
- **girl** → girls, girlish
- Y más...

---

## 🔧 Personalización

### Añadir Palabras Personalizadas

Simplemente edita el campo `blocked_words`:
```
child, kid, baby, custom_word, another_word
```

### Desactivar Expansiones

Si solo quieres detectar las palabras **exactas** de tu lista:
- `expand_variations: False`
- `detect_contained: False`

---

## 🔗 Integración en Workflows

### Uso Básico
```
[Load Prompt] → [TextPromptBlocker] → [KSampler/Prompt]
```

### Con Lógica Condicional
```
[Load Prompt] → [TextPromptBlocker (soft)] → [Switch Node] → [Ruta A / Ruta B]
                         ↓
                   [is_blocked]
```

### Testing con Preview
```
[Load Prompt] → [TextPromptBlockerPreview] → [Show Text]
```

---

## ⚠️ Notas Importantes

1. **Word Boundaries**: Con `detect_contained: True`, detecta la palabra en cualquier posición. Esto significa que "kidnap" SÍ activará el filtro por "kid". Si no deseas esto, usa `detect_contained: False`.

2. **Performance**: El nodo está optimizado para listas de hasta ~100 palabras. Para listas más grandes, considera dividir en múltiples nodos.

3. **Case Sensitivity**: Por defecto ignora mayúsculas/minúsculas. Activa `case_sensitive` si necesitas distinción.

---

## 📄 Licencia

MIT License - Libre para uso personal y comercial.

---

## 🐛 Problemas Conocidos

- Ninguno reportado

## 📬 Soporte

Si encuentras bugs o quieres sugerir mejoras, abre un issue en el repositorio.
