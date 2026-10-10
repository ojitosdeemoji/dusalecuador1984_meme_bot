"""Script de verificación de contingencia (fallback) ante caídas de X."""

import asyncio
import io
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.image_source import acquire_image_with_fallback
from src.image_composer import (
    load_and_sanitize_image,
    render_meme,
    export_to_bluesky_jpeg,
    analyze_image_metrics,
)
from src.text_processor import extract_phrases_from_pdf, get_available_phrase


async def main_async() -> None:
    print("[FALLBACK] Iniciando prueba de conmutación por falla de X...")

    local_images_dir = ROOT_DIR / "data" / "images"
    pdf_file = ROOT_DIR / "data" / "corpus.pdf"

    # 1. Obtener frase
    phrases = extract_phrases_from_pdf(pdf_file)
    selected_phrase = phrases[0] if phrases else "FRASE DE PRUEBA DE FALLBACK"

    # 2. Forzar explícitamente la falla de X (pool=None, force_fallback=True)
    print("[FALLBACK] Simulando desconexión completa de X...")
    raw_bytes, img_hash, metadata = await acquire_image_with_fallback(
        pool=None,
        active_usernames=[],
        used_hashes=[],
        local_images_dir=local_images_dir,
        force_fallback=True,
    )

    print(f"[FALLBACK] Conmutación exitosa a fuente local:")
    print(f"  - Archivo seleccionado: {metadata['source_file']}")
    print(f"  - Motivo de fallback: {metadata['fallback_reason']}")
    print(f"  - Hash SHA-256: {img_hash[:16]}...")

    # 3. Componer meme con la imagen de reserva
    sanitized_img = load_and_sanitize_image(io.BytesIO(raw_bytes))
    meme_canvas = render_meme(
        sanitized_img,
        top_text="SISTEMA DE CONTINGENCIA",
        bottom_text="FALLBACK LOCAL ACTIVADO CON EXITO",
    )

    jpeg_data = export_to_bluesky_jpeg(meme_canvas)
    output_path = ROOT_DIR / "fallback_preview.jpg"
    output_path.write_bytes(jpeg_data)

    metrics = analyze_image_metrics(sanitized_img)

    # 4. Generar reporte
    summary_path = ROOT_DIR / "fallback_summary.md"
    content = f"""## Reporte de Prueba de Contingencia (Fallback)

- **Estado de simulación:** Fallo deliberado de conexión en X ejecutado con éxito.
- **Acción del sistema:** Conmutación automática a reserva local sin interrupción de servicio.
- **Imagen local utilizada:** `{metadata['source_file']}`
- **Motivo de conmutación:** `{metadata['fallback_reason']}`
- **Dimensiones:** `{meme_canvas.size[0]} x {meme_canvas.size[1]} px`
- **Proporción de aspecto:** `{metrics['aspect_ratio']}`
- **Luminosidad:** `{metrics['approx_luminosity']} / 255`
- **Artefacto:** Imagen generada disponible para descarga (*fallback-preview*).
"""
    summary_path.write_text(content, encoding="utf-8")
    print(f"✔ PRUEBA DE FALLBACK SUPERADA: Meme exportado en {output_path.name}.")


def main() -> None:
    asyncio.run(main_async())


if __name__ == "__main__":
    main()
