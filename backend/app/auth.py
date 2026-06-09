"""Single-user app password + session cookie (verso-plan.md §7).

A journal is more sensitive than a step count, so even behind a VPN/proxy we add
one boring password. If ``VERSO_PASSWORD`` is empty, auth is disabled (dev
default). The session cookie holds a stateless HMAC token derived from the
password, so it survives restarts and needs no server-side session store; change
the password and all existing sessions are invalidated.
"""
from __future__ import annotations

import hashlib
import hmac
import os

from fastapi import HTTPException, Request

from . import config

SESSION_COOKIE = "verso_session"
COOKIE_MAX_AGE = 60 * 60 * 24 * 30  # 30 days
# Set VERSO_COOKIE_SECURE=1 when served over HTTPS (recommended behind TLS).
COOKIE_SECURE = os.environ.get("VERSO_COOKIE_SECURE", "") in {"1", "true", "True"}


def enabled() -> bool:
    return bool(config.PASSWORD)


def session_token() -> str:
    """Stable token for the current password (single-user, stateless)."""
    return hmac.new(
        config.PASSWORD.encode("utf-8"),
        b"verso-session-v1",
        hashlib.sha256,
    ).hexdigest()


def check_password(password: str) -> bool:
    if not enabled():
        return False
    return hmac.compare_digest(password, config.PASSWORD)


def is_authenticated(request: Request) -> bool:
    if not enabled():
        return True
    cookie = request.cookies.get(SESSION_COOKIE, "")
    return bool(cookie) and hmac.compare_digest(cookie, session_token())


def require_auth(request: Request) -> None:
    if not is_authenticated(request):
        raise HTTPException(status_code=401, detail="authentication required")
