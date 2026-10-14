#!/bin/zsh
set -euo pipefail
LMS="${LMS_BIN:-$HOME/.lmstudio/bin/lms}"
CONTEXT="${QWEN_CONTEXT_LENGTH:-32768}"
[[ "$CONTEXT" == <-> && "$CONTEXT" -ge 4096 && "$CONTEXT" -le 262144 ]] || { echo 'QWEN_CONTEXT_LENGTH must be 4096..262144.' >&2; exit 1; }
if [[ "$(uname -s)" == Darwin && "$CONTEXT" -ge 32768 ]]; then
  memory_bytes=$(/usr/sbin/sysctl -n hw.memsize)
  (( memory_bytes >= 42949672960 )) || { echo 'Default 32K setup requires at least 40 GiB RAM; use QWEN_CONTEXT_LENGTH=8192 on a smaller Mac.' >&2; exit 1; }
fi
"$LMS" daemon up
models_json=$("$LMS" ps --json)
action=$(printf '%s' "$models_json" | python3 -c '
import json,sys
context=int(sys.argv[1])
model=next((m for m in json.load(sys.stdin) if m.get("identifier")=="qwen3.8-27b"),None)
if model is None: print("load")
elif model.get("contextLength")==context and model.get("parallel")==1: print("reuse")
elif model.get("status") not in ("idle",None) or model.get("queued",0): print("busy")
else: print("reload")
' "$CONTEXT")
case "$action" in
  busy) echo 'Qwen is busy with different context settings. Finish the task and rerun.' >&2; exit 1 ;;
  reload) "$LMS" unload qwen3.8-27b ;;
  reuse) echo "Qwen is already loaded with $CONTEXT tokens and one request; reusing it." ;;
esac
if [[ "$action" != reuse ]]; then
  "$LMS" load qwen3.8-27b --identifier qwen3.8-27b --context-length "$CONTEXT" --gpu max --parallel 1 --yes
fi
if ! curl --fail --silent --max-time 3 http://127.0.0.1:1234/v1/models >/dev/null; then
  "$LMS" server start --port 1234 --bind 127.0.0.1
fi
curl --fail --silent --retry 5 --retry-connrefused --retry-delay 1 --max-time 10 http://127.0.0.1:1234/v1/models
