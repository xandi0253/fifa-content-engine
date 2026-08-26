from pathlib import Path

from fifa_content_engine.data_layer.monetization import (
    build_revenue_summary,
    format_revenue_summary,
)
from fifa_content_engine.data_layer.repository import PipelineRepository


def test_build_revenue_summary_empty_repository(tmp_path: Path):
    repo = PipelineRepository(tmp_path)

    summary = build_revenue_summary(repo)

    assert summary.total_amount == 0
    assert summary.entry_count == 0
    assert summary.has_mixed_currencies is False


def test_build_revenue_summary_sums_amounts_and_groups_by_platform(tmp_path: Path):
    repo = PipelineRepository(tmp_path)
    repo.record_revenue(clip_id="c1", platform="youtube", amount=100.0)
    repo.record_revenue(clip_id="c2", platform="youtube", amount=50.0)
    repo.record_revenue(clip_id="c3", platform="tiktok", amount=30.0)

    summary = build_revenue_summary(repo)

    assert summary.total_amount == 180.0
    assert summary.entry_count == 3
    assert summary.total_by_platform == {"youtube": 150.0, "tiktok": 30.0}


def test_build_revenue_summary_flags_mixed_currencies(tmp_path: Path):
    repo = PipelineRepository(tmp_path)
    repo.record_revenue(clip_id="c1", platform="youtube", amount=100.0, currency="BRL")
    repo.record_revenue(clip_id="c2", platform="youtube", amount=20.0, currency="USD")

    summary = build_revenue_summary(repo)

    assert summary.has_mixed_currencies is True
    assert summary.currencies_used == ("BRL", "USD")


def test_build_revenue_summary_single_currency_not_flagged(tmp_path: Path):
    repo = PipelineRepository(tmp_path)
    repo.record_revenue(clip_id="c1", platform="youtube", amount=100.0, currency="BRL")

    summary = build_revenue_summary(repo)

    assert summary.has_mixed_currencies is False


def test_format_revenue_summary_handles_empty():
    from fifa_content_engine.data_layer.monetization import RevenueSummary

    summary = RevenueSummary(total_amount=0, entry_count=0)
    text = format_revenue_summary(summary)

    assert "Nenhuma receita registrada" in text


def test_format_revenue_summary_warns_on_mixed_currencies(tmp_path: Path):
    repo = PipelineRepository(tmp_path)
    repo.record_revenue(clip_id="c1", platform="youtube", amount=100.0, currency="BRL")
    repo.record_revenue(clip_id="c2", platform="youtube", amount=20.0, currency="USD")

    summary = build_revenue_summary(repo)
    text = format_revenue_summary(summary)

    assert "moedas diferentes" in text
