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
