"""Restore only this cleanup's changes; refuse to overwrite subsequent edits."""
import argparse
import hashlib
import json
from pathlib import Path
import zipfile


def digest(content):
    return hashlib.sha256(content).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    parser.add_argument('--backup', type=Path, default=Path(__file__).resolve().parents[1] / '.backups/cleanup-20261116')
    args = parser.parse_args()
    backup = args.backup.resolve()
    root = backup.parent.parent
    changes = json.loads((backup / 'changes.json').read_text(encoding='utf-8'))
    originals = {}
    conflicts = []
    paths = {}
    with zipfile.ZipFile(backup / 'before.zip') as archive:
        for name, hashes in changes.items():
            path = (root / name).resolve()
            if not path.is_relative_to(root) or path == root or path.is_relative_to(backup.parent):
                raise ValueError(f'Unsafe restore path: {name}')
            paths[name] = path
            if path.exists() and not path.is_file():
                conflicts.append(name)
                continue
            actual = digest(path.read_bytes()) if path.exists() else None
            if actual not in (hashes['before'], hashes['after']):
                conflicts.append(name)
            if hashes['before'] is not None:
                content = archive.read(name)
                if digest(content) != hashes['before']:
                    print(f'Backup integrity error: {name}')
                    return 1
                originals[name] = content
    if conflicts:
        print('Later edits detected; nothing restored. Preserve or reconcile these files first:')
        print('\n'.join(conflicts))
        return 1
    if args.check:
        print(f'Restore check passed: {len(changes)} paths; no conflicts.')
        return 0
    for name, path in paths.items():
        if name in originals:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(originals[name])
        elif path.exists():
            path.unlink()
    # Remove only empty directories affected by this cleanup.
    parents = {p for path in paths.values() for p in path.parents if p != root and p.is_relative_to(root)}
    for directory in sorted(parents, key=lambda p: len(p.parts), reverse=True):
        try:
            directory.rmdir()
        except OSError:
            pass
    print(f'Restored {len(changes)} paths. Unrelated files and Git history were preserved.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
