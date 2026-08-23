"""Interface base para ingestão de vídeo.

Esta é apenas a definição do contrato que o Video Engine vai seguir.
A implementação real (FFmpeg, validação de formato, corte de cenas)
entra na Sprint 2.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class VideoSource:
    """Representa um arquivo de vídeo de origem (gravação de partida)."""

    path: Path
    duration_seconds: float | None = None


class VideoIngestor(ABC):
    """Contrato para qualquer ingestor de vídeo do pipeline."""

    @abstractmethod
    def validate(self, source: VideoSource) -> bool:
        """Valida se o arquivo de origem pode ser processado."""

    @abstractmethod
    def prepare(self, source: VideoSource) -> VideoSource:
        """Prepara o vídeo (conversão/normalização) para as próximas etapas."""
