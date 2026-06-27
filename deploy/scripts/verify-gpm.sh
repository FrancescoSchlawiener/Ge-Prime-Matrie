#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BASE="${1:-https://schlawiener.space/GPM}"

paths=(
  "/"
  "/static/style.css"
  "/static/app.js"
  "/static/ikurve_lab.js"
  "/static/geometric_editor.js"
  "/api/health"
)

echo "==> Verifying ${BASE}"
for path in "${paths[@]}"; do
  url="${BASE}${path}"
  code=$(curl -sS -o /tmp/gpm-verify.out -w "%{http_code}" "$url")
  if [ "$code" != "200" ]; then
    echo "FAIL $url -> HTTP $code"
    exit 1
  fi
  echo "OK   $url"
done

if ! grep -q 'renderIcurveLab' /tmp/gpm-verify.out 2>/dev/null; then
  if [ -f /tmp/gpm-verify.out ]; then
    node --check /tmp/gpm-verify.out 2>/dev/null || true
  fi
fi

html=$(curl -sS "${BASE}/")
for needle in '/GPM/static/style.css' 'ikurve_lab.js' 'geometric_editor.js' 'data-url-prefix="/GPM"'; do
  if ! echo "$html" | grep -q "$needle"; then
    echo "FAIL homepage missing: $needle"
    exit 1
  fi
done

js=$(curl -sS "${BASE}/static/ikurve_lab.js")
tmp=$(mktemp)
printf '%s' "$js" > "$tmp"
if command -v node >/dev/null 2>&1; then
  if ! node --check "$tmp" 2>/dev/null; then
    echo "FAIL ikurve_lab.js syntax on live site"
    rm -f "$tmp"
    exit 1
  fi
elif ! printf '%s' "$js" | grep -q 'function renderIcurveLab'; then
  echo "FAIL ikurve_lab.js missing renderIcurveLab on live site"
  rm -f "$tmp"
  exit 1
fi
rm -f "$tmp"

echo "==> All checks passed"
