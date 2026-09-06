from pathlib import Path

from fifa_content_engine.ai_engine.moments import Moment
from fifa_content_engine.content_engine.content_piece import ContentPiece
from fifa_content_engine.publishing_engine.video_metadata import build_video_metadata


def _content_piece(title: str, moment_type: str = "vitoria") -> ContentPiece:
    moment = Moment(
        timestamp_seconds=10.0,
        is_relevant=True,
        moment_type=moment_type,
        score=0.9,
        title=title,
        description="Descrição de teste.",
    )
    return ContentPiece(moment=moment, clip_path=Path("/tmp/clip.mp4"), caption="Legenda completa")


def test_build_video_metadata_default_privacy_is_public():
    metadata = build_video_metadata(_content_piece("Golaço"))

    assert metadata["status"]["privacyStatus"] == "public"


def test_build_video_metadata_uses_caption_as_description():
    metadata = build_video_metadata(_content_piece("Golaço"))

    assert metadata["snippet"]["description"] == "Legenda completa"


def test_build_video_metadata_includes_moment_specific_tags():
    metadata = build_video_metadata(_content_piece("Golaço", moment_type="vitoria"))

    assert "vitoria" in metadata["snippet"]["tags"]
    assert "gameplay" in metadata["snippet"]["tags"]


def test_build_video_metadata_includes_game_name_tag_when_provided():
    metadata = build_video_metadata(_content_piece("Golaço"), game_name="FIFA 26")

    assert "FIFA 26" in metadata["snippet"]["tags"]


def test_build_video_metadata_uses_gaming_category_by_default():
    metadata = build_video_metadata(_content_piece("Golaço"))

    assert metadata["snippet"]["categoryId"] == "20"


def test_build_video_metadata_truncates_long_title():
    long_title = "x" * 150
    metadata = build_video_metadata(_content_piece(long_title))

    assert len(metadata["snippet"]["title"]) == 100


def test_build_video_metadata_respects_custom_privacy_status():
    metadata = build_video_metadata(_content_piece("Golaço"), privacy_status="private")

    assert metadata["status"]["privacyStatus"] == "private"
