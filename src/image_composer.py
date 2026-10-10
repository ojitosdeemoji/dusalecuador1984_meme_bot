"""Módulo de composición visual de memes con Pillow."""

import hashlib
import io
import textwrap
from pathlib import Path
from typing import Dict, Optional, Tuple
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageStat

# Protección contra ataques de descompresión de imágenes (bombas zip)
Image.MAX_IMAGE_PIXELS = 35_000_000

SUPPORTED_FORMATS = {"JPEG", "JPG", "PNG", "WEBP"}
MAX_DIMENSION = 1600
MIN_DIMENSION = 300
MAX_OUTPUT_BYTES = 950_000  # 950 KB (límite de seguridad para Bluesky blob)


def compute_image_hash(image_bytes: bytes) -> str:
    """Calcula el hash SHA-256 de los bytes de una imagen."""
    return hashlib.sha256(image_bytes).hexdigest()


def load_and_sanitize_image(image_input: io.BytesIO | Path | str) -> Image.Image:
    """Abre, valida dimensiones, corrige orientación EXIF y convierte a RGB."""
    try:
        img = Image.open(image_input)
    except Exception as exc:
        raise ValueError(f"No se pudo decodificar el archivo como imagen válida: {exc}") from exc

    if img.format and img.format.upper() not in SUPPORTED_FORMATS:
        raise ValueError(f"Formato de imagen no compatible: {img.format}. Formatos válidos: {SUPPORTED_FORMATS}")

    # Corregir orientación basada en metadatos EXIF si existen
    img = ImageOps.exif_transpose(img)

    width, height = img.size
    if width < MIN_DIMENSION or height < MIN_DIMENSION:
        raise ValueError(f"Dimensiones de imagen demasiado pequeñas: {width}x{height}. Mínimo {MIN_DIMENSION}px.")

    # Redimensionar proporcionalmente si supera el tamaño máximo
    if width > MAX_DIMENSION or height > MAX_DIMENSION:
        img.thumbnail((MAX_DIMENSION, MAX_DIMENSION), Image.Resampling.LANCZOS)

    # Convertir forzosamente a RGB eliminando canal alfa o paletas indexadas
    if img.mode != "RGB":
        rgb_img = Image.new("RGB", img.size, (255, 255, 255))
        if img.mode in ("RGBA", "LA") or (img.mode == "P" and "transparency" in img.info):
            rgb_img.paste(img, mask=img.convert("RGBA").split()[3])
        else:
            rgb_img.paste(img)
        img = rgb_img

    return img


def get_system_font(target_size: int) -> ImageFont.ImageFont | ImageFont.FreeTypeFont:
    """Busca una fuente TrueType legible en el sistema o recurre a la fuente predeterminada."""
    font_candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
        "DejaVuSans-Bold.ttf",
        "arialbd.ttf",
    ]
    for path in font_candidates:
        try:
            return ImageFont.truetype(path, size=target_size)
        except OSError:
            continue
    return ImageFont.load_default()


def calculate_wrapped_text(
    draw: ImageDraw.ImageDraw,
    text: str,
    font: ImageFont.ImageFont | ImageFont.FreeTypeFont,
    max_width: int,
) -> Tuple[list[str], int, int]:
    """Calcula el ajuste de línea y las dimensiones totales del bloque de texto."""
    words = text.split()
    if not words:
        return [], 0, 0

    lines: list[str] = []
    current_line: list[str] = []

    for word in words:
        test_line = " ".join(current_line + [word])
        bbox = draw.textbbox((0, 0), test_line, font=font)
        line_w = bbox[2] - bbox[0]

        if line_w <= max_width or not current_line:
            current_line.append(word)
        else:
            lines.append(" ".join(current_line))
            current_line = [word]

    if current_line:
        lines.append(" ".join(current_line))

    total_h = 0
    max_line_w = 0
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]
        max_line_w = max(max_line_w, w)
        total_h += int(h * 1.25)

    return lines, max_line_w, total_h


def render_meme(
    base_image: Image.Image,
    top_text: Optional[str] = None,
    bottom_text: Optional[str] = None,
) -> Image.Image:
    """Renderiza el texto estilo meme (blanco con contorno negro) sobre la imagen."""
    canvas = base_image.copy()
    draw = ImageDraw.Draw(canvas)
    img_w, img_h = canvas.size

    margin_x = int(img_w * 0.05)
    max_text_w = img_w - (margin_x * 2)
    max_block_h = int(img_h * 0.35)

    positions = []
    if top_text and top_text.strip():
        positions.append(("top", top_text.strip().upper()))
    if bottom_text and bottom_text.strip():
        positions.append(("bottom", bottom_text.strip().upper()))

    for pos, raw_str in positions:
        font_size = int(img_h * 0.08)
        min_font_size = max(14, int(img_h * 0.03))
        selected_font = get_system_font(font_size)
        lines, _, block_h = calculate_wrapped_text(draw, raw_str, selected_font, max_text_w)

        while (block_h > max_block_h or len(lines) > 4) and font_size > min_font_size:
            font_size -= 2
            selected_font = get_system_font(font_size)
            lines, _, block_h = calculate_wrapped_text(draw, raw_str, selected_font, max_text_w)

        stroke_w = max(2, int(font_size * 0.08))

        if pos == "top":
            current_y = int(img_h * 0.04)
        else:
            current_y = img_h - block_h - int(img_h * 0.04)

        for line in lines:
            bbox = draw.textbbox((0, 0), line, font=selected_font)
            line_w = bbox[2] - bbox[0]
            line_h = bbox[3] - bbox[1]
            x = (img_w - line_w) // 2

            draw.text(
                (x, current_y),
                line,
                font=selected_font,
                fill="white",
                stroke_width=stroke_w,
                stroke_fill="black",
            )
            current_y += int(line_h * 1.25)

    return canvas


def export_to_bluesky_jpeg(image: Image.Image) -> bytes:
    """Comprime y exporta la imagen a JPEG asegurando no sobrepasar el límite de Bluesky."""
    quality = 88
    for _ in range(5):
        buffer = io.BytesIO()
        image.save(buffer, format="JPEG", quality=quality, optimize=True)
        size = buffer.tell()

        if size <= MAX_OUTPUT_BYTES:
            return buffer.getvalue()

        quality -= 10
        if quality < 50:
            break

    w, h = image.size
    smaller_img = image.resize((int(w * 0.8), int(h * 0.8)), Image.Resampling.LANCZOS)
    buffer = io.BytesIO()
    smaller_img.save(buffer, format="JPEG", quality=75, optimize=True)
    return buffer.getvalue()


def analyze_image_metrics(image: Image.Image) -> Dict[str, float]:
    """Calcula proporción geométrica y luminosidad perceptual promedio de la imagen."""
    w, h = image.size
    aspect_ratio = round(w / h, 2)
    # Medir luminancia en escala de grises (0 a 255)
    gray = image.convert("L")
    stat = ImageStat.Stat(gray)
    luminosity = round(stat.mean[0], 2)
    return {
        "aspect_ratio": aspect_ratio,
        "approx_luminosity": luminosity,
    }
