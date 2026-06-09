"""Verso — FastAPI app entrypoint.

One process serves the JSON API under /api and (in production) the built Svelte
SPA as static files. During local dev the SPA runs under Vite, which proxies
/api here.
"""
from __future__ import annotations

from fastapi import APIRouter, FastAPI, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from . import config, storage

app = FastAPI(title="Verso", docs_url=None, redoc_url=None)


@app.on_event("startup")
def _startup() -> None:
    config.ensure_dirs()


api = APIRouter(prefix="/api")


@api.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "app": "verso"}


class SaveBody(BaseModel):
    body: str


def _valid_date_or_404(date_str: str) -> None:
    if not storage.is_valid_date(date_str):
        raise HTTPException(status_code=400, detail="invalid date (expected YYYY-MM-DD)")


@api.get("/entry/{date}")
def get_entry(date: str) -> dict:
    """Return the day's entry, or an empty shell if nothing is written yet."""
    _valid_date_or_404(date)
    entry = storage.read_entry(date)
    if entry is None:
        return {
            "date": date,
            "body": "",
            "words": 0,
            "created": None,
            "updated": None,
            "exists": False,
        }
    return {**entry.to_dict(), "exists": True}


@api.put("/entry/{date}")
def put_entry(date: str, payload: SaveBody) -> dict:
    """Create/update (or delete, if emptied) the day's entry. Returns the saved
    entry plus the freshly rebuilt index so the UI can update book + stats."""
    _valid_date_or_404(date)
    entry = storage.write_entry(date, payload.body)
    return {
        "entry": entry.to_dict() if entry else None,
        "deleted": entry is None,
        "index": storage.get_index(),
    }


@api.get("/entries")
def list_entries() -> dict:
    """Metadata for every entry, newest first (for the nav list in P8)."""
    return {"entries": storage.list_entries_meta()}


@api.get("/index")
def index() -> dict:
    """Derived stats for the book + ember: counts, words, first/last, streak."""
    return storage.get_index()


app.include_router(api)


# --- Static SPA (production single-container) -----------------------------
# Mounted only if a build is present, so local dev (Vite) is unaffected.
if config.STATIC_DIR.is_dir():
    assets = config.STATIC_DIR / "assets"
    if assets.is_dir():
        app.mount("/assets", StaticFiles(directory=assets), name="assets")

    @app.get("/{full_path:path}")
    def spa(full_path: str):
        # Serve real files (favicon, manifest, fonts); else fall back to the
        # SPA shell so client-side routing works on deep links.
        candidate = config.STATIC_DIR / full_path
        if full_path and candidate.is_file():
            return FileResponse(candidate)
        index = config.STATIC_DIR / "index.html"
        if index.is_file():
            return FileResponse(index)
        return JSONResponse({"detail": "Not found"}, status_code=404)
