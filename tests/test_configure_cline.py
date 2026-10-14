import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location('configure_cline', Path(__file__).resolve().parents[1] / 'scripts/configure_cline.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

class ConfigureTests(unittest.TestCase):
    def test_merge_backup_and_rerun(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'globalState.json'
            original = {'unrelated': {'keep': True}, 'planModeApiProvider': 'cloud'}
            path.write_text(json.dumps(original))
            module.configure(path)
            state = json.loads(path.read_text())
            self.assertEqual(state['unrelated'], original['unrelated'])
            self.assertEqual(state['planModeApiProvider'], 'lmstudio')
            self.assertEqual(state['actModeLmStudioModelId'], 'qwen3.8-27b')
            backup = path.with_name(path.name + '.before-local-qwen.bak')
            self.assertEqual(json.loads(backup.read_text()), original)
            before = path.read_bytes()
            module.configure(path)
            self.assertEqual(path.read_bytes(), before)
            self.assertEqual(json.loads(backup.read_text()), original)

    def test_bad_profile_is_not_overwritten(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'globalState.json'
            path.write_text('[]')
            with self.assertRaises(ValueError):
                module.configure(path)
            self.assertEqual(path.read_text(), '[]')

    def test_fresh_profile(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'nested/globalState.json'
            module.configure(path)
            state = json.loads(path.read_text())
            self.assertTrue(state['welcomeViewCompleted'])
            self.assertEqual(state['planModeLmStudioModelId'], state['actModeLmStudioModelId'])

if __name__ == '__main__':
    unittest.main()
