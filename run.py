"""Launch the paper reproduction or an archived research view."""

from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
LEGACY = ROOT / ".backups" / "legacy-root-20261117"


def main():
    args = sys.argv[1:]
    environments = (ROOT / ".venv/Scripts/python.exe", ROOT / ".venv/bin/python")
    interpreter = next((str(path) for path in environments if path.is_file()), sys.executable)
    if args[:1] == ["reproduce"]:
        return subprocess.call(
            [interpreter, "-B", str(ROOT / "script/run_all.py"), *args[1:]],
            cwd=ROOT,
        )
    return subprocess.call([interpreter, "-B", str(LEGACY / "run.py"), *args], cwd=LEGACY)


if __name__ == "__main__":
    raise SystemExit(main())
