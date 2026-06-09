"""Markdown-file storage for journal entries.

One file per day: ``<DATA_DIR>/entries/YYYY-MM-DD.md`` with YAML frontmatter
(``date``, ``created``, ``updated``, ``words``) followed by the body. This module
is the single source of truth for reading/writing entries and for the derived
index (counts + streak), which is cached in memory and mirrored to
``index.json`` so the book never re-scans the folder on every request.
"""
from __future__ import annotations

import datetime as dt
import json
import re
import threading
from dataclasses import dataclass

import frontmatter

from . import config

_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
_lock = threading.RLock()  # serialize writes + index rebuilds (single-user app)


# --- helpers --------------------------------------------------------------

def is_valid_date(date_str: str) -> bool:
    if not _DATE_RE.match(date_str):
        return False
    try:
        dt.date.fromisoformat(date_str)
        return True
    except ValueError:
        return False


def _path_for(date_str: str):
    return config.ENTRIES_DIR / f"{date_str}.md"


def count_words(body: str) -> int:
    return len(body.split())


def _now_iso() -> str:
    # Local, timezone-aware (e.g. 2026-06-08T21:14:00+01:00), seconds precision.
    return dt.datetime.now().astimezone().replace(microsecond=0).isoformat()


def today_str() -> str:
    return dt.date.today().isoformat()


# --- entries --------------------------------------------------------------

@dataclass
class Entry:
    date: str
    created: str
    updated: str
    words: int
    body: str

    def to_dict(self) -> dict:
        return {
            "date": self.date,
            "created": self.created,
            "updated": self.updated,
            "words": self.words,
            "body": self.body,
        }


def _as_str(value) -> str:
    # PyYAML parses ISO timestamps into datetime/date objects; normalize back
    # to isoformat so the 'T' separator and offset survive a read/write cycle.
    if isinstance(value, (dt.datetime, dt.date)):
        return value.isoformat()
    return str(value) if value is not None else ""


def read_entry(date_str: str) -> Entry | None:
    path = _path_for(date_str)
    if not path.is_file():
        return None
    post = frontmatter.loads(path.read_text(encoding="utf-8"))
    meta = post.metadata
    return Entry(
        date=_as_str(meta.get("date", date_str)),
        created=_as_str(meta.get("created", "")),
        updated=_as_str(meta.get("updated", "")),
        words=int(meta.get("words", count_words(post.content))),
        body=post.content,
    )


def _serialize(entry: Entry) -> str:
    # Written by hand for exact frontmatter shape (spec §3); body verbatim.
    fm = (
        "---\n"
        f"date: {entry.date}\n"
        f"created: {entry.created}\n"
        f"updated: {entry.updated}\n"
        f"words: {entry.words}\n"
        "---\n"
    )
    body = entry.body.rstrip("\n")
    return fm + body + "\n" if body else fm


def write_entry(date_str: str, body: str) -> Entry | None:
    """Create or update the entry for ``date_str``.

    An empty/whitespace-only body deletes the day's file (so an emptied day
    stops counting toward streak/totals). Returns the saved Entry, or ``None``
    if the write resulted in deletion.
    """
    if not is_valid_date(date_str):
        raise ValueError(f"invalid date: {date_str!r}")

    with _lock:
        config.ensure_dirs()
        path = _path_for(date_str)

        if not body.strip():
            if path.is_file():
                path.unlink()
            _rebuild_index_locked()
            return None

        existing = read_entry(date_str)
        now = _now_iso()
        entry = Entry(
            date=date_str,
            created=existing.created if existing and existing.created else now,
            updated=now,
            words=count_words(body),
            body=body,
        )
        path.write_text(_serialize(entry), encoding="utf-8")
        _rebuild_index_locked()
        return entry


def list_dates() -> list[str]:
    """All entry dates, newest first."""
    if not config.ENTRIES_DIR.is_dir():
        return []
    dates = [
        p.stem
        for p in config.ENTRIES_DIR.glob("*.md")
        if is_valid_date(p.stem)
    ]
    dates.sort(reverse=True)
    return dates


def list_entries_meta() -> list[dict]:
    """Lightweight metadata for every entry (newest first), no bodies."""
    out: list[dict] = []
    for date_str in list_dates():
        e = read_entry(date_str)
        if e is None:
            continue
        preview = " ".join(e.body.split())[:120]
        out.append(
            {
                "date": e.date,
                "updated": e.updated,
                "words": e.words,
                "preview": preview,
            }
        )
    return out


# --- streak + index -------------------------------------------------------

def compute_streak(dates: set[dt.date], today: dt.date) -> dict:
    """Consecutive-day streak with a one-day 'warm embers' grace (§8).

    - wrote today              -> state 'lit'
    - wrote yesterday, not today -> state 'warm' (grace; still counts)
    - last entry >= 2 days ago -> state 'cold', count resets to 0
    """
    if not dates:
        return {"count": 0, "state": "cold"}
    last = max(dates)
    gap = (today - last).days
    if gap >= 2:
        return {"count": 0, "state": "cold"}

    count = 0
    day = last
    while day in dates:
        count += 1
        day -= dt.timedelta(days=1)

    state = "lit" if gap <= 0 else "warm"
    return {"count": count, "state": state}


def _build_index() -> dict:
    date_strs = list_dates()
    dates = {dt.date.fromisoformat(d) for d in date_strs}
    total_words = 0
    for d in date_strs:
        e = read_entry(d)
        if e:
            total_words += e.words
    streak = compute_streak(dates, dt.date.today())
    return {
        "entries": len(date_strs),
        "words": total_words,
        "first": date_strs[-1] if date_strs else None,
        "last": date_strs[0] if date_strs else None,
        "streak": streak,
        "generated": _now_iso(),
    }


_index_cache: dict | None = None


def _rebuild_index_locked() -> dict:
    global _index_cache
    _index_cache = _build_index()
    config.ensure_dirs()
    config.INDEX_PATH.write_text(
        json.dumps(_index_cache, indent=2), encoding="utf-8"
    )
    return _index_cache


def rebuild_index() -> dict:
    with _lock:
        return _rebuild_index_locked()


def get_index() -> dict:
    """Cached index. The streak depends on *today*, so recompute it cheaply on
    read (entry/word totals stay cached; only the date math is redone)."""
    global _index_cache
    with _lock:
        if _index_cache is None:
            if config.INDEX_PATH.is_file():
                try:
                    _index_cache = json.loads(
                        config.INDEX_PATH.read_text(encoding="utf-8")
                    )
                except (json.JSONDecodeError, OSError):
                    _index_cache = None
            if _index_cache is None:
                return _rebuild_index_locked()
        # Refresh streak against the current day without a full folder scan.
        dates = {dt.date.fromisoformat(d) for d in list_dates()}
        self_consistent = len(dates) == _index_cache.get("entries")
        if not self_consistent:
            return _rebuild_index_locked()
        _index_cache["streak"] = compute_streak(dates, dt.date.today())
        return _index_cache
