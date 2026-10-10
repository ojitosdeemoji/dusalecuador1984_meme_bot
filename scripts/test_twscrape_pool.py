"""Script de prueba de inicialización y verificación del pool de twscrape."""

import asyncio
import os
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.x_scraper import initialize_x_pool, verify_x_account_status


async def main_async() -> None:
    print("[TWSCRAPE] Iniciando prueba de pool de cuentas...")

    username = os.getenv("X_USERNAME")
    auth_token = os.getenv("X_AUTH_TOKEN")
    ct0 = os.getenv("X_CT0")

    if not username or not auth_token or not ct0:
        print("ERROR CRÍTICO: Faltan variables de entorno requeridas (X_USERNAME, X_AUTH_TOKEN, X_CT0).")
        sys.exit(1)

    db_path = ROOT_DIR / "accounts.db"
    print(f"[TWSCRAPE] Inicializando base de datos local en: {db_path.name}")

    try:
        pool = await initialize_x_pool(
            db_path=db_path,
            username=username,
            auth_token=auth_token,
            ct0=ct0,
        )
    except Exception as exc:
        print(f"ERROR al inicializar pool: {exc}")
        sys.exit(1)

    print("[TWSCRAPE] Verificando estado de sesión con los endpoints de X...")
    try:
        is_active = await verify_x_account_status(pool, username)
    except Exception as exc:
        print(f"ERROR durante la verificación de sesión en X: {exc}")
        print("Causa probable: Restricción de IP en GitHub Actions o sesión expirada.")
        sys.exit(1)

    if not is_active:
        print(f"ADVERTENCIA: La cuenta @{username.strip().lstrip('@')} no quedó en estado activo.")
        print("Es posible que las cookies hayan expirado o que X requiera revalidación web.")
        sys.exit(1)

    print(f"✔ CONEXIÓN EXITOSA CON X: Cuenta @{username.strip().lstrip('@')} activa y autorizada en el pool.")


def main() -> None:
    asyncio.run(main_async())


if __name__ == "__main__":
    main()
