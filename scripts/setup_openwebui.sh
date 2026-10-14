#!/usr/bin/env bash
# macOS/Linux: isolated Open WebUI installation; no system Python changes.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
STATE="$ROOT/.local/open-webui"
mkdir -p "$STATE/bin" "$STATE/config"
export UV_CACHE_DIR="$STATE/cache"
export UV_PYTHON_INSTALL_DIR="$STATE/python"
if command -v uv >/dev/null 2>&1; then
  UV="$(command -v uv)"
else
  UV="$STATE/bin/uv"
  if [ ! -x "$UV" ]; then
    curl --fail --location --retry 3 https://astral.sh/uv/install.sh -o "$STATE/install-uv.sh"
    UV_INSTALL_DIR="$STATE/bin" UV_NO_MODIFY_PATH=1 XDG_CONFIG_HOME="$STATE/config" sh "$STATE/install-uv.sh"
  fi
fi
if [ ! -x "$STATE/venv/bin/python" ]; then
  "$UV" venv --python 3.11 "$STATE/venv"
fi
"$UV" pip install --python "$STATE/venv/bin/python" 'open-webui==0.11.4'
printf '\nInstalled Open WebUI. Start it with:\n  bash "%s/scripts/start_openwebui.sh"\n' "$ROOT"
