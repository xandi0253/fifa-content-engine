"""Corta um trecho específico de um vídeo (do minuto X ao minuto Y).

Usa -c copy (sem recodificar) para ser rápido -- o mesmo padrão que já
era feito manualmente com ffmpeg antes de rodar o pipeline em um trecho
específico, agora embutido no próprio pipeline.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

from .errors import TrimError

FFMPEG_TIMEOUT_SECONDS = 120


def trim_video(
    video_path: Path, start_seconds: float, end_seconds: float, output_dir: Path
) -> Path:
    """Corta o trecho [start_seconds, end_seconds] do vídeo em um novo arquivo.

    Levanta TrimError se o intervalo for inválido ou o ffmpeg falhar.
    """
    if end_seconds <= start_seconds:
        raise TrimError(
            f"Intervalo inválido: início ({start_seconds}s) deve ser "
            f"menor que o fim ({end_seconds}s)"
        )
    if start_seconds < 0:
        raise TrimError(f"Início não pode ser negativo: {start_seconds}s")

    output_dir.mkdir(parents=True, exist_ok=True)
    duration = end_seconds - start_seconds
    output_path = output_dir / f"{video_path.stem}_trim_{int(start_seconds)}_{int(end_seconds)}.mp4"

    command = [
        "ffmpeg",
        "-y",
        "-ss",
        str(start_seconds),
        "-i",
        str(video_path),
        "-t",
        str(duration),
        "-c",
        "copy",
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
        raise TrimError("ffmpeg não encontrado no sistema. Verifique se está instalado.") from exc
    except subprocess.TimeoutExpired as exc:
        raise TrimError(f"ffmpeg expirou ao cortar trecho de {video_path}") from exc

    if result.returncode != 0:
        raise TrimError(
            f"ffmpeg falhou ao cortar trecho de {video_path}: {result.stderr.strip()[-2000:]}"
        )

    if not output_path.exists():
        raise TrimError(
            f"ffmpeg terminou sem erro mas o arquivo cortado não foi criado: {output_path}"
        )

    return output_path
