"""Busca estatísticas reais de vídeos publicados no TikTok (views, likes, comentários).

Limitação conhecida: esta função exige o video_id definitivo do TikTok,
não o publish_id que o TikTokPublisher retorna hoje (ver docs/SPRINT-7.md).
A Content Posting API não garante esse video_id no fluxo de status atual
— capturar isso é um bom próximo passo, fora do escopo desta sprint.
"""

from __future__ import annotations

import requests

from .errors import TikTokUploadError

API_BASE_URL = "https://open.tiktokapis.com/v2"
QUERY_ENDPOINT = f"{API_BASE_URL}/video/query/"
REQUEST_TIMEOUT_SECONDS = 30

STATS_FIELDS = "id,view_count,like_count,comment_count,share_count"


def get_video_stats(video_id: str, access_token: str) -> dict:
    """Retorna view_count, like_count, comment_count e share_count do vídeo."""
    response = requests.post(
        QUERY_ENDPOINT,
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json; charset=UTF-8",
        },
        params={"fields": STATS_FIELDS},
        json={"filters": {"video_ids": [video_id]}},
        timeout=REQUEST_TIMEOUT_SECONDS,
    )
    data = response.json()
    error = data.get("error", {})

    if response.status_code != 200 or error.get("code") != "ok":
        raise TikTokUploadError(f"Falha ao buscar estatísticas do vídeo {video_id}: {data}")

    videos = data.get("data", {}).get("videos", [])
    if not videos:
        raise TikTokUploadError(f"Vídeo {video_id} não encontrado no TikTok")

    video = videos[0]

    return {
        "view_count": video.get("view_count", 0),
        "like_count": video.get("like_count", 0),
        "comment_count": video.get("comment_count", 0),
        "share_count": video.get("share_count", 0),
    }
