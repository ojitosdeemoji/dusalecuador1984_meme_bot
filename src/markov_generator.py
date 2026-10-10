"""Generador de texto mediante cadenas de Markov para cadáver exquisito digital."""

import random
import re
from typing import Dict, List, Optional, Set, Tuple


def tokenize_sentence(sentence: str) -> List[str]:
    """Divide una oración en palabras limpias preservando mayúsculas y acentos."""
    cleaned = sentence.strip(" \"'«»“”")
    words = cleaned.split()
    return [w.strip(" \"'«»“”") for w in words if w.strip()]


def build_markov_chain(sentences: List[str]) -> Tuple[Dict[Tuple[str, str], List[str]], List[Tuple[str, str]]]:
    """Construye el modelo de transiciones de segundo orden (bigramas a lista de siguientes palabras)."""
    transitions: Dict[Tuple[str, str], List[str]] = {}
    starters: List[Tuple[str, str]] = []

    for sentence in sentences:
        words = tokenize_sentence(sentence)
        if len(words) < 3:
            continue

        # Registrar iniciadores de oración (primer bigrama con mayúscula)
        if words[0] and words[0][0].isupper():
            starters.append((words[0], words[1]))

        for i in range(len(words) - 2):
            prefix = (words[i], words[i + 1])
            suffix = words[i + 2]
            transitions.setdefault(prefix, []).append(suffix)

    return transitions, starters


def is_coherent_ending(word: str) -> bool:
    """Comprueba si una palabra no termina en preposición, conjunción o artículo débil."""
    weak_endings = {
        "de", "del", "la", "el", "los", "las", "un", "una", "unos", "unas",
        "y", "e", "o", "u", "en", "con", "por", "para", "sin", "sobre", "tras",
        "a", "al", "hacia", "hasta", "como", "que", "se", "su", "sus", "mi", "tu",
    }
    clean_w = word.lower().strip(".,;:!?")
    return clean_w not in weak_endings


def generate_markov_sentence(
    sentences: List[str],
    used_hashes: List[str],
    compute_hash_fn,
    min_words: int = 5,
    max_words: int = 16,
    max_attempts: int = 60,
) -> Optional[str]:
    """Genera una oración sintética original que no exista en el PDF ni haya sido usada antes."""
    if not sentences or len(sentences) < 5:
        return None

    transitions, starters = build_markov_chain(sentences)
    if not starters or not transitions:
        return None

    verbatim_set: Set[str] = {s.strip().lower() for s in sentences}
    used_set: Set[str] = set(used_hashes)

    for _ in range(max_attempts):
        current_pair = random.choice(starters)
        generated_words = [current_pair[0], current_pair[1]]
        target_len = random.randint(min_words, max_words)

        for _ in range(target_len - 2):
            next_options = transitions.get(current_pair)
            if not next_options:
                break
            next_word = random.choice(next_options)
            generated_words.append(next_word)
            current_pair = (current_pair[1], next_word)

            # Cierre anticipado si encontramos un signo de puntuación final
            if next_word.endswith((".", "!", "?")) and len(generated_words) >= min_words:
                break

        # Validaciones de calidad y gramática
        if len(generated_words) < min_words:
            continue

        last_word = generated_words[-1]
        if not is_coherent_ending(last_word):
            # Recortar última palabra si es una preposición o nexo inconcluso
            generated_words.pop()
            if len(generated_words) < min_words:
                continue

        candidate_text = " ".join(generated_words).strip()
        # Asegurar puntuación de cierre
        if not candidate_text.endswith((".", "!", "?")):
            candidate_text += "."

        # Capitalizar primera letra
        candidate_text = candidate_text[0].upper() + candidate_text[1:]

        candidate_lower = candidate_text.lower().strip(".")
        # Comprobar que no sea idéntica a una frase verbatim del PDF
        if candidate_lower in verbatim_set:
            continue

        candidate_hash = compute_hash_fn(candidate_text)
        if candidate_hash in used_set:
            continue

        return candidate_text

    return None
