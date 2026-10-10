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

    required_keys = ["version", "published", "used_phrase_hashes", "used_image_hashes"]
    for key in required_keys:
        if key not in state:
            print(f"ERROR CRÍTICO: Clave obligatoria '{key}' ausente en state.json.")
            sys.exit(1)

    published = state["published"]
    used_phrases = state["used_phrase_hashes"]
    used_images = state["used_image_hashes"]
    last_refresh = state.get("last_metrics_refresh", "(Nunca sincronizado)")

    print(f"[ESTADO] Versión de esquema: {state['version']}")
    print(f"[ESTADO] Total de publicaciones registradas: {len(published)}")
    print(f"[ESTADO] Hashes de frases almacenados: {len(used_phrases)}")
    print(f"[ESTADO] Hashes de imágenes almacenados: {len(used_images)}")
    print(f"[ESTADO] Último refresco de métricas: {last_refresh}")

    if len(used_phrases) != len(set(used_phrases)):
        print("ERROR: Hashes de frases duplicados dentro de 'used_phrase_hashes'.")
        sys.exit(1)

    if len(used_images) != len(set(used_images)):
        print("ERROR: Hashes de imágenes duplicados dentro de 'used_image_hashes'.")
        sys.exit(1)

    print("\n--- HISTORIAL DE PUBLICACIONES CON MÉTRICAS ---")
    for index, entry in enumerate(published, start=1):
        p_text = entry.get("phrase_text", "(Sin texto guardado)")
        url = entry.get("post_url", "(Sin URL)")
        date = entry.get("published_at", "(Sin fecha)")
        src_type = entry.get("source_type", "local")

        likes = entry.get("likes", 0)
        reposts = entry.get("reposts", 0)
        replies = entry.get("replies", 0)
        quotes = entry.get("quotes", 0)
        m_date = entry.get("metrics_updated_at", "(No actualizado)")

        print(f"Post #{index} | Fecha: {date}")
        print(f"  - Frase: \"{p_text}\"")
        if src_type == "x_twitter":
            author = entry.get("source_author", "Desconocido")
            print(f"  - Fuente: X/Twitter (@{author})")
        else:
            img_file = entry.get("source_file", "(Desconocido)")
            fb = " (Fallback activado)" if entry.get("fallback_activated") else ""
            print(f"  - Fuente: Catálogo Local ({img_file}){fb}")

        print(f"  - Métricas: {likes} likes | {reposts} reposts | {replies} respuestas | {quotes} citas")
        print(f"  - Última actualización métricas: {m_date}")
        print(f"  - Enlace Bluesky: {url}")
    print("------------------------------------------------\n")

    print("✔ AUDITORÍA SUPERADA: Integridad y métricas persistidas correctamente.")


if __name__ == "__main__":
    main()
