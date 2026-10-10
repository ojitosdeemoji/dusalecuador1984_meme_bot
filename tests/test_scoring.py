"""Pruebas unitarias para el módulo de scoring de memes."""

from src.scoring import (
    calculate_raw_score,
    calculate_normalized_score,
    get_learning_phase,
    analyze_aesthetic_trends,
)


def test_calculate_raw_score():
    """Comprueba la ponderación de likes, reposts, replies y quotes."""
    score = calculate_raw_score(likes=10, reposts=3, replies=2, quotes=1)
    # 10*1 + 3*2 + 2*3 + 1*2 = 10 + 6 + 6 + 2 = 24.0
    assert score == 24.0


def test_calculate_normalized_score_growth_fairness():
    """Comprueba que a igual interacción, una publicación reciente tenga mayor o igual score."""
    raw = 20.0
    score_nueva = calculate_normalized_score(raw, age_hours=5.0)    # < 12h -> factor 1.0
    score_madura = calculate_normalized_score(raw, age_hours=48.0)  # 48/12 = 4 -> sqrt(4) = 2.0

    assert score_nueva == 20.0
    assert score_madura == 10.0
    assert score_nueva > score_madura


def test_learning_phase_transitions():
    """Valida los umbrales de aprendizaje gradual (30 y 100 publicaciones)."""
    phase_1, _ = get_learning_phase(15)
    assert "Fase 1" in phase_1

    phase_2, _ = get_learning_phase(50)
    assert "Fase 2" in phase_2

    phase_3, _ = get_learning_phase(150)
    assert "Fase 3" in phase_3


def test_analyze_aesthetic_trends_aggregations():
    """Comprueba que el cálculo de promedios formales no falle con datos válidos."""
    sample = [
        {"text_position": "top_and_bottom", "source_type": "x_twitter", "score": 10.0},
        {"text_position": "top_and_bottom", "source_type": "local_fallback", "score": 20.0},
        {"text_position": "bottom_only", "source_type": "x_twitter", "score": 5.0},
    ]
    trends = analyze_aesthetic_trends(sample)
    assert trends["avg_score_by_position"]["top_and_bottom"] == 15.0
    assert trends["avg_score_by_position"]["bottom_only"] == 5.0
