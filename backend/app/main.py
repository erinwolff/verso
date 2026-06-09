"""Verso — FastAPI app entrypoint.

One process serves the JSON API under /api and (in production) the built Svelte
SPA as static files. During local dev the SPA runs under Vite, which proxies
/api here.
"""
from __future__ import annotations

from fastapi import APIRouter, FastAPI
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from . import config

app = FastAPI(title="Verso", docs_url=None, redoc_url=None)


@app.on_event("startup")
def _startup() -> None:
    config.ensure_dirs()


api = APIRouter(prefix="/api")


@api.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "app": "verso"}


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
