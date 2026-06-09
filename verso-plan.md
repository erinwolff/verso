# Verso — Build Plan

A self-hosted, local-first journaling app with a quiet, firelit-study
aesthetic. Runs as a single lightweight Docker container, reached in the browser
from desktop and phone — same shape as your existing BP and fitness trackers.
The product is built around one motivating idea: **a leather book whose
page-block visibly thickens as you keep writing**, day after day.

This file is the working spec. Build it with Claude Code one phase at a time.
Commit after each phase. Keep this file in the repo root.

---

## 1. Vision (don't lose this)

- **Mood:** a dimly lit fantasy study at dusk. Warm dark background, firelight
  glowing low in one corner, a serif you'd actually want to read by.
- **Desktop layout:** a two-page spread. Left page (*verso*) is today's entry.
  Right page (*recto*) is reserved for the book — the reward you're working
  toward. This is the view that should look great.
- **Mobile layout:** single column, much simpler. Editor on top, a small book +
  streak below. Same palette and serif, none of the spread machinery.
- **The hook:** the book gets physically thicker as entries accumulate. A count
  and a thickness readout ("47 entries · 2.3 cm thick") sell the metaphor. The
  streak shows as "kept alight," tied to the fire theme — not a generic counter.
- **Tone of the incentive:** gentle accumulation, not gamified nagging.

Anti-goals: no cloud account, no telemetry, no notification guilt. A private
object you own, sitting on your own hardware.

---

## 2. Architecture

Self-hosted web app, one container, one volume:

```
[ browser: desktop spread ]  \
                              >--->  [ Verso container :8000 ]  --->  [ /data volume ]
[ browser: mobile PWA      ]  /         (serves UI + API)            entries + index
```

- One image serves both the UI and the API. No separate frontend/backend
  services to orchestrate.
- All state lives in a mounted volume (`/data`), so backups and export are just
  "grab the folder."
- Sits behind whatever you already use for the other trackers (reverse proxy,
  Tailscale/VPN, etc.). Add a simple app password too — see Section 7.

---

## 3. Stack

All FOSS, all runs on Pop!\_OS. Recommendation called out; tradeoffs listed.

### Backend: **FastAPI (Python 3.12)** — decided

Matches your existing BP/fitness trackers, so one mental model across all your
self-hosted apps. FastAPI is tiny and fast, and serves the built frontend's
static assets plus the JSON `/api` from a single uvicorn process.

### Frontend: **Svelte + Vite (SPA, TypeScript)**

Built to static assets by Vite, served by FastAPI. Svelte's transitions make the
firelight flicker and book-growth animations trivial, and the output is small.
Plain Svelte SPA, not SvelteKit — its server features aren't needed and a static
build keeps the single-container story clean.

Single container: Vite builds the SPA → FastAPI serves it + the `/api` routes.

### Styling: **plain CSS with custom properties**

No Tailwind, no UI kit. Bespoke dark theme via the tokens in Section 5.
Self-host **EB Garamond** (OFL) for entries — no Google Fonts call.

### PWA

Add a manifest + service worker so the mobile view installs to your GrapheneOS
home screen and opens full-screen like a native app. Offline-friendly for
reading; writes sync when the container's reachable.

### Storage: **markdown files in the volume** (recommended)

| Option | Pros | Cons |
|---|---|---|
| **Markdown files + frontmatter** ✅ | You own the data as plain text; export is the data itself; greppable, future-proof, syncs/backs-up by copying the folder. | Aggregation is manual (trivial at journal scale). |
| SQLite (one file in the volume) | Conventional for trackers, single-file backup, easy queries. | Opaque blob; export needs a step; weaker "own it" story. |

**Pick markdown files.** One file per day:
`/data/entries/2026-06-08.md` with YAML frontmatter:

```markdown
---
date: 2026-06-08
created: 2026-06-08T21:14:00+01:00
updated: 2026-06-08T21:40:00+01:00
words: 218
---
The rain held off until evening, so I walked the long way back...
```

Past entries are editable: an edit bumps `updated` and recomputes `words`.

Keep a small derived index (counts, streak) cached in memory or
`/data/index.json`, rebuilt on write — so the book doesn't re-scan the folder on
every request.

---

## 4. Export (first-class, not an afterthought)

Offer from a settings/export screen:

- **Zip of markdown** — the entries folder as-is. The native, lossless format.
- **Single combined `.md`** — all entries concatenated, newest or oldest first.
- **JSON** — `[{date, created, words, body}]` for piping elsewhere.
- **PDF (optional)** — a bound-book styled export; nice keepsake, later phase.

Implement as API routes returning a download. Since storage is already
markdown, the zip export is close to free.

---

## 5. Design tokens (exact — this *is* the vibe)

```css
:root {
  --bg:           #1b1613;  /* warm charcoal, the room */
  --surface-edge: #2c2520;  /* hairline borders */
  --ink:          #e3d9ca;  /* entry text */
  --ink-bright:   #e8dfd2;  /* headings, the book count */
  --muted:        #8a7e6f;  /* dates, captions */

  --fire:         #d98a3d;  /* firelight accent, caret, flame icon */
  --fire-glow:    214,128,52; /* rgb() for the radial glow + flicker */
  --fire-soft:    #e0c9a6;  /* "kept alight" text */

  --leather:      #6e3a24;  /* book cover */
  --gilt:         rgba(201,168,106,0.55); /* cover border + crest */
  --page:         #efe6d4;  /* page edges (the thickness) */
  --page-shade:   #d9cdb6;  /* alternating page lines */

  --serif: "EB Garamond", Georgia, serif;
}
```

Rules: entries + book count use `--serif`; UI chrome can be sans. Dark-only.
Firelight is a radial glow low in one corner, flicker optional and **off by
default** (don't distract or burn phone battery).

---

## 6. The filling book (the centerpiece)

`Book.svelte`, on the recto page (and a small version on mobile). Closed leather
book at a slight angle with a **visible page-block** whose **width scales with
entry count**.

- Cover: `--leather` rect, `--gilt` inset border + diamond crest.
- Page-block: stacked thin cream lines (`--page`/`--page-shade` alternating),
  the fore-edge. Width grows with entries.
- Curve: `width = clamp(6px, base + log2(entries+1) * k, maxWidth)`. Log keeps
  every entry feeling additive without overflowing at year five. Tune `k`
  against counts of 1, 30, 365, 1000.
- **Ghost outline:** faint full-size book silhouette behind the real pages, so
  day one is a thin sliver inside what it'll become — aspirational, not sad.
- Caption: `{entries} entries bound · {thickness} thick` (e.g. `entries*0.5mm`
  → cm, one decimal, rounded — no float noise).
- Growth animation: on save, widen the block by one leaf (~400ms tween).

Empty state: ghost book + "Your book is empty. Write the first page."

---

## 7. Auth (a journal is more sensitive than BP numbers)

Even behind your VPN/proxy, add a **single-user app password** — a journal
leaking is worse than a step count leaking.

- Set via env var (`VERSO_PASSWORD`), checked server-side, session cookie.
- Keep it boring: one password, HTTP-only cookie, done. No user accounts.
- If you also gate at the network layer like your other trackers, this is
  defense in depth, not redundancy.

---

## 8. Firelight & streak

- **Hearth:** a `pointer-events:none` radial glow layer behind the spread,
  `radial-gradient(120% 90% at 18% 118%, rgba(var(--fire-glow),0.34), ... transparent)`.
  Optional ~5s opacity flicker, off by default.
- **Streak:** computed server-side from entry dates. Ember pill: flame icon +
  "{n} days kept alight". Forgiving — a one-day grace ("embers still warm")
  before reset. Decide before building.

---

## 9. Docker

Single multi-stage image, small runtime layer.

`Dockerfile` (sketch):
```dockerfile
# build the Svelte SPA
FROM node:22-alpine AS web
WORKDIR /web
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ .
RUN npm run build            # -> /web/dist

# runtime: FastAPI serves the SPA + /api
FROM python:3.12-slim
WORKDIR /app
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY backend/ .
COPY --from=web /web/dist ./static
ENV VERSO_DATA_DIR=/data
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

`compose.yaml` (sketch):
```yaml
services:
  verso:
    build: .
    ports: ["8000:8000"]
    volumes:
      - ./data:/data
    environment:
      - VERSO_DATA_DIR=/data
      - VERSO_PASSWORD=change-me
    restart: unless-stopped
```

Slots into your existing reverse-proxy/VPN setup like the other trackers.

---

## 10. Phased build plan

- [ ] **P0 — Scaffold.** FastAPI backend in `backend/app/` + Vite Svelte SPA in
      `frontend/`. uvicorn serves the built SPA; dev runs Vite + uvicorn. Commit.
- [ ] **P1 — Design system.** `tokens.css`, self-host EB Garamond, dark room
      background, empty centered spread frame.
- [ ] **P2 — Storage layer.** FastAPI module: read/write/list entry markdown
      files in `VERSO_DATA_DIR`, parse/write frontmatter, maintain the index.
- [ ] **P3 — Editor (verso).** Left-page textarea, serif ink, fire caret, date
      header. Debounced autosave via `/api`. Loads/saves **any date** (past
      entries editable); edits bump `updated` + `words`.
- [ ] **P4 — Stats + streak.** Counts and streak from the index, exposed to the
      UI.
- [ ] **P5 — The book (recto).** `Book.svelte`: cover, page-block, ghost
      outline, caption, log-scaled width, wired to live counts.
- [ ] **P6 — Hearth + ember.** Firelight glow + flicker toggle; "kept alight"
      pill.
- [ ] **P7 — Growth + day-one polish.** Animate page-block on save; verify
      empty and year-five states both look intentional.
- [ ] **P8 — Navigation.** Browse past entries (quiet date list / prev-next) and
      open any for editing. Needed because past entries are editable.
- [ ] **P9 — Responsive + PWA.** Mobile single-column layout; manifest + service
      worker; installs on GrapheneOS.
- [ ] **P10 — Export.** Zip / combined-md / JSON download routes.
- [ ] **P11 — Auth.** Single-user password + session cookie.
- [ ] **P12 — Docker.** Dockerfile + compose; build, run, mount volume, deploy
      behind your proxy.
- [ ] **P13 (optional) — PDF export.** Bound-book styled PDF.

---

## 11. Driving this with Claude Code

- Keep this file in the repo root. Start sessions: *"Read verso-plan.md. We're
  on phase P_. Implement only that phase, then stop for review."*
- One phase per commit. The design details in Sections 5–6 are easy to lose if
  it batches phases.
- Add a short `CLAUDE.md` with hard constraints: dark-only, exact tokens,
  markdown-file storage, single small container, no telemetry/cloud, FOSS deps.
- Resolve ambiguities yourself and tell it the decision — don't let it guess.

---

## 12. Open decisions

- ~~Backend: SvelteKit vs FastAPI~~ → **FastAPI** (matches your other trackers).
- Streak grace: hard reset vs one-day "warm embers"?
- ~~Past entries: editable or frozen~~ → **editable** (edits bump `updated`).
- One entry per day (recommended — reinforces cadence) vs multiple?
- Thickness curve `k`: tune against 1 / 30 / 365 / 1000 entries.
