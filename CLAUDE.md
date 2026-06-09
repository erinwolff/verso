# Verso — constraints for Claude Code

Verso is a self-hosted, local-first journaling app. Read `verso-plan.md` for the
full spec and the phased build plan. Work one phase at a time; commit per phase.

## Hard constraints (do not violate)

- **Dark-only.** No light theme. Use the exact design tokens in `verso-plan.md`
  §5 (`frontend/src/lib/tokens.css`). Do not invent colors.
- **Storage is markdown files** in `VERSO_DATA_DIR` (`/data` in prod), one file
  per day: `entries/YYYY-MM-DD.md` with YAML frontmatter. No SQLite.
- **One entry per day.** A date maps to exactly one file.
- **Single small container.** One image: Vite builds the SPA → FastAPI serves
  the static assets *and* the `/api` routes from one uvicorn process.
- **No cloud, no telemetry, no third-party calls.** Self-host EB Garamond (OFL);
  no Google Fonts. No analytics.
- **FOSS deps only.**
- **Serif for entries + book count** (`--serif`); UI chrome may be sans.

## Resolved open decisions (`verso-plan.md` §12)

- Backend: **FastAPI** (Python). Frontend: **Svelte 5 + Vite SPA, TypeScript**.
- Past entries: **editable**; an edit bumps `updated` and recomputes `words`.
- Streak grace: **one-day "warm embers"** — a single missed day keeps the streak
  in a warm-ember state before it resets.
- Thickness curve: `width = clamp(6px, 6 + log2(n+1)*20, 220px)`;
  thickness label = `n * 0.5mm` rendered in cm to one decimal.

## Layout

- `backend/` — FastAPI app (`app/main.py`, etc.), `requirements.txt`.
- `frontend/` — Svelte SPA; `npm run build` → `frontend/dist`.
- `/data` (prod) — entries + `index.json`.

## Dev

- Backend: `cd backend && uvicorn app.main:app --reload --port 8000`
- Frontend: `cd frontend && npm run dev` (proxies `/api` to :8000)
- Prod/single-container: SPA built into `backend/static`, served by FastAPI.
