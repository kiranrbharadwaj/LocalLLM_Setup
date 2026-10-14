#!/usr/bin/env bash
# Default setup after LM Studio/model and documented prerequisites are present.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
command -v npm >/dev/null || { echo 'Install Node.js 18+ and npm first.' >&2; exit 1; }
[[ -x "$HOME/.lmstudio/bin/lms" ]] || { echo 'Install lms and download Qwen first; see SETUP_GUIDE.md.' >&2; exit 1; }
export QWEN_CONTEXT_LENGTH="${QWEN_CONTEXT_LENGTH:-32768}"
# Stop early if the editor is open, before changing the runtime.
bash "$ROOT/scripts/setup_cline.sh"
zsh "$ROOT/scripts/start-qwen.sh"
bash "$ROOT/scripts/install_macos_startup.sh"
npm --prefix "$ROOT/documents/Repo/assistant-bridge" ci
bash "$ROOT/scripts/setup_openwebui.sh"
echo 'Default setup complete. Qwen API is running; login startup is enabled.'
echo 'Open VS Code and use Cline. For browser chat: bash scripts/start_openwebui.sh'
