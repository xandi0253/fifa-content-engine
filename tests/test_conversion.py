from pathlib import Path

import pytest

from fifa_content_engine.video_engine import ffprobe
from fifa_content_engine.video_engine.conversion import normalize
from fifa_content_engine.video_engine.errors import VideoConversionError


def test_normalize_produces_valid_mp4(synthetic_video: Path, tmp_path: Path):
    output_dir = tmp_path / "output"
    result_path = normalize(synthetic_video, output_dir)

    assert result_path.exists()
    assert result_path.suffix == ".mp4"

    probed = ffprobe.probe(result_path)
    assert probed.has_video_stream is True
    assert probed.video_codec == "h264"


def test_normalize_raises_on_invalid_source(tmp_path: Path):
    fake_source = tmp_path / "not_real.mp4"
    fake_source.write_text("lixo")
    output_dir = tmp_path / "output"

    with pytest.raises(VideoConversionError):
        normalize(fake_source, output_dir)
