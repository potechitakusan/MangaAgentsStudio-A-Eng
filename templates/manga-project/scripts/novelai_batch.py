"""Batch NovelAI panel request JSON, let humans select candidates, and rebuild PNG/PSD pages with the same placement.

Preserve requests, candidates, selections, and page composition in files for repeatable human-run selection.

  list      List requests, candidate counts, and selections (no network)
  vars      List character, style, and background variables from .env.novelai (no network)
  env-set   Write a prompt variable to .env.novelai (leave other settings unchanged)
  env-migrate Move variables and auxiliary settings from .env etc. in earlier versions to .env.novelai
  templatize Replace matching variable values in request JSON with ${VARIABLE_NAME}
  generate  Generate requests per page, all pages, or IDs sequentially, one image each (dry run by default)
  adopt     Select an image from candidates
  adopt-latest Adopt the highest-numbered PNG in each target folder at once (no network)
  move-unknown Move execution records without images (unknown result) to failed/ after confirmation (not deleted; no network)
  build    Rebuild page PNGs (PSD if requested) from selections, panel placement, and typesetting

Generation uses novelai_api.py validation, cost checks, and execution records; stop on failure without automatic retry.
Never display or save API key values.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import re
import secrets
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parent))
import novelai_api as api  # noqa: E402

REQUESTS_DIR = "input/novelai/requests"
ADOPTED = "input/novelai/adopted.json"
CANDIDATES_DIR = "output/novelai/candidates"
PAGES_DIR = "input/pages"
BUILD_DIR = "output/build"
# Split configuration into three files: .env (shared settings such as API keys and URLs), .env.novelai (NovelAI prompt variables and auxiliary settings),
# and .env.pixai (for PixAI; not read by this script). API keys can still be placed under .secrets/ as before (KEY_FILES in novelai_api.py).
VAR_FILE = ".env.novelai"
VAR_FILES = (VAR_FILE,)
# Locations where variables and auxiliary settings were placed in earlier versions. If any remain there, do not silently ignore them; stop and prompt migration with env-migrate.
LEGACY_VAR_FILES = (".env", ".secrets/novelai.env", ".secrets/.env")
VAR_NAME = re.compile(r"NOVELAI_(?:CHAR|STYLE|BACKGROUND)_[A-Z0-9_]+")
VAR_ASSIGNMENT = re.compile(r"^\s*(?:export\s+)?(NOVELAI_(?:CHAR|STYLE|BACKGROUND)_[A-Z0-9_]+)\s*=(.*)$")
VAR_HELP = "NOVELAI_CHAR_, NOVELAI_STYLE_, or NOVELAI_BACKGROUND_ followed by uppercase ASCII letters, digits, or underscores"
PLACEHOLDER = re.compile(r"\$\{([^}]*)\}")
REQUEST_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9_-]{0,63}")
PAGE_OF = re.compile(r"p(\d{1,3})-")


class BatchError(api.ClientError):
    pass


# ---------------------------------------------------------------- Preflight prompt checks (term detection, not quality judgments)

NEGATION = re.compile(r"\b(?:not|without|neither|never|don't|doesn't|isn't|no(?!\s+humans\b)\s+[a-z]+)\b", re.I)
INTENT = re.compile(r"\b(?:as if|about to|trying to|going to|seems? to|appears? to|wants? to|awkward(?:ly)?|feeling)\b", re.I)
PERSON = re.compile(r"\b(?:\d\s*(?:girl|boy|other)s?|solo)\b", re.I)
# Numeric ages (25 years old, etc.) may not affect appearance; man/woman may create an extra person alongside 1girl/1boy
# (user instruction, 2026-09-29). Exclude terms such as teenage, high school student, and adult from this check.
EXTRA_PERSON = re.compile(r"(?:\b\d+\s*(?:years?[\s-]*old|yo|y/o)\b|\bage[ds]?\s*\d+\b|\d+\s*歳|\b(?:men|women|man|woman)\b)", re.I)
BODY_PART = re.compile(r"\b(?:shoes?|feet|foot|legs?|hands?|fingers?|arms?|lower body)\b", re.I)
COUNT = re.compile(r"\b(\d)\s*(girl|boy|other)s?\b", re.I)
CAMERA = re.compile(r"\b(from above|from below|from behind|from side|from the side|high angle|low angle|dutch angle)\b", re.I)


def positive_texts(request: dict) -> list[str]:
    texts = [request.get("input") or ""]
    caption = ((request.get("parameters") or {}).get("v4_prompt") or {}).get("caption") or {}
    texts.append(caption.get("base_caption") or "")
    texts += [c.get("char_caption", "") for c in caption.get("char_captions") or [] if isinstance(c, dict)]
    return [t for t in texts if isinstance(t, str) and t]


def lint_prompt(request: dict) -> list[str]:
    """Warn about wording unlikely to convey text-storyboard intent visually."""
    # The quality tag "no text" is officially added to the positive prompt; exclude it from negation warnings.
    text = re.sub(r"\bno text\b", "", " , ".join(positive_texts(request)), flags=re.I)
    warnings = []
    found = sorted({m.group(0).lower() for m in NEGATION.finditer(text)})
    if found:
        warnings.append("Negative wording in the positive prompt: " + ", ".join(found) + ". These terms may produce the opposite result. Move them to negative_prompt; use no humans for an empty cast.")
    found = sorted({m.group(0).lower() for m in INTENT.finditer(text)})
    if found:
        warnings.append("Intent wording: " + ", ".join(found) + ". Describe visible face, hand, and body positions.")
    found = sorted({m.group(0).lower() for m in EXTRA_PERSON.finditer(text)})
    if found:
        warnings.append("Numeric age / man/woman: " + ", ".join(found) + ". Numeric ages may not affect appearance; man/woman can add a separate person alongside 1girl/1boy. "
                        "Describe characters with 1girl, 1boy, solo, and appearance terms.")
    no_humans = re.search(r"\bno humans\b", text, re.I)
    if BODY_PART.search(text) and not PERSON.search(text) and not no_humans:
        warnings.append("A body part is specified without a character. Identify whose body, e.g. 1boy, lower body, standing.")
    if no_humans and PERSON.search(text):
        warnings.append("Both no humans and character terms are specified.")
    # Sum maximum counts per character type to avoid double-counting repeated 1girl terms in appearance templates.
    kinds: dict[str, int] = {}
    for number, kind in COUNT.findall(request.get("input") or ""):
        kinds[kind.lower()] = max(kinds.get(kind.lower(), 0), int(number))
    people = sum(kinds.values())
    captions = (((request.get("parameters") or {}).get("v4_prompt") or {}).get("caption") or {}).get("char_captions")
    if people >= 2 and not captions:
        warnings.append(f"{people} people in one prompt. Split into one-person panels or describe posture and spatial relationships before appearance.")
    return warnings


CHARACTERS = "input/novelai/characters.json"
# Auxiliary settings. Read only lines matching the names listed here in order: environment variables -> .env.novelai (never read API keys or other settings).
SETTING_NAMES = {"NOVELAI_QUALITY_TAGS", "NOVELAI_UC_PRESET", "NOVELAI_UC_PRESET_TEXT", "NOVELAI_CHECK_IDENTITY"}
SETTING_ASSIGNMENT = re.compile(r"^\s*(?:export\s+)?(" + "|".join(sorted(SETTING_NAMES)) + r")\s*=(.*)$")


def legacy_lines(root: Path) -> list[tuple[str, int, str]]:
    """Variable and auxiliary setting lines remaining in earlier locations (.env, .secrets) as (file, line_index, variable_name). Values are never returned."""
    found = []
    for relative in LEGACY_VAR_FILES:
        path = api.project_path(root, relative)
        if not path.is_file():
            continue
        for index, line in enumerate(path.read_text(encoding="utf-8-sig").splitlines()):
            match = VAR_ASSIGNMENT.match(line) or SETTING_ASSIGNMENT.match(line)
            if match:
                found.append((relative, index, match.group(1)))
    return found


def check_legacy(root: Path) -> None:
    found = legacy_lines(root)
    if found:
        raise BatchError(f"NovelAI variables and auxiliary settings belong in {VAR_FILE}. Found in legacy locations: "
                         + ", ".join(f"{name} ({relative})" for relative, _, name in found)
                         + f". Run `python -X utf8 scripts/novelai_batch.py env-migrate` to move them to {VAR_FILE}"
                         " (API keys and other lines are left unchanged).")


def env_migrate(root: Path, dry_run: bool) -> list[tuple[str, str]]:
    """Move variable and auxiliary setting lines from legacy locations to the end of .env.novelai and remove them from the source files. Preserve API keys and other lines."""
    found = legacy_lines(root)
    target = api.project_path(root, VAR_FILE)
    current = target.read_text(encoding="utf-8-sig").splitlines() if target.is_file() else []
    existing = {m.group(1) for line in current if (m := VAR_ASSIGNMENT.match(line) or SETTING_ASSIGNMENT.match(line))}
    names = [name for _, _, name in found]
    clash = sorted({n for n in names if n in existing or names.count(n) > 1})
    if clash:
        raise BatchError(f"Cannot migrate because the same name exists in {VAR_FILE} or multiple locations; keep one location: " + ", ".join(clash))
    if dry_run or not found:
        return [(relative, name) for relative, _, name in found]
    lines_by_file: dict[str, set[int]] = {}
    for relative, index, _ in found:
        lines_by_file.setdefault(relative, set()).add(index)
    moved_lines = []
    source_updates = []
    for relative, indexes in lines_by_file.items():
        path = api.project_path(root, relative)
        lines = path.read_text(encoding="utf-8-sig").splitlines()
        moved_lines += [lines[i] for i in sorted(indexes)]
        kept = [line for i, line in enumerate(lines) if i not in indexes]
        source_updates.append((path, "\n".join(kept) + ("\n" if kept else "")))
    # Commit the destination before removing source lines so a copy of the values is always preserved on save failure or interruption.
    temporary = target.with_name(target.name + ".tmp")
    temporary.write_text("\n".join(current + moved_lines) + "\n", encoding="utf-8")
    temporary.replace(target)
    for path, kept in source_updates:
        temporary = path.with_name(path.name + ".tmp")
        temporary.write_text(kept, encoding="utf-8")
        temporary.replace(path)
    return [(relative, name) for relative, _, name in found]


def read_setting(root: Path, name: str) -> str | None:
    if name not in SETTING_NAMES:
        raise BatchError(f"Not an allowed auxiliary setting: {name}")
    check_legacy(root)
    if name in os.environ:
        return os.environ[name]
    pattern = re.compile(r"^\s*(?:export\s+)?" + re.escape(name) + r"\s*=(.*)$")
    for relative in VAR_FILES:
        path = api.project_path(root, relative)
        if not path.is_file():
            continue
        for line in path.read_text(encoding="utf-8-sig").splitlines():
            match = pattern.match(line)
            if match:
                return parse_value(match.group(1))
    return None


def identity_check_enabled(root: Path) -> bool:
    """Perform identifying-feature checks only when NOVELAI_CHECK_IDENTITY=1 (or true, yes, on) is specified."""
    return (read_setting(root, "NOVELAI_CHECK_IDENTITY") or "").strip().lower() in {"1", "true", "yes", "on"}


def load_characters(root: Path) -> dict | None:
    """Identifying features per character and cast per request. Skip this check if the file is absent."""
    path = root / CHARACTERS
    if not path.is_file():
        return None
    data = api.read_json(path)
    if not isinstance(data.get("characters"), dict) or not isinstance(data.get("cast", {}), dict):
        raise BatchError(f"{CHARACTERS} must contain characters and cast objects.")
    return data


def lint_identity(request_id: str, request: dict, characters: dict | None) -> list[str]:
    """Check that each request contains identifying features such as hair color, glasses shape, and clothing layers."""
    if characters is None:
        return []
    text = " , ".join(positive_texts(request)).lower()
    cast = characters.get("cast", {}).get(request_id)
    if cast is None:
        if PERSON.search(text) or BODY_PART.search(text):
            return [f"Character absent from cast in {CHARACTERS}. Register names and visible features (no humans for an empty cast)."]
        return []
    warnings = []
    for name, expected in cast.items():
        features = (characters["characters"].get(name) or {}).get("features")
        if not isinstance(features, dict):
            warnings.append(f"Cast member {name} is absent from characters.")
            continue
        keys = list(features) if expected == "all" else expected
        if not isinstance(keys, list) or any(k not in features for k in keys):
            warnings.append(f"Cast features for {name} do not match characters (use \"all\" or an array of feature names).")
            continue
        missing = [k for k in keys if str(features[k]).lower() not in text]
        if missing:
            warnings.append(f"Missing identifying features for {name}: " + ", ".join(f"{k} ({features[k]})" for k in missing)
                            + ". Use the canonical wording or exclude invisible features in cast.")
    return warnings


def camera_of(request: dict) -> str | None:
    match = CAMERA.search(" , ".join(positive_texts(request)))
    return match.group(1).lower() if match else None


# ---------------------------------------------------------------- Common helpers

def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rel(root: Path, path: Path) -> str:
    return path.relative_to(root).as_posix()


def write_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def request_files(root: Path) -> dict[str, Path]:
    folder = root / REQUESTS_DIR
    files = {}
    for path in sorted(folder.glob("*.json")) if folder.is_dir() else []:
        if not REQUEST_ID.fullmatch(path.stem):
            raise BatchError(f"Invalid characters in request filename: {path.name}")
        files[path.stem] = path
    return files


def page_of(request_id: str) -> int | None:
    match = PAGE_OF.match(request_id)
    return int(match.group(1)) if match else None


def select_ids(root: Path, pages: list[int] | None, ids: list[str] | None, all_pages: bool) -> list[str]:
    files = request_files(root)
    if ids:
        missing = [i for i in ids if i not in files]
        if missing:
            raise BatchError("Missing request JSON: " + ", ".join(missing))
        return ids
    if all_pages:
        chosen = [i for i in files if page_of(i) is not None]
    elif pages:
        chosen = [i for i in files if page_of(i) in pages]
    else:
        raise BatchError("Specify --page, --ids, or --all.")
    if not chosen:
        raise BatchError("No matching request JSON. Filenames must start with a page number, e.g. p01-01.json.")
    return chosen


def candidates(root: Path, request_id: str) -> list[Path]:
    folder = root / CANDIDATES_DIR / request_id
    return sorted((p for p in folder.glob("r*.png") if p.is_file() and re.fullmatch(r"r[0-9]{3,}", p.stem)),
                  key=lambda p: int(p.stem[1:])) if folder.is_dir() else []


def run_records(root: Path, request_id: str) -> list[Path]:
    folder = root / CANDIDATES_DIR / request_id
    return [p for p in folder.glob("r*.novelai.json") if p.is_file() and re.fullmatch(r"r[0-9]{3,}\.novelai\.json", p.name)] if folder.is_dir() else []


def unknown_records(root: Path, request_id: str) -> list[Path]:
    """Execution records without PNGs (unknown result)."""
    return sorted((r for r in run_records(root, request_id) if not r.with_name(r.name.split(".")[0] + ".png").is_file()),
                  key=lambda r: int(r.name.split(".")[0][1:]))


def next_candidate(root: Path, request_id: str) -> int:
    """Find the next candidate number; stop on records without PNGs (unknown result) to prevent resending."""
    unknown = [r.name for r in unknown_records(root, request_id)]
    if unknown:
        raise BatchError(f"{request_id} has execution records with unknown results: {', '.join(unknown)}. "
                         "Check results and consumption at NovelAI, then move records to failed/ before retrying "
                         f"(python -X utf8 scripts/novelai_batch.py move-unknown --ids {request_id}).")
    numbers = [int(p.stem[1:]) for p in candidates(root, request_id)] + [int(r.name.split(".")[0][1:]) for r in run_records(root, request_id)]
    return max(numbers or [0]) + 1


def candidate_ids(root: Path, pages: list[int] | None, ids: list[str] | None, all_pages: bool) -> list[str]:
    """Request IDs with candidate folders. Includes records for panels whose request JSON was deleted or renamed."""
    if ids:
        bad = [i for i in ids if not REQUEST_ID.fullmatch(i)]
        if bad:
            raise BatchError("Invalid characters in request ID: " + ", ".join(bad))
        return ids
    folder = root / CANDIDATES_DIR
    found = sorted(p.name for p in folder.iterdir() if p.is_dir() and REQUEST_ID.fullmatch(p.name)) if folder.is_dir() else []
    return found if all_pages else [i for i in found if page_of(i) in (pages or [])]


def move_unknown(root: Path, ids: list[str], number: int | None, confirmed: bool, note: str) -> list[tuple[str, int, Path | None]]:
    """Move execution records with unknown results to failed/<timestamp>-rNNN/ (not deleted). Without confirmed, only return targets."""
    found = []
    for request_id in ids:
        for record in unknown_records(root, request_id):
            n = int(record.name.split(".")[0][1:])
            if number is None or n == number:
                found.append((request_id, n))
    moved = []
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    for request_id, n in found:
        if not confirmed:
            moved.append((request_id, n, None))
            continue
        folder = root / CANDIDATES_DIR / request_id
        files = [p for p in folder.glob(f"r{n:03d}.*") if p.is_file()]
        target = folder / "failed" / f"{stamp}-r{n:03d}"
        target.mkdir(parents=True)  # Stop if a destination with the same name already exists.
        for path in files:
            path.replace(target / path.name)
        write_json(target / "moved.json", {"action": "move-unknown", "request_id": request_id, "kind": "novelai", "number": n,
                                           "files": [p.name for p in files], "moved_at": datetime.now().isoformat(timespec="seconds"),
                                           "note": note})
        moved.append((request_id, n, target))
    return moved


def load_adopted(root: Path) -> dict:
    path = root / ADOPTED
    if not path.is_file():
        return {"schema_version": 1, "adopted": {}}
    data = api.read_json(path)
    data.setdefault("adopted", {})
    return data


# ---------------------------------------------------------------- Character, style, and background prompt variables

def parse_value(raw: str) -> str:
    raw = raw.strip()
    if raw[:1] in ("'", '"'):
        end = raw.find(raw[0], 1)
        if end < 0:
            raise BatchError("Unclosed quotes in variable value.")
        return raw[1:end]
    return re.split(r"\s+#", raw, maxsplit=1)[0].strip()


def read_variables(root: Path) -> dict[str, tuple[str, str]]:
    """Read only the three permitted variable types from environment variables and .env.novelai; never expand or display API keys or other settings."""
    check_legacy(root)
    found: dict[str, list[tuple[str, str]]] = {}
    for name, value in os.environ.items():
        if VAR_NAME.fullmatch(name):
            found.setdefault(name, []).append((value, "Environment variable"))
    for relative in VAR_FILES:
        path = api.project_path(root, relative)
        if not path.is_file():
            continue
        for line in path.read_text(encoding="utf-8-sig").splitlines():
            match = VAR_ASSIGNMENT.match(line)
            if match:
                found.setdefault(match.group(1), []).append((parse_value(match.group(2)), relative))
    duplicated = [f"{n} ({' / '.join(s for _, s in v)})" for n, v in found.items() if len(v) > 1]
    if duplicated:
        raise BatchError("Duplicate variable locations; keep one location: " + ", ".join(duplicated))
    return {name: values[0] for name, values in found.items()}


def expand(value, variables: dict[str, tuple[str, str]], used: set[str]):
    if isinstance(value, str):
        def replace(match):
            name = match.group(1)
            if not VAR_NAME.fullmatch(name):
                raise BatchError(f"Invalid variable: ${{{name}}}. Variable names must start with {VAR_HELP}.")
            if name not in variables:
                raise BatchError(f"Variable {name} not found in {VAR_FILE} or other sources. Check with vars.")
            used.add(name)
            return variables[name][0]
        return PLACEHOLDER.sub(replace, value)
    if isinstance(value, list):
        return [expand(v, variables, used) for v in value]
    if isinstance(value, dict):
        return {k: expand(v, variables, used) for k, v in value.items()}
    return value


def resolved_request(root: Path, request_id: str, variables) -> tuple[dict, set[str]]:
    raw = api.read_json(request_files(root)[request_id])
    used: set[str] = set()
    return expand(raw, variables, used), used


def env_set(root: Path, name: str, value: str) -> str:
    if not VAR_NAME.fullmatch(name):
        raise BatchError(f"Variable names must start with {VAR_HELP}.")
    if "\n" in value or "\r" in value:
        raise BatchError("The value must be a single line.")
    if '"' in value and "'" in value:
        raise BatchError("A value cannot contain both ' and \".")
    elsewhere = [s for n, (_, s) in read_variables(root).items() if n == name and s != VAR_FILE]
    if elsewhere:
        raise BatchError(f"{name} exists in {elsewhere[0]}. Edit it there or remove the duplicate.")
    quote = "'" if '"' in value else '"'
    new_line = f"{name}={quote}{value}{quote}"
    path = api.project_path(root, VAR_FILE)
    lines = path.read_text(encoding="utf-8-sig").splitlines() if path.is_file() else []
    pattern = re.compile(r"^\s*(?:export\s+)?" + re.escape(name) + r"\s*=")
    replaced = False
    for i, line in enumerate(lines):
        if pattern.match(line):
            lines[i] = new_line
            replaced = True
    if not replaced:
        lines.append(new_line)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text("\n".join(lines) + "\n", encoding="utf-8")
    temporary.replace(path)
    return "updated" if replaced else "added"


def templatize(root: Path, name: str, dry_run: bool) -> dict[str, int]:
    variables = read_variables(root)
    if name not in variables:
        raise BatchError(f"Variable {name} not found. Set it with env-set first.")
    value = variables[name][0]
    if len(value) < 8:
        raise BatchError("Value too short for safe automatic replacement.")
    counts = {}

    def walk(node):
        if isinstance(node, str):
            counts["_"] = counts.get("_", 0) + node.count(value)
            return node.replace(value, "${" + name + "}")
        if isinstance(node, list):
            return [walk(v) for v in node]
        if isinstance(node, dict):
            return {k: walk(v) for k, v in node.items()}
        return node

    result = {}
    for request_id, path in request_files(root).items():
        counts.clear()
        data = walk(api.read_json(path))
        if counts.get("_"):
            result[request_id] = counts["_"]
            if not dry_run:
                write_json(path, data)
    return result


# ---------------------------------------------------------------- Generation and adoption

def generate(root: Path, args) -> None:
    ids = select_ids(root, args.page, args.ids, args.all)
    if len(ids) > args.max:
        raise BatchError(f"{len(ids)} requests exceed the limit of {args.max}. Split by page or specify --max.")
    variables = read_variables(root)
    plan = []
    warned = []
    cameras: dict[int | None, list[tuple[str, str | None]]] = {}
    characters = load_characters(root) if identity_check_enabled(root) else None
    if characters is not None:
        print("Identifying-feature check: enabled (NOVELAI_CHECK_IDENTITY)")
    for request_id in ids:
        request, used = resolved_request(root, request_id, variables)
        notes = lint_prompt(request) + lint_identity(request_id, request, characters)
        cameras.setdefault(page_of(request_id), []).append((request_id, camera_of(request)))
        existing = candidates(root, request_id)
        mode = args.seed if args.seed != "auto" else ("request" if not existing else "random")
        if mode == "random":
            request.setdefault("parameters", {})["seed"] = secrets.randbelow(4294967296)
        request, payload = api.prepare_request_data(root, request)
        number = next_candidate(root, request_id)
        output = f"{CANDIDATES_DIR}/{request_id}/r{number:03d}.png"
        params = request["parameters"]
        plan.append((request_id, request, payload, output))
        print(f"{request_id}: {params['width']}×{params['height']}px / {params['steps']} steps / seed {params['seed']}"
              f" / variables {','.join(sorted(used)) or 'none'} → {output}")
        for note in notes:
            print(f"  [Warning] {note}")
        if notes:
            warned.append(request_id)
    selected = set(ids)
    for page in cameras:
        if page is None:
            continue
        # Even for partial regeneration, check all page panels in p01-03 format, excluding replacement variants.
        base_ids = [i for i in request_files(root) if page_of(i) == page and re.fullmatch(r"p\d{1,3}-\d{1,3}", i)]
        items = [(i, camera_of(resolved_request(root, i, variables)[0])) for i in base_ids]
        for i in range(2, len(items)):
            if not selected.intersection(r for r, _ in items[i - 2:i + 1]):
                continue
            run = [c for _, c in items[i - 2:i + 1]]
            if run[0] and run.count(run[0]) == 3:
                print(f"  [Warning] {items[i][0]}: Three consecutive panels use the same camera angle ({run[0]}). Check storyboard intent.")
                warned.append(items[i][0])
    if warned:
        print(f"Prompt warnings: {len(set(warned))}. Fix them or document reasons in docs/production/NOVELAI-BATCH.md before"
              " sending with --accept-warnings. See request-prompt construction in docs/knowledge/novelai-composed-production.md.")
    if not args.execute:
        print(f"Not sent ({len(plan)} requests). Execution requires --execute and cost confirmation.")
        return
    if warned and not args.accept_warnings:
        raise BatchError("Not sent because prompt warnings remain (" + ", ".join(sorted(set(warned))) + ").")
    done = []
    for index, (request_id, request, payload, output) in enumerate(plan):
        if index:
            time.sleep(args.interval)
        print(f"[{index + 1}/{len(plan)}] {request_id}")
        try:
            api.execute_generation(root, request, payload, output, args)
        except api.ClientError as error:
            raise BatchError(f"Stopped at {request_id} ({len(done)} succeeded). Remaining requests were not sent. No automatic retry.\n{error}") from None
        done.append(output)
    print(f"Completed: {len(done)}. Compare candidates and record the selected number with adopt.")
    print("Example: python -X utf8 scripts/novelai_batch.py adopt " + plan[0][0] + " --candidate " + Path(plan[0][3]).stem[1:])


def adopt(root: Path, request_id: str, number: int | None, file: str | None) -> Path:
    if request_id not in request_files(root) and not file:
        raise BatchError(f"Missing request JSON: {request_id}")
    if file:
        path = api.project_path(root, file)
    else:
        path = root / CANDIDATES_DIR / request_id / f"r{number:03d}.png"
    if not path.is_file():
        raise BatchError("Selected image not found: " + (rel(root, path) if path.is_relative_to(root) else str(file)))
    data = load_adopted(root)
    data["adopted"][request_id] = {"path": rel(root, path), "sha256": sha(path), "adopted_at": now()}
    write_json(root / ADOPTED, data)
    return path


def adopt_latest(root: Path, ids: list[str], dry_run: bool) -> dict[str, Path]:
    """Check candidates for every target first, then save the selections in one write."""
    chosen = {}
    missing = []
    for request_id in ids:
        available = candidates(root, request_id)
        if not available:
            missing.append(request_id)
        else:
            chosen[request_id] = available[-1]
    if missing:
        raise BatchError("No candidate PNGs for: " + ", ".join(missing) + ". The selection record was not changed.")
    if not dry_run:
        data = load_adopted(root)
        timestamp = now()
        for request_id, path in chosen.items():
            data["adopted"][request_id] = {"path": rel(root, path), "sha256": sha(path), "adopted_at": timestamp}
        write_json(root / ADOPTED, data)
    return chosen


# ---------------------------------------------------------------- Page rebuilding

def placement(frame, image_size, focus, zoom, rotation):
    """Cover the panel bounding box with the image. focus is its desired center point (0 to 1)."""
    x0, y0, x1, y1 = frame
    bw, bh = x1 - x0, y1 - y0
    iw, ih = image_size
    theta = math.radians(rotation)
    c, s = math.cos(theta), math.sin(theta)
    need_w, need_h = bw * abs(c) + bh * abs(s), bw * abs(s) + bh * abs(c)
    scale = max(need_w / iw, need_h / ih) * zoom
    fx, fy = focus[0] * iw, focus[1] * ih
    notes = []
    if not rotation:
        hw, hh = bw / (2 * scale), bh / (2 * scale)
        cx, cy = min(max(fx, hw), iw - hw) if iw >= 2 * hw else iw / 2, min(max(fy, hh), ih - hh) if ih >= 2 * hh else ih / 2
        # Report edge limits only along movable axes, not axes where the image fits the panel exactly.
        movable_x, movable_y = iw - 2 * hw > 1, ih - 2 * hh > 1
        if (movable_x and abs(cx - fx) > 0.5) or (movable_y and abs(cy - fy) > 0.5):
            notes.append("focus exceeded the image edge; the visible region was clamped.")
        fx, fy = cx, cy
    ox, oy = bw / 2, bh / 2
    # Inverse transform from panel to source coordinates (PIL AFFINE format).
    a, b = c / scale, s / scale
    d, e = -s / scale, c / scale
    return [a, b, fx - (a * ox + b * oy), d, e, fy - (d * ox + e * oy)], notes


def build(root: Path, page: int, write_psd: bool) -> Path:
    from PIL import Image
    import export_composed_psd as exporter
    import typeset_manga as typesetter

    manifest_path = root / PAGES_DIR / f"page-{page:02d}.json"
    if not manifest_path.is_file():
        raise BatchError(f"Page manifest not found: {rel(root, manifest_path)}")
    manifest = api.read_json(manifest_path)
    if manifest.get("schema_version") != 1:
        raise BatchError("Page manifest schema_version must be 1.")
    layout = api.read_json(api.project_path(root, manifest["layout"]))
    working = layout["dimensions"]["working"]
    size = [int(round(working["width"])), int(round(working["height"]))]
    polygons = {p["order"]: [list(v) for v in p["polygon"]] for p in layout["template"]["panels"]}
    adopted = load_adopted(root)["adopted"]

    base = root / BUILD_DIR / f"page-{page:02d}"
    number = 1 + max([int(p.name[1:]) for p in base.glob("v[0-9][0-9][0-9]")] or [0])
    out_dir = base / f"v{number:03d}"

    panels, notes, missing = [], {}, []
    for entry in manifest.get("panels", []):
        order = entry["panel"]
        if order not in polygons:
            raise BatchError(f"Panel {order} is absent from the layout.")
        if entry.get("source"):
            source = entry["source"]
        elif entry.get("request"):
            chosen = adopted.get(entry["request"])
            if not chosen:
                missing.append(entry["request"])
                continue
            source = chosen["path"]
            if sha(api.project_path(root, source)) != chosen["sha256"]:
                raise BatchError(f"Selected image changed since adoption: {source}")
        else:
            continue  # Panel without artwork
        with Image.open(api.project_path(root, source)) as opened:
            image_size = opened.size
        polygon = polygons[order]
        xs, ys = [v[0] for v in polygon], [v[1] for v in polygon]
        frame = [min(xs), min(ys), max(xs), max(ys)]
        affine, note = placement(frame, image_size, entry.get("focus", [0.5, 0.5]), float(entry.get("zoom", 1.0)),
                                 float(entry.get("rotation", 0)))
        a, b, c, d, e, f = affine
        uncovered = False
        for px, py in polygon:  # A panel corner outside the source image has no artwork.
            lx, ly = px - frame[0], py - frame[1]
            sx, sy = a * lx + b * ly + c, d * lx + e * ly + f
            uncovered |= not (-1 <= sx <= image_size[0] + 1 and -1 <= sy <= image_size[1] + 1)
        if uncovered:
            note = note + ["Part of the panel has no artwork. Review focus, zoom, or rotation, or adjust manually in the PSD."]
        if note:
            notes[f"Panel {order}"] = note
        panel = {"name": entry.get("name", f"Panel {order:02d}"), "source": source, "frame": frame,
                 "inverse_affine": affine, "polygon": polygon}
        if entry.get("original_source"):
            panel["original_source"] = entry["original_source"]
        panels.append(panel)
    if missing:
        raise BatchError("Images not yet selected: " + ", ".join(missing) + ". Select with adopt before build.")

    # Create balloons, text, in-world text, and frames as transparent layers. Frames near the top hide artwork outside panels.
    typeset_spec = api.read_json(api.project_path(root, manifest["typeset"])) if manifest.get("typeset") else {
        "schema_version": 1, "balloons": []}
    typeset_spec.setdefault("layout", manifest["layout"])
    report = typesetter.render(typeset_spec, root, out_dir / "typeset", None, not manifest.get("frames_in_art", False))

    # Place extra assets such as sound effects above frames and below balloons.
    extra = []
    for index, item in enumerate(manifest.get("overlays", []), 1):
        with Image.open(api.project_path(root, item["source"])) as opened:
            image = opened.convert("RGBA")
        scale = float(item.get("scale", 1.0))
        if scale != 1.0:
            image = image.resize((max(1, round(image.width * scale)), max(1, round(image.height * scale))), Image.Resampling.LANCZOS)
        if item.get("rotation"):
            image = image.rotate(float(item["rotation"]), resample=Image.Resampling.BICUBIC, expand=True)
        path = out_dir / "overlays" / f"{index:02d}.png"
        path.parent.mkdir(parents=True, exist_ok=True)
        image.save(path)
        cx, cy = item["center"]
        extra.append({"name": item.get("name", f"Extra asset {index:02d}"), "source": rel(root, path),
                      "position": [int(round(cx - image.width / 2)), int(round(cy - image.height / 2))]})
    overlays = []
    for layer in report["overlays_for_export_composed_psd"]:
        if layer["name"] == "Balloons":
            overlays.extend(extra)
            extra = []
        overlays.append(layer)
    overlays.extend(extra)

    spec = {"schema_version": 1, "page": {"size": size, "dpi": manifest.get("dpi", 300)}, "panels": panels, "overlays": overlays}
    result = exporter.export(spec, root, Path(rel(root, out_dir / f"page-{page:02d}")), write_psd, False)
    # Build reduced/annotated review images from completed pages including artwork; typesetting-folder samples omit artwork.
    review = typesetter.review_images(out_dir / f"page-{page:02d}.png", typeset_spec, root, out_dir, f"page-{page:02d}")
    write_json(out_dir / "build.json", {
        "schema_version": 1, "built_at": now(), "page": page, "manifest": rel(root, manifest_path),
        "manifest_sha256": sha(manifest_path), "panels": [{"name": p["name"], "source": p["source"]} for p in panels],
        "placement_notes": notes, "typeset_summary": report["summary"], "typeset_check": rel(root, out_dir / "typeset" / "check.json"),
        "png": result["output_png"], "psd": rel(root, out_dir / f"page-{page:02d}.psd") if write_psd else None,
        "review_display": rel(root, review["display"]), "review_check_overlay": rel(root, review["check_overlay"]),
        "psd_verification": result["verification"]})
    print(f"page {page}: {result['output_png']}" + (f" (with PSD)" if write_psd else "") +
          f" / typesetting checks: {report['summary']['error']} errors, {report['summary']['warning']} warnings")
    print(f"  Review (with artwork): {rel(root, review['display'])}; annotated: {rel(root, review['check_overlay'])} (do not publish)")
    for name, messages in notes.items():
        print(f"  [Placement] {name}: {' / '.join(messages)}")
    for issue in report["issues"]:
        if issue["level"] == "error":
            print(f"  [error] {issue['code']} {issue['target']}: {issue['message_ja']}")
    return out_dir


# ---------------------------------------------------------------- CLI

def pages_from_manifests(root: Path) -> list[int]:
    folder = root / PAGES_DIR
    found = [int(m.group(1)) for p in folder.glob("page-*.json") if (m := re.fullmatch(r"page-(\d{2,3})", p.stem))] if folder.is_dir() else []
    if not found:
        raise BatchError(f"No page manifests found, e.g. {PAGES_DIR}/page-01.json.")
    return sorted(found)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    commands = parser.add_subparsers(dest="command", required=True)
    listing = commands.add_parser("list", help="List requests, candidates, and selections")
    listing.add_argument("--page", type=int, action="append")
    show = commands.add_parser("vars", help="List character, style, and background variables")
    show.add_argument("--show-values", action="store_true", help="Also display values (prompt text)")
    setter = commands.add_parser("env-set", help="Write a character, style, or background variable to .env.novelai")
    setter.add_argument("name")
    group = setter.add_mutually_exclusive_group(required=True)
    group.add_argument("--value")
    group.add_argument("--value-file", help="UTF-8 text file containing the value (project-relative path)")
    migrate = commands.add_parser("env-migrate", help="Move variables and auxiliary settings from .env or .secrets in earlier versions to .env.novelai")
    migrate.add_argument("--dry-run", action="store_true", help="Display variable names to move without modifying files")
    templ = commands.add_parser("templatize", help="Replace variable values in request JSON with ${VARIABLE_NAME}")
    templ.add_argument("name")
    templ.add_argument("--dry-run", action="store_true")
    gen = commands.add_parser("generate", help="Generate one image per request sequentially (dry run by default)")
    gen.add_argument("--page", type=int, action="append", help="Page number; repeatable")
    gen.add_argument("--ids", type=lambda s: [v for v in s.split(",") if v], help="Comma-separated request IDs")
    gen.add_argument("--all", action="store_true", help="Requests for all pages (p01-... format)")
    gen.add_argument("--seed", choices=("auto", "request", "random"), default="auto",
                     help="auto: request seed on first run, random seeds afterward (default)")
    gen.add_argument("--interval", type=float, default=3.0, help="Interval between requests (seconds)")
    gen.add_argument("--max", type=int, default=30, help="Maximum requests per run")
    gen.add_argument("--execute", action="store_true", help="Send human-requested generation")
    gen.add_argument("--accept-warnings", action="store_true", help="Prompt warnings reviewed and reasons for retaining them recorded")
    costs = gen.add_mutually_exclusive_group()
    costs.add_argument("--confirm-zero-anlas", action="store_true")
    costs.add_argument("--allow-anlas", action="store_true")
    gen.add_argument("--confirm-v5-allowance", action="store_true")
    gen.add_argument("--cost-note")
    pick = commands.add_parser("adopt", help="Record the selected image")
    pick.add_argument("request_id")
    which = pick.add_mutually_exclusive_group(required=True)
    which.add_argument("--candidate", type=int, help="Candidate number (3 for r003.png)")
    which.add_argument("--file", help="Specify a project image directly, e.g. a corrected version")
    latest = commands.add_parser("adopt-latest", help="Adopt the highest-numbered PNG in each folder at once")
    target = latest.add_mutually_exclusive_group(required=True)
    target.add_argument("--page", type=int, action="append", help="Page number; repeatable")
    target.add_argument("--ids", type=lambda s: [v for v in s.split(",") if v], help="Comma-separated request IDs")
    target.add_argument("--all", action="store_true", help="Requests for all pages (p01-... format)")
    latest.add_argument("--dry-run", action="store_true", help="Show the targets without changing the selection record")
    unknown = commands.add_parser("move-unknown", help="Move execution records with unknown results to failed/ (displays targets by default)")
    target = unknown.add_mutually_exclusive_group(required=True)
    target.add_argument("--page", type=int, action="append", help="Page number; repeatable")
    target.add_argument("--ids", type=lambda s: [v for v in s.split(",") if v], help="Comma-separated request IDs")
    target.add_argument("--all", action="store_true", help="All requests with candidate folders")
    unknown.add_argument("--candidate", type=int, help="Record number (3 for r003.novelai.json). If omitted, all unknown records for the targets")
    unknown.add_argument("--confirm-checked", action="store_true",
                         help="Verified NovelAI image history and Anlas consumption, confirming no image was produced (or it is unneeded)")
    unknown.add_argument("--note", default="", help="Verification notes (saved in moved.json)")
    make = commands.add_parser("build", help="Rebuild page PNG (PSD if requested)")
    make.add_argument("--page", type=int, action="append")
    make.add_argument("--all", action="store_true")
    make.add_argument("--write-psd", action="store_true", help="Also create PSD after PNG confirmation, when requested")
    args = parser.parse_args(argv)
    root = Path(__file__).resolve().parents[1]
    try:
        if not (root / "project.json").is_file():
            raise BatchError("Use the copy of this script in a work project's scripts/ folder.")
        if args.command == "list":
            adopted = load_adopted(root)["adopted"]
            for request_id, path in request_files(root).items():
                if args.page and page_of(request_id) not in args.page:
                    continue
                used = set(PLACEHOLDER.findall(path.read_text(encoding="utf-8-sig")))
                chosen = adopted.get(request_id, {}).get("path", "not selected")
                print(f"{request_id}: {len(candidates(root, request_id))} candidates / selected {chosen} / variables {','.join(sorted(used)) or 'none'}")
        elif args.command == "vars":
            variables = read_variables(root)
            if not variables:
                print(f"No character, style, or background prompt variables (NOVELAI_CHAR_, NOVELAI_STYLE_, NOVELAI_BACKGROUND_ in {VAR_FILE}).")
            for name, (value, source) in sorted(variables.items()):
                print(f"{name} ({source}, {len(value)} characters)" + (f": {value}" if args.show_values else ""))
        elif args.command == "env-set":
            value = args.value if args.value is not None else api.project_path(root, args.value_file).read_text(encoding="utf-8-sig").strip()
            print(f"{args.name} {env_set(root, args.name, value)} in {VAR_FILE} (other lines unchanged).")
        elif args.command == "env-migrate":
            moved = env_migrate(root, args.dry_run)
            for relative, name in moved:
                print(f"{name}: {relative} → {VAR_FILE}" + (" (check only)" if args.dry_run else ""))
            print(f"No lines to migrate. Variables and auxiliary settings are in {VAR_FILE}." if not moved else
                  "API keys and other lines were preserved in their original files (values not displayed).")
        elif args.command == "templatize":
            result = templatize(root, args.name, args.dry_run)
            for request_id, count in result.items():
                print(f"{request_id}: {count} occurrences" + (" (dry run)" if args.dry_run else ""))
            if not result:
                print("No matching occurrences to replace.")
        elif args.command == "generate":
            generate(root, args)
        elif args.command == "adopt":
            path = adopt(root, args.request_id, args.candidate, args.file)
            print(f"{args.request_id}: Selected {rel(root, path)}.")
        elif args.command == "adopt-latest":
            if args.ids == []:
                raise BatchError("Specify request IDs with --ids.")
            ids = select_ids(root, args.page, args.ids, args.all)
            chosen = adopt_latest(root, ids, args.dry_run)
            for request_id, path in chosen.items():
                print(f"{request_id}: {rel(root, path)}" + (" (check only)" if args.dry_run else " selected."))
        elif args.command == "move-unknown":
            if args.ids == []:
                raise BatchError("Specify request IDs with --ids.")
            ids = candidate_ids(root, args.page, args.ids, args.all)
            moved = move_unknown(root, ids, args.candidate, args.confirm_checked, args.note)
            for request_id, number, target in moved:
                print(f"{request_id}: r{number:03d}.novelai.json" + (f" → {rel(root, target)}" if target else " (unknown result; check only)"))
            if not moved:
                print("No execution records with unknown results.")
            elif not args.confirm_checked:
                print("Check NovelAI image history and Anlas consumption. If no image was produced (or it is unneeded), pass --confirm-checked"
                      " to move the record to failed/. If an image was produced, save it in the same folder as rNNN.png without moving the record.")
        elif args.command == "build":
            pages = pages_from_manifests(root) if args.all else (args.page or [])
            if not pages:
                raise BatchError("Specify --page or --all.")
            for page in pages:
                build(root, page, args.write_psd)
    except api.ClientError as error:
        print("Error: " + str(error), file=sys.stderr)
        return 1
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(f"Error: {type(error).__name__}: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
