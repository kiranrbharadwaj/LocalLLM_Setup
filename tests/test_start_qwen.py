import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts/start-qwen.sh'

class LauncherTests(unittest.TestCase):
    def run_launcher(self, model):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'models.json').write_text(json.dumps([model] if model else []))
            for name, text in {
                'lms': '#!/bin/sh\necho "$*" >> "$FIXTURE/log"\nif [ "$1" = ps ]; then cat "$FIXTURE/models.json"; fi\n',
                'curl': '#!/bin/sh\nexit 0\n',
            }.items():
                path = root / name
                path.write_text(text)
                path.chmod(0o755)
            env = dict(os.environ, FIXTURE=str(root), LMS_BIN=str(root/'lms'),
                       QWEN_CONTEXT_LENGTH='8192', PATH=str(root)+os.pathsep+os.environ['PATH'])
            result = subprocess.run(['zsh', str(SCRIPT)], env=env, text=True, capture_output=True)
            return result, (root/'log').read_text()

    def test_matching_model_is_reused(self):
        result, log = self.run_launcher({'identifier':'qwen3.8-27b','contextLength':8192,'parallel':1,'status':'idle'})
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn('load qwen', log)

    def test_idle_mismatch_is_reloaded(self):
        result, log = self.run_launcher({'identifier':'qwen3.8-27b','contextLength':4096,'parallel':4,'status':'idle'})
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('unload qwen3.8-27b', log)
        self.assertIn('--context-length 8192 --gpu max --parallel 1 --yes', log)

    def test_busy_mismatch_is_not_interrupted(self):
        result, log = self.run_launcher({'identifier':'qwen3.8-27b','contextLength':4096,'parallel':4,'status':'generating'})
        self.assertNotEqual(result.returncode, 0)
        self.assertNotIn('unload', log)
        self.assertNotIn('--context-length', log)

if __name__ == '__main__':
    unittest.main()
