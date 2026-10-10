"""Pruebas unitarias para el mecanismo de contingencia (fallback)."""

import io
from pathlib import Path
from PIL import Image
import pytest

from src.image_source import acquire_image_with_fallback


@pytest.mark.asyncio
async def test_fallback_activates_when_x_disabled(tmp_path: Path):
    """Verifica que el selector recurra a las imágenes locales si X no está disponible."""
    # Crear catálogo local temporal con una imagen simulada
    images_dir = tmp_path / "images"
    images_dir.mkdir()
    dummy_img = Image.new("RGB", (400, 400), color=(50, 100, 150))
    img_path = images_dir / "reserva_test.jpg"
    dummy_img.save(img_path, format="JPEG")

    # Ejecutar con X deshabilitado (force_fallback=True, pool=None)
    raw_bytes, img_hash, metadata = await acquire_image_with_fallback(
        pool=None,
        active_usernames=[],
        used_hashes=[],
        local_images_dir=images_dir,
        force_fallback=True,
    )

    assert len(raw_bytes) > 0
    assert len(img_hash) == 64
    assert metadata["fallback_activated"] is True
    assert metadata["source_type"] == "local_fallback"
    assert metadata["source_file"] == "reserva_test.jpg"
