from pathlib import Path

import pytest

from fifa_content_engine.content_engine.clip_extraction import extract_clip
from fifa_content_engine.content_engine.errors import ClipExtractionError
from fifa_content_engine.video_engine.ffprobe import probe


def test_extract_clip_creates_mp4_with_expected_duration(synthetic_video: Path, tmp_path: Path):
    output_dir = tmp_path / "clips"
    clip_path = extract_clip(
        synthetic_video,
        start_seconds=0.5,
        end_seconds=2.0,
        output_dir=output_dir,
        clip_name="clip1",
    )

    assert clip_path.exists()
    assert clip_path.suffix == ".mp4"

    result = probe(clip_path)
    assert result.duration_seconds == pytest.approx(1.5, abs=0.3)


def test_extract_clip_raises_on_invalid_window(synthetic_video: Path, tmp_path: Path):
    with pytest.raises(ClipExtractionError):
        extract_clip(
            synthetic_video,
            start_seconds=2.0,
            end_seconds=1.0,
            output_dir=tmp_path / "clips",
            clip_name="invalid",
        )


def test_extract_clip_raises_on_missing_video(tmp_path: Path):
    missing = tmp_path / "missing.mp4"
    with pytest.raises(ClipExtractionError):
        extract_clip(
            missing,
            start_seconds=0.0,
            end_seconds=1.0,
            output_dir=tmp_path / "clips",
            clip_name="x",
        )
