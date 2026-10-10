"""Pruebas unitarias de prevención estricta de duplicados."""

import pytest
from src.text_processor import compute_hash, get_available_phrase
from src.state_manager import record_entry


def test_phrase_exhaustion_and_exclusion():
    """Valida que get_available_phrase ignore frases usadas y respete el orden."""
    pool_frases = [
        "El sujeto trascendental determina la experiencia",
        "El fenómeno no es la cosa en sí misma",
        "La razón pura contiene los principios a priori",
    ]

    used_hashes = []

    # 1. Primera selección
    primera = get_available_phrase(pool_frases, used_hashes)
    assert primera == "El sujeto trascendental determina la experiencia"
    used_hashes.append(compute_hash(primera))

    # 2. Segunda selección (debe avanzar a la segunda)
    segunda = get_available_phrase(pool_frases, used_hashes)
    assert segunda == "El fenómeno no es la cosa en sí misma"
    assert segunda != primera
    used_hashes.append(compute_hash(segunda))

    # 3. Tercera selección
    tercera = get_available_phrase(pool_frases, used_hashes)
    assert tercera == "La razón pura contiene los principios a priori"
    used_hashes.append(compute_hash(tercera))

    # 4. Agotamiento total del pool
    cuarta = get_available_phrase(pool_frases, used_hashes)
    assert cuarta is None


def test_record_entry_accumulates_without_corruption():
    """Comprueba que registrar entradas consecutivas acumule el historial sin sobreescribir."""
    estado = {
        "version": 1,
        "published": [],
        "used_phrase_hashes": [],
        "used_image_hashes": [],
    }

    # Registrar publicación 1
    h_frase_1 = "hash_frase_01"
    h_img_1 = "hash_img_01"
    record_entry(estado, h_frase_1, h_img_1, {"post_url": "https://bsky.app/1"})

    # Registrar publicación 2
    h_frase_2 = "hash_frase_02"
    h_img_2 = "hash_img_02"
    record_entry(estado, h_frase_2, h_img_2, {"post_url": "https://bsky.app/2"})

    assert len(estado["published"]) == 2
    assert len(estado["used_phrase_hashes"]) == 2
    assert len(estado["used_image_hashes"]) == 2
    assert estado["published"][0]["post_url"] == "https://bsky.app/1"
    assert estado["published"][1]["post_url"] == "https://bsky.app/2"
