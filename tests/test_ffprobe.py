from pathlib import Path

import pytest

from fifa_content_engine.video_engine import ffprobe
from fifa_content_engine.video_engine.errors import VideoValidationError


def test_probe_reads_synthetic_video(synthetic_video: Path):
    result = ffprobe.probe(synthetic_video)
    assert result.has_video_stream is True
    assert result.video_codec == "h264"
    assert result.duration_seconds > 0


def test_probe_raises_on_missing_file(tmp_path: Path):
    missing = tmp_path / "does_not_exist.mp4"
    with pytest.raises(VideoValidationError):
        ffprobe.probe(missing)


def test_probe_raises_on_non_video_file(tmp_path: Path):
    text_file = tmp_path / "not_a_video.mp4"
    text_file.write_text("isto não é um vídeo")
    with pytest.raises(VideoValidationError):
        ffprobe.probe(text_file)
