"""Orquestador principal de ejecución del bot (simulación y publicación)."""

import argparse
from datetime import datetime, timezone
import sys
from pathlib import Path
from typing import List, Tuple

# Inyectar raíz del proyecto en sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.state_manager import load_state, save_state, record_entry
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
    analyze_image_metrics,
)
from src.publisher import publish_meme_to_bluesky

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
    """Selecciona la primera imagen disponible cuyo hash no haya sido registrado."""
    image_files = sorted([
        f for f in images_dir.iterdir()
        if f.is_file() and f.suffix.lower() in VALID_EXTENSIONS
    ])

    if not image_files:
        raise FileNotFoundError(f"No hay imágenes válidas en el directorio: {images_dir}")

    used_set = set(used_hashes)

    for img_path in image_files:
        content = img_path.read_bytes()
        img_hash = compute_image_hash(content)
        if img_hash not in used_set:
            return img_path, content, img_hash

    # Si se usaron todas, reciclar la primera
    first_path = image_files[0]
    first_content = first_path.read_bytes()
    first_hash = compute_image_hash(first_content)
    print("[AVISO] Todas las imágenes locales han sido utilizadas al menos una vez. Reutilizando la primera.")
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
    metrics: dict,
    post_info: dict | None = None,
) -> str:
    """Construye el reporte estructurado en formato Markdown para GitHub Step Summary."""
    if dry_run:
        status_line = "🟡 **MODO SIMULACIÓN (DRY RUN - SIN PUBLICAR)**"
        post_section = "- **Publicación:** Omitida deliberadamente por el modo simulación."
    else:
        status_line = "🟢 **PUBLICACIÓN CONFIRMADA EN BLUESKY**"
        post_section = f"""- **URL Pública:** [{post_info['post_url']}]({post_info['post_url']})
- **URI AT-Protocol:** `{post_info['uri']}`
- **CID del post:** `{post_info['cid']}`"""

    return f"""## Reporte de Ejecución: meme-bot

**Estado:** {status_line}

### 1. Composición Visual
- **Imagen base:** `{image_name}`
- **Dimensiones finales:** `{dimensions[0]} x {dimensions[1]} px` (Proporción: `{metrics['aspect_ratio']}`)
- **Luminosidad perceptual:** `{metrics['approx_luminosity']} / 255`
- **Peso de salida (JPEG):** `{file_size_kb:.2f} KB`
- **Hash SHA-256 de imagen:** `{image_hash[:16]}...`

### 2. Contenido Textual (Cadáver Exquisito)
- **Frase original extraída:**
  > "{phrase}"
- **Hash SHA-256 de frase:** `{phrase_hash[:16]}...`
- **Distribución:**
  - **Texto superior:** `{top_text if top_text else "(Vacío)"}`
  - **Texto inferior:** `{bottom_text if bottom_text else "(Vacío)"}`

### 3. Registro y Publicación
{post_section}
- **Persistencia en state.json:** {"Omitida (Dry Run)" if dry_run else "Registrada atómicamente"}
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

    state_file = ROOT_DIR / "data" / "state.json"
    pdf_file = ROOT_DIR / "data" / "corpus.pdf"
    images_dir = ROOT_DIR / "data" / "images"
    output_image_path = ROOT_DIR / "output_meme.jpg"
    summary_path = ROOT_DIR / "summary.md"

    # 1. Cargar estado
    state = load_state(state_file)
    used_phrases = state.get("used_phrase_hashes", [])
    used_images = state.get("used_image_hashes", [])
    print(f"[ESTADO] Frases previas: {len(used_phrases)} | Imágenes previas: {len(used_images)}")

    # 2. Selección de frase
    phrases = extract_phrases_from_pdf(pdf_file)
    selected_phrase = get_available_phrase(phrases, used_phrases)

    if not selected_phrase:
        print("ERROR CRÍTICO: Se han agotado las frases disponibles en el PDF.")
        sys.exit(1)

    phrase_hash = compute_hash(selected_phrase)
    print(f"[TEXTO] Frase seleccionada: \"{selected_phrase}\" (Hash: {phrase_hash[:12]}...)")

    # 3. Selección de imagen
    img_path, img_bytes, img_hash = select_local_image(images_dir, used_images)
    print(f"[IMAGEN] Imagen seleccionada: {img_path.name} (Hash: {img_hash[:12]}...)")

    # 4. Renderizado gráfico
    sanitized_image = load_and_sanitize_image(img_path)
    top_text, bottom_text = split_phrase_into_meme_layout(selected_phrase)

    meme_canvas = render_meme(
        sanitized_image,
        top_text=top_text,
        bottom_text=bottom_text,
    )

    jpeg_bytes = export_to_bluesky_jpeg(meme_canvas)
    file_size_kb = len(jpeg_bytes) / 1024
    output_image_path.write_bytes(jpeg_bytes)

    # 5. Métricas visuales
    metrics = analyze_image_metrics(sanitized_image)
    w, h = meme_canvas.size

    post_info = None

    # 6. Publicación si no es dry-run
    if not args.dry_run:
        print("[PUBLICACIÓN] Publicando en Bluesky...")
        post_caption = f"{selected_phrase}\n\n#cadáverexquisito #bot"
        alt_description = f"Meme generado por bot de cadáver exquisito: '{selected_phrase}'"

        try:
            post_info = publish_meme_to_bluesky(
                image_bytes=jpeg_bytes,
                post_text=post_caption,
                alt_text=alt_description,
                width=w,
                height=h,
            )
            print(f"[PUBLICACIÓN] Éxito: {post_info['post_url']}")
        except Exception as exc:
            print(f"ERROR CRÍTICO AL PUBLICAR: {exc}")
            sys.exit(1)

        # 7. Persistir en el estado
        text_pos = "top_and_bottom" if (top_text and bottom_text) else ("top_only" if top_text else "bottom_only")
        lines_count = (1 if top_text else 0) + (1 if bottom_text else 0)
        now_iso = datetime.now(timezone.utc).isoformat()

        entry_metadata = {
            "uri": post_info["uri"],
            "cid": post_info["cid"],
            "post_url": post_info["post_url"],
            "published_at": now_iso,
            "source_type": "local_image",
            "source_file": img_path.name,
            "source_author": "archivo_local",
            "source_license": "autorizada_local",
            "phrase_text": selected_phrase,
            "lines_count": lines_count,
            "text_position": text_pos,
            "aspect_ratio": metrics["aspect_ratio"],
            "approx_luminosity": metrics["approx_luminosity"],
            "likes": 0,
            "reposts": 0,
            "replies": 0,
            "quotes": 0,
            "score": 0.0,
        }

        record_entry(state, phrase_hash, img_hash, entry_metadata)
        save_state(state_file, state)
        print(f"[ESTADO] Estado actualizado y guardado en {state_file.name}.")

    # 8. Reporte Markdown
    summary_content = build_markdown_summary(
        dry_run=args.dry_run,
        phrase=selected_phrase,
        phrase_hash=phrase_hash,
        top_text=top_text,
        bottom_text=bottom_text,
        image_name=img_path.name,
        image_hash=img_hash,
        dimensions=(w, h),
        file_size_kb=file_size_kb,
        metrics=metrics,
        post_info=post_info,
    )
    summary_path.write_text(summary_content, encoding="utf-8")


if __name__ == "__main__":
    main()
