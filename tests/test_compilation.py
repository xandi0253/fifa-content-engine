from pathlib import Path

import pytest

from fifa_content_engine.ai_engine.moments import Moment
from fifa_content_engine.content_engine.compilation import (
    build_compilation_piece,
    concatenate_clips,
)
from fifa_content_engine.content_engine.content_piece import ContentPiece
from fifa_content_engine.content_engine.errors import ContentGenerationError
from fifa_content_engine.video_engine.ffprobe import probe


def _clip(synthetic_video: Path, tmp_path: Path, start: float, end: float, name: str) -> Path:
    from fifa_content_engine.content_engine.clip_extraction import extract_clip

    return extract_clip(synthetic_video, start, end, tmp_path / "clips", name)


def test_concatenate_clips_combines_duration(synthetic_video: Path, tmp_path: Path):
    clip1 = _clip(synthetic_video, tmp_path, 0.0, 1.0, "clip1")
    clip2 = _clip(synthetic_video, tmp_path, 1.0, 2.0, "clip2")

    output_path = tmp_path / "combined.mp4"
    result = concatenate_clips([clip1, clip2], output_path)

    assert result.exists()
    probed = probe(result)
    assert probed.duration_seconds == pytest.approx(2.0, abs=0.3)


def test_concatenate_clips_raises_on_empty_list(tmp_path: Path):
    with pytest.raises(ContentGenerationError):
        concatenate_clips([], tmp_path / "output.mp4")


def test_build_compilation_piece_combines_titles_in_description(
    synthetic_video: Path, tmp_path: Path
):
    clip1 = _clip(synthetic_video, tmp_path, 0.0, 1.0, "clip1")
    clip2 = _clip(synthetic_video, tmp_path, 1.0, 2.0, "clip2")

    moment1 = Moment(
        timestamp_seconds=0.5,
        is_relevant=True,
        moment_type="vitoria",
        score=0.9,
        title="Gol 1",
        description="x",
    )
    moment2 = Moment(
        timestamp_seconds=1.5,
        is_relevant=True,
        moment_type="vitoria",
        score=0.7,
        title="Gol 2",
        description="y",
    )
    piece1 = ContentPiece(moment=moment1, clip_path=clip1, caption="c1")
    piece2 = ContentPiece(moment=moment2, clip_path=clip2, caption="c2")

    compiled = build_compilation_piece([piece1, piece2], output_dir=tmp_path / "clips")

    assert compiled.clip_path.exists()
    assert "Gol 1" in compiled.moment.description
    assert "Gol 2" in compiled.moment.description
    assert compiled.moment.score == pytest.approx(0.8)


def test_build_compilation_piece_includes_game_name_in_title(synthetic_video: Path, tmp_path: Path):
    clip1 = _clip(synthetic_video, tmp_path, 0.0, 1.0, "clip1")
    moment1 = Moment(
        timestamp_seconds=0.5,
        is_relevant=True,
        moment_type="vitoria",
        score=0.9,
        title="Gol",
        description="x",
    )
    piece1 = ContentPiece(moment=moment1, clip_path=clip1, caption="c1")

    compiled = build_compilation_piece([piece1], output_dir=tmp_path / "clips", game_name="FIFA 26")

    assert "FIFA 26" in compiled.moment.title


def test_build_compilation_piece_raises_on_empty_list(tmp_path: Path):
    with pytest.raises(ContentGenerationError):
        build_compilation_piece([], output_dir=tmp_path / "clips")
