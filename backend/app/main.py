"""Verso — FastAPI app entrypoint.

One process serves the JSON API under /api and (in production) the built Svelte
SPA as static files. During local dev the SPA runs under Vite, which proxies
/api here.
"""
from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import APIRouter, Depends, FastAPI, HTTPException, Request, Response as Resp
from fastapi.responses import FileResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from . import auth, config, storage


@asynccontextmanager
async def lifespan(app: FastAPI):
    config.ensure_dirs()
    yield


app = FastAPI(title="Verso", docs_url=None, redoc_url=None, lifespan=lifespan)


# Public router: health + auth handshake (no session required).
api = APIRouter(prefix="/api")
# Protected router: everything that touches the journal requires a session.
protected = APIRouter(prefix="/api", dependencies=[Depends(auth.require_auth)])


@api.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "app": "verso"}


class LoginBody(BaseModel):
    password: str


@api.get("/auth")
def auth_state(request: Request) -> dict:
    """Tells the SPA whether to show the login screen."""
    return {
        "required": auth.enabled(),
        "authenticated": auth.is_authenticated(request),
    }


@api.post("/login")
def login(payload: LoginBody, response: Resp) -> dict:
    if not auth.enabled():
        return {"ok": True, "required": False}
    if not auth.check_password(payload.password):
        raise HTTPException(status_code=401, detail="wrong password")
    response.set_cookie(
        auth.SESSION_COOKIE,
        auth.session_token(),
        max_age=auth.COOKIE_MAX_AGE,
        httponly=True,
        samesite="lax",
        secure=auth.COOKIE_SECURE,
        path="/",
    )
    return {"ok": True, "required": True}


@api.post("/logout")
def logout(response: Resp) -> dict:
    response.delete_cookie(auth.SESSION_COOKIE, path="/")
    return {"ok": True}


class SaveBody(BaseModel):
    body: str


def _valid_date_or_404(date_str: str) -> None:
    if not storage.is_valid_date(date_str):
        raise HTTPException(status_code=400, detail="invalid date (expected YYYY-MM-DD)")


@protected.get("/entry/{date}")
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


@protected.put("/entry/{date}")
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


@protected.get("/entries")
def list_entries() -> dict:
    """Metadata for every entry, newest first (for the nav list in P8)."""
    return {"entries": storage.list_entries_meta()}


@protected.get("/index")
def index() -> dict:
    """Derived stats for the book + ember: counts, words, first/last, streak."""
    return storage.get_index()


# --- Export (first-class; storage is already markdown, §4) -----------------

def _stamp() -> str:
    return storage.today_str()


@protected.get("/export/zip")
def export_zip() -> Response:
    """The entries folder as-is, zipped — the native, lossless format."""
    import io
    import zipfile

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for date_str in reversed(storage.list_dates()):  # oldest first in zip
            path = config.ENTRIES_DIR / f"{date_str}.md"
            if path.is_file():
                zf.write(path, arcname=f"entries/{date_str}.md")
    buf.seek(0)
    return Response(
        content=buf.getvalue(),
        media_type="application/zip",
        headers={
            "Content-Disposition": f'attachment; filename="verso-{_stamp()}.zip"'
        },
    )


@protected.get("/export/markdown")
def export_markdown(order: str = "newest") -> Response:
    """All entries concatenated into one readable .md (newest or oldest first)."""
    dates = storage.list_dates()  # newest first
    if order == "oldest":
        dates = list(reversed(dates))
    parts = ["# Verso — journal export\n"]
    for date_str in dates:
        e = storage.read_entry(date_str)
        if e is None:
            continue
        parts.append(f"\n## {date_str}\n\n{e.body.rstrip()}\n")
    text = "\n".join(parts) + "\n"
    return Response(
        content=text,
        media_type="text/markdown; charset=utf-8",
        headers={
            "Content-Disposition": f'attachment; filename="verso-{_stamp()}.md"'
        },
    )


@protected.get("/export/json")
def export_json() -> Response:
    """[{date, created, updated, words, body}] for piping elsewhere."""
    import json as _json

    out = []
    for date_str in reversed(storage.list_dates()):  # oldest first
        e = storage.read_entry(date_str)
        if e:
            out.append(e.to_dict())
    return Response(
        content=_json.dumps(out, ensure_ascii=False, indent=2),
        media_type="application/json",
        headers={
            "Content-Disposition": f'attachment; filename="verso-{_stamp()}.json"'
        },
    )


app.include_router(api)
app.include_router(protected)


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
