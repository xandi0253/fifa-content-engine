"""Fixtures compartilhadas para os testes do Video Engine."""

import subprocess
from pathlib import Path

import pytest


@pytest.fixture
def synthetic_video(tmp_path: Path) -> Path:
    """Gera um vídeo sintético curto (com 2 cortes de cor) para os testes.

    Evita depender de um arquivo real de partida: usa o gerador de padrões
    de teste do próprio ffmpeg (lavfi), com três segmentos de cor diferentes
    para produzir mudanças de cena detectáveis.
    """
    output_path = tmp_path / "synthetic_match.mp4"
    command = [
        "ffmpeg",
        "-y",
        "-f",
        "lavfi",
        "-i",
        "color=c=red:size=320x240:duration=1",
        "-f",
        "lavfi",
        "-i",
        "color=c=blue:size=320x240:duration=1",
        "-f",
        "lavfi",
        "-i",
        "color=c=green:size=320x240:duration=1",
        "-filter_complex",
        "[0:v][1:v][2:v]concat=n=3:v=1:a=0[outv]",
        "-map",
        "[outv]",
        "-r",
        "10",
        str(output_path),
    ]
    subprocess.run(command, capture_output=True, check=True, timeout=60)
    return output_path
