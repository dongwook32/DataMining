import os
from pathlib import Path
import socket
import subprocess
import sys
import tempfile
import time
import unittest
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]


class CliTests(unittest.TestCase):
    def run_cli(self, *args):
        with tempfile.TemporaryDirectory() as cwd:
            return subprocess.run(
                [sys.executable, str(ROOT / 'run.py'), *args], cwd=cwd,
                capture_output=True, encoding='utf-8', timeout=30,
                env={**os.environ, 'PYTHONIOENCODING': 'utf-8'},
            )

    def test_help_outside_project(self):
        result = self.run_cli('--help')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('terminal', result.stdout)

    def test_terminal_uses_saved_results_outside_project(self):
        result = self.run_cli('terminal')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('Strict OOS', result.stdout)

    def test_invalid_port(self):
        result = self.run_cli('web', '--port', '70000', '--no-browser')
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertIn('port must be between', result.stderr)

    def test_web_serves_dashboard_and_data(self):
        with socket.socket() as sock:
            sock.bind(('127.0.0.1', 0))
            port = sock.getsockname()[1]
        proc = subprocess.Popen(
            [sys.executable, str(ROOT / 'run.py'), 'web', '--port', str(port), '--no-browser'],
            cwd=tempfile.gettempdir(), stdout=subprocess.DEVNULL, stderr=subprocess.PIPE,
        )
        try:
            deadline = time.monotonic() + 15
            while time.monotonic() < deadline:
                if proc.poll() is not None:
                    self.fail(proc.stderr.read().decode('utf-8', 'replace'))
                try:
                    with urlopen(f'http://127.0.0.1:{port}/', timeout=1) as response:
                        self.assertIn(b'JKIICE', response.read())
                    break
                except OSError:
                    time.sleep(0.1)
            else:
                self.fail('Dashboard did not start')
            with urlopen(f'http://127.0.0.1:{port}/data/research_data.json') as response:
                self.assertIn(b'study_panel_67m', response.read())
            with self.assertRaises(Exception):
                urlopen(f'http://127.0.0.1:{port}/../.env')
        finally:
            if proc.poll() is None:
                proc.terminate()
            proc.communicate(timeout=5)


if __name__ == '__main__':
    unittest.main()
