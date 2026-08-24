import pytest

from fifa_content_engine.ai_engine.errors import ModelResponseError
from fifa_content_engine.ai_engine.moments import parse_model_response


def test_parse_model_response_valid():
    raw = (
        '{"is_relevant": true, "moment_type": "gol", "score": 0.95, '
        '"title": "Golaço no ângulo", "description": "Chute de fora da área."}'
    )
    moment = parse_model_response(raw, timestamp_seconds=12.5)

    assert moment.timestamp_seconds == 12.5
    assert moment.is_relevant is True
    assert moment.moment_type == "gol"
    assert moment.score == 0.95
    assert moment.title == "Golaço no ângulo"


def test_parse_model_response_invalid_json():
    with pytest.raises(ModelResponseError):
        parse_model_response("isto não é json", timestamp_seconds=1.0)


def test_parse_model_response_missing_keys():
    with pytest.raises(ModelResponseError):
        parse_model_response('{"is_relevant": true}', timestamp_seconds=1.0)


def test_parse_model_response_invalid_moment_type():
    raw = (
        '{"is_relevant": true, "moment_type": "invalido", "score": 0.5, '
        '"title": "x", "description": "y"}'
    )
    with pytest.raises(ModelResponseError):
        parse_model_response(raw, timestamp_seconds=1.0)


def test_parse_model_response_score_out_of_range():
    raw = (
        '{"is_relevant": true, "moment_type": "gol", "score": 1.5, '
        '"title": "x", "description": "y"}'
    )
    with pytest.raises(ModelResponseError):
        parse_model_response(raw, timestamp_seconds=1.0)
