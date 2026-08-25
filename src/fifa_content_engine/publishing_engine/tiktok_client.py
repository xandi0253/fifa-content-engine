"""Wrapper fino em torno da TikTok Content Posting API (Direct Post).

Fluxo de publicação de um vídeo (fonte PULL_FROM_URL):
  1. init_video_post(): inicia a publicação a partir de uma URL pública
     e retorna um publish_id
  2. get_post_status(): consulta o status até ficar PUBLISH_COMPLETE
"""

from __future__ import annotations

import requests

from .errors import TikTokUploadError

API_BASE_URL = "https://open.tiktokapis.com/v2"
INIT_ENDPOINT = f"{API_BASE_URL}/post/publish/video/init/"
STATUS_ENDPOINT = f"{API_BASE_URL}/post/publish/status/fetch/"
REQUEST_TIMEOUT_SECONDS = 30


def init_video_post(access_token: str, video_url: str, title: str, privacy_level: str) -> str:
    """Inicia a publicação de um vídeo a partir de uma URL pública (PULL_FROM_URL).

    Retorna o publish_id usado para consultar o status depois.
    """
    response = requests.post(
        INIT_ENDPOINT,
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json; charset=UTF-8",
        },
        json={
            "post_info": {
                "title": title,
                "privacy_level": privacy_level,
            },
            "source_info": {
                "source": "PULL_FROM_URL",
                "video_url": video_url,
            },
        },
        timeout=REQUEST_TIMEOUT_SECONDS,
    )
    data = response.json()
    error = data.get("error", {})

    if response.status_code != 200 or error.get("code") != "ok":
        raise TikTokUploadError(f"Falha ao iniciar publicação no TikTok: {data}")

    publish_id = data.get("data", {}).get("publish_id")
    if not publish_id:
        raise TikTokUploadError(f"TikTok não retornou publish_id: {data}")

    return publish_id


def get_post_status(access_token: str, publish_id: str) -> dict:
    """Consulta o status da publicação (status, fail_reason, etc.)."""
    response = requests.post(
        STATUS_ENDPOINT,
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json; charset=UTF-8",
        },
        json={"publish_id": publish_id},
        timeout=REQUEST_TIMEOUT_SECONDS,
    )
    data = response.json()
    error = data.get("error", {})

    if response.status_code != 200 or error.get("code") != "ok":
        raise TikTokUploadError(f"Falha ao consultar status da publicação no TikTok: {data}")

    return data.get("data", {})
