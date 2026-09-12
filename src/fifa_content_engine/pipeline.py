"""Orquestra o pipeline completo: validação -> detecção de cena -> análise
por IA -> clipe + legenda -> compilação -> publicação no YouTube.

Usado tanto pelo script de linha de comando (run_pipeline.py) quanto
pela interface web (webapp/app.py) -- a lógica mora aqui uma única vez.
"""

from __future__ import annotations

import os
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path

from .ai_engine.analyzer import AIMomentAnalyzer
from .ai_engine.moments import Moment
from .ai_engine.openai_classifier import OpenAIFrameClassifier
from .content_engine.compilation import build_compilation_piece
from .content_engine.content_piece import ContentPiece
from .content_engine.generator import ContentGenerator
from .data_layer.repository import PipelineRepository
from .publishing_engine.queue import PublishingQueue, PublishResult
from .publishing_engine.youtube_publisher import YouTubePublisher
from .video_engine import scene_detection
from .video_engine.ffmpeg_ingestor import FfmpegVideoIngestor
from .video_engine.ingestion import VideoSource

WORK_DIR = Path(".fifa_pipeline_work")

ProgressCallback = Callable[[str], None]


@dataclass
class PipelineResult:
    """Resultado estruturado de uma execução do pipeline."""

    video_path: Path
    duration_seconds: float = 0.0
    scenes_detected: int = 0
    moments: list[Moment] = field(default_factory=list)
    content_piece: ContentPiece | None = None
    publish_results: list[PublishResult] | None = None
    stopped_reason: str | None = None


def _noop(_message: str) -> None:
    return None


def run_pipeline(
    video_path: Path,
    *,
    game: str | None = None,
    privacy: str = "private",
    burn_captions: bool = False,
    publish: bool = False,
    scene_threshold: float = scene_detection.DEFAULT_SCENE_THRESHOLD,
    work_dir: Path = WORK_DIR,
    data_dir: Path | None = None,
    on_progress: ProgressCallback = _noop,
) -> PipelineResult:
    """Roda o pipeline completo em um vídeo e retorna um PipelineResult.

    on_progress é chamado com uma mensagem de texto a cada etapa relevante,
    para permitir acompanhar o andamento (usado pela interface web para
    reportar progresso em tempo real).
    """
    if not video_path.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {video_path}")

    repository = PipelineRepository(data_dir or Path(os.getenv("DATA_DIR", ".fifa_data")))
    result = PipelineResult(video_path=video_path)

    # 1. Video Engine
    on_progress(f"Processando vídeo: {video_path.name}")
    ingestor = FfmpegVideoIngestor(
        output_dir=work_dir / "normalized", scene_threshold=scene_threshold
    )
    source = VideoSource(path=video_path)

    if not ingestor.validate(source):
        result.stopped_reason = "Vídeo não passou na validação (formato não suportado)."
        on_progress(result.stopped_reason)
        return result

    prepared = ingestor.prepare(source)
    result.duration_seconds = prepared.duration_seconds or 0.0
    result.scenes_detected = len(prepared.scene_timestamps)
    on_progress(
        f"Vídeo normalizado ({result.duration_seconds:.0f}s). "
        f"{result.scenes_detected} cena(s) candidata(s) detectada(s)."
    )

    if not prepared.scene_timestamps:
        result.stopped_reason = "Nenhuma cena detectada -- nada para analisar."
        on_progress(result.stopped_reason)
        return result

    match_id = repository.record_match(
        video_path=str(prepared.path),
        duration_seconds=result.duration_seconds,
        scene_count=result.scenes_detected,
    )

    # 2. AI Engine
    on_progress(f"Analisando {result.scenes_detected} momento(s) com IA...")
    classifier = OpenAIFrameClassifier(game_context=game)
    analyzer = AIMomentAnalyzer(classifier=classifier, frame_output_dir=work_dir / "frames")
    moments = analyzer.analyze(prepared.path, prepared.scene_timestamps)
    result.moments = moments

    relevant_moments = [m for m in moments if m.is_relevant]
    on_progress(f"{len(relevant_moments)} momento(s) relevante(s) de {len(moments)} analisado(s).")

    if not relevant_moments:
        result.stopped_reason = "Nenhum momento relevante encontrado."
        on_progress(result.stopped_reason)
        return result

    # 3. Content Engine
    on_progress(f"Gerando {len(relevant_moments)} clipe(s)...")
    generator = ContentGenerator(
        output_dir=work_dir / "clips", game_name=game, burn_captions=burn_captions
    )
    pieces = generator.generate(prepared.path, moments)

    if len(pieces) > 1:
        on_progress(f"Combinando {len(pieces)} clipes em um vídeo de melhores momentos...")
        pieces = [build_compilation_piece(pieces, output_dir=work_dir / "clips", game_name=game)]

    piece = pieces[0]
    result.content_piece = piece
    on_progress(f"Clipe pronto: {piece.clip_path.name}")

    repository.record_clip(
        match_id=match_id,
        timestamp_seconds=piece.moment.timestamp_seconds,
        moment_type=piece.moment.moment_type,
        score=piece.moment.score,
        title=piece.moment.title,
        description=piece.moment.description,
        clip_path=str(piece.clip_path),
        caption=piece.caption,
    )

    # 4. Publishing Engine
    if not publish:
        on_progress("Modo simulação -- nada foi publicado.")
        return result

    on_progress(f"Publicando no YouTube (privacidade: {privacy})...")
    publisher = YouTubePublisher(privacy_status=privacy, game_name=game)
    publishing_queue = PublishingQueue(publisher=publisher)
    publish_results = publishing_queue.publish_all(pieces)
    result.publish_results = publish_results

    for clip_piece, publish_result in zip(pieces, publish_results, strict=True):
        clip_id = None
        for clip in repository.all_clips():
            if clip["clip_path"] == str(clip_piece.clip_path):
                clip_id = clip["id"]
                break

        repository.record_publication(
            clip_id=clip_id or "desconhecido",
            platform="youtube",
            success=publish_result.success,
            url=publish_result.url,
            error_message=publish_result.error_message,
        )

        if publish_result.success:
            on_progress(f"Publicado com sucesso: {publish_result.url}")
        else:
            on_progress(f"Falha ao publicar: {publish_result.error_message}")

    return result
