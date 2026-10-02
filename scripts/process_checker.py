"""Manage project requirements, verification records, and strong instructions using the standard library."""
from __future__ import annotations

import argparse
from contextlib import contextmanager
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path, PureWindowsPath
import re
import sys
import tempfile
import uuid


REQUIREMENTS = 'config/process-requirements.json'
STATE = '.work/process-checker/state.json'
TURN = '.work/process-checker/turn.json'
BEGIN = '<!-- process-checker:strong:start -->'
END = '<!-- process-checker:strong:end -->'
HOOK_LABEL = 'Process checker requirements review'
CHECKPOINTS = {
    'brief-complete': 'Brief complete',
    'script-complete': 'Text storyboard complete',
    'layout-complete': 'Panel plan complete',
    'name-complete': 'Thumbnail storyboard complete',
    'before-generation': 'Before page generation',
    'after-generation': 'After page generation',
    'page-complete': 'Page complete',
    'before-preview': 'Before PNG preview',
    'after-preview': 'After PNG review',
    'before-psd': 'Before PSD creation',
    'after-psd': 'After PSD creation',
    'before-handoff': 'Before handoff',
}
RANK = {key: index for index, key in enumerate(CHECKPOINTS)}
STATUSES = {'done', 'not-done', 'unverified', 'awaiting-user', 'not-applicable'}
FIELDS = {'id', 'level', 'instruction', 'checkpoint', 'scope', 'condition',
          'completionCriteria', 'carryForward', 'enforcement', 'decision', 'decisionNote'}


LEGACY_VALUES = {'実施済み': 'done', '未実施': 'not-done', '未確認': 'unverified', 'ユーザー回答待ち': 'awaiting-user', '対象外': 'not-applicable', '強く指示': 'strong-instruction', '指示': 'instruction', '相談済み': 'discussed', 'おまかせ': 'delegated'}


def canonical(value):
    return LEGACY_VALUES.get(value, value) if isinstance(value, str) else value


def now():
    return datetime.now(timezone.utc).isoformat()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def nonempty(value):
    return isinstance(value, str) and bool(value.strip())


def digest(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True).encode('utf-8')).hexdigest()


def safe_path(root, relative):
    require(isinstance(relative, str) and relative and '\\' not in relative,
            'Use a project-relative path with / separators.')
    path = Path(relative)
    require(not path.is_absolute() and not PureWindowsPath(relative).drive
            and '..' not in path.parts, 'Paths outside the project are not allowed.')
    target = root / path
    for item in (target, *target.parents):
        if item.exists() or item.is_symlink():
            require(not item.is_symlink()
                    and not (getattr(item.stat(), 'st_file_attributes', 0) & 0x400),
                    'Reading or writing through links is not allowed.')
        if item == root:
            break
    require(target.resolve().is_relative_to(root.resolve()), 'The path is outside the project.')
    return target


def read_json(path):
    try:
        return json.loads(path.read_text(encoding='utf-8-sig'))
    except (OSError, ValueError) as exc:
        raise ValueError(f'Cannot read JSON: {path.name}') from exc


def write_text(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', newline='\n',
                                         dir=path.parent, delete=False) as stream:
            temporary = Path(stream.name)
            stream.write(text)
        os.replace(temporary, path)
    finally:
        if temporary is not None and temporary.exists():
            temporary.unlink()


def write_json(path, value):
    write_text(path, json.dumps(value, ensure_ascii=False, indent=2) + '\n')


def validate_registry(value):
    value = deepcopy(value)
    require(isinstance(value, dict) and set(value) == {'schemaVersion', 'requirements'}
            and type(value['schemaVersion']) is int and value['schemaVersion'] == 1
            and isinstance(value['requirements'], list), 'Invalid requirements file format.')
    seen = set()
    for rule in value['requirements']:
        require(isinstance(rule, dict) and set(rule) == FIELDS, 'Missing or unsupported requirement fields.')
        require(isinstance(rule['id'], str) and re.fullmatch(r'proc-[a-z0-9-]{1,60}', rule['id']),
                'Invalid requirement ID.')
        require(rule['id'] not in seen, 'Duplicate requirement ID.')
        seen.add(rule['id'])
        rule['level'] = canonical(rule['level'])
        rule['decision'] = canonical(rule['decision'])
        require(rule['level'] in ('instruction', 'strong-instruction'), 'Level must be instruction or strong-instruction.')
        require(isinstance(rule['checkpoint'], str) and rule['checkpoint'] in CHECKPOINTS
                and rule['scope'] in ('project', 'page'),
                'Invalid checkpoint or scope.')
        for key in ('instruction', 'condition', 'completionCriteria', 'decisionNote'):
            require(nonempty(rule[key]), f'Provide specific content for {key}.')
            require(BEGIN not in rule[key] and END not in rule[key], 'Instructions must not contain managed-section delimiters.')
        require(type(rule['carryForward']) is bool, 'Specify whether this requirement carries forward.')
        require(rule['decision'] in ('discussed', 'delegated'), 'Record a discussed or delegated decision.')
        allowed = ('report',) if rule['level'] == 'instruction' else ('agents', 'agents+hooks')
        require(rule['enforcement'] in allowed, 'The level and enforcement target do not match.')
    return value


def registry(root):
    # Only an empty array disables requirements. Missing or corrupt JSON is an error.
    return validate_registry(read_json(safe_path(root, REQUIREMENTS)))


def project_root(path):
    root = Path(path).absolute()
    require(safe_path(root, 'project.json').is_file(), 'A project.json is required. Do not run this in the template.')
    require(isinstance(read_json(root / 'project.json'), dict), 'Invalid project.json.')
    return root


@contextmanager
def editing(root):
    lock = safe_path(root, '.work/process-checker/edit.lock')
    lock.parent.mkdir(parents=True, exist_ok=True)
    try:
        descriptor = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError as exc:
        raise ValueError('A requirements update is running. Check execution state before handling a leftover lock.') from exc
    try:
        os.close(descriptor)
        yield
    finally:
        lock.unlink()


def strong_block(data):
    rules = [r for r in data['requirements'] if r['level'] == 'strong-instruction']
    if not rules:
        return ''
    lines = [BEGIN, '## Processes the user strongly requires in this project', '',
             'The source of truth is `config/process-requirements.json`. When conditions apply, complete each process by its checkpoint.',
             'If work is incomplete or evidence unverified, identify the gap before advancing the affected process. Waiting for a reply is not approval.',
             'The main agent decides unspecified creative choices. See `docs/knowledge/process-checker.md`.', '']
    for rule in rules:
        lines.extend([f"- {rule['id']}: {rule['instruction']}",
                      f"  - Checkpoint: {CHECKPOINTS[rule['checkpoint']]} / Scope: {'Each page' if rule['scope'] == 'page' else 'Whole project'}",
                      f"  - Condition: {rule['condition']}", f"  - Completion criteria: {rule['completionCriteria']}"])
    lines.extend(['', f'<!-- process-checker:digest:{digest(rules)} -->', END])
    return '\n'.join(lines)


def projected_agents(root, data):
    path = safe_path(root, 'AGENTS.md')
    body = path.read_text(encoding='utf-8-sig')
    require(body.count(BEGIN) == body.count(END) and body.count(BEGIN) <= 1,
            'The managed section in AGENTS.md is broken. Automatic update stopped.')
    block = strong_block(data)
    if BEGIN in body:
        start, finish = body.index(BEGIN), body.index(END) + len(END)
        require(start < finish - len(END), 'Invalid managed-section delimiter order in AGENTS.md.')
        return body[:start] + block + body[finish:]
    return body.rstrip() + '\n\n' + block + '\n' if block else body


def save_registry(root, data):
    data = validate_registry(data)
    agents = projected_agents(root, data)
    old = registry(root)
    archive = f'.work/process-checker/changes/{uuid.uuid4().hex}.json'
    write_json(safe_path(root, archive), {'at': now(), 'before': old, 'after': data})
    write_json(safe_path(root, REQUIREMENTS), data)
    write_text(safe_path(root, 'AGENTS.md'), agents)


def state(root):
    path = safe_path(root, STATE)
    if not path.exists():
        return {'schemaVersion': 1, 'items': [], 'reports': []}
    value = read_json(path)
    require(isinstance(value, dict) and value.get('schemaVersion') == 1
            and isinstance(value.get('items'), list) and isinstance(value.get('reports'), list),
            'Invalid execution records. Investigate separately from incomplete work.')
    for item in value['items']:
        if isinstance(item, dict):
            item['status'] = canonical(item.get('status'))
            if 'level' in item:
                item['level'] = canonical(item['level'])
        require(isinstance(item, dict) and all(nonempty(item.get(key)) for key in
                ('id', 'subject', 'revision', 'ruleDigest', 'status', 'note'))
                and item['status'] in STATUSES and isinstance(item.get('evidence'), list),
                'Invalid execution-record fields. Inspect the records.')
        require(all(isinstance(entry, dict) and nonempty(entry.get('path'))
                    and isinstance(entry.get('sha256'), str)
                    and re.fullmatch(r'[0-9a-f]{64}', entry['sha256'])
                    for entry in item['evidence']), 'Invalid execution-record evidence.')
    return value


def evidence(root, paths):
    require(isinstance(paths, list) and all(isinstance(p, str) for p in paths), 'Evidence must be an array of relative paths.')
    result = []
    for relative in dict.fromkeys(paths):
        require(not any(part in ('.git', '.secrets') for part in Path(relative).parts), 'Do not register secret files as evidence.')
        path = safe_path(root, relative)
        require(path.is_file(), f'Missing evidence file: {relative}')
        result.append({'path': relative, 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()})
    return result


def effective_items(root, data, current):
    rules = {r['id']: r for r in data['requirements']}
    items = deepcopy(current['items'])
    for item in items:
        rule = rules.get(item['id'])
        if rule is None or item.get('superseded'):
            item['status'] = 'not-applicable'
            continue
        item['level'] = rule['level']
        stale = item['ruleDigest'] != digest(rule)
        for entry in item.get('evidence', []):
            try:
                stale = stale or evidence(root, [entry['path']])[0]['sha256'] != entry['sha256']
            except ValueError:
                stale = True
        if stale:
            item['status'] = 'unverified'
            item['note'] = 'Instructions or evidence changed; verification is required again.'
    return items


def summary(root):
    data = registry(root)
    require(projected_agents(root, data) == safe_path(root, 'AGENTS.md').read_text(encoding='utf-8-sig'),
            'Strong instructions and AGENTS.md differ. Review the content and run sync-agents.')
    items = effective_items(root, data, state(root))
    return {'enabled': bool(data['requirements']), 'requirements': data['requirements'],
            'pending': [item for item in items if item['status'] not in ('done', 'not-applicable')],
            'note': 'Unreported work is not verified. Use the skill to review conditions and evidence.'}


def report(root, value):
    data = registry(root)
    require(isinstance(value, dict), 'The report must be a JSON object.')
    if not data['requirements']:
        return {'enabled': False, 'message': 'There are no requirements; detailed verification is unnecessary.'}
    if value.get('noProgress') is True:
        require(nonempty(value.get('note')), 'Explain why there is no progress.')
        current = state(root)
        current['reports'].append({'at': now(), 'noProgress': True, 'note': value['note']})
        write_json(safe_path(root, STATE), current)
        mark_reported(root, data, no_progress=True)
        return {'message': 'Recorded no process progress. Existing requirements remain incomplete.'}
    checkpoint = value.get('checkpoint')
    require(isinstance(checkpoint, str) and checkpoint in CHECKPOINTS, 'Invalid report checkpoint.')
    require(value.get('scope') in ('project', 'page') and nonempty(value.get('subject'))
            and nonempty(value.get('revision')), 'The report needs a scope, subject ID, and revision.')
    current = state(root)
    current['items'] = effective_items(root, data, current)
    due = []
    for rule in data['requirements']:
        if RANK[rule['checkpoint']] > RANK[checkpoint]:
            continue
        if rule['scope'] == 'page' and value['scope'] != 'page':
            continue
        subject = value['subject'] if rule['scope'] == 'page' else 'project'
        revision = value['revision'] if rule['scope'] == 'page' else 'project'
        matches = [i for i in current['items'] if i['id'] == rule['id'] and i['subject'] == subject
                   and i['revision'] == revision and not i.get('superseded')]
        if matches:
            item = matches[0]
        else:
            for previous in current['items']:
                if previous['id'] == rule['id'] and previous['subject'] == subject:
                    previous['superseded'] = True
            item = {'id': rule['id'], 'subject': subject, 'revision': revision, 'level': rule['level'],
                    'ruleDigest': digest(rule), 'status': 'unverified', 'note': 'Evidence of execution has not been reported.', 'evidence': []}
            current['items'].append(item)
        due.append((rule, item))
    results = value.get('results', [])
    require(isinstance(results, list) and all(isinstance(r, dict) for r in results), 'Verification results must be an array.')
    ids = [r.get('id') for r in results]
    require(all(isinstance(i, str) for i in ids) and len(ids) == len(set(ids))
            and set(ids) <= {r['id'] for r, _ in due}, 'Report IDs are duplicated or outside the current checkpoint scope.')
    for result in results:
        result = deepcopy(result)
        result['status'] = canonical(result.get('status'))
        require(isinstance(result.get('status'), str) and result['status'] in STATUSES
                and nonempty(result.get('note')), 'A status and verification note are required.')
        proof = evidence(root, result.get('evidence', []))
        require(result['status'] != 'done' or proof, 'A done status requires evidence files.')
        rule, item = next(pair for pair in due if pair[0]['id'] == result['id'])
        item.update(status=result['status'], note=result['note'], evidence=proof,
                    ruleDigest=digest(rule), checkedAt=now())
    current['reports'].append({'at': now(), 'checkpoint': checkpoint, 'subject': value['subject'],
                               'revision': value['revision']})
    write_json(safe_path(root, STATE), current)
    mark_reported(root, data)
    return summary(root)


def mark_reported(root, data, no_progress=False):
    path = safe_path(root, TURN)
    if path.exists():
        value = read_json(path)
        value.update(reported=True, registryDigest=digest(data), noProgress=no_progress)
        write_json(path, value)


def import_requirements(root, source):
    require(not registry(root)['requirements'], 'The destination already has instructions; automatic merging is disabled.')
    source = project_root(source)
    require(source.resolve() != root.resolve(), 'Cannot import from the same project.')
    data = registry(source)
    inherited = {'schemaVersion': 1, 'requirements': [deepcopy(r) for r in data['requirements'] if r['carryForward']]}
    save_registry(root, inherited)
    # Do not copy completed or pending-answer states, old artifacts, hook settings, or trust records.
    return {'count': len(inherited['requirements']), 'message': 'Copied only transferable instructions from the selected project. Hooks are not installed.'}


def hook_definitions():
    # Find project.json in parent folders; support projects without Git and invocation from subdirectories.
    code = ("import pathlib,runpy,sys; p=pathlib.Path.cwd(); "
            "r=next(q for q in (p,*p.parents) if (q/'project.json').is_file() "
            "and (q/'scripts/process_checker.py').is_file()); "
            "s=str(r/'scripts/process_checker.py'); sys.argv=[s,'--project',str(r),'hook']; "
            "runpy.run_path(s,run_name='__main__')")
    handler = {'type': 'command', 'command': f'python3 -X utf8 -c "{code}"',
               'commandWindows': f'python -X utf8 -c "{code}"', 'timeout': 15,
               'statusMessage': HOOK_LABEL}
    return {event: [{'hooks': [deepcopy(handler)]}] for event in ('UserPromptSubmit', 'Stop')}


def install_hooks(root, apply):
    require(any(r['enforcement'] == 'agents+hooks' for r in registry(root)['requirements']),
            'No strong instruction has been registered with agreed hook use.')
    path = safe_path(root, '.codex/hooks.json')
    old = read_json(path) if path.exists() else {}
    require(isinstance(old, dict) and isinstance(old.get('hooks', {}), dict), 'Invalid existing hook format.')
    updated = deepcopy(old)
    hooks = updated.setdefault('hooks', {})
    for event, groups in hook_definitions().items():
        existing = hooks.setdefault(event, [])
        require(isinstance(existing, list), 'Invalid existing hook format.')
        # Identify and update only our commands; preserve other handlers.
        for group in existing:
            require(isinstance(group, dict) and isinstance(group.get('hooks'), list), 'Invalid existing hook format.')
            require(all(isinstance(h, dict) for h in group['hooks']), 'Invalid existing hook handler.')
            group['hooks'] = [h for h in group['hooks'] if not
                              (h.get('statusMessage') == HOOK_LABEL and isinstance(h.get('command'), str)
                               and 'scripts/process_checker.py' in h['command'])]
        hooks[event] = [g for g in existing if g['hooks']] + groups
    if apply:
        write_json(safe_path(root, f'.work/process-checker/hooks-before-{uuid.uuid4().hex}.json'), old)
        write_json(path, updated)
    return {'applied': apply, 'configuration': updated,
            'message': 'Saving settings does not establish execution trust. Review and trust them in the Codex Hooks screen, then verify behavior in your environment.'}


def hook(root, event):
    require(isinstance(event, dict), 'Invalid hook event.')
    data = registry(root)
    strong = [r for r in data['requirements'] if r['enforcement'] == 'agents+hooks']
    if not strong:
        return {}
    name = event.get('hook_event_name')
    if name == 'UserPromptSubmit':
        with editing(root):
            write_json(safe_path(root, TURN), {'turnId': event.get('turn_id'), 'reported': False})
        return {'hookSpecificOutput': {'hookEventName': name, 'additionalContext':
                'This project has strong process instructions. Read config/process-requirements.json and '
                'use the process checker before starting and when completing a process. '
                'For discussion only, finish with a noProgress report. Do not repeat the same question while awaiting the user.'}}
    if name != 'Stop':
        return {}
    result = summary(root)
    turn_path = safe_path(root, TURN)
    turn = read_json(turn_path) if turn_path.exists() else {}
    reported = (turn.get('turnId') == event.get('turn_id') and turn.get('reported')
                and turn.get('registryDigest') == digest(data))
    ids = {r['id'] for r in strong}
    missing = [i for i in result['pending'] if i['id'] in ids and i['status'] in ('not-done', 'unverified')]
    if reported and (not missing or turn.get('noProgress') is True):
        return {}
    if event.get('stop_hook_active'):
        return {'systemMessage': 'Automatic process-check continuation stopped after one attempt. State unverified items in the handoff.'}
    return {'decision': 'block', 'reason':
            'Use the process checker to verify this progress and evidence for strong instructions, and save a report. '
            'Use noProgress for discussion without progress, and awaiting-user for matters requiring a reply. '
            'Do not mark unverified work as done or add restrictions to unrelated creative work.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project', default=str(Path(__file__).resolve().parents[1]), help='Project root')
    commands = parser.add_subparsers(dest='command', required=True)
    commands.add_parser('status', help='Show requirements and unresolved verification results')
    commands.add_parser('checkpoints', help='Show supported checkpoints')
    for name in ('add', 'replace'):
        command = commands.add_parser(name, help='Register agreed instructions from JSON')
        command.add_argument('--input', required=True, help='Project-relative input JSON path')
    command = commands.add_parser('remove', help='Remove an instruction revoked by the user')
    command.add_argument('--id', required=True)
    command.add_argument('--decision-note', required=True)
    command = commands.add_parser('report', help='Save evidence verification results')
    command.add_argument('--input', required=True)
    commands.add_parser('sync-agents', help='Update only the managed AGENTS.md section from the reviewed source')
    command = commands.add_parser('import', help='Copy transferable instructions only from the named previous project')
    command.add_argument('--from-project', required=True)
    command = commands.add_parser('validate-source', help='Validate only the named import source format')
    command.add_argument('--from-project', required=True)
    command = commands.add_parser('install-hooks', help='Preview specific hook changes; applying requires a separate flag')
    command.add_argument('--apply', action='store_true')
    commands.add_parser('hook', help='Handle events passed by Codex')
    args = parser.parse_args()
    if args.command == 'checkpoints':
        return CHECKPOINTS
    if args.command == 'validate-source':
        data = registry(project_root(args.from_project))
        return {'count': sum(r['carryForward'] for r in data['requirements'])}
    root = project_root(args.project)
    if args.command == 'status':
        return summary(root)
    if args.command == 'hook':
        return hook(root, json.load(sys.stdin))
    with editing(root):
        data = registry(root)
        if args.command in ('add', 'replace'):
            rule = read_json(safe_path(root, args.input))
            require(isinstance(rule, dict), 'Instructions must be JSON objects.')
            if args.command == 'add':
                rule.setdefault('id', 'proc-' + uuid.uuid4().hex[:12])
                require(rule['id'] not in [r['id'] for r in data['requirements']], 'ID already exists. Use replace to change it.')
                data['requirements'].append(rule)
            else:
                require(rule.get('id') in [r['id'] for r in data['requirements']], 'The ID to replace does not exist.')
                data['requirements'] = [rule if r['id'] == rule['id'] else r for r in data['requirements']]
            save_registry(root, data)
            return {'id': rule['id'], 'message': 'Registered the instruction and reflected strong instructions in AGENTS.md. Configure hooks separately.'}
        if args.command == 'remove':
            require(nonempty(args.decision_note), 'Record the user instruction authorizing removal.')
            require(args.id in [r['id'] for r in data['requirements']], 'The ID to remove does not exist.')
            data['requirements'] = [r for r in data['requirements'] if r['id'] != args.id]
            save_registry(root, data)
            write_json(safe_path(root, f'.work/process-checker/removals/{uuid.uuid4().hex}.json'),
                       {'id': args.id, 'at': now(), 'decisionNote': args.decision_note})
            return {'message': 'Removed the specified instruction. Other instructions and records are preserved.'}
        if args.command == 'sync-agents':
            write_text(safe_path(root, 'AGENTS.md'), projected_agents(root, data))
            return {'message': 'Synchronized strong instructions in AGENTS.md. Hook activation is separate.'}
        if args.command == 'report':
            return report(root, read_json(safe_path(root, args.input)))
        if args.command == 'import':
            return import_requirements(root, args.from_project)
        if args.command == 'install-hooks':
            return install_hooks(root, args.apply)
    raise ValueError('Unsupported operation.')


if __name__ == '__main__':
    try:
        print(json.dumps(main(), ensure_ascii=False, indent=2))
    except (ValueError, OSError, KeyError, TypeError, StopIteration) as exc:
        # Do not silently pass hook errors. Return Stop errors as warnings without infinite continuation.
        if 'hook' in sys.argv:
            print(json.dumps({'systemMessage': 'Process checker could not verify: ' + str(exc)}, ensure_ascii=False))
        else:
            print('Process checker: ' + str(exc), file=sys.stderr)
            sys.exit(1)
