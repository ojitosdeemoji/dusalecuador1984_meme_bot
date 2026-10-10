"""Módulo de procesamiento y curaduría de texto desde documentos PDF."""

import hashlib
import re
from pathlib import Path
from typing import List, Optional
from pypdf import PdfReader


# Patrones de cabeceras, firmas y metadatos editoriales conocidos para suprimir
BOILERPLATE_PATTERNS = [
    r"www\.philosophia\.cl\s*/\s*Escuela\s+de\s+Filosof[ií]a\s+Universidad\s+ARCIS\.?",
    r"Escuela\s+de\s+Filosof[ií]a\s+Universidad\s+ARCIS\.?",
    r"www\.philosophia\.cl",
    r"https?://\S+",
    r"www\.\S+",
]

# Palabras o términos que, de estar presentes, invalidan la oración completa
DISALLOWED_SUBSTRINGS = [
    "philosophia.cl",
    "universidad arcis",
    "escuela de filosofía",
    "http://",
    "https://",
    "www.",
]


def compute_hash(text: str) -> str:
    """Genera un identificador SHA-256 único a partir de un texto normalizado."""
    cleaned = re.sub(r"\s+", " ", text.strip().lower())
    return hashlib.sha256(cleaned.encode("utf-8")).hexdigest()


def remove_boilerplate(raw_text: str) -> str:
    """Elimina patrones de cabecera y URLs específicas del texto en bruto."""
    cleaned = raw_text
    for pattern in BOILERPLATE_PATTERNS:
        cleaned = re.sub(pattern, " ", cleaned, flags=re.IGNORECASE)
    return cleaned


def clean_text(raw_text: str) -> str:
    """Limpia caracteres de control, cabeceras editoriales y normaliza espacios."""
    if not raw_text:
        return ""
    # 1. Quitar cabeceras y dominios conocidos
    text = remove_boilerplate(raw_text)
    # 2. Reemplazar múltiples saltos de línea y tabuladores por espacios simples
    text = re.sub(r"[\r\n\t]+", " ", text)
    # 3. Normalizar espacios múltiples
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def split_into_sentences(text: str, min_words: int = 3, max_words: int = 22) -> List[str]:
    """Divide un texto continuo en oraciones individuales según límites de longitud y reglas de exclusión."""
    cleaned = clean_text(text)
    if not cleaned:
        return []

    # Segmentación por signos de puntuación de cierre (. ! ? ; o saltos lógicos)
    raw_sentences = re.split(r"(?<=[.!?])\s+", cleaned)
    valid_sentences: List[str] = []

    for sentence in raw_sentences:
        candidate = sentence.strip(" \"'«»“”_—–-")
        candidate_lower = candidate.lower()

        # Filtrar si contiene términos prohibidos de cabecera o enlaces
        if any(bad_word in candidate_lower for bad_word in DISALLOWED_SUBSTRINGS):
            continue

        words = candidate.split()
        word_count = len(words)

        if min_words <= word_count <= max_words:
            # Descartar cadenas que parezcan solo números o signos
            if any(char.isalpha() for char in candidate):
                valid_sentences.append(candidate)

    return valid_sentences


def extract_phrases_from_pdf(
    pdf_path: Path,
    max_pages: int = 200,
    max_size_bytes: int = 15 * 1024 * 1024,
) -> List[str]:
    """Extrae, limpia y valida oraciones desde un archivo PDF legible."""
    if not pdf_path.exists():
        raise FileNotFoundError(f"El archivo PDF no existe en la ruta: {pdf_path}")

    file_size = pdf_path.stat().st_size
    if file_size > max_size_bytes:
        raise ValueError(
            f"El archivo PDF excede el límite de tamaño permitido: {file_size} bytes (máx {max_size_bytes})"
        )

    reader = PdfReader(str(pdf_path))
    total_pages = len(reader.pages)

    if total_pages == 0:
        raise ValueError("El archivo PDF no contiene páginas.")

    pages_to_read = min(total_pages, max_pages)
    full_text = ""

    for index in range(pages_to_read):
        page = reader.pages[index]
        extracted = page.extract_text()
        if extracted:
            # Limpiar cabecera inmediatamente a nivel de página para que no contamine la primera frase
            cleaned_page = remove_boilerplate(extracted)
            full_text += " " + cleaned_page

    if not full_text.strip():
        raise ValueError(
            "No se pudo extraer texto del PDF. Verifique que no sea un archivo escaneado o protegido."
        )

    sentences = split_into_sentences(full_text)
    if not sentences:
        raise ValueError(
            "El PDF contiene texto, pero ninguna frase cumplió los criterios de longitud (3 a 22 palabras)."
        )

    return sentences


def get_available_phrase(
    candidates: List[str],
    used_hashes: List[str],
) -> Optional[str]:
    """Selecciona la primera frase disponible cuyo hash no haya sido registrado."""
    used_set = set(used_hashes)
    for phrase in candidates:
        phrase_hash = compute_hash(phrase)
        if phrase_hash not in used_set:
            return phrase
    return None
