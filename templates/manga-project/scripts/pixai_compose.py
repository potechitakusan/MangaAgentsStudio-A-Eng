"""Build PixAI request JSON from style, background, character, LoRA, and style preset arguments.

Saves the assembled request to `input/pixai/requests/<ID>.json` and delegates transmission to
`pixai_batch.py generate` (validation, cost confirmation, execution record, and no-automatic-retry handling).
This script itself does not perform network communication.
Saved request JSON files can be edited by hand, or written directly without using this script.

Request format
  Standard is v2 (POST /v2/image/create): {"api": "v2", "body": {modelVersionId, prompt, negativePrompt, aspectRatio, size,
    mode, style, loras, seed, batchSize, sampling, promptHelper}}
  Using any of the following features builds a v1 request (POST /v1/task): {"api": "v1", "parameters": {prompts, modelId, width, height, lora, ...}}
    Documented v1 features:       --upscale (Hires Fix), --adetailer (face touch-up)
    Client-type-only v1 features: --i2i <image> (--strength; inpaint with --mask), --controlnet <type>:<image>[:<weight>], --reference <image> (IP-Adapter)
                                  (unverified in current official docs; requires --allow-unverified to send)
  In v1, project-local images are written as mediaFile / maskMediaFile / etc., and uploaded and replaced with mediaId at send time.

Models (--model; defaults to PIXAI_MODEL in .env.pixai, or tsubaki2 if unset)
  Names come from config/pixai-models.json (official PixAI models; list with --list-models). Key models:
  tsubaki2  Tsubaki.2 (DiT). Supports mode (lite, standard, pro, ultra) and style presets (--style-preset)
  tsubaki3  Tsubaki.3 (DiT). Verified accepted with mode=pro and rejected with mode=standard (default pro)
  haruka2   Haruka v2 (SDXL). Supports --sampler, --steps, and --cfg-scale
  hoshino2  Hoshino v2 (SDXL)
  Register unlisted models from their model page URL with `scripts/pixai_models.py add`,
  or specify `--model-version-id` together with `--model-type dit|sdxl`.

Prompt order (Danbooru-style convention: count -> characters -> composition -> background -> style -> quality)
  Prompt    Count tags (auto from characters) -> --layout -> characters (type + appearance + pose for 2+ characters; appearance + pose for 1) -> --scene -> --background -> --style -> quality tags
  Negative  PIXAI_NEGATIVE_PROMPT (default negative; DEFAULT_NEGATIVE if unset) -> --negative
PixAI has no per-character prompt slots or placement pins. Put multi-character posture and relative position (left, right, facing each other, etc.) in `--layout` so it appears before appearances.
Input text is concatenated as-is without rewriting. Quality tags already present in the input are not duplicated.
promptHelper (automatic prompt rewriting before generation) defaults to disable to preserve consistency with the text storyboard.

Overrides (priority: CLI argument > environment variable / .env.pixai > default; only these 5 setting names are read, never API keys)
  PIXAI_MODEL            Model name in config/pixai-models.json (e.g. tsubaki2) or version ID. CLI `--model` / `--model-version-id`
  PIXAI_QUALITY_TAGS     Full quality tag string (empty to omit). Defaults to `masterpiece, best quality` from official examples. CLI `--quality-tags`
  PIXAI_NEGATIVE_PROMPT  Full default negative string (empty to omit). Defaults to DEFAULT_NEGATIVE. CLI `--negative-base`
  PIXAI_PROMPT_HELPER    enable or disable. CLI `--prompt-helper`
  PIXAI_CHECK_IDENTITY   Set to 1 to run identity feature checks (`input/pixai/characters.json`) during `generate`
Pass literal values from `PIXAI_STYLE_` / `PIXAI_BACKGROUND_` / `PIXAI_CHAR_` in `.env.pixai` for style, background, and character text.
This script does not read those variables or expand `${VAR_NAME}` (only `${PIXAI_LORA_...}` in `--lora` is written through to the request).
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import secrets
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import pixai_api as api  # noqa: E402
import pixai_batch as batch  # noqa: E402

DEFAULT_MODEL = "tsubaki2"
# Prevent PixAI from drawing text or panel borders (per "Never pass dialogue, text, or balloons to PixAI" in pixai-composed-production.md).
DEFAULT_NEGATIVE = "text, speech bubble, panel border, watermark"
# Source: official first-API-call example ("1girl, green hair, masterpiece, best quality, ...").
DEFAULT_QUALITY = "masterpiece, best quality"
CHAR_FIELDS = ("type", "appearance", "action")
CHAR_OPTION = re.compile(r"--char(\d{1,2})-(type|appearance|action)(?:=(.*))?", re.S)
TYPES = ("girl", "boy", "other")
LORA_ID = re.compile(r"[0-9]{6,30}|\$\{PIXAI_LORA_[A-Z0-9_]+\}")


class ComposeError(api.ClientError):
    pass


# ---------------------------------------------------------------- Tag matching (used only for duplicate detection; input text is not rewritten)

def tag_key(tag: str) -> str:
    """Normalized tag form for comparison, stripping parenthetical emphasis, weights, and whitespace differences."""
    key = tag.strip().lower()
    key = re.sub(r"^\(+|\)+$", "", key)
    key = re.sub(r":\s*-?\d+(?:\.\d+)?$", "", key)
    return re.sub(r"[\s_]+", " ", key).strip()


def split_tags(text: str) -> list[str]:
    return [t.strip() for t in text.split(",") if t.strip()]


def join_text(*parts: str) -> str:
    """Keep input text as-is (trimming only outer whitespace) and join non-empty parts with ', '."""
    return ", ".join(p.strip() for p in parts if p and p.strip())


def merge_quality(quality: str, given: list[str]) -> tuple[str, list[str], list[str]]:
    tokens = [t for text in given for t in split_tags(text)]
    keys = {tag_key(t) for t in tokens}
    added, skipped = [], []
    for tag in split_tags(quality):
        if tag_key(tag) in keys:
            skipped.append(tag)
        else:
            added.append(tag)
            keys.add(tag_key(tag))
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


def build_characters(raw: list[dict]) -> list[dict]:
    characters = []
    for index, item in enumerate(raw, 1):
        unknown = set(item) - set(CHAR_FIELDS)
        if unknown:
            raise ComposeError(f"Unsupported field(s) in character {index}: {', '.join(sorted(unknown))} (PixAI has no per-character placement pins or negative prompts)")
        kind = re.sub(r"^\d+(?=(girl|boy|other)$)", "", str(item.get("type", "girl")).strip().lower())
        if kind not in TYPES:
            raise ComposeError(f"Character {index} type must be one of {' / '.join(TYPES)}.")
        for field in ("appearance", "action"):
            if "${" in str(item.get(field, "")):
                raise ComposeError(f"Character {index} {field} contains ${{...}}. This script does not expand variables; pass literal values.")
        character = {"type": kind, "appearance": str(item.get("appearance", "")).strip(), "action": str(item.get("action", "")).strip()}
        if not character["appearance"]:
            raise ComposeError(f"Specify appearance for character {index} (--char{index}-appearance).")
        characters.append(character)
    return characters


def count_tags(characters: list[dict]) -> str:
    if not characters:
        return "no humans"
    parts = []
    for kind in TYPES:
        n = sum(c["type"] == kind for c in characters)
        if n:
            parts.append(f"{n}{kind}" + ("s" if n > 1 else ""))
    if len(characters) == 1:
        parts.append("solo")
    return ", ".join(parts)


# ---------------------------------------------------------------- Setting resolution

def resolve_model(root: Path, opts) -> tuple[str, str, str, str]:
    """Return (versionId, label, kind, source)."""
    if opts.model_version_id:
        if opts.model:
            raise ComposeError("--model and --model-version-id cannot be specified at the same time.")
        api.check_id(opts.model_version_id, "--model-version-id")
        kind = api.MODEL_TYPES.get(opts.model_version_id) or opts.model_type
        if kind is None:
            raise ComposeError("For unregistered models, also specify --model-type dit or sdxl (used to check mode and sampling support).")
        return opts.model_version_id, opts.model_version_id, kind, "CLI --model-version-id"
    name, source = opts.model, "CLI --model"
    if not name:
        name, source = batch.read_setting(root, "PIXAI_MODEL"), "PIXAI_MODEL"
    if not name:
        name, source = DEFAULT_MODEL, "default"
    name = name.strip()
    if name in api.MODELS:
        model = api.MODELS[name]
        return model["id"], model["label"], model["type"], source
    if re.fullmatch(r"[0-9]{6,30}", name):
        kind = api.MODEL_TYPES.get(name) or opts.model_type
        if kind is None:
            raise ComposeError(f"Model ID from {source} is not in the catalog; also specify --model-type dit or sdxl.")
        return name, name, kind, source
    raise ComposeError(f"Model must be one of {' / '.join(api.MODELS)} or a numeric version ID ({source}). "
                       "Register unlisted models with scripts/pixai_models.py add.")


def resolve_aspect(root: Path, opts) -> tuple[str, str]:
    if opts.aspect_ratio:
        if opts.aspect_ratio not in api.RESOLUTIONS:
            raise ComposeError("--aspect-ratio must be one of " + " / ".join(api.RESOLUTIONS) + ".")
        return opts.aspect_ratio, "CLI"
    aspect = api.layout_aspect(root)
    if aspect:
        return aspect, "closest ratio to generationCanvas in config/page-layout.json"
    return "2:3", "default (generationCanvas not set)"


def resolve_text(root: Path, given: str | None, name: str, default: str) -> tuple[str, str]:
    if given is not None:
        return given, "CLI"
    value = batch.read_setting(root, name)
    if value is not None:
        return value, name
    return default, "default"


def parse_lora(value: str, index: int) -> dict:
    """ID[:weight[:triggerWords]]. ID is numeric or ${PIXAI_LORA_...}."""
    parts = value.split(":", 2)
    lora_id = parts[0].strip()
    if not LORA_ID.fullmatch(lora_id):
        raise ComposeError(f"--lora item {index} ID must be a numeric LoRA version ID or ${{PIXAI_LORA_...}}.")
    item = {"modelId": lora_id}
    if len(parts) > 1 and parts[1].strip():
        try:
            weight = float(parts[1])
        except ValueError:
            raise ComposeError(f"--lora item {index} weight must be a number between 0 and 1.") from None
        if not 0 <= weight <= 1:
            raise ComposeError(f"--lora item {index} weight must be between 0 and 1.")
        item["weight"] = weight
    if len(parts) > 2 and parts[2].strip():
        item["triggerWords"] = parts[2].strip()
    return item


def parse_controlnet(value: str, index: int) -> dict:
    parts = value.split(":", 2)
    if len(parts) < 2 or parts[0] not in api.CONTROLNET_TYPES:
        raise ComposeError(f"--controlnet item {index} must have the form type:image[:weight] (type in {' / '.join(api.CONTROLNET_TYPES)}).")
    item = {"type": parts[0], "mediaFile": parts[1]}
    if len(parts) > 2:
        try:
            item["weight"] = float(parts[2])
        except ValueError:
            raise ComposeError(f"--controlnet item {index} weight must be a number.") from None
    return item


# ---------------------------------------------------------------- Request assembly

def compose(root: Path, opts: argparse.Namespace, raw_chars: list[dict]) -> tuple[dict, dict]:
    characters = build_characters(raw_chars)
    for name in ("layout", "scene", "background", "style", "negative"):
        if "${" in (getattr(opts, name) or ""):
            raise ComposeError(f"--{name} contains ${{...}}. This script does not expand variables; pass literal values.")
    model_id, label, kind, model_source = resolve_model(root, opts)
    quality, quality_source = ("", "omitted (--no-quality-tags)") if opts.no_quality_tags else \
        resolve_text(root, opts.quality_tags, "PIXAI_QUALITY_TAGS", DEFAULT_QUALITY)
    negative_base, negative_source = resolve_text(root, opts.negative_base, "PIXAI_NEGATIVE_PROMPT", DEFAULT_NEGATIVE)
    helper, helper_source = resolve_text(root, opts.prompt_helper, "PIXAI_PROMPT_HELPER", "disable")
    helper = helper.strip().lower()
    if helper not in ("enable", "disable"):
        raise ComposeError("promptHelper must be enable or disable.")
    counts = opts.count_tags if opts.count_tags is not None else count_tags(characters)
    # Because PixAI has no per-character prompt slots, prepend the character type (girl/boy) to each character segment only when there are 2+ characters.
    texts = [join_text(c["type"] if len(characters) > 1 else "", c["appearance"], c["action"]) for c in characters]
    given = [counts, opts.layout, *texts, opts.scene, opts.background, opts.style]
    quality_text, added, skipped = merge_quality(quality, given)
    loras = [parse_lora(v, i) for i, v in enumerate(opts.lora or [], 1)]
    notes = []
    v1 = bool(opts.upscale or opts.adetailer or opts.i2i or opts.mask or opts.controlnet or opts.reference or opts.api == "v1")
    # Default to 4 images per task for complex panels (2+ characters or inpainting) and reworks (IDs that already have candidates).
    # On Tsubaki.3 pro 1k, 1 image costs 4,000 credits vs 7,000 credits for 4 images (verified in user PixAI history on 2026-10-25).
    if opts.batch_size is not None:
        batch_size, batch_source = opts.batch_size, "CLI"
    elif len(characters) >= 2 or opts.mask:
        batch_size, batch_source = 4, "default (2+ characters or inpainting)"
    elif opts.id and batch.candidates(root, opts.id):
        batch_size, batch_source = 4, "default (rework)"
    else:
        batch_size, batch_source = 1, "default"
    if v1 and any("triggerWords" in item for item in loras):
        # v1 lora is just {ID: weight} and has no triggerWords field.
        notes.append("Because v1 has no LoRA triggerWords field, trigger words were appended after character descriptions in the prompt")
    trigger = join_text(*[item.get("triggerWords", "") for item in loras]) if v1 else ""
    prompt = join_text(counts, opts.layout, *texts, trigger, opts.scene, opts.background, opts.style, quality_text)
    negative = join_text(negative_base, opts.negative)
    aspect, aspect_source = resolve_aspect(root, opts)
    seed = opts.seed if opts.seed is not None else secrets.randbelow(4294967296)
    if opts.style_preset and opts.style_custom:
        raise ComposeError("--style-preset and --style-custom cannot be specified at the same time.")
    if opts.style_preset and opts.style_preset not in api.STYLE_PRESETS:
        raise ComposeError("--style-preset must be an official preset name (list with --list-styles).")
    if (opts.mode and not api.supports(model_id, kind, "mode")) or \
            ((opts.style_preset or opts.style_custom) and not api.supports(model_id, kind, "style")):
        raise ComposeError("mode and style presets are supported only on the Tsubaki.2 and Tsubaki.3 families (other models reject mode and ignore style).")
    if kind == "dit" and (opts.sampler or opts.steps or opts.cfg_scale):
        notes.append("sampling (--sampler, --steps, --cfg-scale) is effective only on SDXL and SD v1 (official); it may have no effect on Tsubaki models")
    sampling = {k: v for k, v in (("method", opts.sampler), ("steps", opts.steps), ("cfgScale", opts.cfg_scale)) if v is not None}
    if not v1:
        if len(loras) > 5:
            raise ComposeError("v2 supports at most 5 LoRAs (official).")
        body = {"modelVersionId": model_id, "prompt": prompt, "aspectRatio": aspect, "size": opts.size,
                "seed": seed, "batchSize": batch_size, "promptHelper": helper}
        if negative_source == "default" and not opts.negative and not api.supports(model_id, kind, "negativePrompt"):
            notes.append("Omitted default negative prompt because this model's page indicates negativePrompt is unsupported")
        elif negative:
            body["negativePrompt"] = negative
        mode = opts.mode or (api.default_mode(model_id) if api.supports(model_id, kind, "mode") else None)
        if mode:
            body["mode"] = mode
        if opts.style_preset:
            body["style"] = {"type": "preset", "key": opts.style_preset}
        elif opts.style_custom:
            body["style"] = {"type": "custom", "custom": opts.style_custom}
        if loras:
            body["loras"] = loras
        if sampling:
            body["sampling"] = sampling
        request = {"api": "v2", "body": body}
    else:
        if len(loras) > 3:
            raise ComposeError("v1 supports at most 3 LoRAs (official maxProperties).")
        if opts.size != "1k":
            raise ComposeError("v1 sets dimensions via width and height (512..1280), so --size 1.5k cannot be used.")
        width, height = api.RESOLUTIONS[aspect][0]
        if opts.i2i:
            # i2i and inpainting redraw at the exact dimensions of the source image (and mask must match).
            from PIL import Image
            with Image.open(api.project_path(root, opts.i2i)) as source:
                width, height = source.size
            if opts.mask:
                with Image.open(api.project_path(root, opts.mask)) as mask:
                    if mask.size != (width, height):
                        raise ComposeError(f"Mask dimensions {mask.size[0]}x{mask.size[1]} do not match source image {width}x{height}.")
            if not (512 <= width <= 1280 and 512 <= height <= 1280):
                raise ComposeError(f"Source image dimensions {width}x{height} are outside the v1 range (512..1280px).")
        if max(width, height) > 1280:
            raise ComposeError(f"Aspect ratio {aspect} exceeds the v1 maximum dimension (1280px). Choose another aspect ratio.")
        params = {"prompts": prompt, "modelId": model_id, "width": width, "height": height, "batchSize": batch_size,
                  "promptHelper": {"enable": helper == "enable"}}
        if opts.seed is not None:
            params["seed"] = seed  # v1 seed is absent from current official docs (present in official client types)
        if negative_source == "default" and not opts.negative:
            # Because negativePrompts is an unverified v1 field, do not attach the kit default negative unless explicitly specified.
            notes.append("Omitted default negative prompt in v1 (negativePrompts is not in current official docs; pass --negative-base to include it)")
        elif negative:
            params["negativePrompts"] = negative
            notes.append("v1 negativePrompts is not in current official docs (requires --allow-unverified to send)")
        mode = opts.mode or (api.default_mode(model_id) if api.supports(model_id, kind, "mode") else None)
        if mode:
            params["inferenceProfile"] = mode
        if opts.style_preset:
            params["modelStyle"] = {"type": "key", "keyId": opts.style_preset}
        elif opts.style_custom:
            params["modelStyle"] = {"type": "custom", "custom": opts.style_custom}
        if loras:
            params["lora"] = {item["modelId"]: item.get("weight", 1.0) for item in loras}
        if sampling:
            params.update({"samplingMethod": sampling["method"]} if "method" in sampling else {})
            params.update({"samplingSteps": sampling["steps"]} if "steps" in sampling else {})
            params.update({"cfgScale": sampling["cfgScale"]} if "cfgScale" in sampling else {})
        if opts.upscale:
            params["upscale"] = opts.upscale
        if opts.adetailer:
            params["enableADetailer"] = True
        if opts.i2i:
            params["mediaFile"] = opts.i2i
            if opts.strength is not None:
                params["strength"] = opts.strength
            if opts.mask:
                # White = redraw, black = keep original (verified on 2026-10-25). Mask must match source image dimensions.
                params["maskMediaFile"] = opts.mask
        elif opts.strength is not None or opts.mask:
            raise ComposeError("--strength and --mask must be specified together with --i2i.")
        if opts.controlnet:
            params["controlNets"] = [parse_controlnet(v, i) for i, v in enumerate(opts.controlnet, 1)]
        if opts.reference:
            params["ipAdapter"] = {"enabled": True, "referenceFiles": list(opts.reference)}
        request = {"api": "v1", "parameters": params}
    if kind and not api.MODEL_TYPES.get(model_id):
        request["model_type"] = kind
    info = {"batch_source": batch_source, "label": label, "kind": kind, "model_source": model_source, "quality_source": quality_source, "quality_added": added,
            "quality_skipped": skipped, "negative_source": negative_source, "helper_source": helper_source, "aspect_source": aspect_source,
            "notes": notes, "characters": texts}
    return request, info


def parse_args(argv: list[str]):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter, allow_abbrev=False)
    parser.add_argument("--id", help="Request ID in p01-03 format (input/pixai/requests/<ID>.json)")
    parser.add_argument("--list-styles", action="store_true", help="List style presets (Tsubaki families) and exit")
    parser.add_argument("--list-models", action="store_true", help="List models in config/pixai-models.json and exit")
    parser.add_argument("--api", choices=("v2", "v1"), help="Defaults to v2, or v1 when v1-only features are specified")
    parser.add_argument("--model", help="Model name in config/pixai-models.json (tsubaki2, tsubaki3, haruka2, etc.) or version ID (defaults to PIXAI_MODEL, or tsubaki2)")
    parser.add_argument("--model-version-id", help="Version ID for an unregistered model (https://pixai.art/model/<id>/<versionId>)")
    parser.add_argument("--model-type", choices=("dit", "sdxl"), help="Family type for an unregistered model")
    parser.add_argument("--style", default="", help="Art style text (value from PIXAI_STYLE_...)")
    parser.add_argument("--background", default="", help="Background, location, time of day, lighting (value from PIXAI_BACKGROUND_...)")
    parser.add_argument("--layout", default="", help="Multi-character posture and relative position, placed right after count tags and before appearances "
                        "(e.g. girl on the right, boy on the left, facing each other)")
    parser.add_argument("--scene", default="", help="Composition, camera angle, overall situation (upper body, from below, side by side, etc.)")
    parser.add_argument("--count-tags", help="Manually specify count tags (default is auto from characters; adds solo for 1 character, or no humans when empty)")
    parser.add_argument("--negative", default="", help="Additional negative words (appended after default negative)")
    parser.add_argument("--negative-base", help="Full default negative string (overrides PIXAI_NEGATIVE_PROMPT; empty string to omit). "
                        "Defaults to " + DEFAULT_NEGATIVE)
    quality = parser.add_mutually_exclusive_group()
    quality.add_argument("--quality-tags", help="Override quality tags (empty string to omit)")
    quality.add_argument("--no-quality-tags", action="store_true", help="Do not append quality tags")
    parser.add_argument("--style-preset", help="Style preset (Tsubaki families only; list with --list-styles)")
    parser.add_argument("--style-custom", help="Custom style text inserted before the prompt (Tsubaki families only; advanced)")
    parser.add_argument("--mode", choices=api.MODES, help="Inference mode for Tsubaki.2 / Tsubaki.3 families (defaults to catalog default_mode: standard for Tsubaki.2, pro for Tsubaki.3)")
    parser.add_argument("--lora", action="append", help="LoRA as ID[:weight[:triggerWords]] (ID is numeric or ${PIXAI_LORA_...}). Up to 5 in v2, 3 in v1")
    parser.add_argument("--aspect-ratio", help="Aspect ratio (" + " / ".join(api.RESOLUTIONS) + "). Defaults to closest ratio to generationCanvas")
    parser.add_argument("--size", choices=api.SIZES, default="1k", help="Resolution tier (v2 only; 1.5k has 1536px long edge)")
    parser.add_argument("--batch-size", type=int, choices=(1, 4),
                        help="Images per task (official values are 1 or 4). Defaults to 4 for 2+ characters, inpainting, or reworks, and 1 otherwise")
    parser.add_argument("--sampler", choices=api.SAMPLERS, help="SDXL sampler")
    parser.add_argument("--steps", type=int, help="SDXL steps (1..100)")
    parser.add_argument("--cfg-scale", type=float, help="SDXL CFG scale")
    parser.add_argument("--seed", type=int, help="Random if omitted (v1 omits seed when not specified)")
    parser.add_argument("--prompt-helper", choices=("enable", "disable"), help="Automatic prompt rewriting before generation (default disable)")
    parser.add_argument("--upscale", type=float, help="v1: Hires Fix scale factor (>1 and <=2)")
    parser.add_argument("--adetailer", action="store_true", help="v1: Post-generation face touch-up (ADetailer)")
    parser.add_argument("--i2i", help="v1 (unverified): Project-local source image for i2i")
    parser.add_argument("--strength", type=float, help="v1 (unverified): i2i denoising strength (>0 and <=1)")
    parser.add_argument("--mask", help="v1: Inpainting mask (project-local image matching source dimensions; white = redraw; use with --i2i)")
    parser.add_argument("--controlnet", action="append", help="v1 (unverified): type:project-local-image[:weight] (openpose, canny, depth, etc.)")
    parser.add_argument("--reference", action="append", help="v1 (unverified): IP-Adapter reference image (project-local image for character/style reference)")
    parser.add_argument("--chars-json", help="Character array JSON (relative path in project). Do not combine with --charN-...")
    parser.add_argument("--cast-from", help="Copy character cast registration (cast in characters.json) from an existing request ID")
    parser.add_argument("--force", action="store_true", help="Overwrite an existing request JSON with the same name")
    parser.add_argument("--dry-run", action="store_true", help="Display the assembled request without saving")
    parser.add_argument("--no-check", action="store_true", help="Skip the post-save dry-run lint check")
    parser.add_argument("--execute", action="store_true", help="Send via pixai_batch.py generate after validation")
    parser.add_argument("--accept-warnings", action="store_true")
    parser.add_argument("--confirm-credits", action="store_true")
    parser.add_argument("--allow-unverified", action="store_true")
    parser.add_argument("--cost-note")
    return parser


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    root = Path(__file__).resolve().parents[1]
    try:
        argv, numbered = extract_character_options(argv)
        opts = parse_args(argv).parse_args(argv)
        if opts.list_styles:
            for key, label in sorted(api.STYLE_PRESETS.items()):
                print(f"{key}: {label}")
            return 0
        if opts.list_models:
            for name, model in api.MODELS.items():
                print(f"{name}: {model['label']} ({model['type'].upper()}, modelVersionId {model['id']})"
                      f" {model.get('strengths_ja', '')} / API: {model.get('api', 'not recorded')}")
            return 0
        if not (root / "project.json").is_file():
            raise ComposeError("Run from scripts/ inside a manga project.")
        if not opts.id or not batch.REQUEST_ID.fullmatch(opts.id):
            raise ComposeError("Specify a request ID with --id using ASCII letters, digits, -, or _ (e.g. p01-03).")
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
        request, info = compose(root, opts, raw)
        path = root / batch.REQUESTS_DIR / f"{opts.id}.json"
        print(f"Model: {info['label']} ({info['kind'].upper()}, source={info['model_source']}) / Request format: {request['api']}")
        print(f"Quality tags: source={info['quality_source']} / added={', '.join(info['quality_added']) or 'none'}"
              f" / skipped (already in input)={', '.join(info['quality_skipped']) or 'none'}")
        print(f"Default negative: source={info['negative_source']} / promptHelper: source={info['helper_source']} / Aspect ratio source: {info['aspect_source']}")
        print(f"Images per task: source={info['batch_source']} (4 images cost ~1.75x 1 image; pass --batch-size 1 for 1 image)")
        if request["api"] == "v2":
            body = request["body"]
            print("Prompt: " + body["prompt"])
            print("Negative: " + body.get("negativePrompt", "(none; server default)"))
            width, height = api.RESOLUTIONS[body["aspectRatio"]][api.SIZES.index(body["size"])]
            print(f"Settings: {body['aspectRatio']} {body['size']} ({width}x{height}px) / {body['batchSize']} img / seed {body['seed']}"
                  + (f" / mode {body['mode']}" if "mode" in body else "") + (f" / style {json.dumps(body['style'], ensure_ascii=False)}" if "style" in body else "")
                  + (f" / LoRA {json.dumps(body['loras'], ensure_ascii=False)}" if "loras" in body else ""))
        else:
            params = request["parameters"]
            print("Prompt: " + params["prompts"])
            print("Negative: " + params.get("negativePrompts", "(none; server default)"))
            shown = {k: v for k, v in params.items() if k not in ("prompts", "negativePrompts")}
            print("Settings: " + json.dumps(shown, ensure_ascii=False))
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
            for flag in ("accept_warnings", "confirm_credits", "allow_unverified"):
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
