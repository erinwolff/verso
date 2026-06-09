# syntax=docker/dockerfile:1

# --- build the Svelte SPA -------------------------------------------------
FROM node:22-alpine AS web
WORKDIR /web
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ .
RUN npm run build            # -> /web/dist

# --- runtime: FastAPI serves the SPA + /api -------------------------------
FROM python:3.12-slim
WORKDIR /app

# tzdata so a TZ env var makes "today"/timestamps reflect the user's local day
# (the streak rolls over at local midnight, not UTC).
RUN apt-get update \
    && apt-get install -y --no-install-recommends tzdata \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ .
COPY --from=web /web/dist ./static

ENV VERSO_DATA_DIR=/data \
    VERSO_STATIC_DIR=/app/static \
    PYTHONUNBUFFERED=1
EXPOSE 8000

# Lightweight healthcheck using the stdlib (no curl in slim).
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8000/api/health').status==200 else 1)"

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
