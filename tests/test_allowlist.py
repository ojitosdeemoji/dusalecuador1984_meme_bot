"""Pruebas unitarias para el módulo de allowlist de X."""

import json
from pathlib import Path
import pytest

from src.x_config import load_allowlist, get_active_usernames


def test_get_active_usernames(tmp_path: Path):
    """Comprueba el filtrado y saneamiento de usuarios de X."""
    config_file = tmp_path / "test_allowlist.json"
    dummy_data = {
        "version": 1,
        "accounts": [
            {"username": "@cuenta_activa", "enabled": True},
            {"username": "cuenta_desactivada", "enabled": False},
            {"username": "cuenta_invalida_con_mas_de_quince_caracteres", "enabled": True},
            {"username": "usuario_valido", "enabled": True},
        ]
    }
    config_file.write_text(json.dumps(dummy_data), encoding="utf-8")

    active = get_active_usernames(config_file)
    assert "cuenta_activa" in active  # Arroba eliminada
    assert "usuario_valido" in active
    assert "cuenta_desactivada" not in active
    assert "cuenta_invalida_con_mas_de_quince_caracteres" not in active
    assert len(active) == 2


def test_load_allowlist_missing_file(tmp_path: Path):
    """Comprueba error si no existe el archivo."""
    with pytest.raises(FileNotFoundError):
        load_allowlist(tmp_path / "inexistente.json")
