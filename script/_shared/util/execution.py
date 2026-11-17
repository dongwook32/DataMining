"""Execute research steps in order; a failed step stops the pipeline."""
from pathlib import Path
import os
import subprocess
import sys

from util.paths import ROOT


def run_commands(commands, *, cwd: Path = ROOT, dry_run: bool = False):
    for command in commands:
        print(subprocess.list2cmdline([str(part) for part in command]), flush=True)
        if not dry_run:
            subprocess.run(command, cwd=cwd, check=True,
                           env={**os.environ, 'PYTHONIOENCODING': 'utf-8', 'PYTHONDONTWRITEBYTECODE': '1'})


def run_modules(modules, *, dry_run=False):
    run_commands([[sys.executable, '-B', '-m', module] for module in modules], dry_run=dry_run)
