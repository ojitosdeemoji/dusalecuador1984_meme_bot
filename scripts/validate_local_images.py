"""Validador y auditor del repositorio de imágenes locales autorizadas."""

import sys
from pathlib import Path

# Inyectar raíz del proyecto en sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.image_composer import (
    load_and_sanitize_image,
    compute_image_hash,
    SUPPORTED_FORMATS,
    MIN_DIMENSION,
)

VALID_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}


def main() -> None:
    images_dir = ROOT_DIR / "data" / "images"
    print(f"[IMÁGENES] Inspeccionando directorio local: {images_dir}")

    if not images_dir.exists():
        print(f"ERROR: La carpeta {images_dir} no existe.")
        sys.exit(1)

    # Filtrar solo archivos con extensiones de imagen soportadas
    image_files = [
        f for f in images_dir.iterdir()
        if f.is_file() and f.suffix.lower() in VALID_EXTENSIONS
    ]

    total_found = len(image_files)
    print(f"[IMÁGENES] Archivos de imagen detectados: {total_found}")

    if total_found == 0:
        print("ERROR CRÍTICO: No se encontraron imágenes en data/images/.")
        print("Debe subir al menos 2 imágenes (.jpg, .jpeg, .png o .webp) a dicha carpeta.")
        sys.exit(1)

    errors = 0
    print("\n--- REVISIÓN DE INTEGRIDAD DE IMÁGENES ---")
    for img_path in sorted(image_files):
        try:
            # 1. Carga y saneamiento con el motor real
            sanitized = load_and_sanitize_image(img_path)
            w, h = sanitized.size
            file_bytes = img_path.read_bytes()
            img_hash = compute_image_hash(file_bytes)[:12]
            size_kb = len(file_bytes) / 1024

            print(f"✔ [{img_hash}...] {img_path.name} | {w}x{h} px | {size_kb:.1f} KB | Formato RGB validado")
        except Exception as exc:
            print(f"✖ ERROR en {img_path.name}: {exc}")
            errors += 1
    print("-------------------------------------------\n")

    if errors > 0:
        print(f"ERROR: Se encontraron {errors} imagen(es) con problemas técnicos.")
        sys.exit(1)

    if total_found < 2:
        print("ADVERTENCIA: Se recomienda contar con al menos 2 o 3 imágenes para permitir alternancia.")

    print(f"[IMÁGENES] Auditoría completada: {total_found} imagen(es) listas para composición.")


if __name__ == "__main__":
    main()
