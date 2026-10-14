#!/bin/zsh
set -euo pipefail
LMS="$HOME/.lmstudio/bin/lms"
"$LMS" daemon up
models_json=$("$LMS" ps --json)
loaded=$(printf '%s' "$models_json" | python3 -c 'import json,sys; print(any(m.get("identifier") == "qwen3.8-27b" for m in json.load(sys.stdin)))')
if [[ "$loaded" == "True" ]]; then
  echo "Qwen is already loaded; reusing it."
else
  "$LMS" load 'qwen3.8-27b' --identifier qwen3.8-27b --context-length 8192 --gpu max --yes
fi
if curl --fail --silent --max-time 3 http://127.0.0.1:1234/v1/models >/dev/null; then
  echo "Local API is already responding on port 1234."
else
  "$LMS" server start --port 1234 --bind 127.0.0.1
fi
