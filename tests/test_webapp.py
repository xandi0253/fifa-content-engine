import time
from pathlib import Path
from unittest.mock import patch

import pytest

from fifa_content_engine.ai_engine.moments import Moment
from fifa_content_engine.content_engine.content_piece import ContentPiece
from fifa_content_engine.pipeline import PipelineResult
from fifa_content_engine.webapp.app import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    return app.test_client()


def _wait_for_job(client, job_id, timeout=3.0):
    """Espera o job terminar (status != 'running'), com timeout."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        data = client.get(f"/status/{job_id}").get_json()
        if data.get("status") != "running":
            return data
        time.sleep(0.05)
    raise TimeoutError("Job não terminou a tempo")


def test_index_page_loads(client):
    response = client.get("/")

    assert response.status_code == 200
    assert b"FIFA CONTENT ENGINE" in response.data


def test_run_without_video_path_returns_400(client):
    response = client.post("/run", json={"video_path": ""})

    assert response.status_code == 400
    assert "caminho" in response.get_json()["error"].lower()


def test_run_with_missing_file_returns_400(client, tmp_path: Path):
    missing = tmp_path / "missing.mp4"
    response = client.post("/run", json={"video_path": str(missing)})

    assert response.status_code == 400
    assert "não encontrado" in response.get_json()["error"].lower()


def test_status_for_unknown_job_returns_404(client):
    response = client.get("/status/does-not-exist")

    assert response.status_code == 404


def test_run_success_flow_returns_content_piece(client, synthetic_video: Path):
    moment = Moment(
        timestamp_seconds=1.0,
        is_relevant=True,
        moment_type="vitoria",
        score=0.9,
        title="Gol de Teste",
        description="Descrição de teste",
    )
    piece = ContentPiece(moment=moment, clip_path=Path("/tmp/fake_clip.mp4"), caption="caption")

    def fake_run_pipeline(video_path, **kwargs):
        on_progress = kwargs.get("on_progress")
        if on_progress:
            on_progress("Processando...")
        result = PipelineResult(video_path=video_path)
        result.content_piece = piece
        return result

    with patch("fifa_content_engine.webapp.app.run_pipeline", side_effect=fake_run_pipeline):
        response = client.post("/run", json={"video_path": str(synthetic_video)})
        job_id = response.get_json()["job_id"]
        data = _wait_for_job(client, job_id)

    assert data["status"] == "done"
    assert data["content_piece"]["title"] == "Gol de Teste"
    assert "Processando..." in data["log"]


def test_run_reports_stopped_reason(client, synthetic_video: Path):
    def fake_run_pipeline(video_path, **kwargs):
        result = PipelineResult(video_path=video_path)
        result.stopped_reason = "Nenhuma cena detectada."
        return result

    with patch("fifa_content_engine.webapp.app.run_pipeline", side_effect=fake_run_pipeline):
        response = client.post("/run", json={"video_path": str(synthetic_video)})
        job_id = response.get_json()["job_id"]
        data = _wait_for_job(client, job_id)

    assert data["status"] == "done"
    assert data["stopped_reason"] == "Nenhuma cena detectada."


def test_run_captures_unexpected_exceptions(client, synthetic_video: Path):
    def fake_run_pipeline(video_path, **kwargs):
        raise RuntimeError("falha simulada")

    with patch("fifa_content_engine.webapp.app.run_pipeline", side_effect=fake_run_pipeline):
        response = client.post("/run", json={"video_path": str(synthetic_video)})
        job_id = response.get_json()["job_id"]
        data = _wait_for_job(client, job_id)

    assert data["status"] == "error"
    assert "falha simulada" in data["error"]


def test_run_with_publish_success_includes_url(client, synthetic_video: Path):
    from fifa_content_engine.publishing_engine.queue import PublishResult

    moment = Moment(
        timestamp_seconds=1.0,
        is_relevant=True,
        moment_type="vitoria",
        score=0.9,
        title="Gol",
        description="desc",
    )
    piece = ContentPiece(moment=moment, clip_path=Path("/tmp/fake_clip.mp4"), caption="caption")

    def fake_run_pipeline(video_path, **kwargs):
        result = PipelineResult(video_path=video_path)
        result.content_piece = piece
        result.publish_results = [
            PublishResult(content_piece=piece, success=True, url="https://youtube.com/watch?v=X")
        ]
        return result

    with patch("fifa_content_engine.webapp.app.run_pipeline", side_effect=fake_run_pipeline):
        response = client.post("/run", json={"video_path": str(synthetic_video), "publish": True})
        job_id = response.get_json()["job_id"]
        data = _wait_for_job(client, job_id)

    assert data["publish_url"] == "https://youtube.com/watch?v=X"
