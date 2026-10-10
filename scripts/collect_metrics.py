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
from src.scoring import (
    calculate_raw_score,
    calculate_normalized_score,
    get_learning_phase,
)


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

    # 1. Actualizar métricas crudas en el estado
    now_iso = datetime.now(timezone.utc).isoformat()
    update_published_metrics(state, metrics_by_uri, now_iso)

    # 2. Calcular y asignar el score normalizado a cada publicación
    for entry in published:
        likes = entry.get("likes", 0)
        reposts = entry.get("reposts", 0)
        replies = entry.get("replies", 0)
        quotes = entry.get("quotes", 0)
        age = calculate_age_hours(entry.get("published_at", ""))

        raw_score = calculate_raw_score(likes, reposts, replies, quotes)
        norm_score = calculate_normalized_score(raw_score, age)
        entry["score"] = norm_score

    # 3. Guardar estado con scores persistidos
    save_state(state_path, state)
    print(f"[MÉTRICAS] Scores calculados y guardados en {state_path.name}.")

    phase_name, phase_desc = get_learning_phase(len(published))

    # 4. Construir informe Markdown para GitHub Actions
    summary_path = ROOT_DIR / "metrics_summary.md"
    rows = []

    print("\n--- RESUMEN ACTUALIZADO DE ENGAGEMENT Y SCORE ---")
    for idx, entry in enumerate(published, start=1):
        age_hours = calculate_age_hours(entry.get("published_at", ""))
        url = entry.get("post_url", "(Sin URL)")
        phrase = entry.get("phrase_text", "Texto no registrado")
        short_phrase = phrase[:30] + ("..." if len(phrase) > 30 else "")

        likes = entry.get("likes", 0)
        reposts = entry.get("reposts", 0)
        replies = entry.get("replies", 0)
        quotes = entry.get("quotes", 0)
        score = entry.get("score", 0.0)

        print(f"Post #{idx} | Score: {score:.3f} | Antigüedad: {age_hours:.1f}h | Likes: {likes} | Reposts: {reposts} | Respuestas: {replies}")
        rows.append(
            f"| #{idx} | [{short_phrase}]({url}) | {age_hours:.1f}h | {likes} | {reposts} | {replies} | {quotes} | **{score:.3f}** |"
        )
    print("--------------------------------------------------\n")

    markdown_content = f"""## Reporte de Métricas y Scoring de Obras

- **Total de publicaciones:** {len(published)}
- **Fase de Aprendizaje Artístico:** `{phase_name}`
  > *{phase_desc}*
- **Fórmula de ponderación:** `Likes + (2 × Reposts) + (3 × Respuestas) + (2 × Citas)` corregido por `√(horas / 12)`
- **Última sincronización:** `{now_iso}`

| # | Publicación | Antigüedad | Likes | Reposts | Respuestas | Citas | Score Normalizado |
|---|---|---|---|---|---|---|---|
""" + "\n".join(rows) + "\n"

    summary_path.write_text(markdown_content, encoding="utf-8")
    print(f"✔ REPORTE GENERADO: Informe guardado en {summary_path.name}.")


if __name__ == "__main__":
    main()
