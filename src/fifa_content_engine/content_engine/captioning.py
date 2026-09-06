"""Queima legenda de texto no vídeo do clipe, usando o filtro drawtext do ffmpeg.

Usa `fontfile` explícito (em vez de `font` por nome) para evitar depender
do fontconfig -- em builds do ffmpeg para Windows, o fontconfig às vezes
não encontra o arquivo de configuração padrão e a chamada falha
("Fontconfig error: Cannot load default config file"). Apontar direto
para um arquivo .ttf contorna esse problema por completo.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

from .errors import ContentGenerationError

FFMPEG_TIMEOUT_SECONDS = 300

# Caminhos de fonte comuns por sistema operacional, em ordem de preferência.
# O primeiro que existir no sistema é usado.
_CANDIDATE_FONT_PATHS = [
    "C:/Windows/Fonts/arial.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    "/System/Library/Fonts/Helvetica.ttc",
]


def find_available_font() -> str | None:
    """Retorna o primeiro caminho de fonte válido encontrado no sistema,
    ou None se nenhum dos caminhos conhecidos existir.
    """
    for candidate in _CANDIDATE_FONT_PATHS:
        if Path(candidate).exists():
            return candidate
    return None


def _escape_ffmpeg_text(text: str) -> str:
    """Escapa caracteres especiais do filtro drawtext (: ' \\)."""
    return text.replace("\\", "\\\\").replace(":", "\\:").replace("'", "\\'")


def burn_caption(
    clip_path: Path,
    text: str,
    output_path: Path,
    font_path: str | None = None,
) -> Path:
    """Queima o texto no rodapé do vídeo e salva em output_path.

    Levanta ContentGenerationError se nenhuma fonte for encontrada (nem a
    informada em font_path, nem nenhuma das candidatas conhecidas), ou se
    o ffmpeg falhar.
    """
    resolved_font = font_path or find_available_font()
    if not resolved_font:
        raise ContentGenerationError(
            "Nenhuma fonte encontrada para queimar a legenda. Informe "
            "font_path explicitamente ou instale uma fonte em um dos "
            f"caminhos conhecidos: {_CANDIDATE_FONT_PATHS}"
        )
    if not Path(resolved_font).exists():
        raise ContentGenerationError(f"Arquivo de fonte não encontrado: {resolved_font}")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    escaped_text = _escape_ffmpeg_text(text)
    drawtext_filter = (
        f"drawtext=fontfile='{resolved_font}':text='{escaped_text}':"
        "fontcolor=white:fontsize=28:borderw=2:bordercolor=black:"
        "x=(w-text_w)/2:y=h-th-30"
    )

    command = [
        "ffmpeg",
        "-y",
        "-i",
        str(clip_path),
        "-vf",
        drawtext_filter,
        "-c:a",
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
        raise ContentGenerationError(
            "ffmpeg não encontrado no sistema. Verifique se está instalado."
        ) from exc
    except subprocess.TimeoutExpired as exc:
        raise ContentGenerationError(f"ffmpeg expirou ao legendar {clip_path}") from exc

    if result.returncode != 0:
        raise ContentGenerationError(
            f"ffmpeg falhou ao queimar legenda em {clip_path}: {result.stderr.strip()[-2000:]}"
        )

    if not output_path.exists():
        raise ContentGenerationError(
            f"ffmpeg terminou sem erro mas o vídeo legendado não foi criado: {output_path}"
        )

    return output_path
