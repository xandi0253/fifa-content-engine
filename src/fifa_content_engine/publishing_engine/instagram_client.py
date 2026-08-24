"""Wrapper fino em torno da Instagram Graph API (contêiner de mídia + publicação).

Fluxo de publicação de um Reel:
  1. create_media_container(): cria um contêiner apontando para a URL do vídeo
  2. get_container_status(): consulta até o contêiner ficar pronto (FINISHED)
  3. publish_container(): publica o contêiner pronto, virando um post de verdade
  4. get_media_permalink(): busca a URL pública do post publicado
"""

from __future__ import annotations

import requests

from .errors import InstagramUploadError

GRAPH_API_BASE_URL = "https://graph.facebook.com/v19.0"
REQUEST_TIMEOUT_SECONDS = 30


def create_media_container(ig_user_id: str, access_token: str, video_url: str, caption: str) -> str:
    """Cria um contêiner de mídia do tipo Reels e retorna seu id."""
    response = requests.post(
        f"{GRAPH_API_BASE_URL}/{ig_user_id}/media",
        data={
            "media_type": "REELS",
            "video_url": video_url,
            "caption": caption,
            "access_token": access_token,
        },
        timeout=REQUEST_TIMEOUT_SECONDS,
    )
    data = response.json()

    if response.status_code != 200 or "id" not in data:
        raise InstagramUploadError(f"Falha ao criar contêiner de mídia no Instagram: {data}")

    return data["id"]


def get_container_status(container_id: str, access_token: str) -> str:
    """Retorna o status_code atual do contêiner (ex: IN_PROGRESS, FINISHED, ERROR)."""
    response = requests.get(
        f"{GRAPH_API_BASE_URL}/{container_id}",
        params={"fields": "status_code", "access_token": access_token},
        timeout=REQUEST_TIMEOUT_SECONDS,
    )
    data = response.json()

    if response.status_code != 200 or "status_code" not in data:
        raise InstagramUploadError(f"Falha ao consultar status do contêiner no Instagram: {data}")

    return data["status_code"]


def publish_container(ig_user_id: str, access_token: str, container_id: str) -> str:
    """Publica um contêiner já pronto (FINISHED) e retorna o id da mídia publicada."""
    response = requests.post(
        f"{GRAPH_API_BASE_URL}/{ig_user_id}/media_publish",
        data={"creation_id": container_id, "access_token": access_token},
        timeout=REQUEST_TIMEOUT_SECONDS,
    )
    data = response.json()

    if response.status_code != 200 or "id" not in data:
        raise InstagramUploadError(f"Falha ao publicar contêiner no Instagram: {data}")

    return data["id"]


def get_media_permalink(media_id: str, access_token: str) -> str:
    """Busca a URL pública (permalink) da mídia publicada."""
    response = requests.get(
        f"{GRAPH_API_BASE_URL}/{media_id}",
        params={"fields": "permalink", "access_token": access_token},
        timeout=REQUEST_TIMEOUT_SECONDS,
    )
    data = response.json()

    if response.status_code != 200 or "permalink" not in data:
        raise InstagramUploadError(f"Falha ao buscar permalink da mídia no Instagram: {data}")

    return data["permalink"]
