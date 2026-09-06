"""Orquestra a geração de conteúdo: janela de corte, clipe e legenda por Moment."""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

from fifa_content_engine.ai_engine.moments import Moment
from fifa_content_engine.video_engine.ffprobe import probe

from .caption import build_caption
from .captioning import burn_caption
from .clip_duration import compute_clip_window
from .clip_extraction import extract_clip
from .content_piece import ContentPiece


class ContentGenerator:
    """Gera um ContentPiece (clipe + legenda) para cada Moment relevante."""

    def __init__(
        self,
        output_dir: Path,
        game_name: str | None = None,
        burn_captions: bool = False,
    ):
        self.output_dir = output_dir
        self.game_name = game_name
        self.burn_captions = burn_captions

    def generate(self, video_path: Path, moments: Sequence[Moment]) -> list[ContentPiece]:
        """Gera conteúdo apenas para os moments marcados como relevantes.

        A janela de corte é calculada por compute_clip_window() e sempre
        recortada para caber dentro da duração real do vídeo. Se
        burn_captions=True, o título do momento é queimado no rodapé do
        clipe (ver captioning.burn_caption).
        """
        relevant_moments = [m for m in moments if m.is_relevant]
        if not relevant_moments:
            return []

        video_duration = probe(video_path).duration_seconds

        pieces = []
        for index, moment in enumerate(relevant_moments):
            before, after = compute_clip_window(moment)
            start = max(0.0, moment.timestamp_seconds - before)
            end = min(video_duration, moment.timestamp_seconds + after)

            clip_name = f"{video_path.stem}_moment_{index}_{moment.moment_type}"
            clip_path = extract_clip(video_path, start, end, self.output_dir, clip_name)

            if self.burn_captions:
                captioned_path = self.output_dir / f"{clip_name}_captioned.mp4"
                clip_path = burn_caption(clip_path, moment.title, captioned_path)

            caption = build_caption(moment, game_name=self.game_name)

            pieces.append(ContentPiece(moment=moment, clip_path=clip_path, caption=caption))

        return pieces
