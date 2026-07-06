#!/usr/bin/env sh
# Stop dev servers on ports 8000 and 5173 (Linux/macOS).
for port in 8000 5173; do
  pid=$(lsof -ti :"$port" 2>/dev/null || true)
  if [ -n "$pid" ]; then
    kill $pid 2>/dev/null || true
    echo "Stopped port $port (pid $pid)"
  fi
done
