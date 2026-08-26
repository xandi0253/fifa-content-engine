"""Command-line entry point: configurações, dashboard, analytics e receita do pipeline."""

import argparse
from pathlib import Path

from .config import get_settings
from .data_layer.analytics import print_performance_report
from .data_layer.dashboard import print_summary
from .data_layer.monetization import print_revenue_summary
from .data_layer.repository import PipelineRepository


def main() -> None:
    parser = argparse.ArgumentParser(prog="fifa-content-engine")
    subparsers = parser.add_subparsers(dest="command")
    subparsers.add_parser(
        "dashboard", help="Mostra o resumo do pipeline (partidas/clipes/publicações)"
    )
    subparsers.add_parser(
        "analytics", help="Mostra o desempenho do conteúdo (views/likes por plataforma)"
    )
    subparsers.add_parser("revenue", help="Mostra a receita registrada manualmente")

    args = parser.parse_args()
    settings = get_settings()
    repository = PipelineRepository(Path(settings.data_dir))

    if args.command == "dashboard":
        print_summary(repository)
    elif args.command == "analytics":
        print_performance_report(repository)
    elif args.command == "revenue":
        print_revenue_summary(repository)
    else:
        print(f"{settings.app_name} | ambiente={settings.environment}")


if __name__ == "__main__":
    main()
