from pathlib import Path

from fifa_content_engine.data_layer.repository import PipelineRepository


def test_record_match_persists_and_returns_id(tmp_path: Path):
    repo = PipelineRepository(tmp_path)

    match_id = repo.record_match(video_path="/tmp/match.mp4", duration_seconds=90.0, scene_count=5)

    matches = repo.all_matches()
    assert len(matches) == 1
    assert matches[0]["id"] == match_id
    assert matches[0]["video_path"] == "/tmp/match.mp4"
    assert matches[0]["scene_count"] == 5


def test_record_clip_persists_with_match_reference(tmp_path: Path):
    repo = PipelineRepository(tmp_path)
    match_id = repo.record_match(video_path="/tmp/match.mp4", duration_seconds=90.0, scene_count=5)

    clip_id = repo.record_clip(
        match_id=match_id,
        timestamp_seconds=12.0,
        moment_type="gol",
        score=0.9,
        title="Gol de placa",
        description="Descrição",
        clip_path="/tmp/clip.mp4",
        caption="Legenda",
    )

    clips = repo.all_clips()
    assert len(clips) == 1
    assert clips[0]["id"] == clip_id
    assert clips[0]["match_id"] == match_id
    assert clips[0]["moment_type"] == "gol"


def test_record_publication_persists_with_clip_reference(tmp_path: Path):
    repo = PipelineRepository(tmp_path)
    clip_id = repo.record_clip(
        match_id="m1",
        timestamp_seconds=12.0,
        moment_type="gol",
        score=0.9,
        title="x",
        description="y",
        clip_path="/tmp/clip.mp4",
        caption="Legenda",
    )

    repo.record_publication(
        clip_id=clip_id, platform="youtube", success=True, url="https://youtube.com/x"
    )

    publications = repo.all_publications()
    assert len(publications) == 1
    assert publications[0]["clip_id"] == clip_id
    assert publications[0]["platform"] == "youtube"
    assert publications[0]["success"] is True


def test_record_publication_stores_error_message_on_failure(tmp_path: Path):
    repo = PipelineRepository(tmp_path)

    repo.record_publication(clip_id="c1", platform="tiktok", success=False, error_message="timeout")

    publications = repo.all_publications()
    assert publications[0]["success"] is False
    assert publications[0]["error_message"] == "timeout"


def test_ids_are_unique_across_records(tmp_path: Path):
    repo = PipelineRepository(tmp_path)

    id1 = repo.record_match(video_path="a.mp4", duration_seconds=1.0, scene_count=0)
    id2 = repo.record_match(video_path="b.mp4", duration_seconds=1.0, scene_count=0)

    assert id1 != id2


def test_record_stats_snapshot_persists_metrics(tmp_path):
    repo = PipelineRepository(tmp_path)

    snapshot_id = repo.record_stats_snapshot(
        clip_id="c1", platform="youtube", metrics={"view_count": 100, "like_count": 10}
    )

    snapshots = repo.all_stats_snapshots()
    assert len(snapshots) == 1
    assert snapshots[0]["id"] == snapshot_id
    assert snapshots[0]["clip_id"] == "c1"
    assert snapshots[0]["metrics"]["view_count"] == 100
