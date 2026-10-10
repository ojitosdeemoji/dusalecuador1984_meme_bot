"""Módulo de conexión y extracción mediante twscrape para X (Twitter)."""

import asyncio
from pathlib import Path
from typing import Optional
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

    # Formato de cookies estandarizado para twscrape
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
    
    # login_all verifica el token contra el endpoint GraphQL viewer de X
    await pool.login_all()
    
    account = await pool.get_account(clean_user)
    if account is None:
        return False
        
    return bool(account.active)
