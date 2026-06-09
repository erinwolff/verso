"""Runtime configuration, all from the environment."""
from __future__ import annotations

import os
from pathlib import Path

# Where journal entries + the derived index live. /data in the container.
DATA_DIR = Path(os.environ.get("VERSO_DATA_DIR", "./data")).resolve()
ENTRIES_DIR = DATA_DIR / "entries"
INDEX_PATH = DATA_DIR / "index.json"

# Single-user app password (P11). Empty string = auth disabled (dev default).
PASSWORD = os.environ.get("VERSO_PASSWORD", "")

# Directory holding the built SPA. Populated by the Docker build (P12); during
# local dev the SPA is served by Vite instead, so this may not exist.
STATIC_DIR = Path(os.environ.get("VERSO_STATIC_DIR", "./static")).resolve()


def ensure_dirs() -> None:
    ENTRIES_DIR.mkdir(parents=True, exist_ok=True)
