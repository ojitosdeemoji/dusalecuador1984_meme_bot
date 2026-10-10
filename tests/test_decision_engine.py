"""Pruebas unitarias para el motor de decisión creativa y aprendizaje."""

from src.decision_engine import compute_feature_averages, decide_creative_parameters


def test_decision_mode_exploration_in_phase_1():
    """Valida que con menos de 30 publicaciones el modo siempre sea 'exploration'."""
    dummy_state = {
        "version": 1,
        "published": [{"score": 10.0, "generation_method": "markov_chain"}] * 5,
    }
    decision = decide_creative_parameters(dummy_state)
    assert decision["decision_mode"] == "exploration"
    assert decision["exploit_probability"] == 0.0
    assert "Fase 1" in decision["phase_name"]


def test_compute_feature_averages():
    """Comprueba el cálculo correcto de promedios para técnicas de texto."""
    sample = [
        {"score": 10.0, "generation_method": "markov_chain"},
        {"score": 20.0, "generation_method": "markov_chain"},
        {"score": 5.0, "generation_method": "verbatim_extract"},
    ]
    averages = compute_feature_averages(sample)
    assert averages["text_methods"]["markov_chain"] == 15.0
    assert averages["text_methods"]["verbatim_extract"] == 5.0


def test_decision_engine_output_keys():
    """Valida que el diccionario de decisiones contenga las claves obligatorias."""
    empty_state = {"published": []}
    plan = decide_creative_parameters(empty_state)
    assert "decision_mode" in plan
    assert "use_markov" in plan
    assert "target_method" in plan
    assert isinstance(plan["use_markov"], bool)
