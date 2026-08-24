"""Regras de duração variável dos clipes, por tipo de momento e score.

Cada tipo de momento tem um padding base (segundos antes/depois do
timestamp). O score do momento (0 a 1) ajusta esse padding: scores mais
altos esticam o clipe um pouco, scores mais baixos encolhem.
"""

from __future__ import annotations

from fifa_content_engine.ai_engine.moments import Moment

# (segundos_antes, segundos_depois) para cada tipo de momento.
MOMENT_PADDING_SECONDS: dict[str, tuple[float, float]] = {
    "gol": (8.0, 12.0),
    "comemoracao": (3.0, 10.0),
    "lance_perigoso": (5.0, 5.0),
    "defesa": (4.0, 6.0),
    "falta": (3.0, 5.0),
    "outro": (3.0, 5.0),
}

# Em score=0.0 o padding é reduzido para 70%; em score=1.0 é esticado para 130%.
MIN_SCORE_MULTIPLIER = 0.7
MAX_SCORE_MULTIPLIER = 1.3


def _score_multiplier(score: float) -> float:
    return MIN_SCORE_MULTIPLIER + (MAX_SCORE_MULTIPLIER - MIN_SCORE_MULTIPLIER) * score


def compute_clip_window(moment: Moment) -> tuple[float, float]:
    """Retorna (segundos_antes, segundos_depois) já ajustados pelo score.

    Tipos de momento desconhecidos usam o mesmo padding de "outro".
    """
    before, after = MOMENT_PADDING_SECONDS.get(moment.moment_type, MOMENT_PADDING_SECONDS["outro"])
    multiplier = _score_multiplier(moment.score)
    return before * multiplier, after * multiplier
