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

`npm run build` produces `frontend/dist`; the Docker image copies it to
`backend/static`, and FastAPI serves both the SPA and `/api` from one process.
See `verso-plan.md` §9 (Docker phase P12).

## Layout

- `backend/` — FastAPI app + `requirements.txt`
- `frontend/` — Svelte 5 + Vite SPA (TypeScript)
- `data/` — journal entries + derived index (gitignored; mounted volume in prod)
