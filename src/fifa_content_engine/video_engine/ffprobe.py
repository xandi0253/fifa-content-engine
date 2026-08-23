"""Wrapper fino em torno do ffprobe para inspecionar arquivos de vídeo."""

from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass
from pathlib import Path

from .errors import VideoValidationError

FFPROBE_TIMEOUT_SECONDS = 30


@dataclass(frozen=True)
class ProbeResult:
    """Metadados relevantes extraídos de um arquivo de vídeo via ffprobe."""

    format_name: str
    duration_seconds: float
    has_video_stream: bool
    video_codec: str | None


def probe(path: Path) -> ProbeResult:
    """Executa ffprobe no arquivo e retorna seus metadados.

    Levanta VideoValidationError se o ffprobe não conseguir ler o arquivo
    (arquivo corrompido, formato não suportado, ou não é um vídeo).
    """
    command = [
        "ffprobe",
        "-v",
        "error",
        "-print_format",
        "json",
        "-show_format",
        "-show_streams",
        str(path),
    ]

    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=FFPROBE_TIMEOUT_SECONDS,
            check=False,
        )
    except FileNotFoundError as exc:
        raise VideoValidationError(
            "ffprobe não encontrado no sistema. Verifique se o ffmpeg está instalado."
        ) from exc
    except subprocess.TimeoutExpired as exc:
        raise VideoValidationError(f"ffprobe expirou ao analisar {path}") from exc

    if result.returncode != 0:
        raise VideoValidationError(f"ffprobe não conseguiu ler {path}: {result.stderr.strip()}")

    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise VideoValidationError(f"Saída inválida do ffprobe para {path}") from exc

    format_info = data.get("format", {})
    streams = data.get("streams", [])

    video_streams = [s for s in streams if s.get("codec_type") == "video"]
    has_video_stream = bool(video_streams)
    video_codec = video_streams[0].get("codec_name") if video_streams else None

    try:
        duration_seconds = float(format_info.get("duration", 0.0))
    except (TypeError, ValueError):
        duration_seconds = 0.0

    return ProbeResult(
        format_name=format_info.get("format_name", "unknown"),
        duration_seconds=duration_seconds,
        has_video_stream=has_video_stream,
        video_codec=video_codec,
    )
