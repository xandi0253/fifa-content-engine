from pathlib import Path

import pytest

from fifa_content_engine.video_engine.errors import TrimError
from fifa_content_engine.video_engine.ffprobe import probe
from fifa_content_engine.video_engine.trimming import trim_video


def test_trim_video_creates_shorter_video(synthetic_video: Path, tmp_path: Path):
    result = trim_video(synthetic_video, start_seconds=0.5, end_seconds=2.0, output_dir=tmp_path)

    assert result.exists()
    probed = probe(result)
    assert probed.duration_seconds == pytest.approx(1.5, abs=0.5)


def test_trim_video_raises_when_end_before_start(synthetic_video: Path, tmp_path: Path):
    with pytest.raises(TrimError):
        trim_video(synthetic_video, start_seconds=2.0, end_seconds=1.0, output_dir=tmp_path)


def test_trim_video_raises_on_negative_start(synthetic_video: Path, tmp_path: Path):
    with pytest.raises(TrimError):
        trim_video(synthetic_video, start_seconds=-1.0, end_seconds=1.0, output_dir=tmp_path)


def test_trim_video_raises_on_missing_source(tmp_path: Path):
    missing = tmp_path / "missing.mp4"
    with pytest.raises(TrimError):
        trim_video(missing, start_seconds=0.0, end_seconds=1.0, output_dir=tmp_path)


def test_trim_video_output_name_includes_range(synthetic_video: Path, tmp_path: Path):
    result = trim_video(synthetic_video, start_seconds=1.0, end_seconds=2.0, output_dir=tmp_path)

    assert "trim_1_2" in result.name
