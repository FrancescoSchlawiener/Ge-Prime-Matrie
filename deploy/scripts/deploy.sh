#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

ENV_FILE="${ENV_FILE:-deploy/.env.deploy}"
if [ -f "$ENV_FILE" ]; then
  # shellcheck disable=SC1090
  source "$ENV_FILE"
fi

SSH_CONFIG="${VPS_SSH_CONFIG:-deploy/ssh.config.local}"
SSH_HOST="${VPS_SSH_HOST:-schlawiener}"
APP_DIR="${APP_DIR:-/opt/ge-prime-matrix}"
BRANCH="${BRANCH:-cursor/hostinger-vps-live-pipe-95cf}"

SSH_OPTS=(-F "$SSH_CONFIG" "$SSH_HOST")

if [ ! -f "$SSH_CONFIG" ]; then
  echo "Missing $SSH_CONFIG — copy deploy/ssh.config.example to deploy/ssh.config.local"
  exit 1
fi

echo "==> Deploying on VPS..."
ssh "${SSH_OPTS[@]}" bash -s <<REMOTE
set -euo pipefail
cd "$APP_DIR"
git fetch origin
git checkout "$BRANCH"
git pull origin "$BRANCH"
docker compose -f deploy/docker-compose.yml up -d --build
docker exec gpm python -c "import urllib.request; print(urllib.request.urlopen('http://127.0.0.1:5000/api/health').read()[:120])"
REMOTE

echo "==> Deploy complete."
echo "    https://schlawiener.space/"
echo "    https://schlawiener.space/GPM/"
