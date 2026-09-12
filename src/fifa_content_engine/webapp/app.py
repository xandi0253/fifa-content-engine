"""Interface web local para rodar o pipeline sem usar o terminal.

Uso:
    python -m fifa_content_engine.webapp.app

Abre em http://127.0.0.1:5000 -- é uma ferramenta local, de um usuário
só, sem login. Não deve ser exposta publicamente na internet.
"""

from __future__ import annotations

import os
import threading
import uuid
from pathlib import Path

from flask import Flask, jsonify, render_template, request

from fifa_content_engine.pipeline import run_pipeline
from fifa_content_engine.video_engine import scene_detection

app = Flask(__name__)

_jobs: dict[str, dict] = {}
_jobs_lock = threading.Lock()


def _load_env_file(path: Path) -> None:
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        os.environ.setdefault(key.strip(), value.strip())


_load_env_file(Path(".env"))


def _update_job(job_id: str, **fields) -> None:
    with _jobs_lock:
        _jobs[job_id].update(fields)


def _append_log(job_id: str, message: str) -> None:
    with _jobs_lock:
        _jobs[job_id]["log"].append(message)


def _run_job(job_id: str, video_path: Path, options: dict) -> None:
    try:
        result = run_pipeline(
            video_path,
            game=options.get("game") or None,
            privacy=options.get("privacy", "private"),
            burn_captions=options.get("burn_captions", False),
            publish=options.get("publish", False),
            scene_threshold=options.get("scene_threshold", scene_detection.DEFAULT_SCENE_THRESHOLD),
            on_progress=lambda message: _append_log(job_id, message),
        )

        if result.stopped_reason:
            _update_job(job_id, status="done", stopped_reason=result.stopped_reason)
            return

        publish_result = result.publish_results[0] if result.publish_results else None

        _update_job(
            job_id,
            status="done",
            content_piece={
                "title": result.content_piece.moment.title,
                "description": result.content_piece.moment.description,
                "clip_path": str(result.content_piece.clip_path),
            }
            if result.content_piece
            else None,
            publish_url=publish_result.url if publish_result else None,
            publish_error=publish_result.error_message if publish_result else None,
        )
    except Exception as exc:  # noqa: BLE001 -- job runner precisa capturar tudo para reportar ao front-end
        _append_log(job_id, f"Erro inesperado: {exc}")
        _update_job(job_id, status="error", error=str(exc))


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/run", methods=["POST"])
def run():
    data = request.get_json(force=True)
    video_path_str = (data.get("video_path") or "").strip()

    if not video_path_str:
        return jsonify({"error": "Informe o caminho do arquivo de vídeo."}), 400

    video_path = Path(video_path_str)
    if not video_path.exists():
        return jsonify({"error": f"Arquivo não encontrado: {video_path}"}), 400

    job_id = uuid.uuid4().hex[:12]
    with _jobs_lock:
        _jobs[job_id] = {"status": "running", "log": []}

    thread = threading.Thread(
        target=_run_job,
        args=(job_id, video_path, data),
        daemon=True,
    )
    thread.start()

    return jsonify({"job_id": job_id})


@app.route("/status/<job_id>")
def status(job_id: str):
    with _jobs_lock:
        job = _jobs.get(job_id)
        if job is None:
            return jsonify({"error": "Job não encontrado."}), 404
        return jsonify(dict(job))


def main() -> None:
    app.run(debug=True, port=5000)


if __name__ == "__main__":
    main()
