"""Módulo de recolección de métricas de engagement mediante AT Protocol (Bluesky)."""

from datetime import datetime, timezone
import os
from typing import Any, Dict, List, Optional
from atproto import Client


def calculate_age_hours(published_at_iso: str) -> float:
    """Calcula la antigüedad en horas de una publicación a partir de su marca de tiempo ISO."""
    try:
        pub_dt = datetime.fromisoformat(published_at_iso)
        if pub_dt.tzinfo is None:
            pub_dt = pub_dt.replace(tzinfo=timezone.utc)
        now_dt = datetime.now(timezone.utc)
        delta_seconds = max(0.0, (now_dt - pub_dt).total_seconds())
        return round(delta_seconds / 3600.0, 2)
    except (ValueError, TypeError):
        return 0.0


def fetch_posts_metrics(
    uris: List[str],
    handle: Optional[str] = None,
    app_password: Optional[str] = None,
) -> Dict[str, Dict[str, int]]:
    """Consulta la API de Bluesky en lotes de hasta 25 publicaciones y extrae métricas."""
    if not uris:
        return {}

    user_handle = handle or os.getenv("BSKY_HANDLE")
    user_password = app_password or os.getenv("BSKY_APP_PASSWORD")

    if not user_handle or not user_password:
        raise ValueError("Credenciales de Bluesky no encontradas (BSKY_HANDLE, BSKY_APP_PASSWORD).")

    clean_handle = user_handle.strip().lstrip("@")
    client = Client()
    client.login(clean_handle, user_password.strip())

    results: Dict[str, Dict[str, int]] = {}

    # La API admite hasta 25 URIs por llamada
    chunk_size = 25
    for i in range(0, len(uris), chunk_size):
        chunk = uris[i : i + chunk_size]
        try:
            response = client.get_posts(chunk)
            for post in response.posts:
                results[post.uri] = {
                    "likes": getattr(post, "like_count", 0) or 0,
                    "reposts": getattr(post, "repost_count", 0) or 0,
                    "replies": getattr(post, "reply_count", 0) or 0,
                    "quotes": getattr(post, "quote_count", 0) or 0,
                }
        except Exception as exc:
            print(f"[METRICS] Advertencia al consultar lote de URIs: {exc}")

    return results
