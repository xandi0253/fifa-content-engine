"""CLI: roda o pipeline completo em um vídeo (validação -> detecção de
cena -> análise por IA -> clipe + legenda -> compilação -> publicação).

Uso:
    python run_pipeline.py caminho/para/gravacao.mp4

Requer OPENAI_API_KEY e YOUTUBE_CLIENT_ID/YOUTUBE_CLIENT_SECRET
configurados no .env. A lógica do pipeline mora em
fifa_content_engine.pipeline -- este script é só a interface de linha
de comando por cima dela.
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

from fifa_content_engine.pipeline import run_pipeline  # noqa: E402
from fifa_content_engine.video_engine import scene_detection  # noqa: E402

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
    args = parser.parse_args()

    if not args.video_path.exists():
        print(f"Erro: arquivo não encontrado: {args.video_path}")
        sys.exit(1)

    input_video_path = args.video_path

    def on_progress(message: str) -> None:
        print(message)

    result = run_pipeline(
        input_video_path,
        game=args.game,
        privacy=args.privacy,
        burn_captions=args.burn_captions,
        publish=args.publish,
        scene_threshold=args.scene_threshold,
        work_dir=WORK_DIR,
        on_progress=on_progress,
    )

    if result.stopped_reason:
        print(f"\n{result.stopped_reason}")
        return

    if not args.publish:
        print("\nPara publicar de verdade, rode novamente com --publish")
    else:
        print("\nRode 'python -m fifa_content_engine dashboard' para ver o resumo.")


if __name__ == "__main__":
    main()
