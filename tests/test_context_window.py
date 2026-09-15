from fifa_content_engine.ai_engine.moments import Moment
from fifa_content_engine.content_engine.context_window import compute_context_window


def _moment(moment_type: str = "vitoria", score: float = 0.8) -> Moment:
    return Moment(
        timestamp_seconds=42.0,
        is_relevant=True,
        moment_type=moment_type,
        score=score,
        title="momento",
        description="descricao",
    )


def test_context_window_preserves_existing_clip_duration_rules():
    context = compute_context_window(_moment("vitoria", 0.8))

    assert context.before_seconds > 0
    assert context.after_seconds > 0
    assert context.total_seconds == context.before_seconds + context.after_seconds


def test_context_window_exposes_setup_and_reaction_inside_existing_window():
    context = compute_context_window(_moment("vitoria", 0.8))

    assert 0 < context.setup_seconds <= context.before_seconds
    assert 0 < context.reaction_seconds <= context.after_seconds


def test_context_window_scales_with_moment_score():
    low = compute_context_window(_moment("vitoria", 0.0))
    high = compute_context_window(_moment("vitoria", 1.0))

    assert high.before_seconds > low.before_seconds
    assert high.after_seconds > low.after_seconds
    assert high.total_seconds > low.total_seconds
