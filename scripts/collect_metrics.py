"""Script de recopilación e informe de métricas de publicaciones en Bluesky."""

from datetime import datetime, timezone
import os
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.state_manager import load_state, save_state, update_published_metrics
from src.metrics_collector import fetch_posts_metrics, calculate_age_hours


def main() -> None:
    print("[MÉTRICAS] Iniciando recolección de engagement en Bluesky...")

    state_path = ROOT_DIR / "data" / "state.json"
    if not state_path.exists():
        print("ERROR: No existe el archivo data/state.json.")
        sys.exit(1)

    state = load_state(state_path)
    published = state.get("published", [])

    if not published:
        print("AVISO: No hay publicaciones registradas en state.json.")
        sys.exit(0)

    # Filtrar entradas que posean URI válida
    uris = [entry["uri"] for entry in published if entry.get("uri")]
    print(f"[MÉTRICAS] Publicaciones encontradas: {len(published)} (Con URI: {len(uris)})")

    if not uris:
        print("AVISO: Ninguna publicación tiene URI registrada para consultar.")
        sys.exit(0)

    try:
        metrics_by_uri = fetch_posts_metrics(uris)
    except Exception as exc:
        print(f"ERROR al consultar la API de Bluesky: {exc}")
        sys.exit(1)

    print(f"[MÉTRICAS] Métricas recuperadas exitosamente para {len(metrics_by_uri)} publicaciones.")

    # 1. Persistir métricas en data/state.json
    now_iso = datetime.now(timezone.utc).isoformat()
    updated_count = update_published_metrics(state, metrics_by_uri, now_iso)
    save_state(state_path, state)
    print(f"[MÉTRICAS] Persistencia completada: {updated_count} entradas actualizadas en {state_path.name}.")

    # 2. Construir informe Markdown para GitHub Actions
    summary_path = ROOT_DIR / "metrics_summary.md"
    rows = []

    print("\n--- RESUMEN ACTUALIZADO DE ENGAGEMENT (PERSISTIDO) ---")
    for idx, entry in enumerate(published, start=1):
        uri = entry.get("uri", "")
        post_metrics = metrics_by_uri.get(uri, {"likes": 0, "reposts": 0, "replies": 0, "quotes": 0})
        age_hours = calculate_age_hours(entry.get("published_at", ""))
        url = entry.get("post_url", "(Sin URL)")
        phrase = entry.get("phrase_text", "Texto no registrado")
        short_phrase = phrase[:35] + ("..." if len(phrase) > 35 else "")

        likes = post_metrics["likes"]
        reposts = post_metrics["reposts"]
        replies = post_metrics["replies"]
        quotes = post_metrics["quotes"]

        print(f"Post #{idx} | Antigüedad: {age_hours:.1f}h | Likes: {likes} | Reposts: {reposts} | Respuestas: {replies} | Citas: {quotes}")
        print(f"  Frase: \"{short_phrase}\"")
        print(f"  URL: {url}")

        rows.append(
            f"| #{idx} | [{short_phrase}]({url}) | {age_hours:.1f}h | {likes} | {reposts} | {replies} | {quotes} |"
        )
    print("------------------------------------------------------\n")

    markdown_content = f"""## Reporte de Métricas Persistidas en el Estado

- **Total de publicaciones consultadas:** {len(published)}
- **Entradas actualizadas en state.json:** {updated_count}
- **Última sincronización:** `{now_iso}`
- **Protocolo:** AT Protocol (\`app.bsky.feed.getPosts\`)

| # | Publicación | Antigüedad | Likes | Reposts | Respuestas | Citas |
|---|---|---|---|---|---|---|
""" + "\n".join(rows) + "\n"

    summary_path.write_text(markdown_content, encoding="utf-8")
    print(f"✔ REPORTE GENERADO: Informe guardado en {summary_path.name}.")


if __name__ == "__main__":
    main()
