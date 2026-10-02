#!/usr/bin/env python3
"""Install optional project skills after checking pinned versions and explicit consent."""

import argparse
from datetime import datetime
import hashlib
import json
import ntpath
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import urllib.request
import uuid
import zipfile


def assert_optional_path(root, relative):
    """Reject paths outside the project and reads/writes through links, including parent links."""
    root = Path(os.path.abspath(root))
    relative = str(relative)
    if ntpath.isabs(relative) or ntpath.splitdrive(relative)[0] or '..' in re.split(r'[\\/]', relative):
        raise ValueError('Paths outside the project are not allowed.')
    path = Path(os.path.abspath(root / relative.replace('\\', '/')))
    if path == root or root not in path.parents:
        raise ValueError('Specify a path inside the project.')
    for current in (path, *path.parents):
        if current.is_symlink() or (hasattr(current, 'is_junction') and current.is_junction()):
            raise ValueError('Installation paths through links are not allowed.')
    return path


def read_json(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def write_optional_json(value, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding='utf-8')


def file_hash(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def get_optional_selection(root):
    path = assert_optional_path(root, 'OPTION.md')
    if not path.exists():
        return 'none'
    rows = re.findall(r'^\|\s*(?:Japanese polishing skill|日本語推敲スキル)\s*\|\s*([^|]*)\|', path.read_text(encoding='utf-8-sig'), re.MULTILINE)
    if not rows:
        return 'none'
    if len(rows) != 1:
        raise ValueError('Duplicate Japanese polishing skill setting rows.')
    value = rows[0].strip().lower()
    if value in ('', '使用しない', '無効', 'none', 'disabled', 'do not use'):
        return 'none'
    if value in ('使用する', '有効', 'humanizer-jp', 'enabled', 'use'):
        return 'humanizer-jp'
    if re.fullmatch(r'japanese-natural-writing(?:[（(]gemini[）)])?', value):
        return 'japanese-natural-writing'
    raise ValueError('Set Japanese polishing skill to none, humanizer-jp, or japanese-natural-writing.')


def find_optional_git():
    return shutil.which('git')


def invoke_optional_git(git, arguments):
    environment = os.environ.copy()
    environment['GIT_TERMINAL_PROMPT'] = '0'
    result = subprocess.run([git, *map(str, arguments)], env=environment, stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT, encoding='utf-8', errors='replace', check=False)
    if result.returncode:
        raise ValueError('Git operation failed: ' + result.stdout)
    return result.stdout.strip()


def get_optional_archive(source, work, git):
    archive = work / 'source.zip'
    if source['method'] == 'git':
        if not re.fullmatch(r'https://github\.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+\.git', source['repository']) or not re.fullmatch(r'[a-f0-9]{40}', source['revision']):
            raise ValueError('Invalid Git source or pinned revision.')
        repo, hooks = work / 'repo', work / 'empty-hooks'
        hooks.mkdir()
        invoke_optional_git(git, ['-c', f'core.hooksPath={hooks}', 'init', '--quiet', repo])
        invoke_optional_git(git, ['-C', repo, '-c', f'core.hooksPath={hooks}', '-c', 'credential.helper=', 'fetch', '--quiet', '--depth=1', source['repository'], source['revision']])
        head = invoke_optional_git(git, ['-C', repo, 'rev-parse', 'FETCH_HEAD'])
        if head != source['revision']:
            raise ValueError('Fetched Git revision does not match.')
        names = list(source['files'])
        tree = invoke_optional_git(git, ['-C', repo, 'ls-tree', '-r', head, '--', *names])
        if re.search(r'^(120000|160000) ', tree, re.MULTILINE):
            raise ValueError('Skill links and submodules are not installed.')
        invoke_optional_git(git, ['-C', repo, '-c', 'core.autocrlf=false', '-c', 'core.eol=lf', 'archive', '--format=zip', f'--output={archive}', head, '--', *names])
    elif source['method'] == 'zip':
        if not re.fullmatch(r'https://note\.com/api/v2/attachments/download/[a-f0-9]+', source['url']) or not re.fullmatch(r'[a-f0-9]{64}', source['revision']):
            raise ValueError('Invalid ZIP source or pinned version.')
        with urllib.request.urlopen(source['url'], timeout=60) as response, archive.open('wb') as output:
            shutil.copyfileobj(response, output)
        if file_hash(archive) != source['revision']:
            raise ValueError('ZIP contents differ from the reviewed version.')
    else:
        raise ValueError('Unsupported retrieval method.')
    return archive


def expand_optional_archive(archive, source, stage):
    expected = {}
    for name, digest in source['files'].items():
        if not re.fullmatch(r'[A-Za-z0-9_.-]+(?:/[A-Za-z0-9_.-]+)*', name) or '..' in name.split('/') or not re.fullmatch(r'[a-f0-9]{64}', digest):
            raise ValueError('Invalid requested file specification.')
        expected[source['prefix'] + name] = (name, digest)
    seen = set()
    with zipfile.ZipFile(archive) as zipped:
        for entry in zipped.infolist():
            if entry.is_dir():
                continue
            if entry.filename not in expected or entry.filename in seen:
                raise ValueError('ZIP contains unexpected or duplicate files.')
            if (entry.external_attr >> 16) & 0xF000 == 0xA000:
                raise ValueError('Links inside ZIP files are not installed.')
            name, digest = expected[entry.filename]
            path = assert_optional_path(stage, name)
            path.parent.mkdir(parents=True, exist_ok=True)
            with zipped.open(entry) as incoming, path.open('xb') as output:
                shutil.copyfileobj(incoming, output)
            if file_hash(path) != digest:
                raise ValueError('Skill file contents do not match the reviewed version.')
            seen.add(entry.filename)
    if len(seen) != len(expected):
        raise ValueError('Required skill files are missing.')


def initialize_optional_skills(project_root, provider='', gemini_consent='Unspecified', consent_note=''):
    root = Path(os.path.abspath(project_root))
    if not (root / 'project.json').is_file():
        raise ValueError('Run this in the distributed comic project.')
    provider = provider or get_optional_selection(root)
    def result(status, message, **extra):
        return dict(status=status, provider=provider, **extra, message=message)
    if provider == 'none':
        return result('disabled', 'Polishing skills are disabled. No external retrieval, Git check, or Gemini call is performed.')
    if provider not in ('humanizer-jp', 'japanese-natural-writing'):
        raise ValueError('Unsupported polishing skill.')
    manifest = read_json(assert_optional_path(root, 'config/optional-skills.json'))
    if manifest['schemaVersion'] != 1:
        raise ValueError('Invalid polishing skill distribution settings.')
    source = manifest['providers'][provider]
    target_relative = '.agents/skills/' + provider
    target = assert_optional_path(root, target_relative)
    state_relative = '.work/optional-skills/' + provider
    receipt_path = assert_optional_path(root, state_relative + '-installed.json')
    consent_path = assert_optional_path(root, state_relative + '-consent.json')
    # Do not treat environment detection or enabling a skill as quota consent.
    if provider == 'japanese-natural-writing' or source['requiresGeminiConsent']:
        if gemini_consent not in ('Unspecified', 'Granted', 'Denied'):
            raise ValueError('Invalid Gemini consent status.')
        if gemini_consent != 'Unspecified':
            if not consent_note.strip():
                raise ValueError('A record of the explicit user response and authorized scope is required.')
            write_optional_json(dict(provider=provider, revision=source['revision'], decision=gemini_consent,
                                     note=consent_note, recordedAt=datetime.now().astimezone().isoformat()), consent_path)
        consent = read_json(consent_path) if consent_path.exists() else None
        if not consent or consent.get('provider') != provider or consent.get('revision') != source['revision'] or not str(consent.get('note') or '').strip():
            return result('needs_gemini_consent', 'Before installation, ask permission to send the selected project text to Gemini and consume quota for polishing.')
        if consent.get('decision') != 'Granted':
            return result('gemini_declined', 'Gemini use is not authorized. Continue ordinary production without retrieving, installing, or invoking this skill.')
    if target.exists():
        if not receipt_path.exists():
            raise ValueError('Existing skills with the same name are not overwritten. Compare with the installation receipt.')
        receipt = read_json(receipt_path)
        if receipt['provider'] != provider or receipt['path'] != target_relative or receipt['revision'] != source['revision']:
            raise ValueError('Installed version or destination differs. Handle updates separately.')
        if set(source['files']) | {'agents/openai.yaml'} != set(receipt['files']):
            raise ValueError('Installation receipt file list does not match.')
        for name, digest in receipt['files'].items():
            path = assert_optional_path(target, name)
            if not path.is_file() or file_hash(path) != digest:
                raise ValueError('Installed skill files were changed or are missing. They will not be overwritten automatically.')
        return result('ready', 'Already installed. No external retrieval is repeated.', path=target_relative)
    git = find_optional_git() if source['method'] == 'git' else None
    if source['method'] == 'git' and not git:
        return result('needs_git_consent', 'Git is missing. Ask permission to install Git and proceed only after authorization.')
    work = assert_optional_path(root, '.work/optional-skills/download-' + uuid.uuid4().hex)
    stage = work / 'skill'
    stage.mkdir(parents=True)
    archive = get_optional_archive(source, work, git)
    expand_optional_archive(archive, source, stage)
    if not (stage / 'SKILL.md').is_file():
        raise ValueError('SKILL.md is missing.')
    # Preserve original text and rights notices; append only the explicit invocation policy.
    policy_path = stage / 'agents/openai.yaml'
    policy = ''
    if policy_path.exists():
        with policy_path.open(encoding='utf-8-sig', newline='') as stream:
            policy = stream.read()
    if re.search(r'^policy\s*:', policy, re.MULTILINE | re.IGNORECASE):
        raise ValueError('Invocation policy has changed. Review it before installation.')
    policy_path.parent.mkdir(parents=True, exist_ok=True)
    policy_path.write_text(policy.rstrip() + '\npolicy:\n  allow_implicit_invocation: false\n', encoding='utf-8', newline='')
    names = dict.fromkeys([*source['files'], 'agents/openai.yaml'])
    receipt = dict(provider=provider, revision=source['revision'], path=target_relative,
                   installedAt=datetime.now().astimezone().isoformat(),
                   files={name: file_hash(stage / name) for name in names},
                   adjustment='Disable implicit invocation. Apply explicitly only to selected targets.')
    target.parent.mkdir(parents=True, exist_ok=True)
    # Recheck links and destination collisions immediately before moving. Retain failed retrievals.
    assert_optional_path(root, stage.relative_to(root))
    assert_optional_path(root, target_relative)
    if target.exists():
        raise ValueError('The destination was created meanwhile. Stop without overwriting it.')
    stage.rename(target)
    write_optional_json(receipt, receipt_path)
    return result('installed', 'Installed in the project. Reopen Codex only if the skill is not recognized.', path=target_relative)


def main(argv=None):
    if sys.version_info < (3, 10):
        print('Python 3.10 or later is required.', file=sys.stderr)
        return 1
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project-root', '-ProjectRoot', default=str(Path(__file__).absolute().parent.parent), help='Comic project location')
    parser.add_argument('--provider', '-Provider', default='', choices=('', 'none', 'humanizer-jp', 'japanese-natural-writing'), help='Effective setting adopted in the conversation')
    parser.add_argument('--gemini-consent', '-GeminiConsent', default='Unspecified', choices=('Unspecified', 'Granted', 'Denied'), help='Actual user response')
    parser.add_argument('--consent-note', '-ConsentNote', default='', help='Actual response and authorized scope')
    args = parser.parse_args(argv)
    try:
        value = initialize_optional_skills(args.project_root, args.provider, args.gemini_consent, args.consent_note)
    except (OSError, ValueError, KeyError, TypeError, zipfile.BadZipFile) as error:
        print('Error: ' + str(error), file=sys.stderr)
        return 1
    print(json.dumps(value, ensure_ascii=False, indent=2))
    return 0


if __name__ == '__main__':
    sys.exit(main())
