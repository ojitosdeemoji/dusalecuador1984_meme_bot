"""Script de validación e informe de la lista blanca de X."""

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.x_config import load_allowlist, get_active_usernames


def main() -> None:
    allowlist_path = ROOT_DIR / "data" / "x_allowlist.json"
    print(f"[ALLOWLIST] Verificando lista blanca de fuentes: {allowlist_path}")

    try:
        data = load_allowlist(allowlist_path)
    except Exception as exc:
        print(f"ERROR CRÍTICO: Archivo de allowlist corrupto o inválido: {exc}")
        sys.exit(1)

    total_declared = len(data.get("accounts", []))
    active_users = get_active_usernames(allowlist_path)

    print(f"[ALLOWLIST] Cuentas declaradas en catálogo: {total_declared}")
    print(f"[ALLOWLIST] Cuentas activas y habilitadas: {len(active_users)}")

    if not active_users:
        print("ERROR: No hay ninguna cuenta activa y válida en data/x_allowlist.json.")
        print("Debe haber al menos 1 cuenta con 'enabled': true y un formato válido de username.")
        sys.exit(1)

    print("\n--- CUENTAS AUTORIZADAS PARA EXTRACCIÓN ---")
    for index, user in enumerate(active_users, start=1):
        print(f"{index}. @{user} (https://x.com/{user})")
    print("-------------------------------------------\n")

    print("✔ ALLOWLIST VALIDADA: Las fuentes están delimitadas y listas para el conector.")


if __name__ == "__main__":
    main()
