"""Command-line entry point: mostra as configurações ou o dashboard do pipeline."""

import argparse
from pathlib import Path

from .config import get_settings
from .data_layer.dashboard import print_summary
from .data_layer.repository import PipelineRepository


def main() -> None:
    parser = argparse.ArgumentParser(prog="fifa-content-engine")
    subparsers = parser.add_subparsers(dest="command")
    subparsers.add_parser(
        "dashboard", help="Mostra o resumo do pipeline (partidas/clipes/publicações)"
    )

    args = parser.parse_args()
    settings = get_settings()

    if args.command == "dashboard":
        repository = PipelineRepository(Path(settings.data_dir))
        print_summary(repository)
    else:
        print(f"{settings.app_name} | ambiente={settings.environment}")


if __name__ == "__main__":
    main()
