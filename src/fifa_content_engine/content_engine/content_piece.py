"""Estrutura de saída do Content Engine: um clipe pronto para publicação."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from fifa_content_engine.ai_engine.moments import Moment


@dataclass(frozen=True)
class ContentPiece:
    """Um Moment já transformado em conteúdo pronto: clipe de vídeo + legenda."""

    moment: Moment
    clip_path: Path
    caption: str
