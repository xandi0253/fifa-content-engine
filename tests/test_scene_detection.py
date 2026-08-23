from pathlib import Path

from fifa_content_engine.video_engine.scene_detection import detect_scenes


def test_detect_scenes_finds_cuts_in_synthetic_video(synthetic_video: Path):
    timestamps = detect_scenes(synthetic_video, threshold=0.3)

    # O vídeo sintético tem 2 cortes de cor (red->blue, blue->green) em ~1s e ~2s.
    assert len(timestamps) >= 2
    assert all(isinstance(t, float) for t in timestamps)


def test_detect_scenes_returns_empty_for_static_video(tmp_path: Path):
    import subprocess

    static_video = tmp_path / "static.mp4"
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-f",
            "lavfi",
            "-i",
            "color=c=red:size=320x240:duration=2",
            "-r",
            "10",
            str(static_video),
        ],
        capture_output=True,
        check=True,
        timeout=60,
    )

    timestamps = detect_scenes(static_video, threshold=0.3)
    assert timestamps == []
