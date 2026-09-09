"""Junta vários clipes em um único vídeo de "melhores momentos"."""

from __future__ import annotations

import subprocess
from pathlib import Path

from fifa_content_engine.ai_engine.moments import Moment

from .caption import build_caption
from .content_piece import ContentPiece
from .errors import ContentGenerationError

FFMPEG_TIMEOUT_SECONDS = 300


def _escape_concat_path(path: Path) -> str:
    """Escapa um caminho para uso no formato de lista do demuxer concat do ffmpeg."""
    return str(path.resolve()).replace("'", "'\\''")


def concatenate_clips(clip_paths: list[Path], output_path: Path) -> Path:
    """Concatena os clipes na ordem dada em um único arquivo de vídeo.

    Recodifica (em vez de -c copy) para garantir compatibilidade mesmo se
    os clipes tiverem pequenas diferenças de parâmetros de codec.
    """
    if not clip_paths:
        raise ContentGenerationError("Nenhum clipe para concatenar")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    list_file = output_path.parent / f"{output_path.stem}_concat_list.txt"
    lines = [f"file '{_escape_concat_path(p)}'" for p in clip_paths]
    list_file.write_text("\n".join(lines), encoding="utf-8")

    command = [
        "ffmpeg",
        "-y",
        "-f",
        "concat",
        "-safe",
        "0",
        "-i",
        str(list_file),
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
        raise ContentGenerationError(
            "ffmpeg não encontrado no sistema. Verifique se está instalado."
        ) from exc
    except subprocess.TimeoutExpired as exc:
        raise ContentGenerationError("ffmpeg expirou ao concatenar clipes") from exc

    if result.returncode != 0:
        raise ContentGenerationError(
            f"ffmpeg falhou ao concatenar clipes: {result.stderr.strip()[-2000:]}"
        )

    if not output_path.exists():
        raise ContentGenerationError(
            f"ffmpeg terminou sem erro mas o vídeo combinado não foi criado: {output_path}"
        )

    return output_path


def build_compilation_piece(
    pieces: list[ContentPiece], output_dir: Path, game_name: str | None = None
) -> ContentPiece:
    """Junta uma lista de ContentPiece já gerados em um único ContentPiece
    representando o vídeo combinado de melhores momentos.
    """
    if not pieces:
        raise ContentGenerationError("Nenhum clipe relevante para compilar")

    clip_paths = [piece.clip_path for piece in pieces]
    output_path = output_dir / "melhores_momentos.mp4"
    combined_path = concatenate_clips(clip_paths, output_path)

    titles = [piece.moment.title for piece in pieces]
    average_score = sum(piece.moment.score for piece in pieces) / len(pieces)

    summary_title = "Melhores Momentos" + (f" — {game_name}" if game_name else "")
    description = "Compilação com: " + "; ".join(titles)

    compiled_moment = Moment(
        timestamp_seconds=0.0,
        is_relevant=True,
        moment_type="compilacao",
        score=average_score,
        title=summary_title,
        description=description,
    )

    caption = build_caption(compiled_moment, game_name=game_name)

    return ContentPiece(moment=compiled_moment, clip_path=combined_path, caption=caption)
