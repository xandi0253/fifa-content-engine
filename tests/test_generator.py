from pathlib import Path

from fifa_content_engine.ai_engine.moments import Moment
from fifa_content_engine.content_engine.generator import ContentGenerator


def _moment(timestamp: float, is_relevant: bool, moment_type: str = "vitoria") -> Moment:
    return Moment(
        timestamp_seconds=timestamp,
        is_relevant=is_relevant,
        moment_type=moment_type,
        score=0.8,
        title="Momento de teste",
        description="Descrição de teste.",
    )


def test_generate_creates_clip_and_caption_for_relevant_moments(
    synthetic_video: Path, tmp_path: Path
):
    generator = ContentGenerator(output_dir=tmp_path / "content")
    moments = [_moment(1.0, is_relevant=True), _moment(2.0, is_relevant=False)]

    pieces = generator.generate(synthetic_video, moments)

    assert len(pieces) == 1
    assert pieces[0].clip_path.exists()
    assert "Momento de teste" in pieces[0].caption


def test_generate_returns_empty_when_no_relevant_moments(synthetic_video: Path, tmp_path: Path):
    generator = ContentGenerator(output_dir=tmp_path / "content")
    moments = [_moment(1.0, is_relevant=False)]

    pieces = generator.generate(synthetic_video, moments)

    assert pieces == []


def test_generate_clamps_window_to_video_duration(synthetic_video: Path, tmp_path: Path):
    generator = ContentGenerator(output_dir=tmp_path / "content")
    # timestamp próximo do início e do fim do vídeo de 3s, para forçar o clamp.
    moments = [_moment(0.1, is_relevant=True, moment_type="vitoria")]

    pieces = generator.generate(synthetic_video, moments)

    assert len(pieces) == 1
    assert pieces[0].clip_path.exists()


def test_generate_includes_game_hashtag_in_caption_when_provided(
    synthetic_video: Path, tmp_path: Path
):
    generator = ContentGenerator(output_dir=tmp_path / "content", game_name="FIFA 26")
    moments = [_moment(1.0, is_relevant=True)]

    pieces = generator.generate(synthetic_video, moments)

    assert "#FIFA26" in pieces[0].caption


def test_generate_burns_captions_when_enabled(synthetic_video: Path, tmp_path: Path):
    from fifa_content_engine.content_engine.captioning import find_available_font

    if find_available_font() is None:
        import pytest

        pytest.skip("Nenhuma fonte disponível neste ambiente de teste")

    generator = ContentGenerator(output_dir=tmp_path / "content", burn_captions=True)
    moments = [_moment(1.0, is_relevant=True)]

    pieces = generator.generate(synthetic_video, moments)

    assert len(pieces) == 1
    assert pieces[0].clip_path.exists()
    assert pieces[0].clip_path.name.endswith("_captioned.mp4")
