"""Módulo de scoring de engagement y balance artístico de aprendizaje."""

import math
from typing import Any, Dict, List, Tuple


def calculate_raw_score(likes: int, reposts: int, replies: int, quotes: int) -> float:
    """Calcula el score bruto considerando el peso del esfuerzo de interacción."""
    raw = (likes * 1.0) + (reposts * 2.0) + (replies * 3.0) + (quotes * 2.0)
    return round(raw, 2)


def calculate_normalized_score(raw_score: float, age_hours: float) -> float:
    """Aplica atenuación no lineal por antigüedad para comparar publicaciones de distinta edad.

    Usa un período base de 12 horas: durante las primeras 12h el factor es 1.0.
    A partir de ahí, crece suavemente como raíz cuadrada del tiempo.
    """
    if raw_score <= 0.0:
        return 0.0

    safe_age = max(0.0, age_hours)
    maturity_factor = math.sqrt(max(1.0, safe_age / 12.0))
    normalized = raw_score / maturity_factor
    return round(normalized, 3)


def get_learning_phase(published_count: int) -> Tuple[str, str]:
    """Determina la fase de aprendizaje del bot según el tamaño del catálogo histórico."""
    if published_count <= 30:
        return (
            "Fase 1: Exploración Pura",
            "100% variabilidad estética. Acumulación de muestra estadística sin sesgos de preferencia.",
        )
    elif published_count <= 100:
        return (
            "Fase 2: Preferencia Suave",
            "80% exploración aleatoria, 20% inclinación leve hacia composiciones con mayor score.",
        )
    else:
        return (
            "Fase 3: Equilibrio Generativo",
            "60% explotación de patrones con mayor recepción, 40% exploración estética obligatoria.",
        )


def analyze_aesthetic_trends(published_entries: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Calcula tendencias preliminares de recepción agrupadas por variables formales."""
    if not published_entries:
        return {}

    by_position: Dict[str, List[float]] = {}
    by_source: Dict[str, List[float]] = {}

    for entry in published_entries:
        score = entry.get("score", 0.0)
        pos = entry.get("text_position", "desconocida")
        src = entry.get("source_type", "desconocida")

        by_position.setdefault(pos, []).append(score)
        by_source.setdefault(src, []).append(score)

    avg_position = {k: round(sum(v) / len(v), 2) for k, v in by_position.items()}
    avg_source = {k: round(sum(v) / len(v), 2) for k, v in by_source.items()}

    return {
        "avg_score_by_position": avg_position,
        "avg_score_by_source": avg_source,
    }
