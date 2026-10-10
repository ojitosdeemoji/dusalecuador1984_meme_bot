"""Script de certificación final y auditoría integral de arquitectura del sistema."""

import json
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

REQUIRED_FILES = [
    # Configuración y dependencias
    "README.md",
    ".gitignore",
    "requirements.txt",
    # Persistencia e insumos
    "data/state.json",
    "data/corpus.pdf",
    "data/x_allowlist.json",
    # Documentación
    "docs/x_policy.md",
    "docs/editorial_schedule.md",
    "docs/operations_manual.md",
    # Módulos del núcleo (src)
    "src/state_manager.py",
    "src/text_processor.py",
    "src/image_composer.py",
    "src/publisher.py",
    "src/x_config.py",
    "src/x_scraper.py",
    "src/image_source.py",
    "src/metrics_collector.py",
    "src/scoring.py",
    "src/markov_generator.py",
    "src/decision_engine.py",
    # Suites de pruebas (tests)
    "tests/test_core.py",
    "tests/test_state_duplication.py",
    "tests/test_allowlist.py",
    "tests/test_fallback.py",
    "tests/test_metrics.py",
    "tests/test_metrics_persistence.py",
    "tests/test_scoring.py",
    "tests/test_markov.py",
    "tests/test_decision_engine.py",
    "tests/test_health_check.py",
    # Workflows principales (.github/workflows)
    ".github/workflows/publish.yml",
    ".github/workflows/metrics.yml",
    ".github/workflows/validate.yml",
    ".github/workflows/health_check.yml",
]


def audit_system_structure() -> None:
    print("=======================================================")
    print("      AUDITORÍA MAESTRA DE CERTIFICACIÓN DE SISTEMA    ")
    print("=======================================================\n")

    # 1. Comprobación de existencia de archivos
    print("[1/4] Verificando árbol de archivos y módulos...")
    missing = []
    for rel_path in REQUIRED_FILES:
        full_path = ROOT_DIR / rel_path
        if not full_path.exists():
            missing.append(rel_path)

    if missing:
        print("ERROR CRÍTICO: Faltan archivos requeridos en el repositorio:")
        for m in missing:
            print(f"  ❌ {m}")
        sys.exit(1)
    print(f"  ✔ Todos los {len(REQUIRED_FILES)} archivos esenciales están presentes.\n")

    # 2. Comprobación de catálogo local de imágenes
    print("[2/4] Verificando catálogo local de contingencia (fallback)...")
    images_dir = ROOT_DIR / "data" / "images"
    valid_ext = {".jpg", ".jpeg", ".png", ".webp"}
    images = [f for f in images_dir.iterdir() if f.is_file() and f.suffix.lower() in valid_ext]
    if not images:
        print("ERROR: data/images/ no contiene archivos de imagen válidos.")
        sys.exit(1)
    print(f"  ✔ Catálogo local operativo con {len(images)} imágenes disponibles.\n")

    # 3. Comprobación de integridad de estado (state.json)
    print("[3/4] Verificando memoria persistente (state.json)...")
    state_file = ROOT_DIR / "data" / "state.json"
    try:
        with open(state_file, "r", encoding="utf-8") as f:
            state = json.load(f)
    except Exception as exc:
        print(f"ERROR: No se pudo leer state.json: {exc}")
        sys.exit(1)

    required_keys = ["version", "published", "used_phrase_hashes", "used_image_hashes"]
    for k in required_keys:
        if k not in state:
            print(f"ERROR: Falta la clave obligatoria '{k}' en state.json.")
            sys.exit(1)

    published_count = len(state["published"])
    phrases_count = len(state["used_phrase_hashes"])
    images_count = len(state["used_image_hashes"])
    print(f"  ✔ Esquema íntegro (v{state['version']}).")
    print(f"  ✔ Obras publicadas asentadas: {published_count}")
    print(f"  ✔ Hashes de frases excluidas: {phrases_count}")
    print(f"  ✔ Hashes de imágenes excluidas: {images_count}\n")

    # 4. Comprobación de la lista blanca de X
    print("[4/4] Verificando lista blanca (x_allowlist.json)...")
    allowlist_file = ROOT_DIR / "data" / "x_allowlist.json"
    try:
        with open(allowlist_file, "r", encoding="utf-8") as f:
            allowlist = json.load(f)
        active_accounts = [a["username"] for a in allowlist.get("accounts", []) if a.get("enabled")]
    except Exception as exc:
        print(f"ERROR: No se pudo procesar x_allowlist.json: {exc}")
        sys.exit(1)

    print(f"  ✔ Cuentas autorizadas activas: {len(active_accounts)} ({', '.join(['@' + u for u in active_accounts])})\n")

    print("=======================================================")
    print("  CERTIFICACIÓN EXITOSA: SISTEMA EN CONDICIÓN DE VUELO  ")
    print("=======================================================")


if __name__ == "__main__":
    audit_system_structure()
