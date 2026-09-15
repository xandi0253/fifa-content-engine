"""Calcula uma janela temporal semantica ao redor de um momento.

A primeira versao preserva exatamente as regras de duracao existentes, mas
explicita as partes editoriais do clipe: preparacao, clímax e resultado/
reacao. Isso cria um contrato pequeno para futuras melhorias multimodais sem
alterar o comportamento atual do pipeline.
"""

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

    @property
    def total_seconds(self) -> float:
        """Duração total da janela, sem considerar limites do vídeo."""
        return self.before_seconds + self.after_seconds


def compute_context_window(moment: Moment) -> ContextWindow:
    """Retorna a janela de contexto sem alterar as regras atuais de duração.

    ``before_seconds`` e ``after_seconds`` continuam vindo de
    ``compute_clip_window``. A divisão semântica é uma camada de metadados:
    parte do trecho anterior representa preparação e parte do trecho posterior
    representa resultado/reação.
    """
    before, after = compute_clip_window(moment)

    # Mantemos pelo menos uma pequena região de preparação e reação quando
    # houver espaço suficiente, sem aumentar a duração do clipe.
    setup_seconds = min(before, max(1.0, before * 0.65)) if before > 0 else 0.0
    reaction_seconds = min(after, max(1.0, after * 0.55)) if after > 0 else 0.0

    return ContextWindow(
        before_seconds=before,
        after_seconds=after,
        setup_seconds=setup_seconds,
        reaction_seconds=reaction_seconds,
    )
