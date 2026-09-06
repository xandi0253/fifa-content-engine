from fifa_content_engine.ai_engine.moments import Moment
from fifa_content_engine.content_engine.caption import build_caption


def test_build_caption_includes_title_description_and_hashtags():
    moment = Moment(
        timestamp_seconds=10.0,
        is_relevant=True,
        moment_type="vitoria",
        score=0.9,
        title="Golaço no ângulo",
        description="Chute certeiro de fora da área.",
    )

    caption = build_caption(moment)

    assert "Golaço no ângulo" in caption
    assert "Chute certeiro de fora da área." in caption
    assert "#Gameplay" in caption
    assert "#Vitória" in caption


def test_build_caption_includes_game_hashtag_when_provided():
    moment = Moment(
        timestamp_seconds=10.0,
        is_relevant=True,
        moment_type="vitoria",
        score=0.9,
        title="Golaço",
        description="y",
    )

    caption = build_caption(moment, game_name="FIFA 26")

    assert "#FIFA26" in caption


def test_build_caption_handles_unknown_moment_type_gracefully():
    moment = Moment(
        timestamp_seconds=10.0,
        is_relevant=True,
        moment_type="tipo_nao_mapeado",
        score=0.5,
        title="x",
        description="y",
    )

    caption = build_caption(moment)

    assert "#Gameplay" in caption
