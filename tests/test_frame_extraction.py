from pathlib import Path

import pytest

from fifa_content_engine.ai_engine.errors import FrameExtractionError
from fifa_content_engine.ai_engine.frame_extraction import extract_frame


def test_extract_frame_creates_jpeg(synthetic_video: Path, tmp_path: Path):
    output_dir = tmp_path / "frames"
    frame_path = extract_frame(synthetic_video, timestamp_seconds=0.5, output_dir=output_dir)

    assert frame_path.exists()
    assert frame_path.suffix == ".jpg"
    assert frame_path.parent == output_dir


def test_extract_frame_raises_on_missing_video(tmp_path: Path):
    missing = tmp_path / "missing.mp4"
    output_dir = tmp_path / "frames"

    with pytest.raises(FrameExtractionError):
        extract_frame(missing, timestamp_seconds=0.5, output_dir=output_dir)
