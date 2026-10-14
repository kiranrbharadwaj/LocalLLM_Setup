#!/usr/bin/env bash
# macOS Apple Silicon; pin the extension whose state schema was verified.
set -euo pipefail
[[ "$(uname -s)" == Darwin && "$(uname -m)" == arm64 ]] || { echo 'Requires Apple Silicon macOS.' >&2; exit 1; }
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
command -v python3 >/dev/null || { echo 'Python 3 is required.' >&2; exit 1; }
# Do not race an editor/CLI that could rewrite shared Cline state.
for pattern in '/(Visual Studio Code|Code)\.app/Contents/MacOS/' '(^|/)cline( |$)'; do
  if pgrep -f "$pattern" >/dev/null; then
    echo 'Quit VS Code and Cline CLI, then rerun. Cursor can stay open.' >&2
    exit 1
  else
    result=$?
    [[ "$result" == 1 ]] || { echo 'Cannot inspect running processes. Run from a normal Mac Terminal.' >&2; exit 1; }
  fi
done
CODE=''
for APP in '/Applications/Visual Studio Code.app' "$HOME/Applications/Visual Studio Code.app"; do
  if [[ -x "$APP/Contents/Resources/app/bin/code" ]]; then
    CODE="$APP/Contents/Resources/app/bin/code"
    break
  fi
done
if [[ -z "$CODE" ]]; then
  mkdir -p "$ROOT/.local/vscode-download" "$HOME/Applications"
  curl --fail --location --retry 3 https://update.code.visualstudio.com/latest/darwin-arm64/stable -o "$ROOT/.local/vscode-download/vscode.zip"
  ditto -x -k "$ROOT/.local/vscode-download/vscode.zip" "$ROOT/.local/vscode-download"
  ditto "$ROOT/.local/vscode-download/Visual Studio Code.app" "$HOME/Applications/Visual Studio Code.app"
  CODE="$HOME/Applications/Visual Studio Code.app/Contents/Resources/app/bin/code"
fi
"$CODE" --install-extension saoudrizwan.claude-dev@4.1.24 --force
python3 "$ROOT/scripts/configure_cline.py"
echo 'Ready: open VS Code, open your project, and use the Cline sidebar.'
echo 'Both Plan and Act use LM Studio. Use Cline, not Copilot Chat or Cursor Agent.'
