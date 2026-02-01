#!/usr/bin/env bash
set -euo pipefail

BACKEND_PORT="${PORT:-5050}"
FRONTEND_PORT="${FRONTEND_PORT:-5173}"
FRONTEND_PUBLIC_DOMAIN="${FRONTEND_PUBLIC_DOMAIN:-http://localhost:${FRONTEND_PORT}}"

(
  cd backend
  FRONTEND_PUBLIC_DOMAIN="$FRONTEND_PUBLIC_DOMAIN" PORT="$BACKEND_PORT" python app.py
) &

(
  cd frontend
  npm run dev -- --host 0.0.0.0 --port "$FRONTEND_PORT"
)
