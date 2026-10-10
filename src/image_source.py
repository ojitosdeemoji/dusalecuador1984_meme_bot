"""Módulo selector y gestor de fuentes de imágenes con contingencia (fallback)."""

import io
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from twscrape import AccountsPool

from src.image_composer import (
    load_and_sanitize_image,
    compute_image_hash,
    analyze_image_metrics,
)
from src.x_scraper import (
    get_user_timeline_image_candidates,
    download_image_bytes,
)

VALID_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}


def select_local_image_fallback(
    images_dir: Path,
    used_hashes: List[str],
) -> Tuple[bytes, str, Dict[str, Any]]:
    """Selecciona una imagen del catálogo local cuando X no está disponible."""
    image_files = sorted([
        f for f in images_dir.iterdir()
        if f.is_file() and f.suffix.lower() in VALID_EXTENSIONS
    ])

    if not image_files:
        raise FileNotFoundError(f"Catálogo local vacío. No hay imágenes en: {images_dir}")

    used_set = set(used_hashes)

    # Buscar primera imagen no utilizada
    for img_path in image_files:
        raw_bytes = img_path.read_bytes()
        img_hash = compute_image_hash(raw_bytes)
        if img_hash not in used_set:
            return raw_bytes, img_hash, {
                "source_type": "local_fallback",
                "source_file": img_path.name,
                "source_author": "archivo_local",
                "source_license": "autorizada_local",
            }

    # Si todas fueron utilizadas, reciclar la primera
    first_path = image_files[0]
    first_bytes = first_path.read_bytes()
    first_hash = compute_image_hash(first_bytes)
    return first_bytes, first_hash, {
        "source_type": "local_fallback",
        "source_file": first_path.name,
        "source_author": "archivo_local",
        "source_license": "autorizada_local_reciclada",
    }


async def acquire_image_with_fallback(
    pool: Optional[AccountsPool],
    active_usernames: List[str],
    used_hashes: List[str],
    local_images_dir: Path,
    force_fallback: bool = False,
) -> Tuple[bytes, str, Dict[str, Any]]:
    """Obtiene una imagen desde X o activa el catálogo local ante cualquier fallo."""
    used_set = set(used_hashes)

    # 1. Intentar extracción en X si no se forzó el fallback
    if not force_fallback and pool and active_usernames:
        for username in active_usernames:
            try:
                candidates = await get_user_timeline_image_candidates(pool, username, limit=5)
                for candidate in candidates:
                    # Descargar y validar que no haya sido utilizada
                    raw_bytes = await download_image_bytes(candidate["image_url"])
                    img_hash = compute_image_hash(raw_bytes)

                    if img_hash not in used_set:
                        # Verificar que Pillow pueda decodificarla
                        load_and_sanitize_image(io.BytesIO(raw_bytes))
                        return raw_bytes, img_hash, {
                            "source_type": "x_twitter",
                            "source_file": candidate["image_url"],
                            "source_author": candidate["author_username"],
                            "source_tweet_url": candidate["tweet_url"],
                            "source_tweet_id": candidate["tweet_id"],
                            "fallback_activated": False,
                        }
            except Exception as exc:
                print(f"[IMAGE_SOURCE] Excepción al consultar @{username} en X: {exc}. Continuando...")

    # 2. Conmutación a contingencia local
    reason = "Forzado por prueba" if force_fallback else "Fallo o agotamiento de fuentes en X"
    print(f"[IMAGE_SOURCE] Activando catálogo local de reserva. Motivo: {reason}")

    raw_bytes, img_hash, metadata = select_local_image_fallback(local_images_dir, used_hashes)
    metadata["fallback_activated"] = True
    metadata["fallback_reason"] = reason

    return raw_bytes, img_hash, metadata
