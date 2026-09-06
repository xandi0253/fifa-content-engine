"""Monta os metadados do vídeo (título, descrição, tags, privacidade) a
partir de um ContentPiece, no formato esperado pela YouTube Data API v3.
"""

from __future__ import annotations

from fifa_content_engine.content_engine.content_piece import ContentPiece

YOUTUBE_TITLE_MAX_LENGTH = 100
DEFAULT_PRIVACY_STATUS = "public"

# Categoria "Gaming" no YouTube Data API v3 -- genérica para qualquer jogo.
GAMING_CATEGORY_ID = "20"

BASE_TAGS = ["gameplay", "highlights", "gaming"]

MOMENT_TAGS: dict[str, list[str]] = {
    "vitoria": ["vitoria"],
    "comemoracao": ["comemoracao"],
    "quase": ["quase la"],
    "acao_intensa": ["acao intensa"],
    "falha": [],
    "outro": [],
}


def build_video_metadata(
    content_piece: ContentPiece,
    privacy_status: str = DEFAULT_PRIVACY_STATUS,
    game_name: str | None = None,
    category_id: str = GAMING_CATEGORY_ID,
) -> dict:
    """Retorna o dict de metadados no formato do corpo `snippet`/`status`
    esperado por `youtube.videos().insert()`.

    game_name (opcional) adiciona o nome do jogo como tag extra.
    category_id (opcional) permite usar outra categoria (ex: Sports, "17",
    se preferir para conteúdo de futebol especificamente).
    """
    moment = content_piece.moment
    title = moment.title[:YOUTUBE_TITLE_MAX_LENGTH]
    tags = BASE_TAGS + ([game_name] if game_name else []) + MOMENT_TAGS.get(moment.moment_type, [])

    return {
        "snippet": {
            "title": title,
            "description": content_piece.caption,
            "tags": tags,
            "categoryId": category_id,
        },
        "status": {
            "privacyStatus": privacy_status,
        },
    }
