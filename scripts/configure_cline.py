#!/usr/bin/env python3
"""Configure the verified Cline 4.1.24 state schema while Cline is closed."""
import argparse
import json
import os
import shutil
import tempfile
from pathlib import Path


def configure(path):
    path.parent.mkdir(parents=True, exist_ok=True)
    state = json.loads(path.read_text()) if path.exists() else {}
    if not isinstance(state, dict):
        raise ValueError('Cline state must be a JSON object; refusing to overwrite it.')
    desired = {
        'welcomeViewCompleted': True,
        'planModeApiProvider': 'lmstudio',
        'actModeApiProvider': 'lmstudio',
        'planModeLmStudioModelId': 'qwen3.8-27b',
        'actModeLmStudioModelId': 'qwen3.8-27b',
        'lmStudioBaseUrl': 'http://127.0.0.1:1234',
        'lmStudioMaxTokens': os.environ.get('QWEN_CONTEXT_LENGTH', '32768'),
    }
    if all(state.get(key) == value for key, value in desired.items()):
        print('Cline already uses local Qwen for Plan and Act.')
        return
    if path.exists():
        # Keep the original profile backup rather than overwriting it on reruns.
        backup = path.with_name(path.name + '.before-local-qwen.bak')
        if not backup.exists():
            shutil.copy2(path, backup)
            backup.chmod(0o600)
    state.update(desired)
    fd, temporary = tempfile.mkstemp(dir=path.parent, prefix='.local-qwen-')
    try:
        with os.fdopen(fd, 'w') as stream:
            json.dump(state, stream, indent=2)
            stream.write('\n')
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)
    print('Configured Cline Plan and Act for local qwen3.8-27b.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--state-file', type=Path,
                        default=Path.home() / '.cline/data/globalState.json')
    configure(parser.parse_args().state_file)
