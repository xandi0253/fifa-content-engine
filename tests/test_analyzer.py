from pathlib import Path

from fifa_content_engine.ai_engine.analyzer import AIMomentAnalyzer
from fifa_content_engine.ai_engine.classifier import FrameClassifier


class FakeFrameClassifier(FrameClassifier):
    """Classificador falso para testes: nunca chama a API da OpenAI de verdade."""

    def __init__(self, responses: list[str]):
        self.responses = responses
        self.calls: list[Path] = []

    def classify(self, image_path: Path) -> str:
        self.calls.append(image_path)
        return self.responses[len(self.calls) - 1]


GOL_RESPONSE = (
    '{"is_relevant": true, "moment_type": "gol", "score": 0.9, '
    '"title": "Gol de placa", "description": "Finalização certeira."}'
)
IRRELEVANT_RESPONSE = (
    '{"is_relevant": false, "moment_type": "outro", "score": 0.1, '
    '"title": "Sem destaque", "description": "Momento neutro de jogo."}'
)


def test_analyze_extracts_frame_and_classifies_each_timestamp(
    synthetic_video: Path, tmp_path: Path
):
    classifier = FakeFrameClassifier(responses=[GOL_RESPONSE, IRRELEVANT_RESPONSE])
    analyzer = AIMomentAnalyzer(classifier=classifier, frame_output_dir=tmp_path / "frames")

    moments = analyzer.analyze(synthetic_video, timestamps=[0.5, 1.5])

    assert len(moments) == 2
    assert len(classifier.calls) == 2
    assert moments[0].moment_type == "gol"
    assert moments[0].is_relevant is True
    assert moments[1].is_relevant is False


def test_analyze_relevant_only_filters_out_irrelevant_moments(
    synthetic_video: Path, tmp_path: Path
):
    classifier = FakeFrameClassifier(responses=[GOL_RESPONSE, IRRELEVANT_RESPONSE])
    analyzer = AIMomentAnalyzer(classifier=classifier, frame_output_dir=tmp_path / "frames")

    relevant_moments = analyzer.analyze_relevant_only(synthetic_video, timestamps=[0.5, 1.5])

    assert len(relevant_moments) == 1
    assert relevant_moments[0].moment_type == "gol"


def test_analyze_with_no_timestamps_returns_empty(synthetic_video: Path, tmp_path: Path):
    classifier = FakeFrameClassifier(responses=[])
    analyzer = AIMomentAnalyzer(classifier=classifier, frame_output_dir=tmp_path / "frames")

    moments = analyzer.analyze(synthetic_video, timestamps=[])

    assert moments == []
