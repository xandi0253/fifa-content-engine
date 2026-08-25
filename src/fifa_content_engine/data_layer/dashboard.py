"""Monta e formata um resumo do estado do pipeline, a partir do repositório."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field

from .repository import PipelineRepository


@dataclass(frozen=True)
class DashboardSummary:
    """Resumo agregado do pipeline: partidas, clipes e publicações."""

    total_matches: int
    total_clips: int
    total_publications: int
    successful_publications: int
    failed_publications: int
    publications_by_platform: dict[str, int] = field(default_factory=dict)

    @property
    def success_rate(self) -> float:
        if self.total_publications == 0:
            return 0.0
        return self.successful_publications / self.total_publications


def build_summary(repository: PipelineRepository) -> DashboardSummary:
    """Lê o repositório e monta o resumo agregado do pipeline."""
    matches = repository.all_matches()
    clips = repository.all_clips()
    publications = repository.all_publications()

    successful = [p for p in publications if p.get("success")]
    failed = [p for p in publications if not p.get("success")]
    platform_counts = Counter(p.get("platform", "desconhecida") for p in publications)

    return DashboardSummary(
        total_matches=len(matches),
        total_clips=len(clips),
        total_publications=len(publications),
        successful_publications=len(successful),
        failed_publications=len(failed),
        publications_by_platform=dict(platform_counts),
    )


def format_summary(summary: DashboardSummary) -> str:
    """Formata o resumo como um relatório de texto para o terminal."""
    lines = [
        "=== FIFA Content Engine — Dashboard ===",
        f"Partidas processadas: {summary.total_matches}",
        f"Clipes gerados: {summary.total_clips}",
        f"Publicações tentadas: {summary.total_publications}",
        f"  - Bem-sucedidas: {summary.successful_publications}",
        f"  - Falhas: {summary.failed_publications}",
        f"  - Taxa de sucesso: {summary.success_rate:.0%}",
    ]

    if summary.publications_by_platform:
        lines.append("Publicações por plataforma:")
        for platform, count in sorted(summary.publications_by_platform.items()):
            lines.append(f"  - {platform}: {count}")

    return "\n".join(lines)


def print_summary(repository: PipelineRepository) -> None:
    """Monta e imprime o relatório do dashboard no terminal."""
    summary = build_summary(repository)
    print(format_summary(summary))
