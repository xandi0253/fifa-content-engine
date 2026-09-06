from pathlib import Path

import pytest

from fifa_content_engine.content_engine.captioning import burn_caption, find_available_font
from fifa_content_engine.content_engine.errors import ContentGenerationError
from fifa_content_engine.video_engine.ffprobe import probe


def test_find_available_font_returns_existing_path_or_none():
    result = find_available_font()
    assert result is None or Path(result).exists()


def test_burn_caption_creates_video_with_text(synthetic_video: Path, tmp_path: Path):
    if find_available_font() is None:
        pytest.skip("Nenhuma fonte disponível neste ambiente de teste")

    output_path = tmp_path / "captioned.mp4"
    result = burn_caption(synthetic_video, "Momento de teste", output_path)

    assert result.exists()
    probed = probe(result)
    assert probed.has_video_stream is True


def test_burn_caption_handles_special_characters(synthetic_video: Path, tmp_path: Path):
    if find_available_font() is None:
        pytest.skip("Nenhuma fonte disponível neste ambiente de teste")

    output_path = tmp_path / "captioned_special.mp4"
    result = burn_caption(synthetic_video, "Texto com: dois pontos, 'aspas' e \\barra", output_path)

    assert result.exists()


def test_burn_caption_raises_when_font_path_does_not_exist(synthetic_video: Path, tmp_path: Path):
    output_path = tmp_path / "captioned.mp4"

    with pytest.raises(ContentGenerationError):
        burn_caption(
            synthetic_video,
            "teste",
            output_path,
            font_path="/caminho/que/nao/existe.ttf",
        )


def test_burn_caption_raises_on_missing_source_video(tmp_path: Path):
    if find_available_font() is None:
        pytest.skip("Nenhuma fonte disponível neste ambiente de teste")

    missing = tmp_path / "missing.mp4"
    output_path = tmp_path / "out.mp4"

    with pytest.raises(ContentGenerationError):
        burn_caption(missing, "teste", output_path)
