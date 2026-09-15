from pathlib import Path

import pytest

from fifa_content_engine.ai_engine.context_analyzer import (
    ContextAnalysis,
    OpenAIContextAnalyzer,
    build_context_timestamps,
    context_strength,
)


def test_build_context_timestamps_preserves_temporal_order_and_video_bounds():
    assert build_context_timestamps(1.0, 20.0) == [0.0, 1.0, 5.0]
    assert build_context_timestamps(19.0, 20.0) == [15.0, 19.0, 20.0]


def test_context_strength_is_conservative_when_uncertain():
    assert context_strength("incerto") == 0.5
    assert context_strength("forte tensão") == 1.0
    assert context_strength("sem reação") == 0.25


def test_context_analysis_is_structured():
    analysis = ContextAnalysis(
        setup="preparação",
        tension="forte",
        climax="gol",
        outcome="vitória",
        reaction="forte reação",
        confidence=0.9,
    )
    assert analysis.confidence == 0.9
    assert analysis.climax == "gol"


def test_openai_context_analyzer_rejects_empty_frames():
    analyzer = OpenAIContextAnalyzer(api_key="test")
    with pytest.raises(Exception, match="Nenhum frame"):
        analyzer.analyze([])


def test_openai_context_analyzer_parses_json_without_calling_provider(monkeypatch, tmp_path: Path):
    class Message:
        content = '{"setup":"forte", "tension":"alta", "climax":"gol", "outcome":"vitória", "reaction":"forte reação", "confidence":0.8}'

    class Choice:
        message = Message()

    class Response:
        choices = [Choice()]

    class Completions:
        def create(self, **_kwargs):
            return Response()

    class Chat:
        completions = Completions()

    class Client:
        chat = Chat()

    analyzer = OpenAIContextAnalyzer(api_key="test")
    analyzer._client = Client()
    frame = tmp_path / "frame.jpg"
    frame.write_bytes(b"fake")

    result = analyzer.analyze([frame])
    assert result.confidence == 0.8
    assert result.reaction == "forte reação"
