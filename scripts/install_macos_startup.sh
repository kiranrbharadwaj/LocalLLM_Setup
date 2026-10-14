#!/usr/bin/env bash
# Install a per-user login job; run again to update the copied launcher.
set -euo pipefail
if [[ "$(uname -s)" != Darwin ]]; then
  echo 'This installer requires macOS.' >&2
  exit 1
fi
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LABEL=com.kiran.local-qwen
AGENTS="$HOME/Library/LaunchAgents"
SUPPORT="$AGENTS/LocalLLM"
LOGS="$HOME/Library/Logs/LocalLLM"
PLIST="$AGENTS/$LABEL.plist"
DOMAIN="gui/$(id -u)"
command -v python3 >/dev/null || { echo 'Python 3 is required.' >&2; exit 1; }
[[ -x "$HOME/.lmstudio/bin/lms" ]] || { echo 'Install LM Studio lms first (see README).' >&2; exit 1; }
mkdir -p "$SUPPORT" "$LOGS"
cp "$ROOT/scripts/start-qwen.sh" "$SUPPORT/start-qwen.sh"
python3 - "$PLIST" <<'PY'
import plistlib,sys
from pathlib import Path
home=Path.home()
config={
 'Label':'com.kiran.local-qwen',
 'ProgramArguments':['/bin/zsh',str(home/'Library/LaunchAgents/LocalLLM/start-qwen.sh')],
 'RunAtLoad':True,
 'KeepAlive':{'SuccessfulExit':False},
 'ThrottleInterval':30,
 'EnvironmentVariables':{'HOME':str(home),'PATH':f'{home}/.local/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin'},
 'StandardOutPath':str(home/'Library/Logs/LocalLLM/startup.log'),
 'StandardErrorPath':str(home/'Library/Logs/LocalLLM/startup-error.log'),
}
Path(sys.argv[1]).write_bytes(plistlib.dumps(config))
PY
plutil -lint "$PLIST"
if launchctl print "$DOMAIN/$LABEL" >/dev/null 2>&1; then
  launchctl bootout "$DOMAIN/$LABEL"
fi
launchctl bootstrap "$DOMAIN" "$PLIST"
launchctl kickstart "$DOMAIN/$LABEL"
echo "Enabled Qwen startup at login. Logs: $LOGS"
echo "Check: launchctl print $DOMAIN/$LABEL"
