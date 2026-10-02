"""Record or check English file hashes against the Japanese source manifest.

This records file correspondence, not semantic-review approval. It never changes
the Japanese baseline; maintain that separately after reviewing upstream changes.
"""
from __future__ import annotations

import argparse
from datetime import date
import json
from pathlib import Path

from localization_sync import sha256
from public_release import public_files

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / 'docs/localization/translation-state.json'
BASELINE = ROOT / 'docs/localization/source-manifest.json'


def build_state():
    baseline = json.loads(BASELINE.read_text(encoding='utf-8-sig'))
    sources = {entry['path']: entry for entry in baseline['files']}
    examples_path = ROOT / 'docs/localization/example-localization.json'
    examples = ({entry['targetPath']: entry['status']
                 for entry in json.loads(examples_path.read_text(encoding='utf-8'))['images']}
                if examples_path.exists() else {})
    records = []
    for target in public_files(ROOT):
        if target == OUTPUT:
            continue  # A document cannot contain its own final content hash.
        relative = target.relative_to(ROOT).as_posix()
        source = sources.pop(relative, None)
        digest = sha256(target)
        if relative.startswith('examples/') and target.suffix in {'.png', '.jpg', '.jpeg'}:
            disposition = {
                'localized': 'english-localized-comic',
                'wordless-ltr-compatible': 'wordless-comic-ltr-compatible',
                'text-free-reference': 'text-free-original-reference',
            }.get(examples.get(relative), 'historical-japanese-artwork')
        elif '/panel-templates/' in relative and target.suffix in {'.json', '.svg', '.png', '.html'}:
            disposition = 'us-reading-order-asset'
        elif '/onomatopoeia/' in relative and target.suffix in {'.webp', '.svg', '.json', '.html'}:
            disposition = 'english-sound-effect-asset'
        elif source is None:
            disposition = 'english-edition-addition'
        elif source['sha256'] == digest:
            disposition = 'unchanged-source'
        else:
            disposition = 'translated-or-adapted'
        records.append({'sourcePath': relative if source else None,
                        'sourceSha256': source['sha256'] if source else None,
                        'targetPath': relative, 'targetSha256': digest,
                        'disposition': disposition})
    for relative, source in sorted(sources.items()):
        records.append({'sourcePath': relative, 'sourceSha256': source['sha256'],
                        'targetPath': None, 'targetSha256': None,
                        'disposition': 'not-in-current-public-scope'})
    return {'schemaVersion': 1, 'locale': 'en-US',
            'localizationVersion': '0.4.1-en-US.3',
            'sourceCommit': baseline['sourceCommit'], 'sourceVersion': baseline['sourceVersion'],
            'recordedOn': date.today().isoformat(),
            'note': 'Hashes establish file correspondence, not semantic approval. See the back-translation review and validation records. This state file excludes its own hash.',
            'files': sorted(records, key=lambda entry: entry['targetPath'] or entry['sourcePath'])}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='Check saved hashes without writing')
    args = parser.parse_args()
    state = build_state()
    if args.check:
        saved = json.loads(OUTPUT.read_text(encoding='utf-8'))
        saved.pop('recordedOn', None)
        state.pop('recordedOn', None)
        if saved != state:
            parser.exit(1, 'English localization state is stale; review changes before recording it again.\n')
        print('English localization state matches all current public files.')
    else:
        OUTPUT.write_text(json.dumps(state, ensure_ascii=False, indent=2)+'\n', encoding='utf-8', newline='\n')
        print(f'Recorded {len(state["files"])} source/target mappings in docs/localization/translation-state.json.')


if __name__ == '__main__':
    main()
