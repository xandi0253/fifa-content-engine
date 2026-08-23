"""Detecção de mudanças de cena usando o filtro nativo do ffmpeg.

Esta é uma detecção puramente visual (mudança brusca de quadro), sem
nenhuma análise de conteúdo por IA — isso é escopo da Sprint 3 (AI Engine).
O objetivo aqui é apenas gerar candidatos a "momentos" que a IA vai
analisar depois.
"""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

from .errors import SceneDetectionError

FFMPEG_TIMEOUT_SECONDS = 600

# Sensibilidade da detecção: 0.0 (tudo é cena nova) a 1.0 (só mudanças bruscas).
DEFAULT_SCENE_THRESHOLD = 0.4

_PTS_TIME_PATTERN = re.compile(r"pts_time:(?P<time>[0-9.]+)")


def detect_scenes(video_path: Path, threshold: float = DEFAULT_SCENE_THRESHOLD) -> list[float]:
    """Retorna uma lista de timestamps (em segundos) onde há mudança de cena.

    Levanta SceneDetectionError se o ffmpeg falhar ao processar o vídeo.
    """
    command = [
        "ffmpeg",
        "-i",
        str(video_path),
        "-filter:v",
        f"select='gt(scene,{threshold})',showinfo",
        "-f",
        "null",
        "-",
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
        raise SceneDetectionError(
            "ffmpeg não encontrado no sistema. Verifique se está instalado."
        ) from exc
    except subprocess.TimeoutExpired as exc:
        raise SceneDetectionError(f"ffmpeg expirou ao detectar cenas em {video_path}") from exc

    # ffmpeg escreve os logs do showinfo no stderr, mesmo em execução bem-sucedida.
    if result.returncode != 0:
        raise SceneDetectionError(
            f"ffmpeg falhou ao detectar cenas em {video_path}: {result.stderr.strip()[-2000:]}"
        )

    timestamps = [float(match.group("time")) for match in _PTS_TIME_PATTERN.finditer(result.stderr)]
    return timestamps
