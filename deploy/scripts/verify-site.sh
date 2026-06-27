#!/usr/bin/env bash
set -euo pipefail

BASE="${1:-https://schlawiener.space}"

paths=(
  "/"
  "/profil.html"
  "/style.css"
  "/info.txt"
)

echo "==> Verifying ${BASE}"
for path in "${paths[@]}"; do
  url="${BASE}${path}"
  code=$(curl -sS -o /dev/null -w "%{http_code}" "$url")
  if [ "$code" != "200" ]; then
    echo "FAIL $url -> HTTP $code"
    exit 1
  fi
  echo "OK   $url"
done

html=$(curl -sS "${BASE}/")
for needle in 'Ge-Prime-Matrix' 'Protos Arché' 'Catpocalypse' 'project-card'; do
  if ! echo "$html" | grep -q "$needle"; then
    echo "FAIL homepage missing: $needle"
    exit 1
  fi
done

echo "==> Site checks passed"
