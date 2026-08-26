"""Busca estatísticas reais de vídeos publicados no YouTube (views, likes, comentários)."""

from __future__ import annotations

import re
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from .errors import YouTubeUploadError
from .youtube_auth import get_credentials

_SHORT_URL_PATTERN = re.compile(r"youtu\.be/([\w-]+)")


def extract_video_id(url: str) -> str | None:
    """Extrai o video_id de uma URL do YouTube (formato watch ou encurtado)."""
    parsed = urlparse(url)

    if parsed.hostname in {"www.youtube.com", "youtube.com"}:
        query_params = parse_qs(parsed.query)
        video_ids = query_params.get("v")
        if video_ids:
            return video_ids[0]

    short_match = _SHORT_URL_PATTERN.search(url)
    if short_match:
        return short_match.group(1)

    return None


def get_video_statistics(
    video_id: str,
    client_id: str | None,
    client_secret: str | None,
    token_path: Path,
) -> dict:
    """Retorna view_count, like_count e comment_count do vídeo (como inteiros).

    Reaproveita a mesma autenticação OAuth do YouTubePublisher (Sprint 5).
    """
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError

    credentials = get_credentials(client_id, client_secret, token_path)
    client = build("youtube", "v3", credentials=credentials)

    try:
        response = client.videos().list(part="statistics", id=video_id).execute()
    except HttpError as exc:
        raise YouTubeUploadError(
            f"Falha ao buscar estatísticas do vídeo {video_id}: {exc}"
        ) from exc

    items = response.get("items", [])
    if not items:
        raise YouTubeUploadError(f"Vídeo {video_id} não encontrado no YouTube")

    statistics = items[0].get("statistics", {})

    return {
        "view_count": int(statistics.get("viewCount", 0)),
        "like_count": int(statistics.get("likeCount", 0)),
        "comment_count": int(statistics.get("commentCount", 0)),
    }
