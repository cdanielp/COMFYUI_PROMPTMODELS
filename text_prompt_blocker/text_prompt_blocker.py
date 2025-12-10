"""
TextPromptBlocker - Nodo de seguridad para ComfyUI
Bloquea o filtra prompts que contengan palabras prohibidas o sus variaciones.

Autor: Custom Node
Versión: 1.0.0
"""

import re
from typing import Tuple, List, Set


class TextPromptBlocker:
    """
    Nodo ComfyUI que analiza prompts y bloquea/filtra contenido prohibido.
    
    Características:
    - Detección de palabras exactas y contenidas (ej: "child" en "grandchild")
    - Expansión automática de variaciones (plurales, sufijos comunes)
    - Dos modos: bloqueo duro (excepción) o filtrado suave (string vacío)
    - Output de debug con la palabra que activó el filtro
    """

    # Expansiones predefinidas para palabras comunes
    # Estas se añaden automáticamente cuando se detecta la palabra base
    KNOWN_EXPANSIONS = {
        "child": ["children", "childish", "childhood", "childlike", "childs"],
        "kid": ["kids", "kiddo", "kiddos", "kiddie", "kiddies"],
        "baby": ["babies", "babyish", "babys"],
        "teen": ["teens", "teenage", "teenager", "teenagers", "teeny"],
        "young": ["younger", "youngest", "youngster", "youngsters", "youngs"],
        "infant": ["infants", "infantile", "infancy"],
        "minor": ["minors"],
        "school": ["schools", "schooler", "schoolers", "schooling"],
        "nursery": ["nurseries"],
        "underage": ["underaged"],
        "preteen": ["preteens", "preteen"],
        "toddler": ["toddlers"],
        "boy": ["boys", "boyish"],
        "girl": ["girls", "girlish"],
    }

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "prompt": ("STRING", {
                    "multiline": True,
                    "default": "",
                    "placeholder": "Ingresa el prompt a validar..."
                }),
                "blocked_words": ("STRING", {
                    "multiline": True,
                    "default": "child, kid, baby, infant, underage, young, school, nursery, teen, minor, toddler, preteen",
                    "placeholder": "Palabras prohibidas separadas por coma"
                }),
            },
            "optional": {
                "case_sensitive": ("BOOLEAN", {"default": False}),
                "hard_block": ("BOOLEAN", {
                    "default": True,
                    "label_on": "Bloqueo Duro (Excepción)",
                    "label_off": "Filtrado Suave (String vacío)"
                }),
                "detect_contained": ("BOOLEAN", {
                    "default": True,
                    "label_on": "Detectar en palabras compuestas",
                    "label_off": "Solo palabras exactas"
                }),
                "expand_variations": ("BOOLEAN", {
                    "default": True,
                    "label_on": "Expandir variaciones automáticamente",
                    "label_off": "Solo palabras exactas de la lista"
                }),
            }
        }

    RETURN_TYPES = ("STRING", "BOOLEAN", "STRING")
    RETURN_NAMES = ("allowed_output", "is_blocked", "matched_word")
    FUNCTION = "validate_prompt"
    CATEGORY = "Text/Security"
    OUTPUT_NODE = False

    def _build_word_set(self, blocked_words: str, expand: bool) -> Set[str]:
        """
        Construye el conjunto completo de palabras a bloquear.
        Incluye expansiones si está habilitado.
        """
        words = set()
        
        for word in blocked_words.split(","):
            word = word.strip().lower()
            if not word:
                continue
                
            words.add(word)
            
            # Añadir expansiones conocidas
            if expand and word in self.KNOWN_EXPANSIONS:
                words.update(self.KNOWN_EXPANSIONS[word])
            
            # Generar variaciones automáticas básicas
            if expand:
                # Plural simple (+s)
                words.add(f"{word}s")
                # Plural -es (para palabras terminadas en consonante)
                words.add(f"{word}es")
                # Sufijos comunes
                for suffix in ["ish", "like", "hood", "ness"]:
                    words.add(f"{word}{suffix}")
        
        return words

    def _check_contained(self, text: str, words: Set[str]) -> str | None:
        """
        Busca si alguna palabra prohibida está CONTENIDA en el texto.
        Detecta 'child' en 'grandchild', 'schoolchild', etc.
        Retorna la palabra encontrada o None.
        """
        text_lower = text.lower()
        
        # Ordenar por longitud descendente para detectar la más específica primero
        sorted_words = sorted(words, key=len, reverse=True)
        
        for word in sorted_words:
            if word in text_lower:
                return word
        
        return None

    def _check_word_boundary(self, text: str, words: Set[str], case_sensitive: bool) -> str | None:
        """
        Busca palabras con límites de palabra (word boundaries).
        Más preciso pero no detecta palabras compuestas.
        Retorna la palabra encontrada o None.
        """
        check_text = text if case_sensitive else text.lower()
        
        for word in words:
            check_word = word if case_sensitive else word.lower()
            pattern = rf"\b{re.escape(check_word)}\b"
            
            if re.search(pattern, check_text, re.IGNORECASE if not case_sensitive else 0):
                return word
        
        return None

    def validate_prompt(
        self,
        prompt: str,
        blocked_words: str,
        case_sensitive: bool = False,
        hard_block: bool = True,
        detect_contained: bool = True,
        expand_variations: bool = True
    ) -> Tuple[str, bool, str]:
        """
        Valida el prompt contra la lista de palabras prohibidas.
        
        Returns:
            Tuple[str, bool, str]: (prompt_permitido, está_bloqueado, palabra_detectada)
        """
        
        # Si el prompt está vacío, dejarlo pasar
        if not prompt or not prompt.strip():
            return (prompt, False, "")
        
        # Si no hay palabras bloqueadas, dejarlo pasar
        if not blocked_words or not blocked_words.strip():
            return (prompt, False, "")
        
        # Construir conjunto de palabras a bloquear
        word_set = self._build_word_set(blocked_words, expand_variations)
        
        # Buscar coincidencias
        matched = None
        
        if detect_contained:
            # Modo agresivo: busca la palabra en cualquier parte
            matched = self._check_contained(prompt, word_set)
        else:
            # Modo preciso: solo palabras completas
            matched = self._check_word_boundary(prompt, word_set, case_sensitive)
        
        # Si se encontró una coincidencia
        if matched:
            if hard_block:
                # Modo duro: lanzar excepción para detener el workflow
                raise Exception(
                    f"🚫 PROMPT BLOQUEADO\n"
                    f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                    f"Palabra detectada: '{matched}'\n"
                    f"El workflow ha sido detenido por seguridad.\n"
                    f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
                )
            else:
                # Modo suave: retornar string vacío pero no crashear
                return ("", True, matched)
        
        # Si no hay coincidencias, el prompt es válido
        return (prompt, False, "")


class TextPromptBlockerPreview:
    """
    Versión de preview que NO bloquea, solo muestra qué detectaría.
    Útil para testing y debugging.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "prompt": ("STRING", {
                    "multiline": True,
                    "default": ""
                }),
                "blocked_words": ("STRING", {
                    "multiline": True,
                    "default": "child, kid, baby, infant, underage, young, school, nursery, teen, minor, toddler, preteen"
                }),
            },
            "optional": {
                "detect_contained": ("BOOLEAN", {"default": True}),
                "expand_variations": ("BOOLEAN", {"default": True}),
            }
        }

    RETURN_TYPES = ("STRING", "STRING", "STRING")
    RETURN_NAMES = ("original_prompt", "status", "detected_words")
    FUNCTION = "preview_check"
    CATEGORY = "Text/Security"
    OUTPUT_NODE = True

    def preview_check(
        self,
        prompt: str,
        blocked_words: str,
        detect_contained: bool = True,
        expand_variations: bool = True
    ) -> Tuple[str, str, str]:
        """
        Analiza el prompt sin bloquearlo, solo reporta lo que encontraría.
        """
        
        blocker = TextPromptBlocker()
        word_set = blocker._build_word_set(blocked_words, expand_variations)
        
        # Buscar TODAS las coincidencias para el preview
        found_words = []
        prompt_lower = prompt.lower()
        
        if detect_contained:
            for word in sorted(word_set, key=len, reverse=True):
                if word in prompt_lower:
                    found_words.append(word)
        else:
            for word in word_set:
                pattern = rf"\b{re.escape(word)}\b"
                if re.search(pattern, prompt_lower):
                    found_words.append(word)
        
        # Eliminar duplicados manteniendo orden
        found_words = list(dict.fromkeys(found_words))
        
        if found_words:
            status = f"⚠️ DETECTADO: {len(found_words)} palabra(s) prohibida(s)"
            detected = ", ".join(found_words[:10])  # Limitar a 10 para no saturar
            if len(found_words) > 10:
                detected += f"... (+{len(found_words) - 10} más)"
        else:
            status = "✅ LIMPIO: No se detectaron palabras prohibidas"
            detected = ""
        
        return (prompt, status, detected)
