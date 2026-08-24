"""Interface base para publicadores de conteúdo (contrato do Publishing Engine)."""

from __future__ import annotations

from abc import ABC, abstractmethod

from fifa_content_engine.content_engine.content_piece import ContentPiece


class VideoPublisher(ABC):
    """Contrato para qualquer publicador de vídeo do pipeline."""

    @abstractmethod
    def publish(self, content_piece: ContentPiece) -> str:
        """Publica o clipe e retorna a URL do vídeo publicado."""
