#!/usr/bin/env bash
set -euo pipefail

# First-time VPS setup for schlawiener.space
# Run on the VPS as root: bash deploy/scripts/setup-vps.sh

APP_DIR="${APP_DIR:-/opt/ge-prime-matrix}"
SITE_DIR="${SITE_DIR:-/var/www/schlawiener}"
REPO_URL="${REPO_URL:-https://github.com/francescoschlawiener/ge-prime-matrie.git}"
BRANCH="${BRANCH:-cursor/hostinger-vps-live-pipe-95cf}"

echo "==> Installing packages..."
export DEBIAN_FRONTEND=noninteractive
apt-get update -qq
apt-get install -y -qq git curl ca-certificates nginx certbot python3-certbot-nginx

if ! command -v docker >/dev/null 2>&1; then
  echo "==> Installing Docker..."
  curl -fsSL https://get.docker.com | sh
  systemctl enable docker
  systemctl start docker
fi

echo "==> Creating directories..."
mkdir -p "$APP_DIR" "$SITE_DIR" /var/www/certbot

if [ ! -d "$APP_DIR/.git" ]; then
  echo "==> Cloning repository..."
  git clone "$REPO_URL" "$APP_DIR"
fi

cd "$APP_DIR"
git fetch origin
git checkout "$BRANCH" 2>/dev/null || git checkout -b "$BRANCH" "origin/$BRANCH" 2>/dev/null || git checkout main

echo "==> Syncing static site..."
rsync -a --delete deploy/site/ "$SITE_DIR/"

echo "==> Installing nginx config..."
cp deploy/nginx/schlawiener.space.conf /etc/nginx/sites-available/schlawiener.space
ln -sf /etc/nginx/sites-available/schlawiener.space /etc/nginx/sites-enabled/schlawiener.space
rm -f /etc/nginx/sites-enabled/default

if [ ! -f /etc/letsencrypt/live/schlawiener.space/fullchain.pem ]; then
  echo "==> Obtaining SSL certificate..."
  nginx -t && systemctl reload nginx
  certbot --nginx -d schlawiener.space -d www.schlawiener.space --non-interactive --agree-tos -m admin@schlawiener.space || true
fi

echo "==> Building and starting GPM..."
docker compose -f deploy/docker-compose.yml up -d --build

nginx -t && systemctl reload nginx

echo "==> Done."
echo "    Site:  https://schlawiener.space/"
echo "    GPM:   https://schlawiener.space/GPM/"
echo "    Check: curl -s http://127.0.0.1:5000/api/health"
