from pathlib import Path

from fifa_content_engine.video_engine.ffmpeg_ingestor import FfmpegVideoIngestor
from fifa_content_engine.video_engine.ingestion import VideoSource


def test_validate_accepts_synthetic_video(synthetic_video: Path, tmp_path: Path):
    ingestor = FfmpegVideoIngestor(output_dir=tmp_path / "out")
    source = VideoSource(path=synthetic_video)

    assert ingestor.validate(source) is True


def test_validate_rejects_unsupported_extension(tmp_path: Path):
    ingestor = FfmpegVideoIngestor(output_dir=tmp_path / "out")
    fake = tmp_path / "video.txt"
    fake.write_text("não é vídeo")
    source = VideoSource(path=fake)

    assert ingestor.validate(source) is False


def test_validate_rejects_missing_file(tmp_path: Path):
    ingestor = FfmpegVideoIngestor(output_dir=tmp_path / "out")
    source = VideoSource(path=tmp_path / "missing.mp4")

    assert ingestor.validate(source) is False


def test_prepare_returns_enriched_video_source(synthetic_video: Path, tmp_path: Path):
    output_dir = tmp_path / "out"
    ingestor = FfmpegVideoIngestor(output_dir=output_dir)
    source = VideoSource(path=synthetic_video)

    prepared = ingestor.prepare(source)

    assert prepared.path.exists()
    assert prepared.path.parent == output_dir
    assert prepared.duration_seconds is not None and prepared.duration_seconds > 0
    assert prepared.video_codec == "h264"
    assert len(prepared.scene_timestamps) >= 2
