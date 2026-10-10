"""Script de verificación segura de autenticación con Bluesky."""

import os
import sys
from atproto import Client


def main() -> None:
    print("[AUTH] Verificando credenciales de Bluesky...")

    handle = os.getenv("BSKY_HANDLE")
    app_password = os.getenv("BSKY_APP_PASSWORD")

    if not handle or not handle.strip():
        print("ERROR CRÍTICO: La variable de entorno BSKY_HANDLE no está configurada o está vacía.")
        sys.exit(1)

    if not app_password or not app_password.strip():
        print("ERROR CRÍTICO: La variable de entorno BSKY_APP_PASSWORD no está configurada o está vacía.")
        sys.exit(1)

    clean_handle = handle.strip().lstrip("@")
    clean_password = app_password.strip()

    client = Client()

    try:
        profile = client.login(clean_handle, clean_password)
    except Exception as exc:
        print(f"ERROR DE AUTENTICACIÓN: No se pudo iniciar sesión en Bluesky: {exc}")
        print("Verifique que BSKY_HANDLE no contenga errores y que BSKY_APP_PASSWORD sea una App Password activa.")
        sys.exit(1)

    # Confirmación segura sin exponer credenciales
    print("✔ CONEXIÓN EXITOSA CON BLUESKY")
    print(f"[AUTH] Handle verificado: @{profile.handle}")
    print(f"[AUTH] Nombre visible: {profile.display_name if profile.display_name else '(Sin nombre visible)'}")
    print(f"[AUTH] DID registrado: {profile.did}")
    print("[AUTH] Las credenciales son válidas y el cliente está listo para publicar.")


if __name__ == "__main__":
    main()
