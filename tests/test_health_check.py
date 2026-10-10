"""Pruebas unitarias para el monitor de salud del sistema."""

import json
from pathlib import Path
from PIL import Image

from scripts.health_check import evaluate_system_health


def test_evaluate_system_health_clean(tmp_path: Path):
    """Comprueba el reporte de salud con insumos suficientes."""
    # Estado ficticio
    state_file = tmp_path / "state.json"
    state_file.write_text(json.dumps({
        "version": 1,
        "published": [{"score": 1.0}],
        "used_phrase_hashes": ["hash1"],
        "used_image_hashes": ["img1"],
        "last_metrics_refresh": "2026-10-10T12:00:00Z"
    }), encoding="utf-8")

    # Imágenes ficticias
    img_dir = tmp_path / "images"
    img_dir.mkdir()
    for i in range(3):
        im = Image.new("RGB", (300, 300), color=(10, 20, 30))
        im.save(img_dir / f"test_{i}.jpg")

    # Allowlist ficticia
    allowlist_file = tmp_path / "x_allowlist.json"
    allowlist_file.write_text(json.dumps({
        "version": 1,
        "accounts": [{"username": "cuenta_test", "enabled": True}]
    }), encoding="utf-8")

    # Inexistencia de PDF simulado para prueba
    pdf_file = tmp_path / "corpus.pdf"

    health = evaluate_system_health(state_file, pdf_file, img_dir, allowlist_file)
    assert health["published_total"] == 1
    assert health["local_images_count"] == 3
    assert health["active_x_sources"] == 1
    assert "Fase 1" in health["learning_phase"]
