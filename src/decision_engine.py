"""Motor de decisiones creativas y balance de aprendizaje (Exploración vs. Explotación)."""

import random
from typing import Any, Dict, List, Tuple

from src.scoring import get_learning_phase


def compute_feature_averages(published_entries: List[Dict[str, Any]]) -> Dict[str, Dict[str, float]]:
    """Calcula el score promedio obtenido por cada variante de texto y composición."""
    markov_scores: List[float] = []
    verbatim_scores: List[float] = []

    for entry in published_entries:
        score = float(entry.get("score", 0.0))
        method = entry.get("generation_method", "")
        if method == "markov_chain" or entry.get("is_markov"):
            markov_scores.append(score)
        else:
            verbatim_scores.append(score)

    avg_markov = round(sum(markov_scores) / len(markov_scores), 3) if markov_scores else 0.0
    avg_verbatim = round(sum(verbatim_scores) / len(verbatim_scores), 3) if verbatim_scores else 0.0

    return {
        "text_methods": {
            "markov_chain": avg_markov,
            "verbatim_extract": avg_verbatim,
        }
    }


def decide_creative_parameters(state_data: Dict[str, Any]) -> Dict[str, Any]:
    """Determina los parámetros creativos de la próxima obra según la etapa de aprendizaje."""
    published = state_data.get("published", [])
    count = len(published)
    phase_name, _ = get_learning_phase(count)

    # 1. Definir probabilidad de explotación según la etapa
    if count <= 30:
        exploit_prob = 0.0   # Fase 1: 100% Exploración
    elif count <= 100:
        exploit_prob = 0.20  # Fase 2: 20% Explotación, 80% Exploración
    else:
        exploit_prob = 0.60  # Fase 3: 60% Explotación, 40% Exploración

    should_exploit = (random.random() < exploit_prob) and (count >= 10)
    decision_mode = "exploitation" if should_exploit else "exploration"

    # 2. Decisión del método textual (Markov vs. Verbatim)
    if should_exploit:
        trends = compute_feature_averages(published)
        scores = trends["text_methods"]
        # Explotar la técnica con mayor rendimiento histórico
        if scores["markov_chain"] > scores["verbatim_extract"]:
            use_markov = True
            preferred_method = "markov_chain"
        elif scores["verbatim_extract"] > scores["markov_chain"]:
            use_markov = False
            preferred_method = "verbatim_extract"
        else:
            use_markov = random.random() < 0.5
            preferred_method = "markov_chain" if use_markov else "verbatim_extract"
    else:
        # Exploración pura: 50% de probabilidad uniforme
        use_markov = random.random() < 0.5
        preferred_method = "markov_chain" if use_markov else "verbatim_extract"

    return {
        "decision_mode": decision_mode,
        "phase_name": phase_name,
        "use_markov": use_markov,
        "target_method": preferred_method,
        "exploit_probability": exploit_prob,
    }
