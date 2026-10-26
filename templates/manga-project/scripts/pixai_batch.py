"""Batch-test per-panel PixAI request JSON files, let a human select candidates, and rebuild page PNGs and PSDs with consistent placement.

Saves all requests, candidates, adoptions, and page manifests to files so a human can iterate and pick adopted images.

  list          List requests, candidate counts, and adoption status (no network)
  vars          List character, style, background, and LoRA variables in .env.pixai (no network)
  env-set       Write a prompt variable to .env.pixai (leaves other settings untouched)
  templatize    Replace matching literal text in request JSON files with ${VAR_NAME}
  generate      Sequentially generate requests by page, all pages, or selected IDs one task at a time (dry-run by default)
  fetch         Re-fetch execution records interrupted while waiting for completion via taskId (does not resend generation)
  adopt         Select an adopted image from candidates
  adopt-latest  Batch-adopt the highest-numbered PNG in each target candidate folder (no network)
  move-unknown  Move imageless execution records (unknown result) to failed/ after confirmation (does not delete; no network)
  build         Rebuild page PNGs (and PSDs when requested) from adopted images, panel placement, and typesetting specs

Generation uses the same validation, cost confirmation, and execution records as pixai_api.py, and stops without automatic retry on failure.
API key values are never displayed or saved.
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
import pixai_api as api  # noqa: E402

REQUESTS_DIR = "input/pixai/requests"
ADOPTED = "input/pixai/adopted.json"
CANDIDATES_DIR = "output/pixai/candidates"
PAGES_DIR = "input/pages"
BUILD_DIR = "output/build"
# Configuration files are split into three: .env (API keys, URLs, and shared settings), .env.novelai (NovelAI; not read by this script),
# and .env.pixai (PixAI prompt variables and auxiliary settings). API keys can also live under .secrets/ (pixai_api.py KEY_FILES).
VAR_FILE = ".env.pixai"
VAR_FILES = (VAR_FILE,)
VAR_NAME = re.compile(r"PIXAI_(?:CHAR|STYLE|BACKGROUND|LORA)_[A-Z0-9_]+")
VAR_ASSIGNMENT = re.compile(r"^\s*(?:export\s+)?(PIXAI_(?:CHAR|STYLE|BACKGROUND|LORA)_[A-Z0-9_]+)\s*=(.*)$")
VAR_HELP = "uppercase ASCII letters, digits, and _ starting with PIXAI_CHAR_, PIXAI_STYLE_, PIXAI_BACKGROUND_, or PIXAI_LORA_"
PLACEHOLDER = re.compile(r"\$\{([^}]*)\}")
REQUEST_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9_-]{0,63}")
PAGE_OF = re.compile(r"p(\d{1,3})-")


class BatchError(api.ClientError):
    pass


# ---------------------------------------------------------------- Pre-send prompt inspection (wording detection, not quality judgment)

NEGATION = re.compile(r"\b(?:not|without|neither|never|don't|doesn't|isn't|no(?!\s+humans\b)\s+[a-z]+)\b", re.I)
INTENT = re.compile(r"\b(?:as if|about to|trying to|going to|seems? to|appears? to|wants? to|awkward(?:ly)?|feeling)\b", re.I)
PERSON = re.compile(r"\b(?:\d\+?\s*(?:girl|boy|other)s?|multiple (?:girls|boys|others)|crowd|solo)\b", re.I)
# Numeric ages (e.g. 25 years old) have little visual effect, and man/woman can spawn an extra person alongside 1girl/1boy.
EXTRA_PERSON = re.compile(r"(?:\b\d+\s*(?:years?[\s-]*old|yo|y/o)\b|\bage[ds]?\s*\d+\b|\d+\s*歳|\b(?:men|women|man|woman)\b)", re.I)
BODY_PART = re.compile(r"\b(?:shoes?|feet|foot|legs?|hands?|fingers?|arms?|lower body)\b", re.I)
COUNT = re.compile(r"\b(\d)\s*(girl|boy|other)s?\b", re.I)
# When there are 2+ characters, pixai_compose.py starts each character segment with a bare type tag (girl/boy/other) and places --layout before them.
POSITION = re.compile(r"\b(?:left|right|facing each other|face to face|side by side|back to back|in front of|behind)\b", re.I)
CAMERA = re.compile(r"\b(from above|from below|from behind|from side|from the side|high angle|low angle|dutch angle)\b", re.I)
# PixAI supports parenthetical emphasis (like A1111/ComfyUI) and does not support square or curly brackets (official v1 prompts documentation).
UNSUPPORTED_BRACKETS = re.compile(r"[\[\]{}]")
COLON_WEIGHT = re.compile(r"-?\d+(?:\.\d+)?::|::")


def positive_texts(request: dict) -> list[str]:
    if request.get("api") == "v1":
        params = request.get("parameters") or {}
        return [t for t in (params.get("prompts"),) if isinstance(t, str) and t]
    body = request.get("body") or {}
    texts = [body.get("prompt") or ""]
    texts += [item.get("triggerWords", "") for item in body.get("loras") or [] if isinstance(item, dict)]
    style = body.get("style")
    if isinstance(style, dict) and style.get("type") == "custom":
        texts.append(style.get("custom") or "")
    return [t for t in texts if isinstance(t, str) and t]


def lint_prompt(request: dict) -> list[str]:
    """Warn about phrasing that rarely translates into the image or syntax that does not work on PixAI."""
    text = re.sub(r"\bno text\b", "", " , ".join(positive_texts(request)), flags=re.I)
    warnings = []
    found = sorted({m.group(0).lower() for m in NEGATION.finditer(text)})
    if found:
        warnings.append("Negative wording in positive prompt: " + ", ".join(found) + ". The model may react to the negated word and draw it anyway; move exclusions to negativePrompt, or use no humans for an empty scene")
    found = sorted({m.group(0).lower() for m in INTENT.finditer(text)})
    if found:
        warnings.append("Intent phrasing: " + ", ".join(found) + ". Describe visible face, hand, and body poses instead")
    found = sorted({m.group(0).lower() for m in EXTRA_PERSON.finditer(text)})
    if found:
        warnings.append("Numeric age or man/woman: " + ", ".join(found) + ". Numeric ages have little visual effect, and man/woman can spawn an extra person alongside 1girl/1boy; "
                        "describe characters using 1girl/1boy/solo and visible traits")
    no_humans = re.search(r"\bno humans\b", text, re.I)
    if BODY_PART.search(text) and not PERSON.search(text) and not no_humans:
        warnings.append("Body part mentioned without a person tag. Specify whose body it is, e.g. 1boy, lower body, standing")
    if no_humans and PERSON.search(text):
        warnings.append("Both no humans and person tags are present at the same time")
    if UNSUPPORTED_BRACKETS.search(text):
        warnings.append("Square or curly brackets detected. PixAI supports only parenthetical emphasis (word:1.2) (official)")
    if COLON_WEIGHT.search(text):
        warnings.append("NovelAI-style weight syntax (1.2::word::) detected. Write (word:1.2) on PixAI")
    kinds: dict[str, int] = {}
    for number, kind in COUNT.findall(text):
        kinds[kind.lower()] = max(kinds.get(kind.lower(), 0), int(number))
    people = sum(kinds.values())
    tags = [t.strip().lower() for t in text.split(",")]
    first = next((i for i, t in enumerate(tags) if t in ("girl", "boy", "other")), None)
    placed = first is not None and any(POSITION.search(t) for t in tags[:first])
    if people >= 2 and not placed:
        warnings.append(f"Packing {people} people into a single prompt (PixAI has no per-character prompt slots). Split into separate single-character panels or "
                        "place posture and relative position (left, right, facing each other, etc.) before appearances (pixai_compose.py --layout)")
    helper = (request.get("body") or {}).get("promptHelper") if request.get("api") == "v2" else \
        ((request.get("parameters") or {}).get("promptHelper") or {}).get("enable")
    if helper in ("enable", True):
        warnings.append("promptHelper is enabled. PixAI rewrites the prompt before generation, which can cause drift from the text storyboard")
    return warnings


CHARACTERS = "input/pixai/characters.json"
# Auxiliary settings. Read only lines matching the names listed here in order: environment variables -> .env.pixai (never read API keys, etc.).
SETTING_NAMES = {"PIXAI_MODEL", "PIXAI_QUALITY_TAGS", "PIXAI_NEGATIVE_PROMPT", "PIXAI_PROMPT_HELPER", "PIXAI_CHECK_IDENTITY"}


def read_setting(root: Path, name: str) -> str | None:
    if name not in SETTING_NAMES:
        raise BatchError(f"Not a permitted auxiliary setting: {name}")
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
    """Run character identity feature checks only when PIXAI_CHECK_IDENTITY=1 (true, yes, on) is specified."""
    return (read_setting(root, "PIXAI_CHECK_IDENTITY") or "").strip().lower() in {"1", "true", "yes", "on"}


def load_characters(root: Path) -> dict | None:
    """Per-character identifying features and per-request cast. Skipped if the file does not exist."""
    path = root / CHARACTERS
    if not path.is_file():
        return None
    data = api.read_json(path)
    if not isinstance(data.get("characters"), dict) or not isinstance(data.get("cast", {}), dict):
        raise BatchError(f"{CHARACTERS} must contain characters and cast objects.")
    return data


def lint_identity(request_id: str, request: dict, characters: dict | None) -> list[str]:
    """Check whether identifying features (hair color, glasses shape, clothing layering, etc.) are present for each cast member in the request."""
    if characters is None:
        return []
    text = " , ".join(positive_texts(request)).lower()
    cast = characters.get("cast", {}).get(request_id)
    if cast is None:
        if PERSON.search(text) or BODY_PART.search(text):
            return [f"Character absent from cast in {CHARACTERS}. Register names and visible features (no humans for an empty cast)"]
        return []
    warnings = []
    for name, expected in cast.items():
        features = (characters["characters"].get(name) or {}).get("features")
        if not isinstance(features, dict):
            warnings.append(f"Cast member {name} is absent from characters")
            continue
        keys = list(features) if expected == "all" else expected
        if not isinstance(keys, list) or any(k not in features for k in keys):
            warnings.append(f"Cast features for {name} do not match characters (\"all\" or an array of feature names)")
            continue
        missing = [k for k in keys if str(features[k]).lower() not in text]
        if missing:
            warnings.append(f"Missing identifying features for {name}: " + ", ".join(f"{k} ({features[k]})" for k in missing)
                            + ". Use the canonical wording or exclude invisible features in cast")
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
    return [p for p in folder.glob("r*.pixai.json") if p.is_file() and re.fullmatch(r"r[0-9]{3,}\.pixai\.json", p.name)] if folder.is_dir() else []


def record_number(record: Path) -> int:
    return int(record.name.split(".")[0][1:])


def reserved_numbers(record: Path) -> list[int]:
    """When a single task generates multiple images (batchSize 4), the record is saved under the first number and reserves the remaining numbers."""
    try:
        data = json.loads(record.read_text(encoding="utf-8-sig"))
        names = [Path(p).stem for p in data.get("reservedOutputs") or []]
        numbers = [int(n[1:]) for n in names if re.fullmatch(r"r[0-9]{3,}", n)]
    except (OSError, ValueError, AttributeError, TypeError):
        numbers = []
    return numbers or [record_number(record)]


def unknown_records(root: Path, request_id: str) -> list[Path]:
    """Records missing their primary PNG, or multi-image records where some outputs failed to save."""
    found = []
    for record in run_records(root, request_id):
        if not record.with_name(record.name.split(".")[0] + ".png").is_file():
            found.append(record)
            continue
        data = api.read_json(record)
        if data.get("missingOutputs"):
            found.append(record)
    return sorted(found, key=record_number)


def next_candidate(root: Path, request_id: str) -> int:
    """Find the next candidate number; stop on records without PNGs (unknown result) to prevent resending."""
    unknown = [r.name for r in unknown_records(root, request_id)]
    if unknown:
        raise BatchError(f"{request_id} has execution records without images: {', '.join(unknown)}. "
                         f"If it has a taskId, retrieve it with `python -X utf8 scripts/pixai_batch.py fetch --ids {request_id}`. "
                         "If it cannot be retrieved, check your PixAI generation history and credits, then move it to failed/ with "
                         f"`python -X utf8 scripts/pixai_batch.py move-unknown --ids {request_id}` before retrying.")
    numbers = [int(p.stem[1:]) for p in candidates(root, request_id)]
    for record in run_records(root, request_id):
        numbers += reserved_numbers(record)
    return max(numbers or [0]) + 1


def candidate_ids(root: Path, pages: list[int] | None, ids: list[str] | None, all_pages: bool) -> list[str]:
    """Request IDs from candidate folders, including panels whose request JSON was deleted or renamed."""
    if ids:
        bad = [i for i in ids if not REQUEST_ID.fullmatch(i)]
        if bad:
            raise BatchError("Invalid characters in request ID: " + ", ".join(bad))
        return ids
    folder = root / CANDIDATES_DIR
    found = sorted(p.name for p in folder.iterdir() if p.is_dir() and REQUEST_ID.fullmatch(p.name)) if folder.is_dir() else []
    return found if all_pages else [i for i in found if page_of(i) in (pages or [])]


def move_unknown(root: Path, ids: list[str], number: int | None, confirmed: bool, note: str) -> list[tuple[str, int, Path | None]]:
    """Move execution records with unknown results to failed/<timestamp>-rNNN/ (without deleting). Without confirmed, only returns the targets."""
    found = []
    for request_id in ids:
        for record in unknown_records(root, request_id):
            n = record_number(record)
            if number is None or n == number:
                if confirmed and record.with_name(f"r{n:03d}.png").is_file():
                    raise BatchError("Some images are already saved. Do not move to failed/; retrieve the remaining images with fetch.")
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
        target.mkdir(parents=True)  # Stop if destination already exists
        for path in files:
            path.replace(target / path.name)
        write_json(target / "moved.json", {"action": "move-unknown", "request_id": request_id, "kind": "pixai", "number": n,
                                           "files": [p.name for p in files], "moved_at": datetime.now().isoformat(timespec="seconds"),
                                           "note": note})
        moved.append((request_id, n, target))
    return moved


def fetch_unknown(root: Path, ids: list[str]) -> list[tuple[str, list[Path]]]:
    """Query incomplete records that have a taskId and save images if completed. Never resends generation."""
    done = []
    for request_id in ids:
        for record in unknown_records(root, request_id):
            print(f"{request_id}: {record.name}")
            done.append((request_id, api.fetch(root, rel(root, record), log=lambda text: print(text, flush=True))))
    return done


def load_adopted(root: Path) -> dict:
    path = root / ADOPTED
    if not path.is_file():
        return {"schema_version": 1, "adopted": {}}
    data = api.read_json(path)
    data.setdefault("adopted", {})
    return data


# ---------------------------------------------------------------- Character, style, background, and LoRA prompt variables

def parse_value(raw: str) -> str:
    raw = raw.strip()
    if raw[:1] in ("'", '"'):
        end = raw.find(raw[0], 1)
        if end < 0:
            raise BatchError("Unclosed quote in variable value.")
        return raw[1:end]
    return re.split(r"\s+#", raw, maxsplit=1)[0].strip()


def read_variables(root: Path) -> dict[str, tuple[str, str]]:
    """Read only the 4 permitted variable prefixes from environment variables and .env.pixai; never expand or display API keys."""
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
                raise BatchError(f"Invalid variable name: ${{{name}}}. Variable names must start with {VAR_HELP}.")
            if name not in variables:
                raise BatchError(f"Variable {name} not found in {VAR_FILE} or other sources. Check with `vars`.")
            used.add(name)
            return variables[name][0]
        return PLACEHOLDER.sub(replace, value)
    if isinstance(value, list):
        return [expand(v, variables, used) for v in value]
    if isinstance(value, dict):
        # v1 lora is {versionId: weight}, so expand ${PIXAI_LORA_...} in dict keys as well.
        return {expand(k, variables, used): expand(v, variables, used) for k, v in value.items()}
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
    if name.startswith("PIXAI_LORA_") and not re.fullmatch(r"[0-9]{6,30}", value.strip()):
        raise BatchError("PIXAI_LORA_ value must be a LoRA version ID (numeric string from the end of the model page URL).")
    elsewhere = [s for n, (_, s) in read_variables(root).items() if n == name and s != VAR_FILE]
    if elsewhere:
        raise BatchError(f"{name} is already defined in {elsewhere[0]}. Edit it there or remove one definition.")
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
        raise BatchError("Value is too short for automatic replacement to avoid accidental matches.")
    counts = {}

    def walk(node):
        if isinstance(node, str):
            counts["_"] = counts.get("_", 0) + node.count(value)
            return node.replace(value, "${" + name + "}")
        if isinstance(node, list):
            return [walk(v) for v in node]
        if isinstance(node, dict):
            return {walk(k): walk(v) for k, v in node.items()}
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


# ---------------------------------------------------------------- Generation & adoption

def set_seed(request: dict, seed: int) -> None:
    if request.get("api") == "v1":
        request.setdefault("parameters", {})["seed"] = seed
    else:
        request.setdefault("body", {})["seed"] = seed


def set_batch_size(request: dict, count: int) -> None:
    (request.setdefault("parameters", {}) if request.get("api") == "v1" else request.setdefault("body", {}))["batchSize"] = count


def generate(root: Path, args) -> None:
    ids = select_ids(root, args.page, args.ids, args.all)
    if len(ids) > args.max:
        raise BatchError(f"{len(ids)} target(s) exceed the limit of {args.max}. Split by page or specify --max.")
    variables = read_variables(root)
    plan = []
    warned = []
    cameras: dict[int | None, list[tuple[str, str | None]]] = {}
    characters = load_characters(root) if identity_check_enabled(root) else None
    if characters is not None:
        print("Identity feature check: enabled (PIXAI_CHECK_IDENTITY)")
    total_images = 0
    for request_id in ids:
        request, used = resolved_request(root, request_id, variables)
        notes = lint_prompt(request) + lint_identity(request_id, request, characters)
        cameras.setdefault(page_of(request_id), []).append((request_id, camera_of(request)))
        existing = candidates(root, request_id)
        mode = args.seed if args.seed != "auto" else ("request" if not existing else "random")
        # In v1, seed is an unverified field, so do not add a random seed if the request does not already specify one (let the server choose).
        if mode == "random" and (request.get("api") != "v1" or "seed" in (request.get("parameters") or {})):
            set_seed(request, secrets.randbelow(4294967296))
        # Reworks default to 4 images per task (Tsubaki.3 pro 1k costs 4,000 credits for 1 image vs 7,000 for 4 images, verified in user PixAI history).
        size = getattr(args, "batch_size", "auto")
        if size != "auto":
            set_batch_size(request, int(size))
        elif existing and api.batch_size(request) == 1:
            set_batch_size(request, 4)
            print(f"  {request_id}: generating 4 images for rework (pass --batch-size 1 for 1 image)")
        request, api_notes, unverified = api.prepare_request_data(root, request)
        number = next_candidate(root, request_id)
        output = f"{CANDIDATES_DIR}/{request_id}/r{number:03d}.png"
        count = api.batch_size(request)
        total_images += count
        plan.append((request_id, request, unverified, output))
        last = f" .. r{number + count - 1:03d}.png" if count > 1 else ""
        print(f"{request_id}: {api.summary(request)} / vars {','.join(sorted(used)) or 'none'} -> {output}{last}")
        _, uploads = api.send_payload(root, None, request)
        if uploads:
            print("  Pending uploads: " + ", ".join(uploads))
        for note in api_notes:
            print(f"  [Note] {note}")
        if unverified:
            print("  [Unverified fields] " + ", ".join(unverified) + " (requires --allow-unverified to send)")
        for note in notes:
            print(f"  [Warning] {note}")
        if notes:
            warned.append(request_id)
    selected = set(ids)
    for page in cameras:
        if page is None:
            continue
        # Even when regenerating only specific panels, check consecutive camera angles across all base panels on the page (p01-03 format, excluding variants).
        base_ids = [i for i in request_files(root) if page_of(i) == page and re.fullmatch(r"p\d{1,3}-\d{1,3}", i)]
        items = [(i, camera_of(resolved_request(root, i, variables)[0])) for i in base_ids]
        for i in range(2, len(items)):
            if not selected.intersection(r for r, _ in items[i - 2:i + 1]):
                continue
            run = [c for _, c in items[i - 2:i + 1]]
            if run[0] and run.count(run[0]) == 3:
                print(f"  [Warning] {items[i][0]}: same camera angle ({run[0]}) repeats for 3 consecutive panels. Verify against the text storyboard")
                warned.append(items[i][0])
    print(f"Total: {len(plan)} task(s), {total_images} image(s). Check credit consumption on the PixAI screen (cannot be queried via API).")
    if warned:
        print(f"Prompt warnings: {len(set(warned))} item(s). Fix them or record the reason for keeping them in docs/production/PIXAI-BATCH.md, "
              "then pass --accept-warnings to send. See docs/knowledge/pixai-composed-production.md for prompt construction.")
    if not args.execute:
        print(f"Not sent ({len(plan)} item(s)). Execution requires --execute and cost confirmation flags.")
        return
    if warned and not args.accept_warnings:
        raise BatchError("Stopped before sending because prompt warnings remain (" + ", ".join(sorted(set(warned))) + ").")
    for _, request, unverified, _ in plan:  # Verify cost confirmation and unverified fields across all items before sending the first
        api.check_cost(args, request, unverified)
    done = []
    for index, (request_id, request, unverified, output) in enumerate(plan):
        if index:
            time.sleep(args.interval)
        print(f"[{index + 1}/{len(plan)}] {request_id}", flush=True)
        try:
            saved = api.execute_generation(root, request, output, args, unverified, log=lambda text: print(text, flush=True))
        except api.ClientError as error:
            raise BatchError(f"Stopped at {request_id} ({len(done)} succeeded). Remaining items were not sent; no automatic retry was performed.\n{error}") from None
        for path in saved:
            print("  Saved: " + rel(root, path), flush=True)
        done.append(output)
    print(f"Completed: {len(done)} item(s). Compare candidates and record your chosen number with adopt.")
    print("Example: python -X utf8 scripts/pixai_batch.py adopt " + plan[0][0] + " --candidate " + Path(plan[0][3]).stem[1:])


def adopt(root: Path, request_id: str, number: int | None, file: str | None) -> Path:
    if request_id not in request_files(root) and not file:
        raise BatchError(f"Missing request JSON: {request_id}")
    if file:
        path = api.project_path(root, file)
    else:
        path = root / CANDIDATES_DIR / request_id / f"r{number:03d}.png"
    if not path.is_file():
        raise BatchError("Image to adopt not found: " + (rel(root, path) if path.is_relative_to(root) else str(file)))
    data = load_adopted(root)
    data["adopted"][request_id] = {"path": rel(root, path), "sha256": sha(path), "adopted_at": now()}
    write_json(root / ADOPTED, data)
    return path


def adopt_latest(root: Path, ids: list[str], dry_run: bool) -> dict[str, Path]:
    """Verify candidates exist for all targets before saving adoption records in a single batch."""
    chosen = {}
    missing = []
    for request_id in ids:
        available = candidates(root, request_id)
        if not available:
            missing.append(request_id)
        else:
            chosen[request_id] = available[-1]
    if missing:
        raise BatchError("Missing candidate PNGs: " + ", ".join(missing) + ". Adoption records were not modified.")
    if not dry_run:
        data = load_adopted(root)
        timestamp = now()
        for request_id, path in chosen.items():
            data["adopted"][request_id] = {"path": rel(root, path), "sha256": sha(path), "adopted_at": timestamp}
        write_json(root / ADOPTED, data)
    return chosen


# ---------------------------------------------------------------- Page rebuilding

def placement(frame, image_size, focus, zoom, rotation):
    """Cover the panel bounding box with the image. focus is the image point (0..1) placed at the panel center."""
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
        # Do not note axes where the image fits the panel exact-to-edge and cannot pan; note only when panning was clamped at an edge.
        movable_x, movable_y = iw - 2 * hw > 1, ih - 2 * hh > 1
        if (movable_x and abs(cx - fx) > 0.5) or (movable_y and abs(cy - fy) > 0.5):
            notes.append("focus exceeded the image edge; clamped visible region to the edge")
        fx, fy = cx, cy
    ox, oy = bw / 2, bh / 2
    # Panel-local coordinates -> source image coordinates inverse transform (PIL AFFINE format).
    a, b = c / scale, s / scale
    d, e = -s / scale, c / scale
    return [a, b, fx - (a * ox + b * oy), d, e, fy - (d * ox + e * oy)], notes


def build(root: Path, page: int, write_psd: bool) -> Path:
    from PIL import Image
    import export_composed_psd as exporter
    import typeset_manga as typesetter

    manifest_path = root / PAGES_DIR / f"page-{page:02d}.json"
    if not manifest_path.is_file():
        raise BatchError(f"Missing page manifest: {rel(root, manifest_path)}")
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
            raise BatchError(f"Panel {order} is not in the layout.")
        if entry.get("source"):
            source = entry["source"]
        elif entry.get("request"):
            chosen = adopted.get(entry["request"])
            if not chosen:
                missing.append(entry["request"])
                continue
            source = chosen["path"]
            if sha(api.project_path(root, source)) != chosen["sha256"]:
                raise BatchError(f"Adopted image has changed since adoption: {source}")
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
        for px, py in polygon:  # If a panel corner falls outside the source image, that corner has no artwork
            lx, ly = px - frame[0], py - frame[1]
            sx, sy = a * lx + b * ly + c, d * lx + e * ly + f
            uncovered |= not (-1 <= sx <= image_size[0] + 1 and -1 <= sy <= image_size[1] + 1)
        if uncovered:
            note = note + ["Part of the panel has no image coverage; adjust focus, zoom, or rotation, or fine-tune in the PSD"]
        if note:
            notes[f"Panel {order}"] = note
        panel = {"name": entry.get("name", f"Panel {order:02d}"), "source": source, "frame": frame,
                 "inverse_affine": affine, "polygon": polygon}
        if entry.get("original_source"):
            panel["original_source"] = entry["original_source"]
        panels.append(panel)
    if missing:
        raise BatchError("Adopted image not selected for: " + ", ".join(missing) + f" ({ADOPTED}). Select with adopt before running build. "
                         "For panels using artwork from another generator, set source instead of request in the page manifest.")

    # Render typesetting (balloons, dialogue, in-art text, borders) as transparent layers. Borders sit near the top and mask outside panels.
    typeset_spec = api.read_json(api.project_path(root, manifest["typeset"])) if manifest.get("typeset") else {
        "schema_version": 1, "balloons": []}
    typeset_spec.setdefault("layout", manifest["layout"])
    report = typesetter.render(typeset_spec, root, out_dir / "typeset", None, not manifest.get("frames_in_art", False))

    # Place additional overlays such as sound effects above panel borders and below speech balloons.
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
    # Build reduced display and annotated review images from the composited final page (the typeset folder preview does not include panel artwork).
    review = typesetter.review_images(out_dir / f"page-{page:02d}.png", typeset_spec, root, out_dir, f"page-{page:02d}")
    write_json(out_dir / "build.json", {
        "schema_version": 1, "built_at": now(), "builder": "pixai_batch.py", "page": page, "manifest": rel(root, manifest_path),
        "manifest_sha256": sha(manifest_path), "panels": [{"name": p["name"], "source": p["source"]} for p in panels],
        "placement_notes": notes, "typeset_summary": report["summary"], "typeset_check": rel(root, out_dir / "typeset" / "check.json"),
        "png": result["output_png"], "psd": rel(root, out_dir / f"page-{page:02d}.psd") if write_psd else None,
        "review_display": rel(root, review["display"]), "review_check_overlay": rel(root, review["check_overlay"]),
        "psd_verification": result["verification"]})
    print(f"page {page}: {result['output_png']}" + (" (with PSD)" if write_psd else "") +
          f" / typeset check: {report['summary']['error']} error(s), {report['summary']['warning']} warning(s)")
    print(f"  Review (with art): {rel(root, review['display'])}, annotated: {rel(root, review['check_overlay'])} (not for publication)")
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
        raise BatchError(f"No page manifests such as {PAGES_DIR}/page-01.json found.")
    return sorted(found)


def add_target(parser, help_all="All page requests (p01-... format)"):
    target = parser.add_mutually_exclusive_group(required=True)
    target.add_argument("--page", type=int, action="append", help="Page number (can be specified multiple times)")
    target.add_argument("--ids", type=lambda s: [v for v in s.split(",") if v], help="Comma-separated request IDs")
    target.add_argument("--all", action="store_true", help=help_all)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    commands = parser.add_subparsers(dest="command", required=True)
    listing = commands.add_parser("list", help="List requests, candidates, and adoptions")
    listing.add_argument("--page", type=int, action="append")
    show = commands.add_parser("vars", help="List character, style, background, and LoRA variables")
    show.add_argument("--show-values", action="store_true", help="Also display variable values (prompt text)")
    setter = commands.add_parser("env-set", help="Write a character, style, background, or LoRA variable to .env.pixai")
    setter.add_argument("name")
    group = setter.add_mutually_exclusive_group(required=True)
    group.add_argument("--value")
    group.add_argument("--value-file", help="UTF-8 text file containing the value (relative path inside the project)")
    templ = commands.add_parser("templatize", help="Replace matching literal values in request JSON files with ${VAR_NAME}")
    templ.add_argument("name")
    templ.add_argument("--dry-run", action="store_true")
    gen = commands.add_parser("generate", help="Sequentially generate requests one task at a time (dry-run by default)")
    gen.add_argument("--page", type=int, action="append", help="Page number (can be specified multiple times)")
    gen.add_argument("--ids", type=lambda s: [v for v in s.split(",") if v], help="Comma-separated request IDs")
    gen.add_argument("--all", action="store_true", help="All page requests (p01-... format)")
    gen.add_argument("--seed", choices=("auto", "request", "random"), default="auto",
                     help="auto: use request seed on first run and random on subsequent runs (default)")
    gen.add_argument("--batch-size", choices=("auto", "1", "4"), default="auto",
                     help="Images per task. auto: 4 images when candidates already exist (rework), or request batchSize on first run (default)")
    gen.add_argument("--interval", type=float, default=3.0, help="Interval between tasks (seconds)")
    gen.add_argument("--max", type=int, default=30, help="Maximum tasks per run")
    gen.add_argument("--timeout", type=float, default=900, help="Maximum time to wait for a single task (seconds)")
    gen.add_argument("--execute", action="store_true", help="Send user-requested generations")
    gen.add_argument("--accept-warnings", action="store_true", help="Prompt warnings have been reviewed and reasons for keeping them recorded")
    gen.add_argument("--confirm-credits", action="store_true", help="User has explicitly authorized credit consumption for this scope")
    gen.add_argument("--allow-unverified", action="store_true", help="User has agreed to test fields not in current official docs (i2i, reference images, etc.)")
    gen.add_argument("--cost-note")
    again = commands.add_parser("fetch", help="Re-fetch imageless execution records by taskId (does not resend generation)")
    add_target(again, "All requests that have candidate folders")
    pick = commands.add_parser("adopt", help="Record an adopted image")
    pick.add_argument("request_id")
    which = pick.add_mutually_exclusive_group(required=True)
    which.add_argument("--candidate", type=int, help="Candidate number (3 for r003.png)")
    which.add_argument("--file", help="Directly specify a project-local image such as an edited version")
    latest = commands.add_parser("adopt-latest", help="Batch-adopt the highest-numbered PNG in each candidate folder")
    add_target(latest)
    latest.add_argument("--dry-run", action="store_true", help="Display targets without modifying adoption records")
    unknown = commands.add_parser("move-unknown", help="Move execution records with unknown results to failed/ (previews targets by default)")
    add_target(unknown, "All requests that have candidate folders")
    unknown.add_argument("--candidate", type=int, help="Record number (3 for r003.pixai.json); all unknown records for targets if omitted")
    unknown.add_argument("--confirm-checked", action="store_true",
                         help="Confirmed via fetch and PixAI generation history/credits that no image was produced (or is not needed)")
    unknown.add_argument("--note", default="", help="Confirmation note (saved in moved.json)")
    make = commands.add_parser("build", help="Rebuild page PNGs (and PSDs when requested)")
    make.add_argument("--page", type=int, action="append")
    make.add_argument("--all", action="store_true")
    make.add_argument("--write-psd", action="store_true", help="Also build PSD (when requested after PNG verification)")
    args = parser.parse_args(argv)
    root = Path(__file__).resolve().parents[1]
    try:
        if not (root / "project.json").is_file():
            raise BatchError("Run from scripts/ inside a manga project.")
        if args.command == "list":
            adopted = load_adopted(root)["adopted"]
            for request_id, path in request_files(root).items():
                if args.page and page_of(request_id) not in args.page:
                    continue
                used = set(PLACEHOLDER.findall(path.read_text(encoding="utf-8-sig")))
                chosen = adopted.get(request_id, {}).get("path", "unadopted")
                print(f"{request_id}: {len(candidates(root, request_id))} candidate(s) / adopted {chosen} / vars {','.join(sorted(used)) or 'none'}")
        elif args.command == "vars":
            variables = read_variables(root)
            if not variables:
                print(f"No prompt variables found (PIXAI_CHAR_, PIXAI_STYLE_, PIXAI_BACKGROUND_, PIXAI_LORA_ in {VAR_FILE}).")
            for name, (value, source) in sorted(variables.items()):
                print(f"{name} ({source}, {len(value)} chars)" + (f": {value}" if args.show_values else ""))
        elif args.command == "env-set":
            value = args.value if args.value is not None else api.project_path(root, args.value_file).read_text(encoding="utf-8-sig").strip()
            print(f"{env_set(root, args.name, value).capitalize()} {args.name} in {VAR_FILE} (other lines left unchanged).")
        elif args.command == "templatize":
            result = templatize(root, args.name, args.dry_run)
            for request_id, count in result.items():
                print(f"{request_id}: {count} replacement(s)" + (" (dry-run)" if args.dry_run else ""))
            if not result:
                print("No matching occurrences to replace.")
        elif args.command == "generate":
            generate(root, args)
        elif args.command == "fetch":
            if args.ids == []:
                raise BatchError("Specify request IDs with --ids.")
            done = fetch_unknown(root, candidate_ids(root, args.page, args.ids, args.all))
            for request_id, paths in done:
                for path in paths:
                    print(f"  Saved: {rel(root, path)}")
            if not done:
                print("No incomplete records (execution records without images) waiting to be fetched.")
        elif args.command == "adopt":
            path = adopt(root, args.request_id, args.candidate, args.file)
            print(f"{args.request_id}: adopted {rel(root, path)}.")
        elif args.command == "adopt-latest":
            if args.ids == []:
                raise BatchError("Specify request IDs with --ids.")
            ids = select_ids(root, args.page, args.ids, args.all)
            chosen = adopt_latest(root, ids, args.dry_run)
            for request_id, path in chosen.items():
                print(f"{request_id}: {rel(root, path)}" + (" (dry-run)" if args.dry_run else " adopted."))
        elif args.command == "move-unknown":
            if args.ids == []:
                raise BatchError("Specify request IDs with --ids.")
            ids = candidate_ids(root, args.page, args.ids, args.all)
            moved = move_unknown(root, ids, args.candidate, args.confirm_checked, args.note)
            for request_id, number, target in moved:
                print(f"{request_id}: r{number:03d}.pixai.json" + (f" -> {rel(root, target)}" if target else " (unknown result; preview only)"))
            if not moved:
                print("No execution records with unknown results.")
            elif not args.confirm_checked:
                print("Try re-fetching with fetch first. If it cannot be retrieved, check your PixAI generation history and credits, "
                      "and pass --confirm-checked to move it to failed/ once confirmed.")
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
