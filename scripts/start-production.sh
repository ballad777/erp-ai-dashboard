#!/usr/bin/env bash
set -euo pipefail

APP_PORT="${PORT:-3000}"
API_PORT="${API_PORT:-8000}"

cd /app

mkdir -p \
  generated_outputs/.matplotlib \
  generated_outputs/charts \
  generated_outputs/code \
  generated_outputs/data \
  generated_outputs/models \
  generated_outputs/reports

backend/.venv/bin/uvicorn app.main:app \
  --app-dir backend \
  --host 127.0.0.1 \
  --port "${API_PORT}" &

API_PID=$!

cleanup() {
  kill "${API_PID}" 2>/dev/null || true
}
trap cleanup EXIT

until curl -fsS "http://127.0.0.1:${API_PORT}/health" >/dev/null; do
  sleep 0.5
done

cd /app/frontend
INTERNAL_API_BASE_URL="http://127.0.0.1:${API_PORT}" \
  npm run start -- -H 0.0.0.0 -p "${APP_PORT}"
