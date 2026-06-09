import datetime as dt

import pytest

from app import config, storage


@pytest.fixture
def data_dir(tmp_path, monkeypatch):
    """Point storage at a fresh temp data dir and reset the index cache."""
    monkeypatch.setattr(config, "DATA_DIR", tmp_path)
    monkeypatch.setattr(config, "ENTRIES_DIR", tmp_path / "entries")
    monkeypatch.setattr(config, "INDEX_PATH", tmp_path / "index.json")
    monkeypatch.setattr(storage, "_index_cache", None, raising=False)
    config.ensure_dirs()
    return tmp_path


@pytest.fixture
def d():
    return dt.date
