"""Módulo de procesamiento y curaduría de texto desde documentos PDF."""

import hashlib
import re
from pathlib import Path
from typing import List, Optional
from pypdf import PdfReader


def compute_hash(text: str) -> str:
    """Genera un identificador SHA-256 único a partir de un texto normalizado."""
    cleaned = re.sub(r"\s+", " ", text.strip().lower())
    return hashlib.sha256(cleaned.encode("utf-8")).hexdigest()


def clean_text(raw_text: str) -> str:
    """Limpia caracteres de control, saltos innecesarios y normaliza espacios."""
    if not raw_text:
        return ""
    # Reemplazar múltiples saltos de línea y tabuladores por espacios simples
    text = re.sub(r"[\r\n\t]+", " ", raw_text)
    # Reemplazar múltiples espacios por uno solo
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def split_into_sentences(text: str, min_words: int = 3, max_words: int = 22) -> List[str]:
    """Divide un texto continuo en oraciones individuales según límites de longitud."""
    cleaned = clean_text(text)
    if not cleaned:
        return []

    # Segmentación por signos de puntuación de cierre (. ! ? ; o saltos lógicos)
    raw_sentences = re.split(r"(?<=[.!?])\s+", cleaned)
    valid_sentences: List[str] = []

    for sentence in raw_sentences:
        candidate = sentence.strip(" \"'«»“”")
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
    """Extrae y valida oraciones desde un archivo PDF legible."""
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
            full_text += " " + extracted

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
