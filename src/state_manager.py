"""Módulo de persistencia y control de estado para meme-bot."""

import json
from pathlib import Path
from typing import Any, Dict, List


DEFAULT_STATE: Dict[str, Any] = {
    "version": 1,
    "published": [],
    "used_phrase_hashes": [],
    "used_image_hashes": [],
}


def load_state(state_path: Path) -> Dict[str, Any]:
    """Carga el estado desde el archivo JSON especificado.

    Si no existe o está dañado, devuelve una estructura limpia por defecto.
    """
    if not state_path.exists():
        return DEFAULT_STATE.copy()

    try:
        with open(state_path, "r", encoding="utf-8") as file:
            data = json.load(file)
            if not isinstance(data, dict):
                return DEFAULT_STATE.copy()
            # Asegurar claves mínimas
            for key in ["published", "used_phrase_hashes", "used_image_hashes"]:
                if key not in data or not isinstance(data[key], list):
                    data[key] = []
            return data
    except (json.JSONDecodeError, OSError):
        return DEFAULT_STATE.copy()


def save_state(state_path: Path, state_data: Dict[str, Any]) -> None:
    """Guarda los datos de estado en disco con formato legible y ordenado."""
    state_path.parent.mkdir(parents=True, exist_ok=True)
    with open(state_path, "w", encoding="utf-8") as file:
        json.dump(state_data, file, indent=2, ensure_ascii=False)


def is_phrase_used(state_data: Dict[str, Any], phrase_hash: str) -> bool:
    """Verifica si el hash de una frase ya fue utilizado anteriormente."""
    return phrase_hash in state_data.get("used_phrase_hashes", [])


def is_image_used(state_data: Dict[str, Any], image_hash: str) -> bool:
    """Verifica si el hash de una imagen ya fue utilizado anteriormente."""
    return image_hash in state_data.get("used_image_hashes", [])


def record_entry(
    state_data: Dict[str, Any],
    phrase_hash: str,
    image_hash: str,
    metadata: Dict[str, Any],
) -> None:
    """Registra una nueva publicación en el estado y actualiza las listas de exclusión."""
    if phrase_hash and phrase_hash not in state_data["used_phrase_hashes"]:
        state_data["used_phrase_hashes"].append(phrase_hash)

    if image_hash and image_hash not in state_data["used_image_hashes"]:
        state_data["used_image_hashes"].append(image_hash)

    entry = {
        "phrase_hash": phrase_hash,
        "image_hash": image_hash,
        **metadata,
    }
    state_data["published"].append(entry)
