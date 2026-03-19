#!/usr/bin/env bash
set -Eeuo pipefail

echo "[render-deploy] Starting deploy script"

if [[ -z "${DATABASE_URL:-}" ]]; then
	echo "[render-deploy] ERROR: DATABASE_URL is not set"
	exit 1
fi

if [[ -z "${JWT_SECRET_KEY:-}" ]]; then
	echo "[render-deploy] ERROR: JWT_SECRET_KEY is not set"
	exit 1
fi

echo "[render-deploy] Running database migrations"
poetry run flask --app src.app:create_app db upgrade

echo "[render-deploy] Starting gunicorn on port ${PORT:-10000}"
exec poetry run gunicorn src.wsgi:app --bind "0.0.0.0:${PORT:-10000}"