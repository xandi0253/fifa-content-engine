from fifa_content_engine.ai_engine.moment_intelligence import (
    MomentIntelligenceConfig,
    editorial_score,
    select_moments,
)
from fifa_content_engine.ai_engine.moments import Moment


def make_moment(
    timestamp: float,
    moment_type: str,
    score: float,
    *,
    emotion_score: float | None = None,
    retention_score: float | None = None,
) -> Moment:
    return Moment(
        timestamp_seconds=timestamp,
        is_relevant=True,
        moment_type=moment_type,
        score=score,
        title=f"Momento {timestamp}",
        description="Descrição de teste",
        emotion_score=emotion_score,
        retention_score=retention_score,
    )


def test_select_moments_ignores_irrelevant_and_respects_limit():
    moments = [
        make_moment(10, "vitoria", 0.95),
        make_moment(30, "falha", 0.90),
        Moment(50, False, "outro", 1.0, "irrelevante", "ignorar"),
    ]

    selected = select_moments(moments, MomentIntelligenceConfig(max_moments=1))

    assert len(selected) == 1
    assert selected[0].timestamp_seconds == 10


def test_select_moments_avoids_near_duplicates():
    moments = [
        make_moment(10, "vitoria", 0.99),
        make_moment(12, "vitoria", 0.98),
        make_moment(30, "falha", 0.80),
    ]

    selected = select_moments(
        moments,
        MomentIntelligenceConfig(max_moments=3, min_gap_seconds=7),
    )

    assert [m.timestamp_seconds for m in selected] == [10, 30]


def test_select_moments_prefers_diversity_after_best_moment():
    moments = [
        make_moment(10, "vitoria", 0.99, emotion_score=0.9, retention_score=0.9),
        make_moment(30, "vitoria", 0.95, emotion_score=0.9, retention_score=0.9),
        make_moment(50, "falha", 0.88, emotion_score=0.95, retention_score=0.95),
    ]

    selected = select_moments(
        moments,
        MomentIntelligenceConfig(max_moments=2, min_gap_seconds=7),
    )

    assert [m.timestamp_seconds for m in selected] == [10, 50]


def test_editorial_score_uses_retention_and_emotion():
    selected = [make_moment(10, "vitoria", 0.8)]
    lower = make_moment(30, "falha", 0.8, emotion_score=0.2, retention_score=0.2)
    higher = make_moment(30, "falha", 0.8, emotion_score=0.9, retention_score=0.9)

    assert editorial_score(higher, selected, MomentIntelligenceConfig()) > editorial_score(
        lower, selected, MomentIntelligenceConfig()
    )


def test_select_moments_returns_chronological_order():
    moments = [
        make_moment(60, "falha", 0.95),
        make_moment(20, "vitoria", 0.99),
        make_moment(40, "quase", 0.97),
    ]

    selected = select_moments(moments, MomentIntelligenceConfig(max_moments=3))

    assert [m.timestamp_seconds for m in selected] == [20, 40, 60]
