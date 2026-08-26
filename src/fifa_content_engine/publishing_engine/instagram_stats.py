"""Busca estatísticas reais de mídias publicadas no Instagram (likes, comentários).

Limitação conhecida: esta função exige o media_id numérico da Graph API,
não o permalink (ex: https://www.instagram.com/reel/<shortcode>/) que o
InstagramPublisher retorna hoje. O modelo de dados atual não guarda o
media_id separadamente — resolver isso (guardar o media_id junto da
publicação) é um bom próximo passo, fora do escopo desta sprint.
"""

from __future__ import annotations

import requests

from .errors import InstagramUploadError

GRAPH_API_BASE_URL = "https://graph.facebook.com/v19.0"
REQUEST_TIMEOUT_SECONDS = 30


def get_media_insights(media_id: str, access_token: str) -> dict:
    """Retorna like_count e comments_count da mídia (requer o media_id numérico)."""
    response = requests.get(
        f"{GRAPH_API_BASE_URL}/{media_id}",
        params={"fields": "like_count,comments_count", "access_token": access_token},
        timeout=REQUEST_TIMEOUT_SECONDS,
    )
    data = response.json()

    if response.status_code != 200 or "like_count" not in data:
        raise InstagramUploadError(f"Falha ao buscar estatísticas da mídia {media_id}: {data}")

    return {
        "like_count": data.get("like_count", 0),
        "comment_count": data.get("comments_count", 0),
    }
