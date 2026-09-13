from pathlib import Path
from types import SimpleNamespace

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
    monkeypatch.setenv("OPENAI_MODEL", "modelo-de-teste")
    classifier = OpenAIFrameClassifier()

    assert classifier.api_key == "sk-fake-key-for-test"
    assert classifier.model == "modelo-de-teste"


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


def test_classifier_returns_content_from_openai_response(tmp_path: Path):
    image = tmp_path / "frame.jpg"
    image.write_bytes(b"fake")
    classifier = OpenAIFrameClassifier(api_key="fake-key", max_retries=0)
    classifier._client = SimpleNamespace(
        chat=SimpleNamespace(
            completions=SimpleNamespace(
                create=lambda **kwargs: SimpleNamespace(
                    choices=[
                        SimpleNamespace(
                            message=SimpleNamespace(content='{"is_relevant": true}'),
                            finish_reason="stop",
                        )
                    ]
                )
            )
        )
    )

    assert classifier.classify(image) == '{"is_relevant": true}'


def test_classifier_reports_empty_response_with_diagnostic(tmp_path: Path):
    image = tmp_path / "frame.jpg"
    image.write_bytes(b"fake")
    classifier = OpenAIFrameClassifier(api_key="fake-key", max_retries=0)
    classifier._client = SimpleNamespace(
        chat=SimpleNamespace(
            completions=SimpleNamespace(
                create=lambda **kwargs: SimpleNamespace(
                    choices=[
                        SimpleNamespace(
                            message=SimpleNamespace(content=None, refusal="blocked"),
                            finish_reason="stop",
                        )
                    ]
                )
            )
        )
    )

    with pytest.raises(ModelResponseError, match="refusal='blocked'"):
        classifier.classify(image)


def test_classifier_retries_empty_response(tmp_path: Path):
    image = tmp_path / "frame.jpg"
    image.write_bytes(b"fake")
    classifier = OpenAIFrameClassifier(api_key="fake-key", max_retries=1)
    calls = 0

    def create(**kwargs):
        nonlocal calls
        calls += 1
        content = None if calls == 1 else '{"is_relevant": false}'
        return SimpleNamespace(
            choices=[
                SimpleNamespace(
                    message=SimpleNamespace(content=content),
                    finish_reason="stop",
                )
            ]
        )

    classifier._client = SimpleNamespace(
        chat=SimpleNamespace(completions=SimpleNamespace(create=create))
    )

    assert classifier.classify(image) == '{"is_relevant": false}'
    assert calls == 2
