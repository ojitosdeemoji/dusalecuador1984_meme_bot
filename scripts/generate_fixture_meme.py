"""Generador de composición meme con datos fixture para validación en CI."""

import io
from pathlib import Path
from PIL import Image, ImageDraw

from src.image_composer import (
    load_and_sanitize_image,
    render_meme,
    export_to_bluesky_jpeg,
    compute_image_hash,
)


def create_fixture_canvas() -> io.BytesIO:
    """Crea una imagen geométrica de prueba en memoria sin dependencias externas."""
    width, height = 800, 800
    image = Image.new("RGB", (width, height), color=(30, 41, 59))  # Fondo azul pizarra
    draw = ImageDraw.Draw(image)

    # Dibujar elementos geométricos de contraste
    draw.rectangle([60, 60, 740, 740], outline=(203, 213, 225), width=6)
    draw.ellipse([250, 250, 550, 550], fill=(234, 88, 12), outline=(254, 215, 170), width=4)

    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    buffer.seek(0)
    return buffer


def main() -> None:
    print("[FIXTURE] Iniciando generación de meme de prueba...")
    raw_buffer = create_fixture_canvas()

    # 1. Sanear imagen
    sanitized_image = load_and_sanitize_image(raw_buffer)

    # 2. Renderizar meme
    top_text = "ESTO ES UN FIXTURE DE PRUEBA"
    bottom_text = "VALIDACION AUTOMATICA EN GITHUB ACTIONS"
    meme_canvas = render_meme(sanitized_image, top_text=top_text, bottom_text=bottom_text)

    # 3. Exportar JPEG seguro para Bluesky
    jpeg_data = export_to_bluesky_jpeg(meme_canvas)
    image_hash = compute_image_hash(jpeg_data)

    output_path = Path("out.jpg")
    output_path.write_bytes(jpeg_data)

    file_size_kb = len(jpeg_data) / 1024
    print(f"[FIXTURE] Archivo generado exitosamente: {output_path.resolve()}")
    print(f"[FIXTURE] Peso: {file_size_kb:.2f} KB | Hash SHA-256: {image_hash}")


if __name__ == "__main__":
    main()
