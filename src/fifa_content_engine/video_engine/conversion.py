"""Normalização/conversão de vídeo com ffmpeg."""

from __future__ import annotations

import subprocess
from pathlib import Path

from .errors import VideoConversionError

FFMPEG_TIMEOUT_SECONDS = 600

# Formato padrão de saída para as próximas etapas do pipeline (AI Engine, etc.)
TARGET_VIDEO_CODEC = "libx264"
TARGET_AUDIO_CODEC = "aac"
TARGET_CONTAINER_SUFFIX = ".mp4"


def normalize(source_path: Path, output_dir: Path) -> Path:
    """Converte o vídeo de origem para o formato padrão do pipeline (mp4/h264/aac).

    Não força resolução ou fps: apenas normaliza container e codecs para
    garantir compatibilidade com as etapas seguintes (detecção de cenas,
    IA, geração de clipes).

    Levanta VideoConversionError se o ffmpeg falhar.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / (source_path.stem + TARGET_CONTAINER_SUFFIX)

    command = [
        "ffmpeg",
        "-y",
        "-i",
        str(source_path),
        "-c:v",
        TARGET_VIDEO_CODEC,
        "-c:a",
        TARGET_AUDIO_CODEC,
        "-movflags",
        "+faststart",
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
        raise VideoConversionError(
            "ffmpeg não encontrado no sistema. Verifique se está instalado."
        ) from exc
    except subprocess.TimeoutExpired as exc:
        raise VideoConversionError(f"ffmpeg expirou ao converter {source_path}") from exc

    if result.returncode != 0:
        raise VideoConversionError(
            f"ffmpeg falhou ao converter {source_path}: {result.stderr.strip()[-2000:]}"
        )

    if not output_path.exists():
        raise VideoConversionError(
            f"ffmpeg terminou sem erro mas o arquivo de saída não foi criado: {output_path}"
        )

    return output_path
