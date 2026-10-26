"""Build inpainting (partial redraw) and i2i (full-frame redraw) request JSON files from an already-generated panel. No network communication.

Inherits the prompt, negative prompt, model, style preset, mode, LoRAs, and seed from the original request
(`input/pixai/requests/<ID>.json`) and prepends the desired revision (`--add`) to the start of the prompt.
Uses the adopted image by default (or the latest candidate if none is adopted, or `--candidate <number>`).
Saves under an alternate variant ID (such as `p04-01b`) so the original request and candidates remain untouched.
Delegates transmission to `pixai_batch.py generate`.

  # Add cat ears on top of the head (also creates the mask; white = redraw)
  python -X utf8 scripts/pixai_edit.py inpaint p04-01 --add "girl with cat ears on top of head" --ellipse 300,40,260,180
  # Shift the whole panel toward a snowy scene (strength 0.6 keeps composition with a small change; 0.9 makes a larger change)
  python -X utf8 scripts/pixai_edit.py i2i p04-01 --add "snowy park, winter, snow" --strength 0.6

When inpainting an image from a model that does not support inpainting (such as Tsubaki.2, where `inpaint: false` in `config/pixai-models.json`),
omitting `--model` automatically switches to `tsubaki3`. Default batchSize is 4 (in live tests, ~2 out of 4 candidates hit the mark; use `--batch-size 1` for 1 image).
See the "Inpainting" section of `docs/knowledge/pixai-composed-production.md` and `docs/knowledge/pixai-api.md` for details.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
import pixai_api as api  # noqa: E402
import pixai_batch as batch  # noqa: E402
import pixai_mask as mask_tool  # noqa: E402

INPAINT_FALLBACK = "tsubaki3"


class EditError(api.ClientError):
    pass


def source_image(root: Path, request_id: str, candidate: int | None) -> Path:
    if candidate is not None:
        path = api.project_path(root, f"{batch.CANDIDATES_DIR}/{request_id}/r{candidate:03d}.png")
        if not path.is_file():
            raise EditError(f"Candidate r{candidate:03d}.png not found for {request_id}.")
        return path
    adopted = batch.load_adopted(root)["adopted"].get(request_id, {}).get("path")
    if adopted:
        return api.project_path(root, adopted)
    found = batch.candidates(root, request_id)
    if not found:
        raise EditError(f"No images found for {request_id}. Generate candidates first or specify --candidate.")
    return api.project_path(root, found[-1].relative_to(root).as_posix())


def original_settings(request: dict) -> dict:
    """Extract inherited settings from a v2 or v1 request (preserving ${VAR} references unexpanded until send time)."""
    if request.get("api") == "v2":
        body = request.get("body") or {}
        style = body.get("style") or {}
        return {"prompt": body.get("prompt", ""), "negative": body.get("negativePrompt", ""), "model": body.get("modelVersionId"),
                "style": style.get("key") if style.get("type") == "preset" else None, "mode": body.get("mode"), "seed": body.get("seed"),
                "loras": {str(i["modelId"]): i.get("weight", 1) for i in body.get("loras") or []},
                "triggers": [i["triggerWords"] for i in body.get("loras") or [] if i.get("triggerWords")]}
    params = request.get("parameters") or {}
    style = params.get("modelStyle") or {}
    return {"prompt": params.get("prompts", ""), "negative": params.get("negativePrompts", ""), "model": params.get("modelId"),
            "style": style.get("keyId") if style.get("type") == "key" else None, "mode": params.get("inferenceProfile"),
            "seed": params.get("seed"), "loras": dict(params.get("lora") or {}), "triggers": []}


def join_tags(*parts: str) -> str:
    """Join comma-separated tags and deduplicate case-insensitively while preserving input order."""
    seen, out = set(), []
    for part in parts:
        for tag in (t.strip() for t in part.split(",")):
            if tag and tag.lower() not in seen:
                seen.add(tag.lower())
                out.append(tag)
    return ", ".join(out)


def next_id(root: Path, request_id: str) -> str:
    base = request_id.rstrip("bcdefghijklmnopqrstuvwxyz") if request_id[-1:].isalpha() and request_id[-2:-1].isdigit() else request_id
    for letter in "bcdefghijklmnopqrstuvwxyz":
        candidate = base + letter
        if not (root / batch.REQUESTS_DIR / f"{candidate}.json").exists():
            return candidate
    raise EditError("No free alternate variant IDs remain. Specify one with --id.")


def build(root: Path, opts) -> tuple[str, dict, list[str]]:
    if not batch.REQUEST_ID.fullmatch(opts.request_id):
        raise EditError("Specify the source request ID using ASCII letters, digits, -, or _.")
    new_id = opts.id or next_id(root, opts.request_id)
    if not batch.REQUEST_ID.fullmatch(new_id):
        raise EditError("Target request ID must be at most 64 characters of ASCII letters, digits, -, or _.")
    out = api.project_path(root, f"{batch.REQUESTS_DIR}/{new_id}.json")
    if out.exists() and not opts.force:
        raise EditError(f"{batch.REQUESTS_DIR}/{new_id}.json already exists. Pass --force to overwrite.")
    path = api.project_path(root, f"{batch.REQUESTS_DIR}/{opts.request_id}.json")
    if not path.is_file():
        raise EditError(f"{batch.REQUESTS_DIR}/{opts.request_id}.json not found.")
    old = original_settings(api.read_json(path))
    source = source_image(root, opts.request_id, opts.candidate)
    with Image.open(source) as image:
        width, height = image.size
    if not (512 <= width <= 1280 and 512 <= height <= 1280):
        raise EditError(f"Source image dimensions {width}x{height} are outside the v1 range (512..1280px; 1.5k images cannot be edited via v1).")
    notes = []
    if opts.model:
        if opts.model not in api.MODELS:
            raise EditError(f"--model must be a model name in {api.MODELS_FILE}.")
        model_id = api.MODELS[opts.model]["id"]
    else:
        model_id = old["model"]
    kind = api.MODEL_TYPES.get(model_id)
    if opts.command == "inpaint" and not api.supports(model_id, kind, "inpaint"):
        if opts.model:
            raise EditError("This model does not support inpainting. Use --model tsubaki3 or another supported model.")
        model_id = api.MODELS[INPAINT_FALLBACK]["id"]
        kind = api.MODEL_TYPES.get(model_id)
        notes.append(f"Original model does not support inpainting; switching to {api.MODELS[INPAINT_FALLBACK]['label']} (blends well for backgrounds and props)")
    triggers = old["triggers"]
    prompt = ", ".join(p for p in [opts.add.strip(), old["prompt"].strip(), *triggers] if p)
    negative = join_tags(old["negative"], opts.negative)
    params = {"prompts": prompt, "modelId": model_id, "width": width, "height": height, "batchSize": opts.batch_size,
              "promptHelper": {"enable": False}, "mediaFile": source.relative_to(root).as_posix(), "strength": opts.strength}
    if negative:
        params["negativePrompts"] = negative
    if isinstance(old["seed"], int):
        params["seed"] = old["seed"]
    if api.supports(model_id, kind, "mode"):
        mode = old["mode"] if old["mode"] and old["model"] == model_id else api.default_mode(model_id)
        if mode:
            params["inferenceProfile"] = mode
    if old["style"] and not opts.no_style and api.supports(model_id, kind, "style"):
        params["modelStyle"] = {"type": "key", "keyId": old["style"]}
    if old["loras"]:
        if len(old["loras"]) > 3:
            raise EditError("v1 supports at most 3 LoRAs. Reduce the LoRAs in the original request.")
        params["lora"] = old["loras"]
        if old["model"] != model_id:
            notes.append("Because the model changed, LoRAs may not match (pre-send check will inspect the LoRA base model)")
    # Validate the request on a variable-expanded copy before writing mask files.
    # The saved request preserves variable references so future variable edits still apply.
    api.prepare_request_data(root, batch.expand({"api": "v1", "parameters": params}, batch.read_variables(root), set()))
    if opts.command == "inpaint":
        if not opts.ellipse and not opts.rect:
            raise EditError("Specify the mask region with --ellipse or --rect (left,top,width,height).")
        mask_path = api.project_path(root, f"input/pixai/masks/{new_id}.png")
        preview_path = api.project_path(root, f"input/pixai/masks/{new_id}.preview.png")
        if not opts.force and (mask_path.exists() or preview_path.exists()):
            raise EditError("A mask or preview image with the same name already exists. Use another --id or pass --force.")
        mask_path.parent.mkdir(parents=True, exist_ok=True)
        with Image.open(source) as image:
            image.load()
            mask = mask_tool.make_mask(image.size, opts.ellipse, opts.rect, opts.blur)
            mask.save(mask_path)
            mask_tool.preview(image, mask).save(preview_path)
        params["maskMediaFile"] = mask_path.relative_to(root).as_posix()
        share = sum(mask.histogram()[128:]) / (width * height)
        if share > 0.2:
            notes.append(f"Mask covers {share:.0%} of the canvas, which is large; faces, expressions, and props inside the mask will also be redrawn (avoid masking faces)")
    return new_id, {"api": "v1", "parameters": params}, notes


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Build inpaint or i2i request JSON from an existing panel (no network)")
    sub = parser.add_subparsers(dest="command", required=True)
    for name, strength, text in (("inpaint", 0.75, "Redraw only the masked region"), ("i2i", 0.6, "Redraw the entire image")):
        cmd = sub.add_parser(name, help=text)
        cmd.add_argument("request_id", help="Original panel request ID (e.g. p04-01)")
        cmd.add_argument("--add", required=True, help="Revision text including subject (e.g. girl wearing a red beret), prepended to the prompt")
        cmd.add_argument("--negative", default="", help="Words to add to negativePrompts (e.g. halo)")
        cmd.add_argument("--strength", type=float, default=strength, help=f"Denoising strength (default {strength})")
        cmd.add_argument("--candidate", type=int, help="Source candidate number (default is adopted image, or latest candidate)")
        cmd.add_argument("--model", help=f"Model name from {api.MODELS_FILE} (defaults to original request's model)")
        cmd.add_argument("--batch-size", type=int, choices=(1, 4), default=4, help="Images per task (default 4)")
        cmd.add_argument("--id", help="Target request ID to save (defaults to next free variant such as p04-01b)")
        cmd.add_argument("--no-style", action="store_true", help="Do not inherit the original style preset")
        cmd.add_argument("--force", action="store_true", help="Overwrite existing request JSON and mask files")
        if name == "inpaint":
            cmd.add_argument("--ellipse", type=mask_tool.box, action="append", default=[], help="Mask ellipse left,top,width,height (px)")
            cmd.add_argument("--rect", type=mask_tool.box, action="append", default=[], help="Mask rectangle left,top,width,height (px)")
            cmd.add_argument("--blur", type=int, default=10, help="Mask boundary blur radius (px)")
    opts = parser.parse_args(argv)
    root = Path(__file__).resolve().parents[1]
    try:
        if not (root / "project.json").is_file():
            raise EditError("Run from scripts/ inside a manga project.")
        if not 0 < opts.strength <= 1:
            raise EditError("--strength must be greater than 0 and at most 1.")
        new_id, request, notes = build(root, opts)
        out = api.project_path(root, f"{batch.REQUESTS_DIR}/{new_id}.json")
        if out.exists() and not opts.force:
            raise EditError(f"{batch.REQUESTS_DIR}/{new_id}.json already exists. Pass --force to overwrite.")
        api.prepare_request_data(root, batch.expand(request, batch.read_variables(root), set()))  # Verify on expanded copy
        out.write_text(json.dumps(request, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        params = request["parameters"]
        print(f"Saved: {batch.REQUESTS_DIR}/{new_id}.json ({opts.command}, source {params['mediaFile']}, strength {params['strength']}, "
              f"{params['batchSize']} image(s))")
        if "maskMediaFile" in params:
            print(f"Mask: {params['maskMediaFile']} (open overlay preview {params['maskMediaFile'][:-4]}.preview.png before sending)")
        for note in notes:
            print(f"  [Note] {note}")
        print(f"Dry-run check: python -X utf8 scripts/pixai_batch.py generate --ids {new_id}")
        print("Send (requires --allow-unverified for undocumented v1 fields): ... generate --ids "
              f"{new_id} --execute --allow-unverified --confirm-credits --cost-note '...'")
        print(f"Adopt: compare the redrawn region side by side with the original at native resolution, then run: python -X utf8 scripts/pixai_batch.py adopt {opts.request_id} "
              f"--file {batch.CANDIDATES_DIR}/{new_id}/rNNN.png")
        return 0
    except (api.ClientError, OSError) as error:
        print(error, file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
