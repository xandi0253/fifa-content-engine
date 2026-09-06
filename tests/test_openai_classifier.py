from pathlib import Path

import pytest

from fifa_content_engine.ai_engine.errors import ModelResponseError
from fifa_content_engine.ai_engine.openai_classifier import OpenAIFrameClassifier


def test_classifier_raises_without_api_key(tmp_path: Path, monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    classifier = OpenAIFrameClassifier(api_key=None)

    fake_image = tmp_path / "frame.jpg"
    fake_image.write_bytes(b"fake-jpeg-bytes")

    with pytest.raises(ModelResponseError):
        classifier.classify(fake_image)


def test_classifier_uses_env_var_when_no_key_passed(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "sk-fake-key-for-test")
    classifier = OpenAIFrameClassifier()

    assert classifier.api_key == "sk-fake-key-for-test"


def test_classifier_prefers_explicit_key_over_env(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "sk-env-key")
    classifier = OpenAIFrameClassifier(api_key="sk-explicit-key")

    assert classifier.api_key == "sk-explicit-key"


def test_build_system_prompt_is_generic_without_game_context():
    from fifa_content_engine.ai_engine.openai_classifier import build_system_prompt

    prompt = build_system_prompt()

    assert "gameplay" in prompt.lower()
    assert "fifa" not in prompt.lower()


def test_build_system_prompt_mentions_game_when_provided():
    from fifa_content_engine.ai_engine.openai_classifier import build_system_prompt

    prompt = build_system_prompt(game_context="FIFA 26")

    assert "FIFA 26" in prompt


def test_classifier_uses_generic_prompt_by_default():
    classifier = OpenAIFrameClassifier(api_key="fake-key")

    assert "fifa" not in classifier.system_prompt.lower()


def test_classifier_uses_game_specific_prompt_when_given():
    classifier = OpenAIFrameClassifier(api_key="fake-key", game_context="Call of Duty")

    assert "Call of Duty" in classifier.system_prompt
