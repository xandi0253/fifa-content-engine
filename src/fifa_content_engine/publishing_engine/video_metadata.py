"""Monta os metadados do vídeo (título, descrição, tags, privacidade) a
partir de um ContentPiece, no formato esperado pela YouTube Data API v3.
"""

from __future__ import annotations

from fifa_content_engine.content_engine.content_piece import ContentPiece

YOUTUBE_TITLE_MAX_LENGTH = 100
DEFAULT_PRIVACY_STATUS = "public"

# Categoria "Sports" no YouTube Data API v3.
SPORTS_CATEGORY_ID = "17"

BASE_TAGS = ["FIFA26", "futebol", "highlights"]

MOMENT_TAGS: dict[str, list[str]] = {
    "gol": ["gol", "golaço"],
    "comemoracao": ["comemoracao"],
    "lance_perigoso": ["lance perigoso"],
    "defesa": ["defesa"],
    "falta": ["falta"],
    "outro": [],
}


def build_video_metadata(
    content_piece: ContentPiece, privacy_status: str = DEFAULT_PRIVACY_STATUS
) -> dict:
    """Retorna o dict de metadados no formato do corpo `snippet`/`status`
    esperado por `youtube.videos().insert()`.
    """
    moment = content_piece.moment
    title = moment.title[:YOUTUBE_TITLE_MAX_LENGTH]
    tags = BASE_TAGS + MOMENT_TAGS.get(moment.moment_type, [])

    return {
        "snippet": {
            "title": title,
            "description": content_piece.caption,
            "tags": tags,
            "categoryId": SPORTS_CATEGORY_ID,
        },
        "status": {
            "privacyStatus": privacy_status,
        },
    }
