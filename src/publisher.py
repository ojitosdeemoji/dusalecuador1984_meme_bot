"""Módulo de publicación y conexión con AT Protocol (Bluesky)."""

import os
from typing import Any, Dict
from atproto import Client, models


def publish_meme_to_bluesky(
    image_bytes: bytes,
    post_text: str,
    alt_text: str,
    width: int,
    height: int,
    handle: str | None = None,
    app_password: str | None = None,
) -> Dict[str, Any]:
    """Publica una composición de meme en Bluesky con metadatos de accesibilidad.

    Devuelve un diccionario con URI, CID, rkey y la URL pública del post.
    """
    user_handle = handle or os.getenv("BSKY_HANDLE")
    user_password = app_password or os.getenv("BSKY_APP_PASSWORD")

    if not user_handle or not user_password:
        raise ValueError("Credenciales de Bluesky no encontradas en el entorno (BSKY_HANDLE, BSKY_APP_PASSWORD).")

    clean_handle = user_handle.strip().lstrip("@")
    client = Client()
    client.login(clean_handle, user_password.strip())

    # Configurar proporción para evitar recortes arbitrarios en la interfaz
    aspect_ratio = models.AppBskyEmbedDefs.AspectRatio(width=width, height=height)

    # Enviar post con imagen incrustada
    response = client.send_image(
        text=post_text,
        image=image_bytes,
        image_alt=alt_text,
        image_aspect_ratio=aspect_ratio,
    )

    uri = response.uri
    cid = response.cid
    rkey = uri.split("/")[-1]
    post_url = f"https://bsky.app/profile/{clean_handle}/post/{rkey}"

    return {
        "uri": uri,
        "cid": cid,
        "rkey": rkey,
        "post_url": post_url,
    }
