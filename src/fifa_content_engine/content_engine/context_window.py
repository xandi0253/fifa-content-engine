"""Calcula uma janela temporal semântica ao redor de um momento."""

from __future__ import annotations

from dataclasses import dataclass

from fifa_content_engine.ai_engine.moments import Moment

from .clip_duration import compute_clip_window


@dataclass(frozen=True)
class ContextWindow:
    """Janela temporal relativa ao timestamp principal de um momento."""

    before_seconds: float
    after_seconds: float
    setup_seconds: float
    reaction_seconds: float
    confidence: float = 0.0

    @property
    def total_seconds(self) -> float:
        return self.before_seconds + self.after_seconds


def compute_context_window(moment: Moment) -> ContextWindow:
    """Mantém a janela atual e explicita suas regiões editoriais."""
    before, after = compute_clip_window(moment)
    return ContextWindow(
        before_seconds=before,
        after_seconds=after,
        setup_seconds=min(before, max(1.0, before * 0.65)) if before > 0 else 0.0,
        reaction_seconds=min(after, max(1.0, after * 0.55)) if after > 0 else 0.0,
    )


def refine_context_window(
    context: ContextWindow,
    *,
    setup_strength: float,
    reaction_strength: float,
    confidence: float,
) -> ContextWindow:
    """Refina a janela dentro dos limites existentes usando sinais multimodais.

    Os fatores são normalizados para [0, 1]. A duração total nunca ultrapassa
    a janela original; isso mantém a primeira integração conservadora.
    """
    setup = max(0.0, min(1.0, setup_strength))
    reaction = max(0.0, min(1.0, reaction_strength))
    confidence = max(0.0, min(1.0, confidence))

    setup_seconds = context.setup_seconds * (0.75 + 0.25 * setup)
    reaction_seconds = context.reaction_seconds * (0.75 + 0.25 * reaction)
    before = max(setup_seconds, context.before_seconds * 0.75)
    after = max(reaction_seconds, context.after_seconds * 0.75)

    return ContextWindow(
        before_seconds=min(before, context.before_seconds),
        after_seconds=min(after, context.after_seconds),
        setup_seconds=setup_seconds,
        reaction_seconds=reaction_seconds,
        confidence=confidence,
    )
