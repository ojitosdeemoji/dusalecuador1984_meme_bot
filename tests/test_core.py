"""Pruebas unitarias de los módulos principales."""

import io
from pathlib import Path
from PIL import Image
import pytest

from src.state_manager import (
    load_state,
    save_state,
    is_phrase_used,
    is_image_used,
    record_entry,
)
from src.text_processor import (
    compute_hash,
    clean_text,
    split_into_sentences,
    get_available_phrase,
)
from src.image_composer import (
    load_and_sanitize_image,
    render_meme,
    export_to_bluesky_jpeg,
    compute_image_hash,
    MAX_OUTPUT_BYTES,
)


def test_compute_hash_consistency():
    """Comprueba que el hashing de texto normalice espacios y sea determinista."""
    hash1 = compute_hash("Hola   Mundo")
    hash2 = compute_hash("hola mundo")
    assert hash1 == hash2
    assert len(hash1) == 64


def test_split_into_sentences():
    """Valida la separación y filtrado de oraciones por conteo de palabras."""
    texto = "Frase corta. Esta es una oración con suficiente longitud para ser meme. Otra corta."
    resultado = split_into_sentences(texto, min_words=4, max_words=15)
    assert len(resultado) == 1
    assert "suficiente longitud" in resultado[0]


def test_state_lifecycle(tmp_path: Path):
    """Comprueba la lectura, guardado y actualización de estado JSON."""
    ruta_estado = tmp_path / "test_state.json"
    estado = load_state(ruta_estado)
    assert estado["version"] == 1
    assert estado["published"] == []

    # Registrar una entrada
    p_hash = compute_hash("Frase de prueba")
    img_hash = "abc123hash"
    record_entry(estado, p_hash, img_hash, {"origen": "test"})
    save_state(ruta_estado, estado)

    # Recargar y verificar exclusión
    estado_recargado = load_state(ruta_estado)
    assert is_phrase_used(estado_recargado, p_hash) is True
    assert is_image_used(estado_recargado, img_hash) is True
    assert len(estado_recargado["published"]) == 1


def test_get_available_phrase():
    """Comprueba que se descarte una frase si su hash ya existe en el estado."""
    frases = ["Primera frase válida", "Segunda frase válida"]
    usadas = [compute_hash("Primera frase válida")]
    disponible = get_available_phrase(frases, usadas)
    assert disponible == "Segunda frase válida"


def test_image_composer_pipeline():
    """Comprueba la carga, renderizado y compresión de una imagen sintética."""
    # Crear imagen sintética en memoria de 600x600 px en formato PNG
    img_raw = Image.new("RGBA", (600, 600), color=(100, 150, 200, 255))
    buffer_entrada = io.BytesIO()
    img_raw.save(buffer_entrada, format="PNG")
    buffer_entrada.seek(0)

    # 1. Carga y saneamiento
    img_rgb = load_and_sanitize_image(buffer_entrada)
    assert img_rgb.mode == "RGB"
    assert img_rgb.size == (600, 600)

    # 2. Renderizado de texto meme
    meme_img = render_meme(
        img_rgb,
        top_text="TEXTO SUPERIOR DE PRUEBA",
        bottom_text="TEXTO INFERIOR DE PRUEBA",
    )
    assert meme_img.size == (600, 600)

    # 3. Exportación y compresión
    jpeg_bytes = export_to_bluesky_jpeg(meme_img)
    assert len(jpeg_bytes) > 0
    assert len(jpeg_bytes) <= MAX_OUTPUT_BYTES

    # Validar que sea un JPEG válido
    img_final = Image.open(io.BytesIO(jpeg_bytes))
    assert img_final.format == "JPEG"
    assert len(compute_image_hash(jpeg_bytes)) == 64
