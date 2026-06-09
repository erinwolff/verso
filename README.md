# Verso

A self-hosted, local-first journaling app with a quiet, firelit-study aesthetic.
A leather book whose page-block visibly thickens as you keep writing.

See [`verso-plan.md`](./verso-plan.md) for the full spec and phased build plan,
and [`CLAUDE.md`](./CLAUDE.md) for the hard constraints.

## Dev

Two processes during development:

```sh
# backend (terminal 1)
cd backend
python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
VERSO_DATA_DIR=../data uvicorn app.main:app --reload --port 8000

# frontend (terminal 2)
cd frontend
npm install
npm run dev          # http://localhost:5173, proxies /api -> :8000
```

## Production (single container)

A multi-stage image builds the SPA and serves it + `/api` from one uvicorn
process. Everything lives in the `./data` volume — back up by copying the folder.

```sh
# edit compose.yaml first: set VERSO_PASSWORD and TZ, pick a host port
docker compose up -d --build
```

Defaults: host port `8330` → container `8000`, `TZ=America/Los_Angeles`. Set
`VERSO_PASSWORD` to enable the login gate, and `VERSO_COOKIE_SECURE=1` when
served over HTTPS behind your reverse proxy. Slots in beside the other trackers
on your Tailscale network.

## Layout

- `backend/` — FastAPI app + `requirements.txt`
- `frontend/` — Svelte 5 + Vite SPA (TypeScript)
- `data/` — journal entries + derived index (gitignored; mounted volume in prod)
