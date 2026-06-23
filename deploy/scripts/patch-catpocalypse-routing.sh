#!/usr/bin/env bash
# Move catpocalypse from apex (/) to /catpocalypse/ on the VPS.
# Run once on the VPS after pulling this repo.
set -euo pipefail

COMPOSE="/opt/catpocalypse/deploy/docker-compose.yml"

if [ ! -f "$COMPOSE" ]; then
  echo "Catpocalypse compose not found at $COMPOSE"
  exit 1
fi

cp "$COMPOSE" "${COMPOSE}.bak.$(date +%Y%m%d%H%M%S)"

python3 << 'PY'
from pathlib import Path

path = Path("/opt/catpocalypse/deploy/docker-compose.yml")
text = path.read_text(encoding="utf-8")

old_labels = '''    labels:
      - traefik.enable=true
      # Apex domain
      - traefik.http.routers.catpocalypse.rule=Host(`${DOMAIN}`)
      - traefik.http.routers.catpocalypse.entrypoints=websecure
      - traefik.http.routers.catpocalypse.tls.certresolver=letsencrypt
      - traefik.http.routers.catpocalypse.middlewares=secure-headers@file
      - traefik.http.services.catpocalypse.loadbalancer.server.port=80
      # www -> apex redirect (separate router, same service)
      - traefik.http.routers.catpocalypse-www.rule=Host(`www.${DOMAIN}`)
      - traefik.http.routers.catpocalypse-www.entrypoints=websecure
      - traefik.http.routers.catpocalypse-www.tls.certresolver=letsencrypt
      - traefik.http.routers.catpocalypse-www.middlewares=redirect-www-to-apex@file,secure-headers@file
      - traefik.http.routers.catpocalypse-www.service=catpocalypse'''

new_labels = '''    labels:
      - traefik.enable=true
      - traefik.docker.network=traefik-public
      - traefik.http.routers.catpocalypse.rule=Host(`schlawiener.space`) && PathPrefix(`/catpocalypse`)
      - traefik.http.routers.catpocalypse.entrypoints=websecure
      - traefik.http.routers.catpocalypse.tls.certresolver=letsencrypt
      - traefik.http.routers.catpocalypse.priority=100
      - traefik.http.routers.catpocalypse.middlewares=cat-redirect-slash,cat-stripprefix,secure-headers@file
      - traefik.http.middlewares.cat-redirect-slash.redirectregex.regex=^https?://([^/]+)/catpocalypse$$
      - traefik.http.middlewares.cat-redirect-slash.redirectregex.replacement=https://$${1}/catpocalypse/
      - traefik.http.middlewares.cat-redirect-slash.redirectregex.permanent=true
      - traefik.http.middlewares.cat-stripprefix.stripprefix.prefixes=/catpocalypse
      - traefik.http.services.catpocalypse.loadbalancer.server.port=80
      - traefik.http.routers.catpocalypse-www.rule=Host(`www.schlawiener.space`)
      - traefik.http.routers.catpocalypse-www.entrypoints=websecure
      - traefik.http.routers.catpocalypse-www.tls.certresolver=letsencrypt
      - traefik.http.routers.catpocalypse-www.middlewares=redirect-www-to-apex@file,secure-headers@file
      - traefik.http.routers.catpocalypse-www.service=catpocalypse'''

if old_labels not in text:
    if "PathPrefix(`/catpocalypse`)" in text:
        print("Already patched.")
    else:
        raise SystemExit("Unexpected catpocalypse compose format — patch manually.")
else:
    path.write_text(text.replace(old_labels, new_labels), encoding="utf-8")
    print("Patched catpocalypse routing to /catpocalypse/")
PY

cd /opt/catpocalypse/deploy
docker compose up -d catpocalypse
echo "Catpocalypse now at https://schlawiener.space/catpocalypse/"
