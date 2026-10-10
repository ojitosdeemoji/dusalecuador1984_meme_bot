"""Módulo de configuración y control de la lista blanca (allowlist) de X."""

import json
import re
from pathlib import Path
from typing import Any, Dict, List

# Nombres de usuario en X: 1 a 15 caracteres alfanuméricos o guión bajo
X_USERNAME_REGEX = re.compile(r"^[A-Za-z0-9_]{1,15}$")


def load_allowlist(config_path: Path) -> Dict[str, Any]:
    """Carga y valida el archivo de lista blanca."""
    if not config_path.exists():
        raise FileNotFoundError(f"No se encontró el archivo de allowlist en: {config_path}")

    with open(config_path, "r", encoding="utf-8") as file:
        data = json.load(file)

    if not isinstance(data, dict):
        raise ValueError("El archivo de allowlist debe ser un objeto JSON.")

    if "accounts" not in data or not isinstance(data["accounts"], list):
        raise ValueError("El archivo de allowlist debe contener una lista 'accounts'.")

    return data


def get_active_usernames(config_path: Path) -> List[str]:
    """Devuelve únicamente los nombres de usuario activos y válidos, sin arroba."""
    data = load_allowlist(config_path)
    active_users: List[str] = []

    for entry in data.get("accounts", []):
        if not isinstance(entry, dict):
            continue

        raw_user = entry.get("username", "")
        clean_user = raw_user.strip().lstrip("@")
        is_enabled = entry.get("enabled", False)

        if is_enabled and X_USERNAME_REGEX.match(clean_user):
            if clean_user not in active_users:
                active_users.append(clean_user)

    return active_users
