"""Validador e inspeccionador del archivo PDF fuente (corpus)."""

import sys
from pathlib import Path

# Inyectar la raíz del proyecto en sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.text_processor import extract_phrases_from_pdf, compute_hash


def main() -> None:
    pdf_path = ROOT_DIR / "data" / "corpus.pdf"
    print(f"[PDF] Inspeccionando archivo: {pdf_path}")

    if not pdf_path.exists():
        print(f"ERROR: No se encontró el archivo en {pdf_path}")
        print("Verifique haber subido el archivo con el nombre exacto 'corpus.pdf' dentro de 'data/'.")
        sys.exit(1)

    file_size_kb = pdf_path.stat().st_size / 1024
    print(f"[PDF] Archivo detectado. Tamaño: {file_size_kb:.2f} KB")

    try:
        phrases = extract_phrases_from_pdf(pdf_path)
    except Exception as exc:
        print(f"ERROR CRÍTICO AL PROCESAR EL PDF: {exc}")
        print("Causa probable: El PDF está escaneado como imagen (sin capa de texto), protegido por contraseña o corrupto.")
        sys.exit(1)

    total_phrases = len(phrases)
    print(f"[PDF] Éxito: Se extrajeron {total_phrases} frases válidas para memes.")

    if total_phrases < 5:
        print("ADVERTENCIA: Se obtuvieron menos de 5 frases utilizables. Se recomienda utilizar un corpus más extenso.")

    print("\n--- MUESTRA DE LAS PRIMERAS 5 FRASES ---")
    for index, phrase in enumerate(phrases[:5], start=1):
        p_hash = compute_hash(phrase)[:12]
        print(f"{index}. [{p_hash}...] \"{phrase}\"")
    print("----------------------------------------\n")


if __name__ == "__main__":
    main()
