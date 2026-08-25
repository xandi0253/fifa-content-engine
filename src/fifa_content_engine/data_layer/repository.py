"""Repositório do pipeline: registra partidas, clipes e publicações.

Esta camada não depende de video_engine/ai_engine/content_engine/
publishing_engine — são esses módulos que chamam o repositório para
persistir o que produzem (a dependência vai na direção contrária,
mantendo o Data Layer como uma camada de base).
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from pathlib import Path

from .json_store import JSONStore

MATCHES_TABLE = "matches"
CLIPS_TABLE = "clips"
PUBLICATIONS_TABLE = "publications"


def _new_id() -> str:
    return uuid.uuid4().hex[:12]


def _now_iso() -> str:
    return datetime.now(UTC).isoformat()


class PipelineRepository:
    """Registra os resultados de cada etapa do pipeline em um JSONStore."""

    def __init__(self, data_dir: Path):
        self.store = JSONStore(data_dir)

    def record_match(self, video_path: str, duration_seconds: float, scene_count: int) -> str:
        """Registra um vídeo processado pelo Video Engine. Retorna o match_id."""
        match_id = _new_id()
        self.store.append(
            MATCHES_TABLE,
            {
                "id": match_id,
                "video_path": video_path,
                "duration_seconds": duration_seconds,
                "scene_count": scene_count,
                "processed_at": _now_iso(),
            },
        )
        return match_id

    def record_clip(
        self,
        match_id: str,
        timestamp_seconds: float,
        moment_type: str,
        score: float,
        title: str,
        description: str,
        clip_path: str,
        caption: str,
    ) -> str:
        """Registra um clipe gerado pelo Content Engine. Retorna o clip_id."""
        clip_id = _new_id()
        self.store.append(
            CLIPS_TABLE,
            {
                "id": clip_id,
                "match_id": match_id,
                "timestamp_seconds": timestamp_seconds,
                "moment_type": moment_type,
                "score": score,
                "title": title,
                "description": description,
                "clip_path": clip_path,
                "caption": caption,
                "created_at": _now_iso(),
            },
        )
        return clip_id

    def record_publication(
        self,
        clip_id: str,
        platform: str,
        success: bool,
        url: str | None = None,
        error_message: str | None = None,
    ) -> str:
        """Registra o resultado de uma tentativa de publicação. Retorna o id do registro."""
        publication_id = _new_id()
        self.store.append(
            PUBLICATIONS_TABLE,
            {
                "id": publication_id,
                "clip_id": clip_id,
                "platform": platform,
                "success": success,
                "url": url,
                "error_message": error_message,
                "published_at": _now_iso(),
            },
        )
        return publication_id

    def all_matches(self) -> list[dict]:
        return self.store.read_all(MATCHES_TABLE)

    def all_clips(self) -> list[dict]:
        return self.store.read_all(CLIPS_TABLE)

    def all_publications(self) -> list[dict]:
        return self.store.read_all(PUBLICATIONS_TABLE)
