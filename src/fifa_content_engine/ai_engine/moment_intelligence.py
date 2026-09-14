"""Inteligência editorial para selecionar momentos variados e com potencial de retenção.

Esta camada é deliberadamente genérica: não conhece FIFA, futebol ou qualquer
jogo específico. Ela recebe momentos já classificados e evita que a compilação
seja apenas uma lista dos maiores scores individuais.
"""

from __future__ import annotations

import os
from dataclasses import dataclass

from .moments import Moment


@dataclass(frozen=True)
class MomentIntelligenceConfig:
    """Configuração segura e ajustável da seleção editorial."""

    max_moments: int = 8
    min_gap_seconds: float = 7.0
    diversity_weight: float = 0.20
    novelty_weight: float = 0.15
    emotion_weight: float = 0.15


# Fallback universal quando modelos antigos ainda não retornam emoção.
_EMOTION_BY_TYPE = {
    "vitoria": 0.85,
    "quase": 0.75,
    "comemoracao": 0.80,
    "falha": 0.72,
    "acao_intensa": 0.78,
    "outro": 0.45,
}


def _clamp(value: float) -> float:
    return max(0.0, min(1.0, value))


def _emotion_value(moment: Moment) -> float:
    explicit = getattr(moment, "emotion_score", None)
    if explicit is not None:
        return _clamp(float(explicit))
    return _EMOTION_BY_TYPE.get(moment.moment_type, 0.45)


def editorial_score(moment: Moment, selected: list[Moment], config: MomentIntelligenceConfig) -> float:
    """Calcula um score editorial sem depender do domínio do vídeo.

    O score combina relevância original, emoção, novidade temporal e diversidade
    em relação aos momentos já escolhidos.
    """
    emotion = _emotion_value(moment)

    if selected:
        nearest_gap = min(
            abs(moment.timestamp_seconds - other.timestamp_seconds) for other in selected
        )
        novelty = _clamp(nearest_gap / max(config.min_gap_seconds * 3.0, 1.0))
        same_type_count = sum(other.moment_type == moment.moment_type for other in selected)
    else:
        novelty = 1.0
        same_type_count = 0

    diversity = 1.0 / (1.0 + same_type_count)

    score = (
        moment.score
        + config.emotion_weight * emotion
        + config.novelty_weight * novelty
        + config.diversity_weight * diversity
    )
    return score


def select_moments(
    moments: list[Moment], config: MomentIntelligenceConfig | None = None
) -> list[Moment]:
    """Seleciona momentos relevantes, variados e suficientemente separados.

    A ordem final é temporal, para que a compilação preserve a narrativa da
    gravação. A função é determinística e não altera os objetos recebidos.
    """
    config = config or MomentIntelligenceConfig()
    candidates = [moment for moment in moments if moment.is_relevant]
    if not candidates or config.max_moments <= 0:
        return []

    # Primeiro momento: maior potencial bruto. Depois, a diversidade passa a
    # influenciar a escolha, evitando uma sequência de eventos quase idênticos.
    first = max(candidates, key=lambda item: (item.score, _emotion_value(item)))
    selected = [first]
    remaining = [item for item in candidates if item is not first]

    while remaining and len(selected) < config.max_moments:
        eligible = [
            item
            for item in remaining
            if all(
                abs(item.timestamp_seconds - chosen.timestamp_seconds) >= config.min_gap_seconds
                for chosen in selected
            )
        ]
        if not eligible:
            break

        next_moment = max(
            eligible,
            key=lambda item: (
                editorial_score(item, selected, config),
                item.score,
                _emotion_value(item),
            ),
        )
        selected.append(next_moment)
        remaining.remove(next_moment)

    return sorted(selected, key=lambda item: item.timestamp_seconds)


def config_from_env() -> MomentIntelligenceConfig:
    """Lê ajustes opcionais do ambiente sem obrigar configuração no usuário."""
    return MomentIntelligenceConfig(
        max_moments=max(1, int(os.getenv("MOMENT_MAX_SELECTED", "8"))),
        min_gap_seconds=max(0.0, float(os.getenv("MOMENT_MIN_GAP_SECONDS", "7"))),
        diversity_weight=max(0.0, float(os.getenv("MOMENT_DIVERSITY_WEIGHT", "0.20"))),
        novelty_weight=max(0.0, float(os.getenv("MOMENT_NOVELTY_WEIGHT", "0.15"))),
        emotion_weight=max(0.0, float(os.getenv("MOMENT_EMOTION_WEIGHT", "0.15"))),
    )
