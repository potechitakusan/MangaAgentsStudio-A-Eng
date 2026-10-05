"""Create comic projects without PowerShell. Requires Python 3.10+ and only the standard library."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import unicodedata

ROOT = Path(__file__).absolute().parent.parent
THEMES = 'tsukkomi|allure|stature|horror|conflict|grief|romance|trust|awkwardness|urgency|revelation|payoff|endearment|bargaining|reconciliation'
KNOWLEDGE = re.compile(r'docs/knowledge/supervision/(?:(?:README|routing|sources)\.md|gag/(?:README|mechanisms|design-and-review|know-how)\.md|(?:' + THEMES + r')/README\.md)')
PROJECT_SCRIPTS = ('Resolve-ReviewProfile.ps1', 'resolve_review_profile.py', 'Resolve-ReviewProfile.sh',
                   'Initialize-OptionalSkills.ps1', 'initialize_optional_skills.py', 'Initialize-OptionalSkills.sh',
                   'validate_panel_plan.py', 'prepare_page_layout.py', 'process_checker.py')


def no_links(path: Path) -> None:
    """Allow a missing final path component while rejecting links, including parent links."""
    for item in (path, *path.parents):
        if item.is_symlink() or (hasattr(item, 'is_junction') and item.is_junction()):
            raise ValueError(f'Paths through links are not allowed: {item}')


def read_json(path: Path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def write_json(path: Path, value) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def package_files(root: Path, skip: tuple[str, ...] = ()):
    for item in sorted(root.iterdir()):
        no_links(item)
        if item.is_dir():
            if item.name not in ('__pycache__', *skip):
                yield from package_files(item)
        elif item.is_file():
            yield item
        else:
            raise ValueError(f'Only regular files can be distributed: {item}')


def collect_package(root: Path) -> dict[str, Path]:
    no_links(root)
    template = root / 'templates/manga-project'
    no_links(template / 'config/process-requirements.json')
    process = read_json(template / 'config/process-requirements.json')
    if not isinstance(process, dict) or set(process) != {'schemaVersion', 'requirements'} or type(process['schemaVersion']) is not int or process['schemaVersion'] != 1 or process['requirements'] != []:
        raise ValueError('Keep process requirements empty in the distribution master.')
    no_links(template / 'AGENTS.md')
    if '<!-- process-checker:strong:start -->' in (template / 'AGENTS.md').read_text(encoding='utf-8-sig'):
        raise ValueError('Do not include personal strong instructions in the template AGENTS.md.')
    package = {}

    def add(source: Path, destination: str):
        no_links(source)
        if not source.is_file():
            raise ValueError(f'Missing distribution source file: {source}')
        if destination.casefold() in {name.casefold() for name in package}:
            raise ValueError(f'Duplicate distribution destination: {destination}')
        package[destination] = source

    mappings = (
        ('templates/manga-project', '', {'.md', '.json', '.py'}, {'.gitignore', '.env.example', 'requirements-composition.txt'}, ('agent-modes',)),
        ('docs/knowledge', 'docs/knowledge', {'.md'}, set(), ('supervision',)),
        ('skills', '.agents/skills', {'.md'}, set(), ()),
        ('scripts/video', 'scripts/video', {'.py'}, set(), ()),
    )
    for source_relative, destination, extensions, special, skip in mappings:
        source_root = root / source_relative
        no_links(source_root)
        files = list(package_files(source_root, skip))
        if not files:
            raise ValueError(f'Empty distribution source directory: {source_root}')
        for file in files:
            relative = file.relative_to(source_root).as_posix()
            if any(part in {'.secrets', '.git', '.work', '.codex'} for part in file.relative_to(source_root).parts) or (file.name.startswith('.env') and file.name != '.env.example') or re.search(r'secret|credential|api[-_]?key|token', file.name, re.I):
                raise ValueError(f'Distribution filename may contain secrets: {relative}')
            asset = source_relative == 'templates/manga-project' and (
                relative in {'templates/panel-templates/index.html', 'templates/onomatopoeia/index.html'}
                or re.fullmatch(r'templates/panel-templates/(?:svg|guides)/[^/]+\.svg', relative)
                or re.fullmatch(r'templates/panel-templates/(?:png|previews)/[^/]+\.png', relative)
                or re.fullmatch(r'templates/onomatopoeia/images/[^/]+\.webp', relative)
                or re.fullmatch(r'templates/onomatopoeia/svg/[^/]+\.svg', relative))
            if file.suffix.lower() not in extensions and file.name not in special and not asset:
                raise ValueError(f'Disallowed distribution format: {relative}')
            add(file, f'{destination}/{relative}' if destination else relative)
    manifest_path = root / 'docs/knowledge/supervision/distribution.json'
    no_links(manifest_path)
    manifest = read_json(manifest_path)
    if not isinstance(manifest, dict) or type(manifest.get('schemaVersion')) is not int or manifest['schemaVersion'] != 1 or not isinstance(manifest.get('files'), list) or not manifest['files']:
        raise ValueError('Invalid knowledge distribution manifest.')
    for relative in manifest['files']:
        if not isinstance(relative, str) or not KNOWLEDGE.fullmatch(relative):
            raise ValueError(f'Disallowed knowledge distribution path: {relative}')
        add(root / relative, relative)
    add(manifest_path, manifest_path.relative_to(root).as_posix())
    for name in PROJECT_SCRIPTS:
        add(root / 'scripts' / name, f'scripts/{name}')
    add(root / 'LICENSE', 'docs/toolkit-license.txt')
    return package


def create_project(project_name: str, destination_parent: str | Path | None = None,
                   process_requirements_from: str | Path | None = None,
                   agent_mode: str = 'Codex', what_if: bool = False,
                   root: Path = ROOT) -> dict:
    root = Path(os.path.abspath(root))
    def letter_number(char):
        return unicodedata.category(char)[0] in 'LN'
    if not 1 <= len(project_name) <= 64 or project_name != project_name.strip() or not letter_number(project_name[0]) or not all(letter_number(c) or c in ' _-' for c in project_name) or re.fullmatch(r'CON|PRN|AUX|NUL|COM[0-9¹²³]|LPT[0-9¹²³]', project_name, re.I):
        raise ValueError('Use 1–64 letters, numbers, spaces, underscores, or hyphens for the project name; avoid Windows reserved names.')
    if agent_mode not in {'Codex', 'Claude', 'Antigravity'}:
        raise ValueError('AgentMode must be Codex, Claude, or Antigravity.')
    parent = Path(os.path.abspath(destination_parent if destination_parent is not None else root.parent))
    no_links(parent)
    if not parent.is_dir():
        raise ValueError('The destination parent must be an existing directory.')
    target = parent / project_name
    if target.exists() or target.is_symlink():
        raise ValueError(f'Existing projects are not overwritten: {target}')
    package = collect_package(root)
    if agent_mode == 'Claude':
        for name in ('CLAUDE.md', 'AGENT-MODE.md'):
            source = root / 'templates/manga-project/agent-modes/claude' / name
            no_links(source)
            if not source.is_file():
                raise ValueError(f'Missing Claude mode template: {name}')
            package[name] = source
    if agent_mode == 'Antigravity':
        for name in ('GEMINI.md', 'AGENT-MODE.md'):
            source = root / 'templates/manga-project/agent-modes/antigravity' / name
            no_links(source)
            if not source.is_file():
                raise ValueError(f'Missing Antigravity mode template: {name}')
            package[name] = source
    # Validate settings before creating output.
    from resolve_review_profile import resolve_profile
    resolve_profile(root / 'templates/manga-project/config/review-profiles.json')
    source = None
    if process_requirements_from:
        source = Path(os.path.abspath(process_requirements_from))
        no_links(source)
        if not (source / 'project.json').is_file():
            raise ValueError('The source project must contain project.json.')
        subprocess.run([sys.executable, '-X', 'utf8', str(root / 'scripts/process_checker.py'), 'validate-source', '--from-project', str(source)], check=True, stdout=subprocess.DEVNULL)
    no_links(root / 'distribution-version.txt')
    version = (root / 'distribution-version.txt').read_text(encoding='utf-8-sig').strip()
    result = {'ProjectName': project_name, 'Path': os.path.relpath(target), 'AbsolutePath': str(target), 'Version': version, 'CopiedFiles': len(package), 'AgentMode': agent_mode}
    if what_if:
        return {**result, 'WhatIf': True}
    created = False
    try:
        no_links(parent)
        target.mkdir()  # Do not allow existing directories.
        created = True
        for relative, file in package.items():
            no_links(file)
            dest = target / relative
            no_links(dest)
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(file, dest)
            if dest.suffix == '.sh':
                dest.chmod(dest.stat().st_mode | 0o111)
        ignore = target / '.gitignore'
        ignore.write_text(ignore.read_text(encoding='utf-8-sig').rstrip() + '\n/config/process-requirements.json\n', encoding='utf-8')
        for directory in ('input', 'assets/characters', 'assets/references', 'workflows', 'output', '.secrets'):
            (target / directory).mkdir(parents=True, exist_ok=True)
        now = datetime.now(timezone.utc).isoformat()
        project = {'schemaVersion': 1, 'name': project_name, 'createdAt': now, 'distributionVersion': version, 'sourceKitRelativePath': Path(os.path.relpath(root, target)).as_posix(), 'agentMode': agent_mode, 'locale': 'en-US', 'readingDirection': 'ltr', 'localizationVersion': '0.5.0-en-US.1'}
        if source:
            project['processRequirementsSourceRelativePath'] = Path(os.path.relpath(source, target)).as_posix()
        write_json(target / 'project.json', project)
        if source:
            subprocess.run([sys.executable, '-X', 'utf8', str(target / 'scripts/process_checker.py'), '--project', str(target), 'import', '--from-project', str(source)], check=True, stdout=subprocess.DEVNULL)
        snapshot = [{'path': relative, 'sha256': digest(target / relative)} for relative in sorted(package)]
        write_json(target / 'docs/distribution-snapshot.json', {'version': version, 'createdAt': now, 'files': snapshot})
    except Exception:
        if created:
            print(f'Creation failed. Partial output is retained for inspection: {target}', file=sys.stderr)
        raise
    return result


def main() -> int:
    if sys.version_info < (3, 10):
        print('Python 3.10 or later is required.', file=sys.stderr)
        return 1
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('name', nargs='?', help='Project name')
    parser.add_argument('--project-name', '-ProjectName')
    parser.add_argument('--destination-parent', '-DestinationParent')
    parser.add_argument('--process-requirements-from', '-ProcessRequirementsFrom')
    parser.add_argument('--agent-mode', '-AgentMode', choices=('Codex', 'Claude', 'Antigravity'), default='Codex')
    parser.add_argument('--what-if', '--dry-run', '-WhatIf', action='store_true')
    args = parser.parse_args()
    if bool(args.name) == bool(args.project_name):
        parser.error('Specify the project name as either a positional argument or --project-name, but not both.')
    try:
        result = create_project(args.name or args.project_name, args.destination_parent, args.process_requirements_from, args.agent_mode, args.what_if)
    except (OSError, ValueError, subprocess.CalledProcessError) as error:
        parser.exit(1, f'Error: {error}\n')
    if args.what_if:
        print('Placement preview only. No project was created.', file=sys.stderr)
    else:
        print(f'Comic project created. Absolute destination path: {result["AbsolutePath"]}', file=sys.stderr)
        print(f'Reopen {args.agent_mode} in this folder. Start a new conversation in the project folder before producing the comic.', file=sys.stderr)
        if args.agent_mode == 'Antigravity':
            print('Added GEMINI.md and AGENT-MODE.md. Artwork defaults to NovelAI. Check available generation and image viewing tools and network permissions before drawing.', file=sys.stderr)
        print('If you need help, tell me your environment (Windows, Mac, or Linux; app or VS Code), and I will explain the steps.', file=sys.stderr)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
