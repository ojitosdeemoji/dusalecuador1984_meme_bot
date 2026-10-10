"""Pruebas unitarias para el recolector de métricas."""

from datetime import datetime, timezone, timedelta
from src.metrics_collector import calculate_age_hours


def test_calculate_age_hours_valid():
    """Valida el cálculo de antigüedad en horas respecto a una fecha conocida."""
    now = datetime.now(timezone.utc)
    ten_hours_ago = now - timedelta(hours=10)
    iso_str = ten_hours_ago.isoformat()

    age = calculate_age_hours(iso_str)
    assert 9.9 <= age <= 10.1


def test_calculate_age_hours_invalid():
    """Comprueba que marcas temporales inválidas devuelvan 0.0 sin fallar."""
    assert calculate_age_hours("fecha-invalida") == 0.0
    assert calculate_age_hours("") == 0.0
