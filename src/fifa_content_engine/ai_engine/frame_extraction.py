"""Extração de frames de vídeo em timestamps específicos, via ffmpeg."""

from __future__ import annotations

import subprocess
from pathlib import Path

from .errors import FrameExtractionError

FFMPEG_TIMEOUT_SECONDS = 60


def extract_frame(video_path: Path, timestamp_seconds: float, output_dir: Path) -> Path:
    """Extrai um único frame do vídeo no timestamp informado, como JPEG.

    Levanta FrameExtractionError se o ffmpeg falhar ou o arquivo não for gerado.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    safe_timestamp = f"{timestamp_seconds:.3f}".replace(".", "_")
    output_path = output_dir / f"{video_path.stem}_frame_{safe_timestamp}.jpg"

    command = [
        "ffmpeg",
        "-y",
        "-ss",
        str(timestamp_seconds),
        "-i",
        str(video_path),
        "-frames:v",
        "1",
        "-q:v",
        "2",
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
        raise FrameExtractionError(
            "ffmpeg não encontrado no sistema. Verifique se está instalado."
        ) from exc
    except subprocess.TimeoutExpired as exc:
        raise FrameExtractionError(
            f"ffmpeg expirou ao extrair frame de {video_path} em {timestamp_seconds}s"
        ) from exc

    if result.returncode != 0:
        raise FrameExtractionError(
            f"ffmpeg falhou ao extrair frame de {video_path} em {timestamp_seconds}s: "
            f"{result.stderr.strip()[-2000:]}"
        )

    if not output_path.exists():
        raise FrameExtractionError(
            f"ffmpeg terminou sem erro mas o frame não foi criado: {output_path}"
        )

    return output_path
