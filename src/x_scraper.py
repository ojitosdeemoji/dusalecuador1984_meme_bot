"""Módulo de conexión y extracción mediante twscrape para X (Twitter)."""

import asyncio
from pathlib import Path
from typing import Any, Dict, List, Optional
from twscrape import AccountsPool, API


async def initialize_x_pool(
    db_path: Path,
    username: str,
    auth_token: str,
    ct0: str,
) -> AccountsPool:
    """Inicializa el pool de SQLite de twscrape y registra la cuenta con cookies."""
    if not username or not auth_token or not ct0:
        raise ValueError("Credenciales de X incompletas. Se requieren username, auth_token y ct0.")

    clean_user = username.strip().lstrip("@")
    pool = AccountsPool(str(db_path))
    cookie_str = f"auth_token={auth_token.strip()}; ct0={ct0.strip()}"

    existing = await pool.get_account(clean_user)
    if existing is None:
        await pool.add_account(
            username=clean_user,
            password="dummy_password_unused",
            email="dummy_email@example.com",
            email_password="dummy_email_password_unused",
            cookies=cookie_str,
        )

    return pool


async def verify_x_account_status(pool: AccountsPool, username: str) -> bool:
    """Ejecuta login_all y verifica si la cuenta se encuentra activa en el pool."""
    clean_user = username.strip().lstrip("@")
    await pool.login_all()
    account = await pool.get_account(clean_user)
    if account is None:
        return False
    return bool(account.active)


async def get_user_timeline_image_candidates(
    pool: AccountsPool,
    target_username: str,
    limit: int = 10,
) -> List[Dict[str, Any]]:
    """Obtiene tweets recientes con imágenes directamente desde el muro de un usuario.

    Utiliza UserTweets en lugar de SearchTimeline para evitar bloqueos por 404.
    """
    clean_target = target_username.strip().lstrip("@")
    api = API(pool)
    candidates: List[Dict[str, Any]] = []

    try:
        # 1. Obtener datos y user_id del perfil
        user_info = await api.user_by_login(clean_target)
        if not user_info or not hasattr(user_info, "id"):
            print(f"[X_SCRAPER] No se pudo resolver el perfil para @{clean_target}.")
            return []

        user_id = user_info.id
        print(f"[X_SCRAPER] Perfil @{clean_target} resuelto con ID: {user_id}. Consultando publicaciones recientes...")

        # 2. Consultar tweets directos del perfil
        count = 0
        async for tweet in api.user_tweets(user_id, limit=limit):
            count += 1
            # Filtrar si contiene imágenes
            if tweet.media and hasattr(tweet.media, "photos") and tweet.media.photos:
                for photo in tweet.media.photos:
                    photo_url = getattr(photo, "url", None)
                    if photo_url:
                        candidates.append({
                            "tweet_id": str(tweet.id),
                            "author_username": clean_target,
                            "tweet_url": f"https://x.com/{clean_target}/status/{tweet.id}",
                            "image_url": photo_url,
                            "created_at": tweet.date.isoformat() if tweet.date else "",
                            "tweet_text": (tweet.rawContent or "").strip().replace("\n", " "),
                        })
    except Exception as exc:
        print(f"[X_SCRAPER] Advertencia al consultar muro de @{clean_target}: {exc}")

    return candidates
