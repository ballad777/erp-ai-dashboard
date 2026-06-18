FROM node:22-bookworm-slim AS frontend-builder

WORKDIR /app/frontend

ENV NEXT_TELEMETRY_DISABLED=1
ENV INTERNAL_API_BASE_URL=http://127.0.0.1:8000

COPY frontend/package*.json ./
RUN npm ci

COPY frontend/ ./
RUN npm run build -- --webpack


FROM node:22-bookworm-slim AS runner

WORKDIR /app

ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1
ENV PYTHONUNBUFFERED=1
ENV MPLCONFIGDIR=/app/generated_outputs/.matplotlib

RUN apt-get update \
  && apt-get install -y --no-install-recommends \
    curl \
    fonts-dejavu-core \
    libgomp1 \
    python3 \
    python3-pip \
    python3-venv \
  && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt backend/requirements.txt
RUN python3 -m venv /app/backend/.venv \
  && /app/backend/.venv/bin/pip install --upgrade pip \
  && /app/backend/.venv/bin/pip install --no-cache-dir -r backend/requirements.txt

COPY backend/ backend/
COPY sample_datasets/ sample_datasets/
COPY generated_outputs/README.md generated_outputs/README.md
COPY generated_outputs/charts/.gitkeep generated_outputs/charts/.gitkeep
COPY generated_outputs/code/.gitkeep generated_outputs/code/.gitkeep
COPY generated_outputs/data/.gitkeep generated_outputs/data/.gitkeep
COPY generated_outputs/models/.gitkeep generated_outputs/models/.gitkeep
COPY generated_outputs/reports/.gitkeep generated_outputs/reports/.gitkeep

COPY --from=frontend-builder /app/frontend/.next frontend/.next
COPY --from=frontend-builder /app/frontend/node_modules frontend/node_modules
COPY --from=frontend-builder /app/frontend/package*.json frontend/
COPY --from=frontend-builder /app/frontend/next.config.js frontend/next.config.js

COPY scripts/start-production.sh scripts/start-production.sh
RUN chmod +x scripts/start-production.sh

EXPOSE 3000

CMD ["/app/scripts/start-production.sh"]
