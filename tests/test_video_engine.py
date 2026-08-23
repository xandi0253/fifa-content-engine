from pathlib import Path

from fifa_content_engine.video_engine.ingestion import VideoIngestor, VideoSource


class DummyIngestor(VideoIngestor):
    def validate(self, source: VideoSource) -> bool:
        return source.path.suffix == ".mp4"

    def prepare(self, source: VideoSource) -> VideoSource:
        return source


def test_dummy_ingestor_validates_mp4():
    ingestor = DummyIngestor()
    source = VideoSource(path=Path("partida.mp4"))
    assert ingestor.validate(source) is True


def test_dummy_ingestor_rejects_other_formats():
    ingestor = DummyIngestor()
    source = VideoSource(path=Path("partida.avi"))
    assert ingestor.validate(source) is False
