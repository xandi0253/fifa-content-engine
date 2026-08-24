"""Corte de clipes de vídeo com ffmpeg, a partir de uma janela de tempo."""

from __future__ import annotations

import subprocess
from pathlib import Path

from .errors import ClipExtractionError

FFMPEG_TIMEOUT_SECONDS = 300


def extract_clip(
    video_path: Path,
    start_seconds: float,
    end_seconds: float,
    output_dir: Path,
    clip_name: str,
) -> Path:
    """Corta o trecho [start_seconds, end_seconds] do vídeo em um novo arquivo.

    Usa re-encode (não apenas -c copy) para garantir cortes precisos no
    ponto exato solicitado, já que o vídeo de entrada já está normalizado
    (Sprint 2) e o custo de recodificar um clipe curto é baixo.

    Levanta ClipExtractionError se o ffmpeg falhar ou o arquivo não for gerado.
    """
    if end_seconds <= start_seconds:
        raise ClipExtractionError(
            f"Janela de corte inválida: start={start_seconds}, end={end_seconds}"
        )

    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"{clip_name}.mp4"
    duration = end_seconds - start_seconds

    command = [
        "ffmpeg",
        "-y",
        "-ss",
        str(start_seconds),
        "-i",
        str(video_path),
        "-t",
        str(duration),
        "-c:v",
        "libx264",
        "-c:a",
        "aac",
        str(output_path),
    ]

    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=FFMPEG_TIMEOUT_SECONDS,
            check=False,
        )
    except FileNotFoundError as exc:
        raise ClipExtractionError(
            "ffmpeg não encontrado no sistema. Verifique se está instalado."
        ) from exc
    except subprocess.TimeoutExpired as exc:
        raise ClipExtractionError(f"ffmpeg expirou ao cortar clipe de {video_path}") from exc

    if result.returncode != 0:
        raise ClipExtractionError(
            f"ffmpeg falhou ao cortar clipe de {video_path}: {result.stderr.strip()[-2000:]}"
        )

    if not output_path.exists():
        raise ClipExtractionError(
            f"ffmpeg terminou sem erro mas o clipe não foi criado: {output_path}"
        )

    return output_path
