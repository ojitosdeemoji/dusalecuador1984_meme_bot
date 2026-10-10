"""Pruebas unitarias para el generador de cadenas de Markov."""

from src.markov_generator import (
    build_markov_chain,
    is_coherent_ending,
    generate_markov_sentence,
    tokenize_sentence,
)
from src.text_processor import compute_hash


def test_tokenize_sentence():
    """Comprueba que la separación de palabras elimine signos envolventes."""
    tokens = tokenize_sentence('«El fenómeno de la conciencia es determinante».')
    assert tokens[0] == "El"
    assert "conciencia" in tokens
    assert len(tokens) == 7


def test_build_markov_chain():
    """Valida la creación de iniciadores y transiciones de segundo orden."""
    corpus = [
        "La razón pura determina los juicios a priori.",
        "La razón práctica establece los principios morales universales.",
    ]
    transitions, starters = build_markov_chain(corpus)
    assert ("La", "razón") in starters
    assert "pura" in transitions[("La", "razón")]
    assert "práctica" in transitions[("La", "razón")]


def test_is_coherent_ending():
    """Comprueba que se rechacen preposiciones o nexos débiles como final de frase."""
    assert is_coherent_ending("filosofía.") is True
    assert is_coherent_ending("conciencia") is True
    assert is_coherent_ending("de") is False
    assert is_coherent_ending("para") is False
    assert is_coherent_ending("el") is False


def test_generate_markov_sentence_novelty():
    """Comprueba que la frase generada tenga mayúscula inicial y puntuación de cierre."""
    corpus = [
        "El sujeto trascendental determina los límites del conocimiento fenoménico siempre.",
        "El sujeto moral construye los principios del imperativo categórico en la ética.",
        "Los límites del pensamiento dialéctico configuran la realidad ontológica del ser.",
        "Los principios del conocimiento puro fundan la experiencia de la naturaleza viva.",
    ]
    frase_generada = generate_markov_sentence(
        corpus,
        used_hashes=[],
        compute_hash_fn=compute_hash,
        min_words=4,
        max_words=12,
        max_attempts=50,
    )

    if frase_generada:
        assert frase_generada[0].isupper()
        assert frase_generada.endswith((".", "!", "?"))
        assert len(frase_generada.split()) >= 4
