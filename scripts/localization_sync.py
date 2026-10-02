"""Compare an updated Japanese checkout with the recorded English-edition baseline.

Read-only by default. Reports paths and hashes, never copies or overwrites source
or translated files. Use --output only to save the resulting JSON report.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
IGNORED = {'.git', '.work', 'backup', 'backups', '.agents', '.codex', '.venv',
           'venv', '__pycache__', 'node_modules', '.secrets', '.pytest_cache'}


def sha256(path):
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def excluded(path):
    return (any(part in IGNORED for part in path.parts)
            or path.name.startswith('.env') and path.name != '.env.example'
            or path.suffix in {'.pyc', '.pyo', '.bak', '.tmp', '.log'}
            or path.as_posix() in {'docs/PLAN.md', 'docs/PROGRESS.md'})


def inventory(source):
    source = Path(source).resolve(strict=True)
    if not source.is_dir():
        raise ValueError('Source must be a directory.')
    # Match the initial baseline: use tracked content when given a Git checkout.
    # A source export without .git is also supported, excluding local artifacts.
    if (source / '.git').exists():
        result = subprocess.run(['git', '-C', str(source), 'ls-files', '-z'],
                                check=True, capture_output=True)
        names = [Path(n) for n in result.stdout.decode('utf-8').split('\0') if n]
    else:
        names = []
        for current, directories, files in os.walk(source, followlinks=False):
            directories[:] = [name for name in directories if name not in IGNORED]
            for name in files:
                names.append((Path(current) / name).relative_to(source))
    output = {}
    for relative in names:
        if excluded(relative):
            continue
        target = source / relative
        if not target.exists():
            continue  # A tracked but locally deleted source is a deletion.
        if not target.is_file():
            raise ValueError(f'Non-file source entry: {relative.as_posix()}')
        for candidate in (target, *target.parents):
            if candidate == source:
                break
            if candidate.is_symlink() or (getattr(candidate.stat(), 'st_file_attributes', 0) & 0x400):
                raise ValueError(f'Linked source path: {relative.as_posix()}')
        output[relative.as_posix()] = sha256(target)
    return output


def compare(baseline, current):
    previous = {item['path']: item['sha256'] for item in baseline['files']}
    changes = []
    for path in sorted(previous.keys() | current.keys()):
        old, new = previous.get(path), current.get(path)
        if old == new:
            continue
        changes.append({'path': path, 'change': 'added' if old is None else 'deleted' if new is None else 'modified',
                        'previousSha256': old, 'currentSha256': new})
    return {'schemaVersion': 1, 'baselineSourceCommit': baseline.get('sourceCommit'),
            'baselineSourceVersion': baseline.get('sourceVersion'),
            'counts': {kind: sum(row['change'] == kind for row in changes)
                       for kind in ('added', 'modified', 'deleted')},
            'changes': changes,
            'nextStep': 'Review source differences against the previous Japanese revision, update the English edition, then refresh the baseline only after review and validation.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', required=True, type=Path, help='Updated Japanese kit root (read only)')
    parser.add_argument('--baseline', type=Path, default=ROOT/'docs/localization/source-manifest.json')
    parser.add_argument('--output', type=Path, help='Optional new JSON report; an existing file is never overwritten')
    args = parser.parse_args()
    try:
        baseline = json.loads(args.baseline.read_text(encoding='utf-8-sig'))
        if baseline.get('schemaVersion') != 1 or not isinstance(baseline.get('files'), list):
            raise ValueError('Invalid baseline manifest.')
        if args.source.resolve() == ROOT:
            raise ValueError('Choose the Japanese source checkout, not this English edition.')
        report = compare(baseline, inventory(args.source))
        body = json.dumps(report, ensure_ascii=False, indent=2)+'\n'
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            with args.output.open('x', encoding='utf-8') as stream:
                stream.write(body)
        print(body, end='')
    except (OSError, ValueError, subprocess.CalledProcessError) as error:
        parser.exit(1, f'Localization comparison failed: {error}\n')


if __name__ == '__main__':
    main()
