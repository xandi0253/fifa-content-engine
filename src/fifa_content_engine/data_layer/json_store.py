"""Armazenamento simples em arquivos JSON, um arquivo por "tabela".

Cada tabela é um arquivo `<nome>.json` contendo uma lista de registros
(dicts). Não é um banco de dados de verdade — é o suficiente para o
volume de dados deste pipeline (execuções batch, não alta concorrência).
"""

from __future__ import annotations

import json
from pathlib import Path

from .errors import DataLayerError


class JSONStore:
    """Lê e escreve listas de registros em arquivos JSON, por tabela."""

    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def _table_path(self, table: str) -> Path:
        return self.data_dir / f"{table}.json"

    def read_all(self, table: str) -> list[dict]:
        """Retorna todos os registros da tabela. Lista vazia se não existir ainda."""
        path = self._table_path(table)
        if not path.exists():
            return []

        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise DataLayerError(f"Arquivo de dados corrompido: {path}") from exc

    def append(self, table: str, record: dict) -> None:
        """Adiciona um registro ao final da tabela."""
        records = self.read_all(table)
        records.append(record)
        path = self._table_path(table)
        path.write_text(json.dumps(records, indent=2, ensure_ascii=False), encoding="utf-8")
