from pathlib import Path

import pytest

from fifa_content_engine.data_layer.errors import DataLayerError
from fifa_content_engine.data_layer.json_store import JSONStore


def test_read_all_returns_empty_list_for_missing_table(tmp_path: Path):
    store = JSONStore(tmp_path)

    assert store.read_all("matches") == []


def test_append_and_read_all_roundtrip(tmp_path: Path):
    store = JSONStore(tmp_path)

    store.append("matches", {"id": "1", "video_path": "a.mp4"})
    store.append("matches", {"id": "2", "video_path": "b.mp4"})

    records = store.read_all("matches")

    assert len(records) == 2
    assert records[0]["id"] == "1"
    assert records[1]["id"] == "2"


def test_append_creates_data_dir_if_missing(tmp_path: Path):
    data_dir = tmp_path / "nested" / "data"
    store = JSONStore(data_dir)

    store.append("clips", {"id": "1"})

    assert (data_dir / "clips.json").exists()


def test_read_all_raises_on_corrupted_file(tmp_path: Path):
    store = JSONStore(tmp_path)
    (tmp_path / "matches.json").write_text("isto não é json válido")

    with pytest.raises(DataLayerError):
        store.read_all("matches")


def test_tables_are_independent(tmp_path: Path):
    store = JSONStore(tmp_path)

    store.append("matches", {"id": "m1"})
    store.append("clips", {"id": "c1"})

    assert store.read_all("matches") == [{"id": "m1"}]
    assert store.read_all("clips") == [{"id": "c1"}]
