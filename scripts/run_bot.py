"""Orquestador principal de ejecución del bot (simulación y publicación)."""

import argparse
import sys
from pathlib import Path
from typing import List, Tuple

# Inyectar raíz del proyecto en sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.state_manager import load_state, is_phrase_used, is_image_used
from src.text_processor import (
    extract_phrases_from_pdf,
    compute_hash,
    get_available_phrase,
)
from src.image_composer import (
    load_and_sanitize_image,
    render_meme,
    export_to_bluesky_jpeg,
    compute_image_hash,
)

VALID_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}


def split_phrase_into_meme_layout(phrase: str) -> Tuple[str, str]:
    """Divide una frase en texto superior e inferior de forma equilibrada."""
    words = phrase.split()
    total_words = len(words)

    if total_words <= 5:
        return "", phrase.strip()

    midpoint = total_words // 2
    top_part = " ".join(words[:midpoint]).strip()
    bottom_part = " ".join(words[midpoint:]).strip()
    return top_part, bottom_part


def select_local_image(images_dir: Path, used_hashes: List[str]) -> Tuple[Path, bytes, str]:
    """Selecciona la primera imagen disponible de la carpeta cuyo hash no haya sido registrado."""
    image_files = sorted([
        f for f in images_dir.iterdir()
        if f.is_file() and f.suffix.lower() in VALID_EXTENSIONS
    ])

    if not image_files:
        raise FileNotFoundError(f"No hay imágenes válidas en el directorio: {images_dir}")

    used_set = set(used_hashes)

    # 1. Intentar seleccionar una imagen no usada
    for img_path in image_files:
        content = img_path.read_bytes()
        img_hash = compute_image_hash(content)
        if img_hash not in used_set:
            return img_path, content, img_hash

    # 2. Si todas ya fueron usadas, advertir y reciclar la primera
    first_path = image_files[0]
    first_content = first_path.read_bytes()
    first_hash = compute_image_hash(first_content)
    print("[AVISO] Todas las imágenes locales han sido utilizadas al menos una vez. Reutilizando la primera del catálogo.")
    return first_path, first_content, first_hash


def build_markdown_summary(
    dry_run: bool,
    phrase: str,
    phrase_hash: str,
    top_text: str,
    bottom_text: str,
    image_name: str,
    image_hash: str,
    dimensions: Tuple[int, int],
    file_size_kb: float,
) -> str:
    """Construye el reporte estructurado en formato Markdown para GitHub Step Summary."""
    mode_badge = "🟡 MODO SIMULACIÓN (DRY RUN - SIN PUBLICAR)" if dry_run else "🟢 MODO PRODUCCIÓN (PUBLICACIÓN ACTIVA)"
    
    return f"""## Reporte de Ejecución: meme-bot

**Estado:** {mode_badge}

### 1. Composición Visual
- **Imagen base:** `{image_name}`
- **Dimensiones finales:** `{dimensions[0]} x {dimensions[1]} px`
- **Peso de salida (JPEG):** `{file_size_kb:.2f} KB` (Límite Bluesky: 950 KB)
- **Hash SHA-256 de imagen:** `{image_hash[:16]}...`

### 2. Contenido Textual (Cadáver Exquisito)
- **Frase original extraída:**
  > "{phrase}"
- **Hash SHA-256 de frase:** `{phrase_hash[:16]}...`
- **Distribución de meme:**
  - **Texto superior (Top):** `{top_text if top_text else "(Vacío)"}`
  - **Texto inferior (Bottom):** `{bottom_text if bottom_text else "(Vacío)"}`

### 3. Registro de Persistencia
- **Modificación de state.json:** `{"Omitida (Dry Run)" if dry_run else "Registrada exitosamente"}`
- **Publicación en Bluesky:** `{"Omitida (Dry Run)" if dry_run else "Confirmada"}`
"""


def main() -> None:
    parser = argparse.ArgumentParser(description="Orquestador de meme-bot.")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Ejecuta el pipeline sin publicar y sin alterar state.json.",
    )
    args = parser.parse_args()

    print(f"[BOT] Iniciando ciclo de ejecución. Modo Dry Run: {args.dry_run}")

    # Rutas clave
    state_file = ROOT_DIR / "data" / "state.json"
    pdf_file = ROOT_DIR / "data" / "corpus.pdf"
    images_dir = ROOT_DIR / "data" / "images"
    output_image_path = ROOT_DIR / "output_meme.jpg"
    summary_path = ROOT_DIR / "summary.md"

    # 1. Cargar estado
    state = load_state(state_file)
    used_phrases = state.get("used_phrase_hashes", [])
    used_images = state.get("used_image_hashes", [])
    print(f"[ESTADO] Frases previamente usadas: {len(used_phrases)} | Imágenes usadas: {len(used_images)}")

    # 2. Extraer frases y seleccionar candidata
    phrases = extract_phrases_from_pdf(pdf_file)
    selected_phrase = get_available_phrase(phrases, used_phrases)

    if not selected_phrase:
        print("ERROR CRÍTICO: Se han agotado las frases disponibles en el PDF.")
        sys.exit(1)

    phrase_hash = compute_hash(selected_phrase)
    print(f"[TEXTO] Frase seleccionada: \"{selected_phrase}\" (Hash: {phrase_hash[:12]}...)")

    # 3. Seleccionar imagen
    img_path, img_bytes, img_hash = select_local_image(images_dir, used_images)
    print(f"[IMAGEN] Imagen seleccionada: {img_path.name} (Hash: {img_hash[:12]}...)")

    # 4. Procesamiento gráfico
    sanitized_image = load_and_sanitize_image(img_path)
    top_text, bottom_text = split_phrase_into_meme_layout(selected_phrase)

    meme_canvas = render_meme(
        sanitized_image,
        top_text=top_text,
        bottom_text=bottom_text,
    )

    jpeg_bytes = export_to_bluesky_jpeg(meme_canvas)
    file_size_kb = len(jpeg_bytes) / 1024

    # Guardar imagen para artefacto
    output_image_path.write_bytes(jpeg_bytes)
    print(f"[COMPOSICIÓN] Imagen exportada a {output_image_path.name} ({file_size_kb:.2f} KB)")

    # 5. Generar reporte Markdown
    summary_content = build_markdown_summary(
        dry_run=args.dry_run,
        phrase=selected_phrase,
        phrase_hash=phrase_hash,
        top_text=top_text,
        bottom_text=bottom_text,
        image_name=img_path.name,
        image_hash=img_hash,
        dimensions=meme_canvas.size,
        file_size_kb=file_size_kb,
    )
    summary_path.write_text(summary_content, encoding="utf-8")

    # 6. Publicación y persistencia
    if args.dry_run:
        print("[DRY RUN] Simulación completada con éxito. No se registraron cambios en state.json.")
        return

    # Si se desmarca dry-run antes de configurar Bluesky
    print("ERROR: La publicación real requiere credenciales de Bluesky (Fase 7 y 8).")
    sys.exit(1)


if __name__ == "__main__":
    main()
