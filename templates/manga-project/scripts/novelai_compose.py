"""Build NovelAI (V5 / V4.5) request JSON from style, background, and per-character arguments.

Saves the assembled request to `input/novelai/requests/<ID>.json` and delegates transmission to
`novelai_batch.py generate` (validation, cost check, execution record, and no-automatic-retry handling).
This script itself does not perform network communication.
Saved request JSON files can be edited by hand, or written directly without using this script.

Standard request builder for NovelAI API generation. Uses V5 (`nai-diffusion-5-curated` by default);
use V4.5 only when explicitly requested by the user.
When additional features such as i2i or references are needed, adapt this script while keeping the
request JSON format and routing transmission through `novelai_batch.py generate` / `novelai_api.py generate`
(check specifications and costs in `docs/knowledge/novelai-api.md` first).

Prompt order (official: count -> characters -> other, with quality tags at the end)
  Base       Count tags (auto from characters) -> --scene -> --background -> --style -> quality tags (auto)
  Character  Character type (girl/boy/other; no number) -> appearance -> pose / action
  Negative   Undesired Content preset (auto) -> --negative
Input text is concatenated as-is without rewriting (preserving spaces and commas).

Per-model web UI defaults (quality tags, Undesired Content presets, Guidance, and transmitted parameters) are in MODELS.
Quality tags already present in the input are not duplicated (use `--allow-duplicate-quality` to keep web UI duplicates).

Overrides (priority: CLI argument > environment variable / .env.novelai > default; only these 4 setting names are read, never API keys)
  NOVELAI_QUALITY_TAGS      Full quality tag string (empty to omit). CLI `--quality-tags`
  NOVELAI_UC_PRESET         Undesired Content preset name (heavy, light, human, none). CLI `--uc-preset`
  NOVELAI_UC_PRESET_TEXT    Full Undesired Content preset string (empty to omit). CLI `--uc-preset-text`
  NOVELAI_CHECK_IDENTITY    Set to 1 to run identity feature checks (`characters.json`) during `generate`. Off by default

Specify characters by number such as `--char1-appearance` (up to the model's maximum):
  --charN-type girl|boy|other   --charN-appearance appearance   --charN-action pose/action
  --charN-pos x,y (0..1 placement pin; enabled by default only when specified for all characters; toggle with --coords on/off)   --charN-negative per-character negative
To pass an array, use `--chars-json` (an array of objects with the field names above).
Pass literal values from `NOVELAI_STYLE_` / `NOVELAI_BACKGROUND_` / `NOVELAI_CHAR_` in `.env.novelai` for style, background, and character text.
This script does not read those variables or expand `${VAR_NAME}`.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import secrets
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import novelai_api as api  # noqa: E402
import novelai_batch as batch  # noqa: E402

DEFAULT_MODEL = "nai-diffusion-5-curated"
# Source: docs.novelai.net/en/image/undesiredcontent/ and web UI PNG uc metadata (V5 Curated: 2026-10-05; V4.5 Curated: same date).
V5_UC = {
    "heavy": "lowres, artistic error, film grain, scan artifacts, worst quality, bad quality, jpeg artifacts, "
             "very displeasing, chromatic aberration, dithering, halftone, screentone, multiple views, logo, "
             "too many watermarks, negative space, blank page",
    "light": "lowres, bad hands, bad anatomy, artistic error, sepia, white haze, worst quality, very displeasing, "
             "jpeg artifacts, 0::ai-generated::",
    "human": "lowres, artistic error, film grain, scan artifacts, worst quality, bad quality, jpeg artifacts, "
             "very displeasing, chromatic aberration, dithering, halftone, screentone, multiple views, logo, "
             "too many watermarks, negative space, blank page, @_@, mismatched pupils, glowing eyes, bad anatomy",
    "none": "",
}
# In V5 Full web UI PNGs, Heavy began with "nsfw, ", but per user instruction (2026-10-05) this script does not add nsfw.
# To match the web UI verbatim, pass the full text including nsfw to --uc-preset-text. light and human are unverified on V5 Full.
V5_FULL_UC = {"heavy": V5_UC["heavy"], "none": ""}
# Official docs describe V4.5 Heavy as identical to V5, but V4.5 web UI PNGs contained the text below. Web UI output is treated as canonical; light and human are omitted because they are unverified.
V45_UC = {
    "heavy": "blurry, lowres, upscaled, artistic error, film grain, scan artifacts, worst quality, bad quality, "
             "jpeg artifacts, very displeasing, chromatic aberration, halftone, multiple views, logo, "
             "too many watermarks, negative space, blank page",
    "none": "",
}
# Common parameters recorded in web UI PNGs. If omitted, API defaults differ from the web UI (deliberate_euler_ancestral_bug / prefer_brownian).
COMMON_PARAMETERS = {
    "cfg_rescale": 0.0, "legacy_v3_extend": False, "controlnet_strength": 1.0, "dynamic_thresholding": False,
    "sm": False, "sm_dyn": False, "deliberate_euler_ancestral_bug": False, "prefer_brownian": True,
    "n_samples": 1, "image_format": "png",
}
MODELS = {
    "nai-diffusion-5-curated": {
        "label": "V5 Curated", "steps": 23, "quality": "very aesthetic, masterpiece, no text", "uc": V5_UC, "scale": 7.0,
        "max_characters": 22, "grid": None, "extra": {"straight_alpha": True},
        "status": "Pixel-identical match with web UI PNG at the same seed and input (2026-10-05, when matching 2nd character coordinates with --coords off)"},
    "nai-diffusion-5-full": {
        "label": "V5 Full", "steps": 23, "quality": "very aesthetic, masterpiece, no text", "uc": V5_FULL_UC, "scale": 7.0,
        "max_characters": 22, "grid": None, "extra": {"straight_alpha": True},
        "status": "Pixel-identical match with web UI PNG (Source V5 0ADF9AB7) at the same seed and input (2026-10-05, when including leading nsfw from web UI uc; script default omits nsfw)"},
    "nai-diffusion-4-5-curated": {
        "label": "V4.5 Curated", "steps": 28, "quality": "very aesthetic, masterpiece, no text, -0.8::feet::, rating:general",
        "uc": V45_UC, "scale": 5.0, "max_characters": 6, "grid": 5, "extra": {},
        "status": "Pixel-identical match with web UI PNG (Source V4.5 C02D4F98) at the same seed and input (2026-10-05)"},
}
CHAR_FIELDS = ("type", "appearance", "action", "pos", "negative")
CHAR_OPTION = re.compile(r"--char(\d{1,2})-(type|appearance|action|pos|negative)(?:=(.*))?", re.S)
TYPES = ("girl", "boy", "other")
WEIGHTED = re.compile(r"^\s*-?\d+(?:\.\d+)?::")


class ComposeError(api.ClientError):
    pass


# ---------------------------------------------------------------- Tag matching (used only for duplicate detection; input text is not rewritten)

def tag_key(tag: str) -> str:
    """Normalized tag form for comparison, stripping weights, brackets, and whitespace differences."""
    key = tag.strip().lower()
    key = re.sub(r"^[\s{}\[\]]+|[\s{}\[\]]+$", "", key)
    key = re.sub(r"^-?\d+(?:\.\d+)?::", "", key)
    key = re.sub(r"::$", "", key)
    return re.sub(r"[\s_]+", " ", key).strip()


def canon(tag: str) -> str:
    return re.sub(r"\s+", " ", tag.strip().lower())


def split_tags(text: str) -> list[str]:
    return [t.strip() for t in text.split(",") if t.strip()]


def join_text(*parts: str) -> str:
    """Keep input text as-is (trimming only outer whitespace) and join non-empty parts with ', '."""
    return ", ".join(p.strip() for p in parts if p and p.strip())


def merge_quality(quality: str, given: list[str], allow_duplicate: bool) -> tuple[str, list[str], list[str]]:
    """Skip quality tags already present in the input and return (joined_text, added_tags, skipped_tags). Weighted terms (-0.8::feet::) match only when the weight also matches."""
    tokens = [t for text in given for t in split_tags(text)]
    keys, canons = {tag_key(t) for t in tokens}, {canon(t) for t in tokens}
    added, skipped = [], []
    for tag in split_tags(quality):
        present = canon(tag) in canons if WEIGHTED.match(tag) else tag_key(tag) in keys
        if present and not allow_duplicate:
            skipped.append(tag)
        else:
            added.append(tag)
            if not WEIGHTED.match(tag):
                keys.add(tag_key(tag))
            canons.add(canon(tag))  # Deduplicate within override quality strings as well
    return ", ".join(added), added, skipped


# ---------------------------------------------------------------- Characters

def extract_character_options(argv: list[str]) -> tuple[list[str], dict[int, dict]]:
    """Extract --charN-... options and pass remaining arguments to standard argparse."""
    rest, chars, i = [], {}, 0
    while i < len(argv):
        match = CHAR_OPTION.fullmatch(argv[i])
        if not match:
            rest.append(argv[i])
            i += 1
            continue
        number, field, inline = int(match.group(1)), match.group(2), match.group(3)
        if inline is None:
            if i + 1 >= len(argv):
                raise ComposeError(f"Missing value for {argv[i]}.")
            value, i = argv[i + 1], i + 2
        else:
            value, i = inline, i + 1
        if field in chars.setdefault(number, {}):
            raise ComposeError(f"Duplicate --char{number}-{field}.")
        chars[number][field] = value
    return rest, chars


def parse_pos(value, label: str) -> tuple[float, float]:
    try:
        x, y = ([float(v) for v in re.split(r"[,\s]+", value.strip())] if isinstance(value, str) else [float(v) for v in value])
    except (ValueError, TypeError):
        raise ComposeError(f"Specify {label} as x,y (e.g. 0.3,0.5).") from None
    if not (0 <= x <= 1 and 0 <= y <= 1):
        raise ComposeError(f"x and y for {label} must be between 0 and 1 (top-left origin).")
    return round(x, 4), round(y, 4)


def snap(value: float, grid: int) -> float:
    """V4.5 placement uses a 5x5 grid; snap coordinates to the cell center."""
    return (min(int(value * grid), grid - 1) + 0.5) / grid


def build_characters(raw: list[dict], profile: dict) -> tuple[list[dict], list[str]]:
    notes = []
    if len(raw) > profile["max_characters"]:
        raise ComposeError(f"{profile['label']} supports at most {profile['max_characters']} characters.")
    characters = []
    for index, item in enumerate(raw, 1):
        unknown = set(item) - set(CHAR_FIELDS)
        if unknown:
            raise ComposeError(f"Unsupported field(s) in character {index}: {', '.join(sorted(unknown))}")
        kind = str(item.get("type", "girl")).strip().lower()
        kind = re.sub(r"^1(?=(girl|boy|other)$)", "", kind)  # Per-character captions do not take a leading number (official)
        if kind not in TYPES:
            raise ComposeError(f"Character {index} type must be one of {' / '.join(TYPES)}.")
        for field in ("appearance", "action", "negative"):
            if "${" in str(item.get(field, "")):
                raise ComposeError(f"Character {index} {field} contains ${{...}}. This script does not expand variables; pass literal values.")
        pos = item.get("pos")
        pos = parse_pos(pos, f"character {index} pos") if pos not in (None, "") else None
        if pos is not None and profile["grid"]:
            snapped = (snap(pos[0], profile["grid"]), snap(pos[1], profile["grid"]))
            if snapped != pos:
                notes.append(f"Snapped character {index} position to {profile['label']} {profile['grid']}x{profile['grid']} grid center {snapped}")
            pos = snapped
        characters.append({"type": kind, "appearance": str(item.get("appearance", "")).strip(),
                           "action": str(item.get("action", "")).strip(), "negative": str(item.get("negative", "")).strip(), "pos": pos})
        if not characters[-1]["appearance"]:
            raise ComposeError(f"Specify appearance for character {index} (--char{index}-appearance).")
    return characters, notes


def count_tags(characters: list[dict]) -> str:
    if not characters:
        return "no humans"
    parts = []
    for kind in TYPES:
        n = sum(c["type"] == kind for c in characters)
        if n:
            parts.append(f"{n}{kind}" + ("s" if n > 1 else ""))
    return ", ".join(parts)


def order_notes(characters: list[dict], grid: int | None) -> list[str]:
    """Note whether character order matches official default order (top-to-bottom, left-to-right)."""
    if not characters or any(c["pos"] is None for c in characters):
        return []
    cells = [(min(int(c["pos"][1] * 5), 4), min(int(c["pos"][0] * 5), 4)) for c in characters]
    if cells != sorted(cells):
        return ["Character order differs from placement pin order (top-to-bottom, left-to-right). Official guidance recommends keeping input order consistent with position"]
    return []


# ---------------------------------------------------------------- Setting resolution

def resolve_uc(root: Path, opts, profile: dict) -> tuple[str, str]:
    """Undesired Content preset text and source. CLI full text > CLI preset name > env full text > env preset name > heavy."""
    def named(name: str, source: str):
        if name not in profile["uc"]:
            raise ComposeError(f"Undesired Content presets for {profile['label']} are only {' / '.join(profile['uc'])} ({source}). "
                               "Use --uc-preset-text to specify custom text.")
        return profile["uc"][name], f"{source}={name}"
    if opts.uc_preset_text is not None:
        return opts.uc_preset_text, "CLI --uc-preset-text"
    if opts.uc_preset:
        return named(opts.uc_preset, "CLI --uc-preset")
    text = batch.read_setting(root, "NOVELAI_UC_PRESET_TEXT")
    if text is not None:
        return text, "NOVELAI_UC_PRESET_TEXT"
    name = batch.read_setting(root, "NOVELAI_UC_PRESET")
    if name:
        return named(name.strip().lower(), "NOVELAI_UC_PRESET")
    return profile["uc"]["heavy"], "default (web UI heavy)"


def resolve_size(root: Path, opts) -> str:
    """Set generation dimensions on opts and return their source. CLI > page-layout.json generationCanvas > web UI default (832x1216)."""
    if (opts.width is None) != (opts.height is None):
        raise ComposeError("Specify both --width and --height.")
    if opts.width is not None:
        source = "CLI"
    else:
        layout = root / "config/page-layout.json"
        canvas = api.read_json(layout).get("generationCanvas") if layout.is_file() else None
        if isinstance(canvas, dict):
            opts.width, opts.height, source = canvas.get("width"), canvas.get("height"), "config/page-layout.json generationCanvas"
        else:
            opts.width, opts.height, source = 832, 1216, "default (web UI default; generationCanvas not set)"
    for size in (opts.width, opts.height):
        if type(size) is not int or size < 64 or size % 64:
            raise ComposeError("Generation dimensions must be multiples of 64 and at least 64.")
    return source


def resolve_quality(root: Path, opts, profile: dict) -> tuple[str, str]:
    if opts.no_quality_tags:
        return "", "omitted (--no-quality-tags)"
    if opts.quality_tags is not None:
        return opts.quality_tags, "CLI --quality-tags"
    env = batch.read_setting(root, "NOVELAI_QUALITY_TAGS")
    if env is not None:
        return env, "NOVELAI_QUALITY_TAGS"
    return profile["quality"], f"default ({profile['label']} web UI quality tags)"


# ---------------------------------------------------------------- Request assembly

def compose(opts: argparse.Namespace, raw_chars: list[dict], quality: str, uc_preset: str) -> tuple[dict, dict]:
    if opts.model not in MODELS:
        raise ComposeError("Supported models: " + " / ".join(MODELS))
    profile = MODELS[opts.model]
    characters, notes = build_characters(raw_chars, profile)
    for name in ("scene", "background", "style", "negative"):
        if "${" in getattr(opts, name):
            raise ComposeError(f"--{name} contains ${{...}}. This script does not expand variables; pass literal values.")
    counts = opts.count_tags if opts.count_tags is not None else count_tags(characters)
    caption_texts = [join_text(c["type"], c["appearance"], c["action"]) for c in characters]
    given = [counts, opts.scene, opts.background, opts.style] + caption_texts
    quality_text, added, skipped = merge_quality(quality, given, opts.allow_duplicate_quality)
    base = join_text(counts, opts.scene, opts.background, opts.style, quality_text)

    negative = join_text(uc_preset, opts.negative)  # Do not deduplicate negative prompt tags (matches web UI)

    given_pos = [c["pos"] is not None for c in characters]
    if opts.coords == "on" and characters and not all(given_pos):
        raise ComposeError("Placement pins (--coords on) require --charN-pos on every character.")
    if opts.coords == "auto" and any(given_pos) and not all(given_pos):
        raise ComposeError("Specify placement pins for all characters or none of them (use --coords off to send coordinates while keeping automatic placement).")
    pinned = bool(characters) and (opts.coords == "on" or (opts.coords == "auto" and all(given_pos)))
    # Even when placement pins are disabled (use_coords=false), centers are still sent and affected the output in live web UI generation (2026-10-05).
    centers = [[{"x": c["pos"][0], "y": c["pos"][1]}] if c["pos"] is not None else [{"x": 0.5, "y": 0.5}] for c in characters]
    v4_prompt = {"caption": {"base_caption": base, "char_captions": [
        {"char_caption": text, "centers": centers[i]} for i, text in enumerate(caption_texts)]},
        "use_coords": pinned, "use_order": True, "legacy_uc": False}
    v4_negative = {"caption": {"base_caption": negative, "char_captions": [
        {"char_caption": c["negative"], "centers": centers[i]} for i, c in enumerate(characters)]},
        "use_coords": pinned, "use_order": False, "legacy_uc": False}

    params = dict(COMMON_PARAMETERS, **profile["extra"])
    params.update(width=opts.width, height=opts.height,
                  steps=opts.steps if opts.steps is not None else profile["steps"],
                  scale=opts.scale if opts.scale is not None else profile["scale"], cfg_rescale=opts.cfg_rescale,
                  sampler=opts.sampler, noise_schedule=opts.noise_schedule,
                  seed=opts.seed if opts.seed is not None else secrets.randbelow(4294967296),
                  negative_prompt=negative, v4_prompt=v4_prompt, v4_negative_prompt=v4_negative)
    request = {"action": "generate", "input": base, "model": opts.model, "parameters": params}
    info = {"quality_added": added, "quality_skipped": skipped, "notes": notes + (order_notes(characters, profile["grid"]) if pinned else []),
            "characters": caption_texts, "pinned": pinned, "profile": profile}
    return request, info


def parse_args(argv: list[str]):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter, allow_abbrev=False)
    parser.add_argument("--id", required=True, help="Request ID in p01-03 format (input/novelai/requests/<ID>.json)")
    parser.add_argument("--model", default=DEFAULT_MODEL, choices=sorted(MODELS))
    parser.add_argument("--style", default="", help="Art style text (value from NOVELAI_STYLE_...)")
    parser.add_argument("--background", default="", help="Background, location, time of day, lighting (value from NOVELAI_BACKGROUND_...)")
    parser.add_argument("--scene", default="", help="Composition, camera angle, overall situation (upper body, eye level, etc.)")
    parser.add_argument("--count-tags", help="Manually specify count tags (default is auto from characters; no humans when empty)")
    parser.add_argument("--negative", default="", help="Additional negative tags (appended after the preset)")
    parser.add_argument("--uc-preset", help="Undesired Content preset name (V5 Curated: heavy/light/human/none; V5 Full & V4.5: heavy/none)")
    parser.add_argument("--uc-preset-text", help="Directly specify the full Undesired Content preset string (empty string to omit)")
    parser.add_argument("--coords", choices=("auto", "on", "off"), default="auto",
                        help="Placement pins. auto=enable when all characters have --charN-pos. off=disable (AI's Choice) while still sending specified centers")
    parser.add_argument("--chars-json", help="Character array JSON (relative path in project). Do not combine with --charN-...")
    quality = parser.add_mutually_exclusive_group()
    quality.add_argument("--quality-tags", help="Override quality tags (empty string to omit)")
    quality.add_argument("--no-quality-tags", action="store_true", help="Do not append quality tags")
    parser.add_argument("--allow-duplicate-quality", action="store_true", help="Keep quality tags even if duplicated in input (to reproduce exact web UI text)")
    parser.add_argument("--width", type=int, help="Generation width (multiple of 64). Defaults to generationCanvas in config/page-layout.json, or 832x1216 if unset")
    parser.add_argument("--height", type=int)
    parser.add_argument("--steps", type=int, help="Defaults to 23 for V5 and 28 for V4.5 (same as novelai_api.py)")
    parser.add_argument("--scale", type=float, help="Prompt Guidance. Defaults to per-model web UI value (7.0 for V5, 5.0 for V4.5)")
    parser.add_argument("--cfg-rescale", type=float, default=0.0)
    parser.add_argument("--sampler", default="k_euler_ancestral")
    parser.add_argument("--noise-schedule", default="karras")
    parser.add_argument("--seed", type=int, help="Random if omitted")
    parser.add_argument("--cast-from", help="Copy character cast registration (cast in characters.json) from an existing request ID")
    parser.add_argument("--force", action="store_true", help="Overwrite an existing request JSON with the same name")
    parser.add_argument("--dry-run", action="store_true", help="Display the assembled request without saving")
    parser.add_argument("--no-check", action="store_true", help="Skip the post-save dry-run lint check")
    parser.add_argument("--execute", action="store_true", help="Send via novelai_batch.py generate after validation")
    parser.add_argument("--accept-warnings", action="store_true")
    costs = parser.add_mutually_exclusive_group()
    costs.add_argument("--confirm-zero-anlas", action="store_true")
    costs.add_argument("--allow-anlas", action="store_true")
    parser.add_argument("--confirm-v5-allowance", action="store_true")
    parser.add_argument("--cost-note")
    return parser


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    root = Path(__file__).resolve().parents[1]
    try:
        argv, numbered = extract_character_options(argv)
        opts = parse_args(argv).parse_args(argv)
        if not (root / "project.json").is_file():
            raise ComposeError("Run from scripts/ inside a manga project.")
        if not batch.REQUEST_ID.fullmatch(opts.id):
            raise ComposeError("Request ID must use only ASCII letters, digits, -, and _ (e.g. p01-03).")
        if opts.chars_json:
            if numbered:
                raise ComposeError("--chars-json and --charN-... cannot be used together.")
            data = json.loads(api.project_path(root, opts.chars_json).read_text(encoding="utf-8-sig"))
            if not isinstance(data, list) or not all(isinstance(c, dict) for c in data):
                raise ComposeError("--chars-json must be an array of character objects.")
            raw = data
        else:
            if sorted(numbered) != list(range(1, len(numbered) + 1)):
                raise ComposeError("Character numbers must be consecutive starting from 1 (--char1-..., --char2-...).")
            raw = [numbered[n] for n in sorted(numbered)]
        profile = MODELS[opts.model]
        quality, quality_source = resolve_quality(root, opts, profile)
        uc_preset, uc_source = resolve_uc(root, opts, profile)
        size_source = resolve_size(root, opts)
        request, info = compose(opts, raw, quality, uc_preset)
        path = root / batch.REQUESTS_DIR / f"{opts.id}.json"
        p = request["parameters"]
        print(f"Model: {profile['label']} ({opts.model}). Basis: {profile['status']}")
        print(f"Quality tags: source={quality_source} / added={', '.join(info['quality_added']) or 'none'}"
              f" / skipped (already in input)={', '.join(info['quality_skipped']) or 'none'}")
        print(f"Undesired Content preset: source={uc_source}")
        print("Base: " + request["input"])
        for i, text in enumerate(info["characters"], 1):
            centers = p["v4_prompt"]["caption"]["char_captions"][i - 1]["centers"][0]
            print(f"Character {i}: {text} @ ({centers['x']}, {centers['y']})" + ("" if info["pinned"] else " (sent even without placement pins)"))
        print("Negative: " + p["negative_prompt"])
        print(f"Dimension source: {size_source}")
        print(f"Settings: {p['width']}x{p['height']}px / {p['steps']} steps / scale {p['scale']} / seed {p['seed']}"
              f" / placement pins {'on' if info['pinned'] else 'off (AI’s Choice)'}")
        if p["width"] * p["height"] > 1048576:
            info["notes"].append("Exceeds 1,048,576 pixels; outside the 0-Anlas Opus free range")
        for note in info["notes"]:
            print(f"  [Note] {note}")
        if opts.dry_run:
            print("Not saved (--dry-run).")
            return 0
        if path.exists() and not opts.force:
            raise ComposeError(f"{batch.rel(root, path)} already exists. Pass --force to overwrite or choose another --id.")
        batch.write_json(path, request)
        print("Saved: " + batch.rel(root, path) + " (can be edited by hand)")
        if opts.cast_from:
            cast_path = root / batch.CHARACTERS
            data = api.read_json(cast_path)
            if opts.cast_from not in data.get("cast", {}):
                raise ComposeError(f"{opts.cast_from} is not in cast of {batch.CHARACTERS}.")
            data["cast"][opts.id] = dict(data["cast"][opts.cast_from])
            batch.write_json(cast_path, data)
            print(f"Copied character cast registration from {opts.cast_from}.")
        if opts.no_check and not opts.execute:
            return 0
        forward = ["generate", "--ids", opts.id, "--seed", "request"]
        if opts.execute:
            forward.append("--execute")
            for flag in ("accept_warnings", "confirm_zero_anlas", "allow_anlas", "confirm_v5_allowance"):
                if getattr(opts, flag):
                    forward.append("--" + flag.replace("_", "-"))
            if opts.cost_note:
                forward += ["--cost-note", opts.cost_note]
        return batch.main(forward)
    except api.ClientError as error:
        print("Error: " + str(error), file=sys.stderr)
        return 1
    except (OSError, ValueError) as error:
        print(f"Error: {type(error).__name__}: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
