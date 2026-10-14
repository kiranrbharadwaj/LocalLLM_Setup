#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
STATE="$ROOT/.local/open-webui"
if [ ! -x "$STATE/venv/bin/open-webui" ]; then
  echo 'Run bash scripts/setup_openwebui.sh first.' >&2
  exit 1
fi
umask 077
mkdir -p "$STATE/data" "$STATE/cache"
export DATA_DIR="$STATE/data"
export HF_HOME="$STATE/cache/huggingface"
export XDG_CACHE_HOME="$STATE/cache"
export WEBUI_AUTH=True
export ENABLE_OLLAMA_API=False
export ENABLE_OPENAI_API=True
export OPENAI_API_BASE_URL=http://127.0.0.1:1234/v1
export OPENAI_API_BASE_URLS="$OPENAI_API_BASE_URL"
export OPENAI_API_KEY="${LMSTUDIO_API_KEY:-lm-studio}"
export OPENAI_API_KEYS="$OPENAI_API_KEY"
export DEFAULT_MODELS=qwen3.8-27b
export OFFLINE_MODE=True
export RAG_EMBEDDING_MODEL_AUTO_UPDATE=False
export DO_NOT_TRACK=True
export SCARF_NO_ANALYTICS=True
export ANONYMIZED_TELEMETRY=False
# Keep the auto-generated session key in the same private directory on restarts.
cd "$STATE"
exec "$STATE/venv/bin/open-webui" serve --host 127.0.0.1 --port 3000
