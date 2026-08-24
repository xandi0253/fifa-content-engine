from fifa_content_engine.ai_engine.moments import Moment
from fifa_content_engine.content_engine.clip_duration import compute_clip_window


def _moment(moment_type: str, score: float) -> Moment:
    return Moment(
        timestamp_seconds=10.0,
        is_relevant=True,
        moment_type=moment_type,
        score=score,
        title="x",
        description="y",
    )


def test_gol_has_larger_padding_than_falta():
    gol_before, gol_after = compute_clip_window(_moment("gol", 0.9))
    falta_before, falta_after = compute_clip_window(_moment("falta", 0.9))

    assert gol_before > falta_before
    assert gol_after > falta_after


def test_higher_score_produces_wider_window():
    low_before, low_after = compute_clip_window(_moment("gol", 0.0))
    high_before, high_after = compute_clip_window(_moment("gol", 1.0))

    assert high_before > low_before
    assert high_after > low_after


def test_unknown_moment_type_falls_back_to_outro():
    outro_before, outro_after = compute_clip_window(_moment("outro", 0.5))
    unknown_before, unknown_after = compute_clip_window(_moment("tipo_nao_mapeado", 0.5))

    assert (unknown_before, unknown_after) == (outro_before, outro_after)
