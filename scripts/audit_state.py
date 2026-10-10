"""Script de auditoría técnica e integridad de state.json."""

import json
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.state_manager import load_state


def main() -> None:
    state_path = ROOT_DIR / "data" / "state.json"
    print(f"[AUDITORÍA] Verificando archivo de persistencia: {state_path}")

    if not state_path.exists():
        print(f"ERROR: No se encontró el archivo de estado en {state_path}")
        sys.exit(1)

    state = load_state(state_path)

    # 1. Validar esquema
    required_keys = ["version", "published", "used_phrase_hashes", "used_image_hashes"]
    for key in required_keys:
        if key not in state:
            print(f"ERROR CRÍTICO: Clave obligatoria '{key}' ausente en state.json.")
            sys.exit(1)

    published = state["published"]
    used_phrases = state["used_phrase_hashes"]
    used_images = state["used_image_hashes"]

    print(f"[ESTADO] Versión de esquema: {state['version']}")
    print(f"[ESTADO] Total de publicaciones registradas: {len(published)}")
    print(f"[ESTADO] Hashes de frases almacenados: {len(used_phrases)}")
    print(f"[ESTADO] Hashes de imágenes almacenados: {len(used_images)}")

    # 2. Comprobar integridad y unicidad de listas
    if len(used_phrases) != len(set(used_phrases)):
        print("ERROR: Se detectaron hashes de frases duplicados dentro de 'used_phrase_hashes'.")
        sys.exit(1)

    if len(used_images) != len(set(used_images)):
        print("ERROR: Se detectaron hashes de imágenes duplicados dentro de 'used_image_hashes'.")
        sys.exit(1)

    # 3. Mostrar detalle de publicaciones realizadas
    print("\n--- HISTORIAL DE PUBLICACIONES EN BLUESKY ---")
    for index, entry in enumerate(published, start=1):
        p_text = entry.get("phrase_text", "(Sin texto guardado)")
        url = entry.get("post_url", "(Sin URL)")
        date = entry.get("published_at", "(Sin fecha)")
        img_name = entry.get("source_file", "(Desconocida)")
        print(f"Post #{index} | Fecha: {date}")
        print(f"  - Frase: \"{p_text}\"")
        print(f"  - Imagen: {img_name}")
        print(f"  - Enlace: {url}")
        print(f"  - Hash frase: {entry.get('phrase_hash', '')[:12]}...")
        print(f"  - Hash imagen: {entry.get('image_hash', '')[:12]}...")
    print("----------------------------------------------\n")

    print("✔ AUDITORÍA SUPERADA: La estructura de persistencia es íntegra y consistente.")


if __name__ == "__main__":
    main()
