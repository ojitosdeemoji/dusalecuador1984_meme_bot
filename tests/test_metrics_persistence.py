"""Pruebas unitarias de persistencia y actualización de métricas en el estado."""

from src.state_manager import update_published_metrics


def test_update_published_metrics_matching_uri():
    """Comprueba que se actualicen las métricas de las publicaciones correspondientes."""
    dummy_state = {
        "version": 1,
        "published": [
            {
                "uri": "at://did:plc:123/app.bsky.feed.post/post1",
                "phrase_text": "Primera frase",
                "likes": 0,
                "reposts": 0,
                "replies": 0,
                "quotes": 0,
            },
            {
                "uri": "at://did:plc:123/app.bsky.feed.post/post2",
                "phrase_text": "Segunda frase",
                "likes": 0,
                "reposts": 0,
                "replies": 0,
                "quotes": 0,
            },
        ],
        "used_phrase_hashes": [],
        "used_image_hashes": [],
    }

    mock_metrics = {
        "at://did:plc:123/app.bsky.feed.post/post1": {
            "likes": 5,
            "reposts": 2,
            "replies": 1,
            "quotes": 0,
        }
    }

    timestamp = "2026-10-10T15:00:00Z"
    actualizados = update_published_metrics(dummy_state, mock_metrics, timestamp)

    assert actualizados == 1
    p1 = dummy_state["published"][0]
    p2 = dummy_state["published"][1]

    # Post 1 debe estar actualizado
    assert p1["likes"] == 5
    assert p1["reposts"] == 2
    assert p1["replies"] == 1
    assert p1["quotes"] == 0
    assert p1["metrics_updated_at"] == timestamp

    # Post 2 no fue consultado, debe permanecer en 0
    assert p2["likes"] == 0
    assert "metrics_updated_at" not in p2

    assert dummy_state["last_metrics_refresh"] == timestamp
