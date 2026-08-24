"""Fila de publicação: processa vários ContentPieces sem deixar uma falha
isolada travar o lote inteiro (importante para automação sem supervisão).
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from fifa_content_engine.content_engine.content_piece import ContentPiece

from .errors import PublishingError
from .publisher import VideoPublisher


@dataclass(frozen=True)
class PublishResult:
    """Resultado da tentativa de publicação de um ContentPiece."""

    content_piece: ContentPiece
    success: bool
    url: str | None = None
    error_message: str | None = None


class PublishingQueue:
    """Publica uma sequência de ContentPieces, isolando falhas por item."""

    def __init__(self, publisher: VideoPublisher):
        self.publisher = publisher

    def publish_all(self, content_pieces: Sequence[ContentPiece]) -> list[PublishResult]:
        results = []

        for piece in content_pieces:
            try:
                url = self.publisher.publish(piece)
                results.append(PublishResult(content_piece=piece, success=True, url=url))
            except PublishingError as exc:
                results.append(
                    PublishResult(content_piece=piece, success=False, error_message=str(exc))
                )

        return results
