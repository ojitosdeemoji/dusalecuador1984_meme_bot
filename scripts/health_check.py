"""Monitor integral de salud del sistema, insumos y autonomía (Health Check)."""

import json
import sys
from pathlib import Path
from typing import Any, Dict

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.state_manager import load_state
from src.text_processor import extract_phrases_from_pdf
from src.x_config import get_active_usernames
from src.scoring import get_learning_phase

DAILY_POSTS_CADENCE = 3


def evaluate_system_health(
    state_path: Path,
    pdf_path: Path,
    images_dir: Path,
    allowlist_path: Path,
) -> Dict[str, Any]:
    """Evalúa métricas de salud, redundancia e insumos del bot."""
    state = load_state(state_path)
    published = state.get("published", [])
    used_phrases = set(state.get("used_phrase_hashes", []))
    used_images = set(state.get("used_image_hashes", []))

    # 1. Análisis de corpus textual
    all_sentences = extract_phrases_from_pdf(pdf_path) if pdf_path.exists() else []
    remaining_literal = max(0, len(all_sentences) - len(used_phrases))

    # Con síntesis de Markov, la autonomía textual es prácticamente ilimitada,
    # pero calculamos los días de frases literales garantizadas:
    days_literal_autonomy = round(remaining_literal / DAILY_POSTS_CADENCE, 1) if DAILY_POSTS_CADENCE > 0 else 0

    # 2. Análisis de catálogo de imágenes locales
    valid_ext = {".jpg", ".jpeg", ".png", ".webp"}
    local_images = [
        f for f in images_dir.iterdir()
        if f.is_file() and f.suffix.lower() in valid_ext
    ] if images_dir.exists() else []

    # 3. Análisis de allowlist
    active_x_users = get_active_usernames(allowlist_path) if allowlist_path.exists() else []

    # 4. Fase de aprendizaje
    phase_name, phase_desc = get_learning_phase(len(published))

    # 5. Determinación del estado general
    alerts = []
    if remaining_literal < 15:
        alerts.append("AVISO: Menos de 15 frases literales restantes en el PDF. Se recomienda agregar más texto o confiar en Markov.")
    if len(local_images) < 2:
        alerts.append("ALERTA: Menos de 2 imágenes en el catálogo local de reserva.")
    if not active_x_users:
        alerts.append("AVISO: No hay cuentas activas en la allowlist de X.")

    status = "OK (Saludable)" if not alerts else "ATENCIÓN (Advertencias detectadas)"

    return {
        "status": status,
        "published_total": len(published),
        "learning_phase": phase_name,
        "learning_desc": phase_desc,
        "corpus_total_sentences": len(all_sentences),
        "corpus_used_phrases": len(used_phrases),
        "corpus_remaining_literal": remaining_literal,
        "estimated_literal_days": days_literal_autonomy,
        "local_images_count": len(local_images),
        "local_images_used": len(used_images),
        "active_x_sources": len(active_x_users),
        "last_metrics_refresh": state.get("last_metrics_refresh", "Nunca"),
        "alerts": alerts,
    }


def main() -> None:
    print("[HEALTH CHECK] Iniciando auditoría de salud del sistema...")

    state_file = ROOT_DIR / "data" / "state.json"
    pdf_file = ROOT_DIR / "data" / "corpus.pdf"
    images_dir = ROOT_DIR / "data" / "images"
    allowlist_file = ROOT_DIR / "data" / "x_allowlist.json"

    health = evaluate_system_health(state_file, pdf_file, images_dir, allowlist_file)

    print(f"\n--- DIAGNÓSTICO GENERAL: {health['status']} ---")
    print(f"- Publicaciones totales acumuladas: {health['published_total']}")
    print(f"- Fase de aprendizaje: {health['learning_phase']}")
    print(f"- Frases literales restantes en PDF: {health['corpus_remaining_literal']} (~{health['estimated_literal_days']} días de publicaciones)")
    print(f"- Generador Markov: Habilitado (autonomía combinatoria complementaria)")
    print(f"- Imágenes locales de reserva: {health['local_images_count']}")
    print(f"- Cuentas activas en allowlist de X: {health['active_x_sources']}")
    print(f"- Último refresco de métricas: {health['last_metrics_refresh']}")

    if health["alerts"]:
        print("\nADVERTENCIAS DEL SISTEMA:")
        for a in health["alerts"]:
            print(f"  ⚠ {a}")
    else:
        print("\n✔ Todos los subsistemas operan dentro de los umbrales normales.")
    print("--------------------------------------------------\n")

    # Generar Step Summary
    summary_path = ROOT_DIR / "health_summary.md"
    alerts_block = "\n".join([f"- ⚠️ {a}" for a in health["alerts"]]) if health["alerts"] else "- ✔ Ninguna advertencia registrada."

    content = f"""## Reporte de Salud y Autonomía del Sistema (Health Check)

**Estado General:** `{health['status']}`

### 1. Indicadores de Publicación y Aprendizaje
- **Total de obras publicadas:** `{health['published_total']}`
- **Fase de aprendizaje:** `{health['learning_phase']}`
- **Cadencia programada:** `3 publicaciones diarias` (11:20, 17:20, 23:20 UTC)
- **Última sincronización de métricas:** `{health['last_metrics_refresh']}`

### 2. Capacidad de Insumos y Autonomía Restante
- **Oraciones literales en PDF:** `{health['corpus_remaining_literal']}` restantes de `{health['corpus_total_sentences']}`
- **Autonomía literal estimada:** `~{health['estimated_literal_days']} días`
- **Generación sintética (Markov):** `Operativa` (expansión combinatoria continua)
- **Catálogo local de reserva:** `{health['local_images_count']}` imágenes
- **Cuentas habilitadas en X:** `{health['active_x_sources']}` cuentas

### 3. Diagnóstico y Alertas
{alerts_block}
"""
    summary_path.write_text(content, encoding="utf-8")
    print(f"[HEALTH CHECK] Informe escrito en {summary_path.name}.")


if __name__ == "__main__":
    main()
