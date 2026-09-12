from pathlib import Path
from unittest.mock import patch

from fifa_content_engine.ai_engine.classifier import FrameClassifier
from fifa_content_engine.pipeline import run_pipeline
from fifa_content_engine.publishing_engine.errors import YouTubeUploadError
from fifa_content_engine.publishing_engine.publisher import VideoPublisher


class FakeClassifier(FrameClassifier):
    def __init__(self, *_args, **_kwargs):
        self.call_count = 0

    def classify(self, image_path):
        self.call_count += 1
        return (
            '{"is_relevant": true, "moment_type": "vitoria", "score": 0.9, '
            f'"title": "Gol {self.call_count}", "description": "desc"}}'
        )


class AllIrrelevantClassifier(FrameClassifier):
    def classify(self, image_path):
        return (
            '{"is_relevant": false, "moment_type": "outro", "score": 0.1, '
            '"title": "x", "description": "y"}'
        )


class FakePublisher(VideoPublisher):
    def publish(self, content_piece):
        return "https://youtube.com/watch?v=FAKE123"


class FailingPublisher(VideoPublisher):
    def publish(self, content_piece):
        raise YouTubeUploadError("falha simulada")


def test_run_pipeline_raises_on_missing_file(tmp_path: Path):
    import pytest

    with pytest.raises(FileNotFoundError):
        run_pipeline(tmp_path / "missing.mp4", work_dir=tmp_path / "work")


def test_run_pipeline_stops_when_no_scenes_detected(synthetic_video: Path, tmp_path: Path):
    # threshold muito alto: vídeo sintético não deve ter corte de cena algum
    result = run_pipeline(
        synthetic_video,
        scene_threshold=0.99,
        work_dir=tmp_path / "work",
        data_dir=tmp_path / "data",
    )

    assert result.stopped_reason is not None
    assert result.content_piece is None


def test_run_pipeline_stops_when_no_relevant_moments(synthetic_video: Path, tmp_path: Path):
    with patch(
        "fifa_content_engine.pipeline.OpenAIFrameClassifier",
        return_value=AllIrrelevantClassifier(),
    ):
        result = run_pipeline(
            synthetic_video,
            scene_threshold=0.15,
            work_dir=tmp_path / "work",
            data_dir=tmp_path / "data",
        )

    assert result.stopped_reason is not None
    assert "relevante" in result.stopped_reason.lower()


def test_run_pipeline_simulation_mode_does_not_publish(synthetic_video: Path, tmp_path: Path):
    with patch("fifa_content_engine.pipeline.OpenAIFrameClassifier", return_value=FakeClassifier()):
        result = run_pipeline(
            synthetic_video,
            scene_threshold=0.15,
            publish=False,
            work_dir=tmp_path / "work",
            data_dir=tmp_path / "data",
        )

    assert result.content_piece is not None
    assert result.publish_results is None


def test_run_pipeline_publishes_when_requested(synthetic_video: Path, tmp_path: Path):
    with (
        patch("fifa_content_engine.pipeline.OpenAIFrameClassifier", return_value=FakeClassifier()),
        patch("fifa_content_engine.pipeline.YouTubePublisher", return_value=FakePublisher()),
    ):
        result = run_pipeline(
            synthetic_video,
            scene_threshold=0.15,
            publish=True,
            work_dir=tmp_path / "work",
            data_dir=tmp_path / "data",
        )

    assert result.publish_results is not None
    assert result.publish_results[0].success is True
    assert result.publish_results[0].url == "https://youtube.com/watch?v=FAKE123"


def test_run_pipeline_records_publication_failure(synthetic_video: Path, tmp_path: Path):
    with (
        patch("fifa_content_engine.pipeline.OpenAIFrameClassifier", return_value=FakeClassifier()),
        patch("fifa_content_engine.pipeline.YouTubePublisher", return_value=FailingPublisher()),
    ):
        result = run_pipeline(
            synthetic_video,
            scene_threshold=0.15,
            publish=True,
            work_dir=tmp_path / "work",
            data_dir=tmp_path / "data",
        )

    assert result.publish_results is not None
    assert result.publish_results[0].success is False


def test_run_pipeline_calls_on_progress_callback(synthetic_video: Path, tmp_path: Path):
    messages = []

    with patch("fifa_content_engine.pipeline.OpenAIFrameClassifier", return_value=FakeClassifier()):
        run_pipeline(
            synthetic_video,
            scene_threshold=0.15,
            work_dir=tmp_path / "work",
            data_dir=tmp_path / "data",
            on_progress=messages.append,
        )

    assert len(messages) > 0
    assert any("vídeo" in m.lower() for m in messages)
