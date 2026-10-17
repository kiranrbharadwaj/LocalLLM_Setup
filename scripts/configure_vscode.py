#!/usr/bin/env python3
"""Prefer Cline by hiding built-in Copilot UI in global macOS VS Code settings."""
import json
import shutil
from pathlib import Path


def configure(path):
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        settings = json.loads(path.read_text()) if path.exists() else {}
    except json.JSONDecodeError:
        print('Existing VS Code settings use JSON comments or unsupported syntax; left unchanged.')
        print('Set "chat.disableAIFeatures": true in VS Code User Settings manually.')
        return
    if not isinstance(settings, dict):
        raise ValueError('VS Code settings must be an object.')
    if settings.get('chat.disableAIFeatures') is True:
        return
    if path.exists():
        backup = path.with_name(path.name + '.before-local-qwen.bak')
        if not backup.exists():
            shutil.copy2(path, backup)
    settings['chat.disableAIFeatures'] = True
    path.write_text(json.dumps(settings, indent=2) + '\n')


if __name__ == '__main__':
    configure(Path.home() / 'Library/Application Support/Code/User/settings.json')
