"""Script de prueba de descarga y validación de una imagen real desde X."""

import asyncio
import io
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
    download_image_bytes,
)
from src.image_composer import (
    load_and_sanitize_image,
    compute_image_hash,
    analyze_image_metrics,
)


async def main_async() -> None:
    print("[DESCARGA X] Iniciando prueba de descarga de imagen...")

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

    db_path = ROOT_DIR / "accounts.db"
    pool = await initialize_x_pool(db_path, username, auth_token, ct0)
    is_active = await verify_x_account_status(pool, username)

    if not is_active:
        print("ERROR: La sesión en X no se encuentra activa.")
        sys.exit(1)

    # 1. Localizar primer candidato con imagen
    target_candidate = None
    for target in active_users:
        print(f"[DESCARGA X] Buscando imagen en muro de @{target}...")
        candidates = await get_user_timeline_image_candidates(pool, target, limit=5)
        if candidates:
            target_candidate = candidates[0]
            break

    if not target_candidate:
        print("ERROR: No se encontraron fotos disponibles en las cuentas activas.")
        sys.exit(1)

    print(f"\n[DESCARGA X] Candidato seleccionado:")
    print(f"  - Autor: @{target_candidate['author_username']}")
    print(f"  - Tweet: {target_candidate['tweet_url']}")
    print(f"  - URL imagen: {target_candidate['image_url']}")

    # 2. Descargar bytes por HTTPS
    print("[DESCARGA X] Descargando archivo binario desde servidores de medios...")
    try:
        raw_bytes = await download_image_bytes(target_candidate["image_url"])
    except Exception as exc:
        print(f"ERROR al descargar imagen: {exc}")
        sys.exit(1)

    raw_size_kb = len(raw_bytes) / 1024
    print(f"[DESCARGA X] Descarga exitosa. Peso recibido: {raw_size_kb:.2f} KB")

    # 3. Saneamiento y validación con Pillow
    print("[DESCARGA X] Pasando imagen por motor de validación Pillow...")
    try:
        sanitized_img = load_and_sanitize_image(io.BytesIO(raw_bytes))
    except Exception as exc:
        print(f"ERROR de validación en Pillow: {exc}")
        sys.exit(1)

    width, height = sanitized_img.size
    img_hash = compute_image_hash(raw_bytes)
    metrics = analyze_image_metrics(sanitized_img)

    print(f"[DESCARGA X] Dimensiones saneadas: {width}x{height} px")
    print(f"[DESCARGA X] Proporción: {metrics['aspect_ratio']} | Luminosidad: {metrics['approx_luminosity']}")
    print(f"[DESCARGA X] Hash SHA-256 de origen: {img_hash[:16]}...")

    # 4. Guardar archivo local para artefacto
    output_path = ROOT_DIR / "downloaded_x_image.jpg"
    sanitized_img.save(output_path, format="JPEG", quality=90)
    print(f"[DESCARGA X] Archivo guardado localmente en: {output_path.name}")

    # 5. Generar Step Summary
    summary_file = ROOT_DIR / "x_download_summary.md"
    content = f"""## Reporte de Descarga y Validación de Imagen de X

- **Autor de origen:** @{target_candidate['author_username']}
- **Tweet origen:** [{target_candidate['tweet_url']}]({target_candidate['tweet_url']})
- **Dimensiones:** `{width} x {height} px`
- **Proporción de aspecto:** `{metrics['aspect_ratio']}`
- **Luminosidad perceptual:** `{metrics['approx_luminosity']} / 255`
- **Hash SHA-256:** `{img_hash[:20]}...`
- **Estado de validación:** Saneada a RGB, corregida de orientación EXIF y conforme para meme.
- **Artefacto:** Archivo disponible para descarga (*x-downloaded-image*).
"""
    summary_file.write_text(content, encoding="utf-8")
    print("✔ PRUEBA DE DESCARGA SUPERADA CON ÉXITO.")


def main() -> None:
    asyncio.run(main_async())


if __name__ == "__main__":
    main()
