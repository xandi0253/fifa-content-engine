"""Orquestra a geração de conteúdo, corte, legenda e contexto editorial."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from pathlib import Path

from fifa_content_engine.ai_engine.moments import Moment
from fifa_content_engine.video_engine.ffprobe import probe

from .caption import build_caption
from .captioning import burn_caption
from .clip_extraction import extract_clip
from .content_piece import ContentPiece
from .context_window import ContextWindow, compute_context_window


class ContentGenerator:
    """Gera um ContentPiece (clipe + legenda) para cada Moment relevante."""

    def __init__(self, output_dir: Path, game_name: str | None = None, burn_captions: bool = False):
        self.output_dir = output_dir
        self.game_name = game_name
        self.burn_captions = burn_captions

    def generate(
        self,
        video_path: Path,
        moments: Sequence[Moment],
        context_windows: Mapping[float, ContextWindow] | None = None,
    ) -> list[ContentPiece]:
        """Gera clipes usando contexto refinado quando fornecido.

        Sem ``context_windows`` o comportamento permanece idêntico ao anterior.
        """
        relevant_moments = [m for m in moments if m.is_relevant]
        if not relevant_moments:
            return []

        video_duration = probe(video_path).duration_seconds
        pieces = []
        for index, moment in enumerate(relevant_moments):
            context = (context_windows or {}).get(moment.timestamp_seconds)
            context = context or compute_context_window(moment)
            start = max(0.0, moment.timestamp_seconds - context.before_seconds)
            end = min(video_duration, moment.timestamp_seconds + context.after_seconds)

            clip_name = f"{video_path.stem}_moment_{index}_{moment.moment_type}"
            clip_path = extract_clip(video_path, start, end, self.output_dir, clip_name)

            if self.burn_captions:
                captioned_path = self.output_dir / f"{clip_name}_captioned.mp4"
                clip_path = burn_caption(clip_path, moment.title, captioned_path)

            caption = build_caption(moment, game_name=self.game_name)
            pieces.append(ContentPiece(moment=moment, clip_path=clip_path, caption=caption))

        return pieces
