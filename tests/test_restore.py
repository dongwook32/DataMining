import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
import zipfile

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts/restore_cleanup.py'


class RestoreTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.backup = self.root / '.backups/cleanup-20261116'
        self.backup.mkdir(parents=True)
        if SCRIPT.exists():
            shutil.copy2(SCRIPT, self.backup / 'restore.py')
        (self.root / 'changed.txt').write_bytes(b'after')
        (self.root / 'added.txt').write_bytes(b'new')
        (self.root / 'unrelated.txt').write_bytes(b'keep')
        digest = lambda value: hashlib.sha256(value).hexdigest()
        changes = {
            'changed.txt': {'before': digest(b'before'), 'after': digest(b'after')},
            'removed.txt': {'before': digest(b'removed'), 'after': None},
            'added.txt': {'before': None, 'after': digest(b'new')},
        }
        (self.backup / 'changes.json').write_text(json.dumps(changes))
        with zipfile.ZipFile(self.backup / 'before.zip', 'w') as archive:
            archive.writestr('changed.txt', b'before')
            archive.writestr('removed.txt', b'removed')

    def run_restore(self, *args):
        return subprocess.run([sys.executable, str(self.backup / 'restore.py'), '--backup', str(self.backup), *args],
                              capture_output=True, timeout=10)

    def test_check_and_restore_are_scoped_and_repeatable(self):
        result = self.run_restore('--check')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual((self.root / 'changed.txt').read_bytes(), b'after')
        result = self.run_restore()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual((self.root / 'changed.txt').read_bytes(), b'before')
        self.assertEqual((self.root / 'removed.txt').read_bytes(), b'removed')
        self.assertFalse((self.root / 'added.txt').exists())
        self.assertEqual((self.root / 'unrelated.txt').read_bytes(), b'keep')
        self.assertEqual(self.run_restore().returncode, 0)

    def test_later_edits_block_all_restoration(self):
        (self.root / 'changed.txt').write_bytes(b'later edit')
        result = self.run_restore()
        self.assertEqual(result.returncode, 1)
        self.assertIn(b'changed.txt', result.stdout)
        self.assertEqual((self.root / 'changed.txt').read_bytes(), b'later edit')
        self.assertTrue((self.root / 'added.txt').exists())
        self.assertFalse((self.root / 'removed.txt').exists())

    def test_corrupt_original_blocks_restoration(self):
        with zipfile.ZipFile(self.backup / 'before.zip', 'w') as archive:
            archive.writestr('changed.txt', b'wrong')
            archive.writestr('removed.txt', b'removed')
        result = self.run_restore()
        self.assertEqual(result.returncode, 1)
        self.assertEqual((self.root / 'changed.txt').read_bytes(), b'after')
