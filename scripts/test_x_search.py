"""Script de prueba de búsqueda y detección de imágenes en X desde allowlist."""

import asyncio
import os
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.x_config import get_active_usernames
from src.x_scraper import (
    initialize_x_pool,
    verify_x_account_status,
    get_user_timeline_image_candidates,
)


async def main_async() -> None:
    print("[EXTRACCIÓN X] Iniciando inspección de cuentas autorizadas...")

    username = os.getenv("X_USERNAME")
    auth_token = os.getenv("X_AUTH_TOKEN")
    ct0 = os.getenv("X_CT0")

    if not username or not auth_token or not ct0:
        print("ERROR CRÍTICO: Variables de entorno de X ausentes.")
        sys.exit(1)

    allowlist_path = ROOT_DIR / "data" / "x_allowlist.json"
    active_users = get_active_usernames(allowlist_path)

    if not active_users:
        print("ERROR: No hay cuentas activas en la allowlist.")
        sys.exit(1)

    print(f"[EXTRACCIÓN X] Cuentas objetivo en allowlist: {active_users}")

    db_path = ROOT_DIR / "accounts.db"
    pool = await initialize_x_pool(db_path, username, auth_token, ct0)
    is_active = await verify_x_account_status(pool, username)

    if not is_active:
        print("ERROR: La sesión en X no se encuentra activa.")
        sys.exit(1)

    all_found = []

    # Recorrer las cuentas activas hasta encontrar candidatos válidos
    for target in active_users:
        print(f"\n[EXTRACCIÓN X] Consultando muro de @{target}...")
        try:
            candidates = await get_user_timeline_image_candidates(pool, target, limit=10)
            print(f"[EXTRACCIÓN X] Fotos detectadas en @{target}: {len(candidates)}")
            if candidates:
                all_found.extend(candidates)
                break
        except Exception as exc:
            print(f"[EXTRACCIÓN X] Error consultando @{target}: {exc}")

    if not all_found:
        print("ERROR: No se detectaron imágenes en las cuentas autorizadas consultadas.")
        sys.exit(1)

    # Imprimir muestra de metadatos detectados
    print("\n--- IMÁGENES DETECTADAS EN X (SOLO LECTURA) ---")
    for index, item in enumerate(all_found[:3], start=1):
        print(f"{index}. Autor: @{item['author_username']}")
        print(f"   Tweet: {item['tweet_url']}")
        print(f"   URL Imagen: {item['image_url']}")
        print(f"   Fecha: {item['created_at']}")
    print("-----------------------------------------------\n")

    # Guardar reporte para GitHub Actions
    summary_file = ROOT_DIR / "x_search_summary.md"
    content = f"""## Reporte de Extracción de Imágenes en X (twscrape)

- **Sesión de servicio:** @{username.strip().lstrip('@')} (Activa)
- **Cuenta fuente consultada:** @{all_found[0]['author_username']}
- **Total de imágenes encontradas:** {len(all_found)}

### Muestra de Publicaciones Detectadas:
"""
    for item in all_found[:3]:
        content += f"- **Tweet:** [{item['tweet_url']}]({item['tweet_url']}) | **Imagen:** `{item['image_url'][:60]}...`\n"

    summary_file.write_text(content, encoding="utf-8")
    print(f"✔ EXTRACCIÓN EXITOSA: Metadatos recuperados y guardados en {summary_file.name}.")


def main() -> None:
    asyncio.run(main_async())


if __name__ == "__main__":
    main()
