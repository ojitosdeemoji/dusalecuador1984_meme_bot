"""Script de prueba e inspección del generador de Markov sobre el corpus real."""

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.text_processor import extract_phrases_from_pdf, compute_hash
from src.markov_generator import generate_markov_sentence


def main() -> None:
    pdf_path = ROOT_DIR / "data" / "corpus.pdf"
    print(f"[MARKOV] Cargando corpus para entrenamiento: {pdf_path}")

    if not pdf_path.exists():
        print("ERROR: data/corpus.pdf no existe.")
        sys.exit(1)

    sentences = extract_phrases_from_pdf(pdf_path)
    print(f"[MARKOV] Oraciones fuente extraídas del PDF: {len(sentences)}")

    print("\n--- GENERACIÓN EXPERIMENTAL DE AFORTISMOS (CADÁVER EXQUISITO) ---")
    used_simulated = []
    generated_count = 0

    for i in range(1, 6):
        synth = generate_markov_sentence(
            sentences=sentences,
            used_hashes=used_simulated,
            compute_hash_fn=compute_hash,
            min_words=5,
            max_words=15,
            max_attempts=100,
        )
        if synth:
            h = compute_hash(synth)[:12]
            used_simulated.append(compute_hash(synth))
            print(f"{i}. [{h}...] \"{synth}\" ({len(synth.split())} palabras)")
            generated_count += 1
        else:
            print(f"{i}. (No se pudo converger en frase original en este ciclo)")
    print("------------------------------------------------------------------\n")

    if generated_count < 3:
        print("ADVERTENCIA: La tasa de generación fue menor a la óptima. El corpus puede ser muy reducido.")
        sys.exit(1)

    print(f"✔ MARKOV OPERATIVO: {generated_count}/5 aforismos sintéticos generados con éxito.")


if __name__ == "__main__":
    main()
