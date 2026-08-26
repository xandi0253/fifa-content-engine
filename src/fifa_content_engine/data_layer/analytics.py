"""Analisa o desempenho do conteúdo publicado, a partir dos snapshots de
métricas registrados no repositório (ver record_stats_snapshot).
"""

from __future__ import annotations

from dataclasses import dataclass

from .repository import PipelineRepository


@dataclass(frozen=True)
class PerformanceEntry:
    """Desempenho mais recente de um clipe em uma plataforma."""

    clip_id: str
    moment_type: str
    score: float
    platform: str
    metrics: dict
    fetched_at: str


def _latest_snapshot_per_clip_and_platform(snapshots: list[dict]) -> dict[tuple, dict]:
    """Reduz os snapshots ao mais recente por (clip_id, platform)."""
    latest: dict[tuple, dict] = {}

    for snapshot in snapshots:
        key = (snapshot["clip_id"], snapshot["platform"])
        current = latest.get(key)
        if current is None or snapshot["fetched_at"] > current["fetched_at"]:
            latest[key] = snapshot

    return latest


def build_performance_report(repository: PipelineRepository) -> list[PerformanceEntry]:
    """Junta clipes com o snapshot de métricas mais recente de cada plataforma.

    Clipes sem nenhum snapshot registrado não aparecem no relatório.
    """
    clips_by_id = {clip["id"]: clip for clip in repository.all_clips()}
    latest_snapshots = _latest_snapshot_per_clip_and_platform(repository.all_stats_snapshots())

    entries = []
    for (clip_id, platform), snapshot in latest_snapshots.items():
        clip = clips_by_id.get(clip_id)
        if clip is None:
            continue

        entries.append(
            PerformanceEntry(
                clip_id=clip_id,
                moment_type=clip["moment_type"],
                score=clip["score"],
                platform=platform,
                metrics=snapshot["metrics"],
                fetched_at=snapshot["fetched_at"],
            )
        )

    return entries


def _primary_metric(metrics: dict) -> int:
    """Escolhe a métrica principal para ordenar o relatório (views, se houver)."""
    return metrics.get("view_count", 0)


def format_performance_report(entries: list[PerformanceEntry]) -> str:
    """Formata o relatório de desempenho, ordenado pela métrica principal."""
    if not entries:
        return "=== Analytics — Desempenho do Conteúdo ===\nNenhuma métrica registrada ainda."

    sorted_entries = sorted(entries, key=lambda e: _primary_metric(e.metrics), reverse=True)

    lines = ["=== Analytics — Desempenho do Conteúdo ==="]
    for entry in sorted_entries:
        metrics_str = ", ".join(f"{k}={v}" for k, v in entry.metrics.items())
        lines.append(
            f"[{entry.platform}] {entry.moment_type} (score={entry.score:.2f}) — {metrics_str}"
        )

    return "\n".join(lines)


def print_performance_report(repository: PipelineRepository) -> None:
    """Monta e imprime o relatório de desempenho no terminal."""
    entries = build_performance_report(repository)
    print(format_performance_report(entries))
