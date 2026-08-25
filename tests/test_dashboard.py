from pathlib import Path

from fifa_content_engine.data_layer.dashboard import build_summary, format_summary
from fifa_content_engine.data_layer.repository import PipelineRepository


def test_build_summary_with_empty_repository(tmp_path: Path):
    repo = PipelineRepository(tmp_path)

    summary = build_summary(repo)

    assert summary.total_matches == 0
    assert summary.total_clips == 0
    assert summary.total_publications == 0
    assert summary.success_rate == 0.0


def test_build_summary_counts_records_correctly(tmp_path: Path):
    repo = PipelineRepository(tmp_path)
    match_id = repo.record_match(video_path="a.mp4", duration_seconds=90.0, scene_count=3)
    clip_id = repo.record_clip(
        match_id=match_id,
        timestamp_seconds=10.0,
        moment_type="gol",
        score=0.9,
        title="x",
        description="y",
        clip_path="clip.mp4",
        caption="Legenda",
    )
    repo.record_publication(clip_id=clip_id, platform="youtube", success=True, url="https://x")
    repo.record_publication(
        clip_id=clip_id, platform="tiktok", success=False, error_message="timeout"
    )

    summary = build_summary(repo)

    assert summary.total_matches == 1
    assert summary.total_clips == 1
    assert summary.total_publications == 2
    assert summary.successful_publications == 1
    assert summary.failed_publications == 1
    assert summary.success_rate == 0.5
    assert summary.publications_by_platform == {"youtube": 1, "tiktok": 1}


def test_format_summary_includes_key_numbers(tmp_path: Path):
    repo = PipelineRepository(tmp_path)
    repo.record_match(video_path="a.mp4", duration_seconds=90.0, scene_count=3)

    summary = build_summary(repo)
    text = format_summary(summary)

    assert "Partidas processadas: 1" in text
    assert "Dashboard" in text
