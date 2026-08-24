"""Hospedagem de mídia: contrato para expor um clipe local em uma URL pública.

A API do Instagram não aceita upload direto de arquivo — ela exige uma
URL pública de onde possa baixar o vídeo. Esta interface é o ponto de
extensão para plugar o serviço de hospedagem escolhido (S3, Cloudflare
R2, etc.). Nenhuma implementação concreta é fornecida nesta sprint —
a hospedagem real fica para configurar depois.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path


class MediaHoster(ABC):
    """Contrato para qualquer hospedeiro de mídia do pipeline."""

    @abstractmethod
    def host(self, clip_path: Path) -> str:
        """Hospeda o clipe local e retorna uma URL pública para acessá-lo."""
