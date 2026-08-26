import time
from pathlib import Path

from fifa_content_engine.data_layer.analytics import (
    build_performance_report,
    format_performance_report,
)
from fifa_content_engine.data_layer.repository import PipelineRepository


def _make_clip(repo: PipelineRepository, moment_type: str = "gol") -> str:
    match_id = repo.record_match(video_path="a.mp4", duration_seconds=90.0, scene_count=3)
    return repo.record_clip(
        match_id=match_id,
        timestamp_seconds=10.0,
        moment_type=moment_type,
        score=0.9,
        title="x",
        description="y",
        clip_path="clip.mp4",
        caption="Legenda",
    )


def test_build_performance_report_empty_without_snapshots(tmp_path: Path):
    repo = PipelineRepository(tmp_path)
    _make_clip(repo)

    entries = build_performance_report(repo)

    assert entries == []


def test_build_performance_report_includes_clip_and_metrics(tmp_path: Path):
    repo = PipelineRepository(tmp_path)
    clip_id = _make_clip(repo, moment_type="gol")
    repo.record_stats_snapshot(
        clip_id=clip_id, platform="youtube", metrics={"view_count": 500, "like_count": 40}
    )

    entries = build_performance_report(repo)

    assert len(entries) == 1
    assert entries[0].clip_id == clip_id
    assert entries[0].moment_type == "gol"
    assert entries[0].platform == "youtube"
    assert entries[0].metrics["view_count"] == 500


def test_build_performance_report_uses_latest_snapshot_per_platform(tmp_path: Path):
    repo = PipelineRepository(tmp_path)
    clip_id = _make_clip(repo)

    repo.record_stats_snapshot(clip_id=clip_id, platform="youtube", metrics={"view_count": 100})
    time.sleep(0.01)
    repo.record_stats_snapshot(clip_id=clip_id, platform="youtube", metrics={"view_count": 300})

    entries = build_performance_report(repo)

    assert len(entries) == 1
    assert entries[0].metrics["view_count"] == 300


def test_build_performance_report_separates_platforms_for_same_clip(tmp_path: Path):
    repo = PipelineRepository(tmp_path)
    clip_id = _make_clip(repo)

    repo.record_stats_snapshot(clip_id=clip_id, platform="youtube", metrics={"view_count": 100})
    repo.record_stats_snapshot(clip_id=clip_id, platform="tiktok", metrics={"view_count": 900})

    entries = build_performance_report(repo)

    assert len(entries) == 2
    platforms = {e.platform for e in entries}
    assert platforms == {"youtube", "tiktok"}


def test_format_performance_report_handles_empty_list():
    text = format_performance_report([])

    assert "Nenhuma métrica registrada" in text


def test_format_performance_report_sorts_by_view_count_descending(tmp_path: Path):
    repo = PipelineRepository(tmp_path)
    clip_id = _make_clip(repo)
    repo.record_stats_snapshot(clip_id=clip_id, platform="youtube", metrics={"view_count": 50})
    repo.record_stats_snapshot(clip_id=clip_id, platform="tiktok", metrics={"view_count": 900})

    entries = build_performance_report(repo)
    text = format_performance_report(entries)

    tiktok_index = text.index("tiktok")
    youtube_index = text.index("youtube")
    assert tiktok_index < youtube_index
