#!/usr/bin/env bash
set -euo pipefail

# First-time VPS setup for schlawiener.space (Traefik stack)
# Run on the VPS as root: bash deploy/scripts/setup-vps.sh

APP_DIR="${APP_DIR:-/opt/ge-prime-matrix}"
REPO_URL="${REPO_URL:-https://github.com/FrancescoSchlawiener/Ge-Prime-Matrie.git}"
BRANCH="${BRANCH:-cursor/hostinger-vps-live-pipe-95cf}"

echo "==> Checking Docker..."
if ! command -v docker >/dev/null 2>&1; then
  curl -fsSL https://get.docker.com | sh
  systemctl enable docker
  systemctl start docker
fi

if ! docker network inspect traefik-public >/dev/null 2>&1; then
  echo "ERROR: traefik-public network missing. Start the Catpocalypse/Traefik stack first."
  exit 1
fi

echo "==> Cloning or updating app..."
mkdir -p "$APP_DIR"
if [ ! -d "$APP_DIR/.git" ]; then
  git clone "$REPO_URL" "$APP_DIR"
fi

cd "$APP_DIR"
git fetch origin
git checkout "$BRANCH"
git pull origin "$BRANCH" || true

echo "==> Moving catpocalypse from / to /catpocalypse/ (if needed)..."
bash deploy/scripts/patch-catpocalypse-routing.sh || true

echo "==> Building and starting site + GPM..."
docker compose -f deploy/docker-compose.yml up -d --build

echo "==> Health check..."
sleep 5
docker exec gpm python -c "import urllib.request; print(urllib.request.urlopen('http://127.0.0.1:5000/api/health').read()[:120])"

echo "==> Done."
echo "    Site:  https://schlawiener.space/"
echo "    GPM:   https://schlawiener.space/GPM/"
echo "    Proto: https://schlawiener.space/protosarche/"
echo "    Cat:   https://schlawiener.space/catpocalypse/"
