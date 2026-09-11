"""Roda o pipeline completo em um vídeo: validação -> detecção de cena ->
análise por IA -> clipe + legenda -> publicação no YouTube.

Uso:
    python run_pipeline.py caminho/para/gravacao.mp4

Requer OPENAI_API_KEY e YOUTUBE_CLIENT_ID/YOUTUBE_CLIENT_SECRET
configurados no .env.
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path


def load_env_file(path: Path) -> None:
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        os.environ.setdefault(key.strip(), value.strip())


load_env_file(Path(".env"))

from fifa_content_engine.ai_engine.analyzer import AIMomentAnalyzer  # noqa: E402
from fifa_content_engine.ai_engine.openai_classifier import OpenAIFrameClassifier  # noqa: E402
from fifa_content_engine.content_engine.compilation import build_compilation_piece  # noqa: E402
from fifa_content_engine.content_engine.generator import ContentGenerator  # noqa: E402
from fifa_content_engine.data_layer.repository import PipelineRepository  # noqa: E402
from fifa_content_engine.publishing_engine.queue import PublishingQueue  # noqa: E402
from fifa_content_engine.publishing_engine.youtube_publisher import YouTubePublisher  # noqa: E402
from fifa_content_engine.video_engine import scene_detection  # noqa: E402
from fifa_content_engine.video_engine.ffmpeg_ingestor import FfmpegVideoIngestor  # noqa: E402
from fifa_content_engine.video_engine.ingestion import VideoSource  # noqa: E402
from fifa_content_engine.video_engine.trimming import trim_video  # noqa: E402

WORK_DIR = Path(".fifa_pipeline_work")


def main() -> None:
    parser = argparse.ArgumentParser(description="Roda o pipeline completo em um vídeo.")
    parser.add_argument("video_path", type=Path, help="Caminho do vídeo de entrada (.mp4)")
    parser.add_argument(
        "--privacy",
        default="private",
        choices=["private", "unlisted", "public"],
        help="Privacidade dos vídeos publicados no YouTube (padrão: private)",
    )
    parser.add_argument(
        "--publish",
        action="store_true",
        help="Publica de verdade no YouTube. Sem essa flag, só mostra o que seria feito.",
    )
    parser.add_argument(
        "--scene-threshold",
        type=float,
        default=scene_detection.DEFAULT_SCENE_THRESHOLD,
        help=(
            "Sensibilidade da detecção de cena, de 0.0 (muito sensível) a "
            f"1.0 (só cortes bruscos). Padrão do projeto: {scene_detection.DEFAULT_SCENE_THRESHOLD}"
        ),
    )
    parser.add_argument(
        "--game",
        default=None,
        help=(
            "Nome do jogo (ex: 'FIFA 26', 'Call of Duty'). Usado no prompt "
            "da IA e nas hashtags/tags. Sem isso, a análise é genérica."
        ),
    )
    parser.add_argument(
        "--burn-captions",
        action="store_true",
        help="Queima o título do momento no rodapé do clipe gerado.",
    )
    parser.add_argument(
        "--start-minute",
        type=float,
        default=None,
        help="Corta o vídeo a partir deste minuto antes de processar (ex: 32).",
    )
    parser.add_argument(
        "--end-minute",
        type=float,
        default=None,
        help="Corta o vídeo até este minuto antes de processar (ex: 37).",
    )
    args = parser.parse_args()

    if (args.start_minute is None) != (args.end_minute is None):
        print("Erro: --start-minute e --end-minute precisam ser usados juntos.")
        sys.exit(1)

    if not args.video_path.exists():
        print(f"Erro: arquivo não encontrado: {args.video_path}")
        sys.exit(1)

    repository = PipelineRepository(Path(os.getenv("DATA_DIR", ".fifa_data")))

    input_video_path = args.video_path
    if args.start_minute is not None:
        print(
            f"\n=== 0/4 — Cortando trecho: {args.start_minute:.1f}min "
            f"até {args.end_minute:.1f}min ==="
        )
        input_video_path = trim_video(
            args.video_path,
            start_seconds=args.start_minute * 60,
            end_seconds=args.end_minute * 60,
            output_dir=WORK_DIR / "trimmed",
        )
        print(f"Trecho cortado: {input_video_path}")

    # 1. Video Engine: validar e normalizar o vídeo, detectar cenas
    print(f"\n=== 1/4 — Video Engine: processando {input_video_path.name} ===")
    ingestor = FfmpegVideoIngestor(
        output_dir=WORK_DIR / "normalized", scene_threshold=args.scene_threshold
    )
    source = VideoSource(path=input_video_path)

    if not ingestor.validate(source):
        print("Erro: vídeo não passou na validação (formato não suportado ou arquivo inválido).")
        sys.exit(1)

    prepared = ingestor.prepare(source)
    print(f"Vídeo normalizado: {prepared.path}")
    print(f"Duração: {prepared.duration_seconds:.1f}s")
    print(f"Cenas candidatas detectadas: {len(prepared.scene_timestamps)}")

    if not prepared.scene_timestamps:
        print("Nenhuma cena detectada -- nada para analisar. Encerrando.")
        return

    match_id = repository.record_match(
        video_path=str(prepared.path),
        duration_seconds=prepared.duration_seconds or 0.0,
        scene_count=len(prepared.scene_timestamps),
    )

    # 2. AI Engine: analisar cada cena candidata
    print(f"\n=== 2/4 — AI Engine: analisando {len(prepared.scene_timestamps)} momentos ===")
    classifier = OpenAIFrameClassifier(game_context=args.game)
    analyzer = AIMomentAnalyzer(classifier=classifier, frame_output_dir=WORK_DIR / "frames")

    moments = analyzer.analyze(prepared.path, prepared.scene_timestamps)
    relevant_moments = [m for m in moments if m.is_relevant]
    print(f"Momentos analisados: {len(moments)}")
    print(f"Momentos relevantes: {len(relevant_moments)}")
    for m in relevant_moments:
        print(
            f"  - [{m.moment_type}] {m.title} (score={m.score:.2f}, t={m.timestamp_seconds:.1f}s)"
        )

    if not relevant_moments:
        print("Nenhum momento relevante encontrado. Encerrando.")
        return

    # 3. Content Engine: gerar clipes e legendas
    print(f"\n=== 3/4 — Content Engine: gerando {len(relevant_moments)} clipes ===")
    generator = ContentGenerator(
        output_dir=WORK_DIR / "clips", game_name=args.game, burn_captions=args.burn_captions
    )
    pieces = generator.generate(prepared.path, moments)
    print(f"Clipes gerados: {len(pieces)}")

    if len(pieces) > 1:
        print(f"Combinando {len(pieces)} clipes em um único vídeo de melhores momentos...")
        pieces = [
            build_compilation_piece(pieces, output_dir=WORK_DIR / "clips", game_name=args.game)
        ]
        print(f"Vídeo combinado: {pieces[0].clip_path}")

    for piece in pieces:
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

    # 4. Publishing Engine: publicar no YouTube
    print(f"\n=== 4/4 — Publishing: YouTube (privacy={args.privacy}) ===")
    if not args.publish:
        print("Modo simulação (sem --publish) -- nada foi publicado de verdade.")
        print("Para publicar de verdade, rode novamente com --publish")
        return

    publisher = YouTubePublisher(privacy_status=args.privacy, game_name=args.game)
    publishing_queue = PublishingQueue(publisher=publisher)
    results = publishing_queue.publish_all(pieces)

    for piece, result in zip(pieces, results, strict=True):
        clip_id = None
        for clip in repository.all_clips():
            if clip["clip_path"] == str(piece.clip_path):
                clip_id = clip["id"]
                break

        repository.record_publication(
            clip_id=clip_id or "desconhecido",
            platform="youtube",
            success=result.success,
            url=result.url,
            error_message=result.error_message,
        )

        if result.success:
            print(f"  ✅ {piece.moment.title} -> {result.url}")
        else:
            print(f"  ❌ {piece.moment.title} -> falhou: {result.error_message}")

    print("\nRode 'python -m fifa_content_engine dashboard' para ver o resumo.")


if __name__ == "__main__":
    main()
