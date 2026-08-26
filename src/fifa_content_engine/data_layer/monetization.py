"""Agrega a receita registrada manualmente por clipe/plataforma.

Sem integração com APIs de pagamento — os valores vêm de
`PipelineRepository.record_revenue()`, informados por quem opera o
pipeline (ex: repasse de anúncios recebido de cada plataforma).
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field

from .repository import PipelineRepository


@dataclass(frozen=True)
class RevenueSummary:
    """Resumo agregado da receita registrada."""

    total_amount: float
    entry_count: int
    total_by_platform: dict[str, float] = field(default_factory=dict)
    currencies_used: tuple[str, ...] = ()

    @property
    def has_mixed_currencies(self) -> bool:
        return len(self.currencies_used) > 1


def build_revenue_summary(repository: PipelineRepository) -> RevenueSummary:
    """Soma a receita registrada. Não converte entre moedas diferentes —
    se houver mais de uma moeda nos registros, o total soma os valores
    numéricos sem conversão (ver has_mixed_currencies para alertar sobre isso).
    """
    entries = repository.all_revenue()

    total_amount = sum(entry["amount"] for entry in entries)
    by_platform: Counter[str] = Counter()
    for entry in entries:
        by_platform[entry["platform"]] += entry["amount"]

    currencies = tuple(sorted({entry.get("currency", "BRL") for entry in entries}))

    return RevenueSummary(
        total_amount=total_amount,
        entry_count=len(entries),
        total_by_platform=dict(by_platform),
        currencies_used=currencies,
    )


def format_revenue_summary(summary: RevenueSummary) -> str:
    """Formata o resumo de receita como relatório de texto."""
    if summary.entry_count == 0:
        return "=== Monetization — Receita Registrada ===\nNenhuma receita registrada ainda."

    currency_label = summary.currencies_used[0] if summary.currencies_used else "BRL"
    lines = [
        "=== Monetization — Receita Registrada ===",
        f"Total: {summary.total_amount:.2f} {currency_label}",
        f"Registros: {summary.entry_count}",
    ]

    if summary.has_mixed_currencies:
        lines.append(
            f"⚠ Atenção: registros em moedas diferentes ({', '.join(summary.currencies_used)}) "
            "foram somados sem conversão."
        )

    if summary.total_by_platform:
        lines.append("Receita por plataforma:")
        for platform, amount in sorted(summary.total_by_platform.items()):
            lines.append(f"  - {platform}: {amount:.2f}")

    return "\n".join(lines)


def print_revenue_summary(repository: PipelineRepository) -> None:
    """Monta e imprime o resumo de receita no terminal."""
    summary = build_revenue_summary(repository)
    print(format_revenue_summary(summary))
