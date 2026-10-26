"""PixAI key loading, connection check, and single-task generation (send -> wait for completion -> save images). Python 3.10+, no extra dependencies.

Uses Pillow only when converting non-PNG responses (WebP / JPEG) into PNG (already required for project page composition).

  python -X utf8 scripts/pixai_api.py key-status                    # Check only the key source (no network)
  python -X utf8 scripts/pixai_api.py status                        # Verify connection and authentication (no image generation)
  python -X utf8 scripts/pixai_api.py generate --request <req.json> # Dry-run validation by default
  python -X utf8 scripts/pixai_api.py fetch --record <record.json>  # Re-fetch a task interrupted while waiting for completion via taskId
  python -X utf8 scripts/pixai_api.py upload --file <image> --execute # Upload a reference / i2i image and obtain a mediaId

Official specification (sources and verification dates in docs/knowledge/pixai-api.md)
  POST /v2/image/create   Current generation API: modelVersionId, prompt, aspectRatio, size, mode, style, loras (up to 5), etc.
  POST /v1/task           Legacy format: parameters containing prompts, modelId, width, height, lora, upscale, enableADetailer, etc.
  GET  /v1/task/{taskId}  Status (waiting, running, completed, failed, cancelled) and outputs.mediaIds / mediaUrls
  GET  /v1/media/{id}     Media info (PUBLIC URLs, etc.)
  POST /v1/media/upload   Upload raw image bytes and obtain a mediaId
Poll at most once per 1.5 seconds (official); this script starts at 3 seconds and backs off up to 10 seconds. Generated images are not stored indefinitely, so save immediately upon completion.
No official API endpoint queries credit balance or consumption. Sending requires explicit user authorization (--confirm-credits) and a confirmation memo (--cost-note).
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
from http.client import HTTPException
from io import BytesIO
import json
import math
import os
from pathlib import Path
import re
import secrets
import struct
import sys
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import HTTPRedirectHandler, Request, build_opener
import zlib


# Pin the destination of the Authorization header. Do not follow redirects on authenticated requests.
API_ROOT = "https://api.pixai.art"
MAX_RESPONSE = 64 * 1024 * 1024
KEY_NAME = "PIXAI_API_KEY"
KEY_FILES = (".secrets/pixai.env", ".secrets/.env", ".env")
KEY_SETUP_GUIDE = (
    "Add the following single line to .env (or .secrets/pixai.env) in the project root:\n"
    "PIXAI_API_KEY=your_actual_key\n"
    "The left-hand side PIXAI_API_KEY is a public setting name; keep the right-hand key value secret.\n"
    "Create a key at https://pixai.art/profile/edit/api. Do not add Bearer, and do not put a bare key on a line by itself.\n"
    "Never paste your actual key into chat. After configuring, run key-status to verify the key source."
)
UPLOADS = "output/pixai/uploads.json"

# Model catalog (name -> modelVersionId, family type, and supported fields). Sources and verification dates are recorded in the file.
# Use scripts/pixai_models.py add to register additional models into the project's catalog.
MODELS_FILE = "config/pixai-models.json"


def load_models(path: Path) -> dict:
    if not path.is_file():
        return {}
    models = json.loads(path.read_text(encoding="utf-8-sig")).get("models") or {}
    for name, model in models.items():
        if not re.fullmatch(r"[a-z0-9][a-z0-9.-]{0,40}", name) or not re.fullmatch(r"[0-9]{6,30}", str(model.get("id", ""))) \
                or model.get("type") not in {"dit", "sdxl"}:
            raise SystemExit(f"Invalid entry {name} in {MODELS_FILE} (name must be lowercase ASCII/digits, id must be digits, type must be dit or sdxl).")
    return models


MODELS = load_models(Path(__file__).resolve().parent.parent / MODELS_FILE)
MODEL_TYPES = {m["id"]: m["type"] for m in MODELS.values()}
MODELS_BY_ID = {m["id"]: m for m in MODELS.values()}
# Project record of verified LoRA base models and terms of use (written by scripts/pixai_models.py lora; cached once checked).
LORAS_FILE = "config/pixai-loras.json"


def lora_notes(root: Path, model_id: str, lora_ids: list[str]) -> list[str]:
    """Check LoRA and generation model compatibility using only the project's local record (no network)."""
    path = root / LORAS_FILE
    records = (json.loads(path.read_text(encoding="utf-8-sig")).get("loras") or {}) if path.is_file() else {}
    model = MODELS_BY_ID.get(model_id, {})
    notes = []
    for lora_id in lora_ids:
        record = records.get(lora_id)
        if record is None:
            notes.append(f"Base model for LoRA {lora_id} is unverified (record it with `scripts/pixai_models.py lora --url <LoRA-page>` to enable checking)")
            continue
        label = record.get("title") or lora_id
        base_type, base_id = record.get("baseModelType"), record.get("baseModelId")
        if base_id and model.get("modelId") and base_id != model["modelId"]:
            notes.append(f"LoRA {label} targets a different model (modelId {base_id}); it may not work or may distort output on {model.get('label', model_id)}")
        elif base_type and model.get("pixaiType") and base_type != model["pixaiType"]:
            notes.append(f"LoRA {label} base model type {base_type} differs from generation model {model.get('label', model_id)} ({model['pixaiType']}); "
                         "it may not work or may distort output")
        elif not model.get("pixaiType"):
            notes.append(f"Generation model type is not in the catalog, so compatibility with LoRA {label} ({base_type or 'unknown type'}) was not checked")
        if record.get("commercialUse") is False:
            notes.append(f"Commercial use is not permitted for LoRA {label} (confirm publishing and sales terms with the user)")
    return notes


SAMPLERS = ("Euler a", "Euler", "LMS", "Heun", "DPM2 Karras", "DPM2 a Karras", "DDIM", "DPM++ 2M Karras",
            "DPM++ 2S a Karras", "DPM++ SDE Karras", "DPM++ 2M SDE Karras", "Restart")
# Source: platform.pixai.art/en/docs/references/supported-resolutions (verified 2026-10-25).
RESOLUTIONS = {
    "1:1": ((1024, 1024), (1536, 1536)), "2:3": ((848, 1280), (1024, 1536)), "3:2": ((1280, 848), (1536, 1024)),
    "3:4": ((864, 1152), (1152, 1536)), "4:3": ((1152, 864), (1536, 1152)), "3:5": ((768, 1280), (912, 1536)),
    "5:3": ((1280, 768), (1536, 912)), "9:16": ((720, 1280), (864, 1536)), "16:9": ((1280, 720), (1536, 864)),
    "1:3": ((512, 1536), (512, 1536)), "3:1": ((1536, 512), (1536, 512)),
}
SIZES = ("1k", "1.5k")
MODES = ("lite", "standard", "pro", "ultra")
# Source: v2 createImage style.key (verified 2026-10-25). Effective only on Tsubaki.2 and Tsubaki.3; ignored on other models.
STYLE_PRESETS = {
    "anime-watercolor-impasto": "Watercolor Glow", "art-crayon": "Art Crayon", "bold-line-soft-color": "Glint & Gloom",
    "chibi": "Chibi", "classic-japanese": "Classic Anime", "clean-flat-illustration": "Clean Flat-Illustration",
    "colored-pencil-grain": "Chromatic Pencil", "cool-warm-oil-contrast": "Seasonal Glow", "desaturated-cool": "Cool Softlight",
    "flat-anime-pastel": "Pastel Flat", "glossy-glass-anime": "Glassy Anime", "grey-blocks-lineless": "Grey Wash",
    "hard-line-monochrome-accent": "Sharp Ink", "high-contrast-retro-vivid": "Neon Vivid", "holographic": "Hyper Pop",
    "korean-style": "Polished Manhwa", "lineart-watercolor-airy": "Luminous Wash",
    "low-saturation-expressive-eyes": "Muted & Transparent", "lucid-dreamy": "Lucid Dreamy",
    "luminous-retro-impasto": "Luminous Impasto", "minimal-flat-color": "Minimal Flat", "modern-oil-glamour": "Modern Glam Anime",
    "moe-pastel": "Moe Pastel", "oil-watercolor-blend": "Water-Infused Oil", "painterly-doodle": "Tender Brushstroke",
    "paper-watercolor": "Soft Aqueous", "pencil-sketch": "Pencil Sketch", "poster-graffiti": "Neon Poster",
    "retro-comic-fusion": "Retro Fusion", "retro-oil-glamour": "Retro Glam Anime", "retro-tv-anime": "90s Retro-Cell",
    "semi-realistic": "Semi-Real", "stable-vaporwave": "Neon Vaporwave", "tinted-sketch": "Tinted Sketch",
    "vintage-collage": "Vintage Collage",
}
V2_KEYS = {"modelVersionId", "prompt", "negativePrompt", "aspectRatio", "size", "mode", "style", "loras", "seed",
           "batchSize", "sampling", "promptHelper"}
# Fields documented in the official v1 reference (createGenerationTask, verified 2026-10-25).
V1_DOCUMENTED = {"prompts", "modelId", "width", "height", "lora", "batchSize", "inferenceProfile", "modelStyle",
                 "enableTile", "upscale", "upscaleSampler", "enableADetailer", "promptHelper"}
# Fields present in the official JavaScript client types (github.com/pixai-art/pixai-client-js parameters.types.ts) but absent from current official docs.
# Requires --allow-unverified to send. Includes i2i (mediaId / strength), ControlNet, and IP-Adapter (reference images).
V1_UNVERIFIED = {"negativePrompts", "seed", "samplingSteps", "samplingMethod", "cfgScale", "clipSkip", "mediaId", "mediaUrl",
                 "strength", "maskMediaId", "maskMediaUrl", "controlNets", "ipAdapter", "latentCouple", "vaeModelId",
                 "upscaleDenoisingSteps", "upscaleDenoisingStrength", "upscaler", "enlarge", "enlargeModel"}
CONTROLNET_TYPES = ("dwpose", "openpose_full", "canny", "depth", "hed", "mlsd", "openpose", "seg", "normal", "scribble")
# Kit-specific fields referencing project-local images. Uploaded at send time and replaced with mediaId (not sent to PixAI under these names).
LOCAL_FILE_KEYS = {"mediaFile": "mediaId", "maskMediaFile": "maskMediaId"}
IMAGE_TYPES = {b"\x89PNG\r\n\x1a\n": ("image/png", ".png"), b"\xff\xd8\xff": ("image/jpeg", ".jpg"),
               b"RIFF": ("image/webp", ".webp"), b"GIF8": ("image/gif", ".gif")}
TERMINAL = {"completed", "failed", "cancelled"}


class ClientError(Exception):
    """User-facing error that excludes keys and raw input payloads."""


class RejectedError(ClientError):
    """Rejected before task creation (HTTP 4xx). Resending will not duplicate credit charges, but fix the cause before resending."""


def project_path(root: Path, relative: str) -> Path:
    path = Path(relative)
    if path.is_absolute() or path.drive or ".." in path.parts:
        raise ClientError("Specify a relative path inside the project root.")
    resolved = (root / path).resolve()
    if not resolved.is_relative_to(root):
        raise ClientError("Links pointing outside the project root are not allowed.")
    return resolved


def read_json(path: Path) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, UnicodeError, ValueError):
        raise ClientError("Cannot read JSON file. Check the file path and format.") from None
    if not isinstance(value, dict):
        raise ClientError("Top-level JSON value must be an object.")
    return value


def write_record(path: Path, data: dict) -> None:
    temporary = path.with_name(path.name + ".tmp")
    with temporary.open("w", encoding="utf-8") as stream:
        json.dump(data, stream, ensure_ascii=False, indent=2)
        stream.write("\n")
    # On Windows, antivirus or search indexing can briefly hold a handle and reject replace() (observed right before send on 2026-10-25).
    for attempt in range(5):
        try:
            temporary.replace(path)
            return
        except PermissionError:
            if attempt == 4:
                raise
            time.sleep(0.2 * (attempt + 1))


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


# ---------------------------------------------------------------- API Key

def load_key(root: Path) -> tuple[str, str]:
    value = os.environ.get(KEY_NAME, "").strip()
    source = "Environment variable " + KEY_NAME
    diagnostics = [source + (": empty value" if KEY_NAME in os.environ else ": not set")]

    def invalid(location: str, reason: str) -> ClientError:
        # Use only fixed source labels in location; never include input lines, secret values, or raw exception text.
        return ClientError(f"[Configuration error] {location}: {reason}\n{KEY_SETUP_GUIDE}")

    if not value:
        for relative in KEY_FILES:
            path = project_path(root, relative)
            if not path.exists():
                diagnostics.append(relative + ": file not found")
                continue
            if not path.is_file():
                raise invalid(relative, "invalid format (not a regular configuration file)")
            try:
                lines = path.read_text(encoding="utf-8-sig").splitlines()
            except UnicodeError:
                raise invalid(relative, "invalid format (cannot read as UTF-8 text)") from None
            except OSError:
                raise invalid(relative, "read failed (check file permissions)") from None
            matches = []
            for line in lines:
                match = re.match(r"^\s*(?:export\s+)?PIXAI_API_KEY\s*=\s*(.*?)\s*$", line)
                if not match and re.match(r"^\s*(?:export\s+)?PIXAI_API_KEY\b", line):
                    raise invalid(relative, "invalid format (separate setting name and value with an ASCII =)")
                if match:
                    candidate = match.group(1)
                    if candidate.startswith(("'", '"')):
                        quote = candidate[0]
                        end = candidate.find(quote, 1)
                        if end < 0 or (candidate[end + 1:].strip() and not candidate[end + 1:].lstrip().startswith("#")):
                            raise invalid(relative, "invalid format (unclosed quote or trailing characters)")
                        candidate = candidate[1:end]
                    else:
                        candidate = "" if candidate.startswith("#") else re.split(r"\s+#", candidate, maxsplit=1)[0].strip()
                    matches.append(candidate)
            if len(matches) > 1:
                raise invalid(relative, "invalid format (duplicate PIXAI_API_KEY lines)")
            if not matches:
                diagnostics.append(relative + ": setting line missing (requires PIXAI_API_KEY=...)")
            elif not matches[0].strip():
                diagnostics.append(relative + ": empty value (key required on the right side of =)")
            else:
                value, source = matches[0], relative
                break
    if not value:
        raise ClientError("[Configuration error] No usable API key found.\n" + "\n".join(diagnostics) + "\n" + KEY_SETUP_GUIDE)
    # Never print the value or its length. Do not perform dotenv variable expansion or command execution.
    if not re.fullmatch(r"[A-Za-z0-9._~+/=-]+", value) or value.lower() in {"your_api_key", "your_key", "replace_me"}:
        raise invalid(source, "invalid format (value contains disallowed characters, spaces, or unreplaced placeholder text)")
    return value, source


# ---------------------------------------------------------------- Network communication

class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


ENDPOINT = re.compile(r"/v2/image/create|/v1/task|/v1/task/[0-9]{1,30}|/v1/media/[0-9]{1,30}|/v1/media/upload")


def error_detail(body: bytes, key: str) -> str:
    """Briefly show only the response code and message (to help fix input errors). Never include the key."""
    try:
        data = json.loads(body.decode("utf-8", "replace"))
    except ValueError:
        return ""
    items = data.get("errors") if isinstance(data, dict) and isinstance(data.get("errors"), list) else [data]
    parts = []
    for item in items[:3]:
        if isinstance(item, dict):
            text = " ".join(str(item[k]) for k in ("code", "message") if isinstance(item.get(k), (str, int)))
            parts.append(text.replace(key, "<KEY>")[:300])
    return (" (response: " + " / ".join(p for p in parts if p) + ")") if any(parts) else ""


def api_request(key: str, method: str, endpoint: str, *, payload: bytes | None = None,
                content_type: str = "application/json", timeout: float = 60) -> tuple[int, bytes]:
    if not ENDPOINT.fullmatch(endpoint) or method not in {"GET", "POST"}:
        raise ClientError("Unsupported API endpoint.")
    # PixAI's API may reject requests without Content-Type due to CSRF protection, so include application/json even on GET.
    headers = {"Authorization": "Bearer " + key, "Accept": "application/json", "User-Agent": "MangaAgentsStudio-PixAI/1",
               "Content-Type": content_type}
    request = Request(API_ROOT + endpoint, data=payload, headers=headers, method=method)
    creating = endpoint in {"/v2/image/create", "/v1/task"}
    retry_note = ("No automatic retry was performed. Check the execution record and your PixAI generation history and credits before retrying."
                  if creating else "No image generation was requested.")
    try:
        with build_opener(NoRedirect()).open(request, timeout=timeout) as response:
            body = response.read(MAX_RESPONSE + 1)
            status = response.status
    except HTTPError as error:
        status = error.code
        detail = error_detail(error.read(4096), key)
        error.close()
        explanations = {
            400: "[Input error] The request content was not accepted.",
            401: "[Authentication failed] The request with this key was not authenticated. Check the key source and validity.",
            402: "[Insufficient credits] Insufficient credits.",
            403: "[Access denied] The server rejected the request. Check key permissions and terms of use.",
            404: "[Not found] The specified task or media was not found.",
            422: "[Input error] A value in the request was not accepted.",
            429: "[Rate limit] Reached the concurrent queued task limit (officially 10) or rate limit.",
        }
        fallback = "[Server error] An error occurred on the server." if status >= 500 else "[API response error] Could not complete the request."
        message = f"HTTP {status}: " + explanations.get(status, fallback) + detail
        if "inferenceProfile" in detail:
            message += " The submitted mode cannot be used with this model. Another mode (such as pro or ultra) may be required."
        if creating and 400 <= status < 500:
            raise RejectedError(message + " No task was created. Fix the cause before sending again.") from None
        raise ClientError(message + " " + retry_note) from None
    except (URLError, OSError, HTTPException):
        raise ClientError("[Network error] API communication did not complete. Key validity cannot be determined from this result alone. "
                          "Check your network, proxy, or environment connection restrictions. " + retry_note) from None
    if len(body) > MAX_RESPONSE:
        raise ClientError("API response exceeded the maximum allowed size.")
    return status, body


def api_json(key: str, method: str, endpoint: str, **kwargs) -> dict:
    _, body = api_request(key, method, endpoint, **kwargs)
    try:
        data = json.loads(body)
    except (ValueError, UnicodeError):
        raise ClientError("[Invalid API response] Response is not valid JSON.") from None
    if not isinstance(data, dict):
        raise ClientError("[Invalid API response] Unexpected response format.")
    return data


def auth_check(key: str) -> str:
    """Query a non-existent task ID and check whether it returns 404 (authenticated) or 401 (invalid key). Generates no images and consumes no credits."""
    try:
        api_request(key, "GET", "/v1/task/0", timeout=30)
    except ClientError as error:
        if str(error).startswith("HTTP 404"):
            return "Authentication succeeded (404 on non-existent task lookup; no image generated)"
        raise
    return "Authentication succeeded (no image generated)"


def download(url: str) -> bytes:
    """Download an image from a public URL without attaching the Authorization header (never send keys to other hosts)."""
    if urlparse(url).scheme != "https":
        raise ClientError("Image URL is not https.")
    request = Request(url, headers={"User-Agent": "MangaAgentsStudio-PixAI/1"})
    try:
        with build_opener().open(request, timeout=120) as response:
            if urlparse(response.geturl()).scheme != "https":
                raise ClientError("Image redirect destination is not https.")
            body = response.read(MAX_RESPONSE + 1)
    except HTTPError as error:
        error.close()
        raise ClientError(f"HTTP {error.code}: Could not download image (generated images are not stored indefinitely).") from None
    except (URLError, OSError, HTTPException):
        raise ClientError("[Network error] Could not download image. You can re-fetch it by taskId (fetch).") from None
    if len(body) > MAX_RESPONSE:
        raise ClientError("Downloaded image exceeded the maximum allowed size.")
    return body


# ---------------------------------------------------------------- Images

def image_kind(data: bytes) -> tuple[str, str] | None:
    for magic, kind in IMAGE_TYPES.items():
        if data.startswith(magic) and (magic != b"RIFF" or data[8:12] == b"WEBP"):
            return kind
    return None


def png_size(data: bytes) -> tuple[int, int]:
    if len(data) < 33 or data[:16] != b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR":
        raise ClientError("Generated output is not a PNG.")
    width, height = struct.unpack(">II", data[16:24])
    if not width or not height:
        raise ClientError("Generated PNG dimensions are invalid.")
    offset, has_pixels = 8, False
    while offset + 12 <= len(data):
        length = struct.unpack(">I", data[offset:offset + 4])[0]
        end = offset + 12 + length
        if end > len(data):
            break
        kind = data[offset + 4:offset + 8]
        expected = struct.unpack(">I", data[end - 4:end])[0]
        if zlib.crc32(data[offset + 4:end - 4]) & 0xFFFFFFFF != expected:
            raise ClientError("Generated PNG CRC mismatch.")
        has_pixels = has_pixels or kind == b"IDAT"
        if kind == b"IEND":
            if length == 0 and end == len(data) and has_pixels:
                return width, height
            break
        offset = end
    raise ClientError("Generated PNG is truncated or structurally invalid.")


def as_png(data: bytes) -> tuple[bytes, str]:
    """Keep PNG as-is; convert WebP or JPEG to PNG via Pillow. Also return the original MIME type."""
    kind = image_kind(data)
    if kind is None:
        raise ClientError("Generated output is not a recognized image.")
    if kind[0] == "image/png":
        return data, kind[0]
    try:
        from PIL import Image
    except ImportError:
        raise ClientError("Pillow is required to convert non-PNG images to PNG (requirements-composition.txt).") from None
    with Image.open(BytesIO(data)) as image:
        out = BytesIO()
        image.convert("RGBA" if "A" in image.getbands() else "RGB").save(out, format="PNG")
    return out.getvalue(), kind[0]


# ---------------------------------------------------------------- Request validation

def default_mode(model_id: str) -> str | None:
    """Default mode filled in during request assembly. Omitted if not set in the catalog (uses server default)."""
    return MODELS_BY_ID.get(model_id, {}).get("default_mode")


def supports(model_id: str, kind: str | None, feature: str) -> bool:
    """Whether a model accepts mode, style, negativePrompt, controlnet, or inpaint. Falls back to family kind when not in catalog (mode and style are DiT-only)."""
    model = MODELS_BY_ID.get(model_id, {})
    if feature in model:
        return bool(model[feature])
    return kind == "dit" if feature in ("mode", "style") else True


def check_mode(model_id: str, mode: str, kind: str | None, notes: list[str]) -> None:
    """Block modes confirmed to be rejected on known models before sending, and record a note for unverified modes."""
    model = MODELS_BY_ID.get(model_id)
    if model is None:
        if kind == "dit":
            notes.append(f"mode {mode} was set on an unregistered DiT model; supported modes are unverified (rejected requests fail with 4xx without creating a task)")
        return
    if mode in model.get("modes_rejected", ()):
        raise ClientError(f"{model['label']} rejects mode {mode} (verified). "
                          + "Use " + " / ".join(model.get("modes_accepted", ())) + ".")
    if mode not in model.get("modes_accepted", ()):
        notes.append(f"Whether mode {mode} is accepted by {model['label']} is unverified (rejected requests fail with 4xx without creating a task)")


def model_type(model_id: str, request: dict) -> str | None:
    """Family type (dit / sdxl) for a known model ID, or from the request's model_type annotation (not sent)."""
    hint = request.get("model_type")
    if hint is not None and hint not in {"dit", "sdxl"}:
        raise ClientError("model_type must be dit or sdxl (non-transmitted annotation).")
    return MODEL_TYPES.get(model_id) or hint


def layout_aspect(root: Path) -> str | None:
    """Closest aspect ratio to generationCanvas in config/page-layout.json."""
    layout = root / "config/page-layout.json"
    canvas = read_json(layout).get("generationCanvas") if layout.is_file() else None
    if not isinstance(canvas, dict) or not all(type(canvas.get(k)) is int and canvas[k] > 0 for k in ("width", "height")):
        return None
    return closest_aspect(canvas["width"], canvas["height"])


def closest_aspect(width: int, height: int) -> str:
    target = math.log(width / height)
    return min(RESOLUTIONS, key=lambda r: abs(math.log(RESOLUTIONS[r][0][0] / RESOLUTIONS[r][0][1]) - target))


def output_size(body: dict) -> tuple[int, int]:
    return RESOLUTIONS[body["aspectRatio"]][SIZES.index(body["size"])]


def check_id(value, label: str) -> None:
    if not isinstance(value, str) or not re.fullmatch(r"[0-9]{6,30}", value):
        raise ClientError(f"{label} must be a PixAI version ID (numeric string from the end of the model page URL).")


def check_seed(value) -> None:
    if type(value) is not int or not 0 <= value <= 4294967295:
        raise ClientError("seed must be an integer between 0 and 4294967295 (random if omitted).")


def prepare_v2(root: Path, request: dict) -> list[str]:
    body = request["body"]
    if not isinstance(body, dict):
        raise ClientError("body must be an object.")
    unknown = set(body) - V2_KEYS
    if "modelId" in unknown:
        raise ClientError("v2 uses modelVersionId instead of modelId (modelId is officially deprecated in v2).")
    if "callbackUrl" in unknown:
        raise ClientError("callbackUrl is not used. Completion is verified by polling in this script.")
    if unknown:
        raise ClientError("Undocumented v2 field(s): " + ", ".join(sorted(unknown)))
    check_id(body.get("modelVersionId"), "modelVersionId")
    if not isinstance(body.get("prompt"), str) or not body["prompt"].strip():
        raise ClientError("Set a generation prompt in body.prompt.")
    if not isinstance(body.get("negativePrompt", ""), str):
        raise ClientError("negativePrompt must be a string.")
    if "aspectRatio" not in body:
        aspect = layout_aspect(root)
        if aspect is None:
            raise ClientError("Specify aspectRatio in the request or configure generationCanvas in config/page-layout.json.")
        body["aspectRatio"] = aspect
    if body["aspectRatio"] not in RESOLUTIONS:
        raise ClientError("aspectRatio must be one of " + " / ".join(RESOLUTIONS) + ".")
    body.setdefault("size", "1k")
    if body["size"] not in SIZES:
        raise ClientError("size must be 1k or 1.5k.")
    kind = model_type(body["modelVersionId"], request)
    notes = []
    if "mode" in body:
        if body["mode"] not in MODES:
            raise ClientError("mode must be one of " + " / ".join(MODES) + ".")
        if kind == "sdxl" or not supports(body["modelVersionId"], kind, "mode"):
            raise ClientError("mode is supported only on the Tsubaki.2 and Tsubaki.3 families. Other models officially reject it with 400.")
        check_mode(body["modelVersionId"], body["mode"], kind, notes)
    if "style" in body:
        style = body["style"]
        if not isinstance(style, dict) or style.get("type") not in {"preset", "custom"}:
            raise ClientError('style must be {"type": "preset", "key": ...} or {"type": "custom", "custom": ...}.')
        if style["type"] == "preset" and (set(style) != {"type", "key"} or style["key"] not in STYLE_PRESETS):
            raise ClientError("style.key must be an official preset name (list with pixai_compose.py --list-styles).")
        if style["type"] == "custom" and (set(style) != {"type", "custom"} or not isinstance(style["custom"], str) or not style["custom"].strip()):
            raise ClientError("Provide style description text in style.custom.")
        if kind == "sdxl" or not supports(body["modelVersionId"], kind, "style"):
            notes.append("style is effective only on the Tsubaki.2 and Tsubaki.3 families; it is officially ignored on this model")
    if body.get("negativePrompt") and not supports(body["modelVersionId"], kind, "negativePrompt"):
        notes.append("This model's page indicates negativePrompt is unsupported; it may have no effect")
    loras = body.get("loras", [])
    if not isinstance(loras, list) or len(loras) > 5:
        raise ClientError("loras must be an array of at most 5 items.")
    for index, item in enumerate(loras, 1):
        if not isinstance(item, dict) or set(item) - {"modelId", "weight", "triggerWords"}:
            raise ClientError(f"loras item {index} may contain only modelId, weight, and triggerWords.")
        check_id(item.get("modelId"), f"loras item {index} modelId")
        weight = item.get("weight", 1)
        if type(weight) not in (int, float) or not math.isfinite(weight) or not 0 <= weight <= 1:
            raise ClientError(f"loras item {index} weight must be between 0 and 1.")
        if not isinstance(item.get("triggerWords", ""), str):
            raise ClientError(f"loras item {index} triggerWords must be a string.")
    body.setdefault("batchSize", 1)
    if body["batchSize"] not in (1, 4) or type(body["batchSize"]) is not int:
        raise ClientError("batchSize must be 1 or 4 (official values).")
    if "sampling" in body:
        sampling = body["sampling"]
        if not isinstance(sampling, dict) or set(sampling) - {"method", "steps", "cfgScale"}:
            raise ClientError("sampling may contain only method, steps, and cfgScale.")
        if "method" in sampling and sampling["method"] not in SAMPLERS:
            raise ClientError("sampling.method must be an official sampler name: " + ", ".join(SAMPLERS))
        if "steps" in sampling and (type(sampling["steps"]) is not int or not 1 <= sampling["steps"] <= 100):
            raise ClientError("sampling.steps must be an integer between 1 and 100.")
        if "cfgScale" in sampling and (type(sampling["cfgScale"]) not in (int, float) or not math.isfinite(sampling["cfgScale"])
                                       or sampling["cfgScale"] <= 0):
            raise ClientError("sampling.cfgScale must be a positive number.")
        if kind == "dit":
            notes.append("sampling is effective only on SDXL and SD v1 (official); it may have no effect on Tsubaki models")
    # Official default is enable (rewrites prompt before sending). Kit default is disable to preserve consistency with the text storyboard.
    body.setdefault("promptHelper", "disable")
    if body["promptHelper"] not in {"enable", "disable"}:
        raise ClientError("promptHelper must be enable or disable.")
    body.setdefault("seed", secrets.randbelow(4294967296))
    check_seed(body["seed"])
    notes += lora_notes(root, body["modelVersionId"], [str(item.get("modelId")) for item in loras])
    if kind is None:
        notes.append(f"modelVersionId is not in {MODELS_FILE}; mode and sampling support were not checked (register with scripts/pixai_models.py add)")
    return notes


def file_reference(root: Path, value, label: str) -> str:
    if not isinstance(value, str) or not value:
        raise ClientError(f"{label} must be a relative path to an image inside the project.")
    path = project_path(root, value)
    if not path.is_file() or image_kind(path.read_bytes()[:16]) is None:
        raise ClientError(f"Image for {label} not found (PNG, JPEG, or WebP): {value}")
    return value


def local_files(root: Path, params: dict) -> list[tuple[str, str]]:
    """Return project-local images inside v1 parameters (kit-specific fields) as (location, relative_path)."""
    found = []
    for key in LOCAL_FILE_KEYS:
        if key in params:
            found.append((key, file_reference(root, params[key], key)))
    for index, item in enumerate(params.get("controlNets") or []):
        if isinstance(item, dict) and "mediaFile" in item:
            found.append((f"controlNets[{index}].mediaFile", file_reference(root, item["mediaFile"], f"controlNets item {index + 1}")))
    adapter = params.get("ipAdapter")
    if isinstance(adapter, dict):
        for index, value in enumerate(adapter.get("referenceFiles") or []):
            found.append((f"ipAdapter.referenceFiles[{index}]", file_reference(root, value, f"ipAdapter reference image {index + 1}")))
    return found


def prepare_v1(root: Path, request: dict) -> tuple[list[str], list[str]]:
    params = request["parameters"]
    if not isinstance(params, dict):
        raise ClientError("parameters must be an object.")
    used_local = {k for k in params if k in LOCAL_FILE_KEYS}
    unknown = set(params) - V1_DOCUMENTED - V1_UNVERIFIED - set(LOCAL_FILE_KEYS)
    if unknown:
        raise ClientError("Unsupported v1 field(s): " + ", ".join(sorted(unknown)))
    for key, target in LOCAL_FILE_KEYS.items():
        if key in params and target in params:
            raise ClientError(f"{key} and {target} cannot be specified at the same time.")
    unverified = sorted((set(params) & V1_UNVERIFIED) | {LOCAL_FILE_KEYS[k] for k in used_local})
    notes = []
    check_id(params.get("modelId"), "modelId")
    if not isinstance(params.get("prompts"), str) or not params["prompts"].strip() or len(params["prompts"]) > 4096:
        raise ClientError("Set a generation prompt of at most 4096 characters in parameters.prompts.")
    for dimension in ("width", "height"):
        size = params.get(dimension)
        if type(size) is not int or not 512 <= size <= 1280:
            raise ClientError("Specify both v1 width and height as integers between 512 and 1280 (official).")
    lora = params.get("lora", {})
    if not isinstance(lora, dict) or len(lora) > 3:
        raise ClientError("v1 lora must be an object of at most 3 items ({versionId: weight}; official maxProperties).")
    notes += lora_notes(root, params["modelId"], list(lora))
    kind = model_type(params["modelId"], request)
    if params.get("controlNets") and not supports(params["modelId"], kind, "controlnet"):
        # Tsubaki.2 returns 403 "This model cannot be used with ControlNets." (2026-10-25). Others follow model page display.
        raise ClientError("This model cannot be used with ControlNet (Tsubaki.2 rejects with 403; first-gen Tsubaki and Hinata v2 list it as unsupported). "
                          "Use an SDXL model (such as haruka2).")
    # Verified on 2026-10-25 (Haruka v2 with regular artwork as input): canny and depth transferred composition; openpose had no effect; scribble ended in failed.
    for item in params.get("controlNets") or []:
        if isinstance(item, dict) and item.get("type") in ("openpose", "openpose_full", "dwpose"):
            notes.append("ControlNet openpose had no effect when given regular artwork (skeleton images unverified); use canny or depth to transfer composition")
        elif isinstance(item, dict) and item.get("type") == "scribble":
            notes.append("ControlNet scribble has been observed to end with task status failed (no image); use canny instead")
    if any(k in params for k in ("maskMediaId", "maskMediaUrl", "maskMediaFile")) and not supports(params["modelId"], kind, "inpaint"):
        # Tsubaki.2 returns 400 "This feature is not yet supported for this model" (2026-10-25).
        raise ClientError("This model does not support inpainting (Tsubaki.2 rejects with 400). Use tsubaki3 or an SDXL model.")
    if params.get("latentCouple") and kind == "dit":
        notes.append("latentCouple was accepted on Tsubaki.2 but had no effect (2026-10-25); use an SDXL model")
    for lora_id, weight in lora.items():
        check_id(lora_id, "lora versionId")
        if type(weight) not in (int, float) or not math.isfinite(weight) or not 0 <= weight <= 1:
            raise ClientError("lora weight must be between 0 and 1.")
    params.setdefault("batchSize", 1)
    if type(params["batchSize"]) is not int or not 1 <= params["batchSize"] <= 4:
        raise ClientError("v1 batchSize must be an integer between 1 and 4.")
    if "inferenceProfile" in params:
        if params["inferenceProfile"] not in MODES:
            raise ClientError("inferenceProfile must be one of " + " / ".join(MODES) + ".")
        kind = model_type(params["modelId"], request)
        if kind == "sdxl" or not supports(params["modelId"], kind, "mode"):
            raise ClientError("inferenceProfile (mode) is supported only on the Tsubaki.2 and Tsubaki.3 families.")
        check_mode(params["modelId"], params["inferenceProfile"], kind, notes)
    if "modelStyle" in params:
        style = params["modelStyle"]
        valid = isinstance(style, dict) and ((style.get("type") == "key" and set(style) == {"type", "keyId"} and isinstance(style["keyId"], str))
                                              or (style.get("type") == "custom" and set(style) == {"type", "custom"} and isinstance(style["custom"], str))
                                              or (style.get("type") == "styleKeyRef" and set(style) == {"type", "refId"} and isinstance(style["refId"], str)))
        if not valid:
            raise ClientError('modelStyle must be {"type": "key", "keyId": ...}, {"type": "custom", "custom": ...}, or {"type": "styleKeyRef", "refId": ...}.')
    if "upscale" in params and (type(params["upscale"]) not in (int, float) or not 1 <= params["upscale"] <= 2):
        raise ClientError("upscale must be between 1 and 2 (1 disables upscale; official docs recommend keeping the long edge within 2048px).")
    for flag in ("enableTile", "enableADetailer"):
        if flag in params and type(params[flag]) is not bool:
            raise ClientError(f"{flag} must be true or false.")
    helper = params.setdefault("promptHelper", {"enable": False})
    if not isinstance(helper, dict) or set(helper) - {"enable"} or type(helper.get("enable", False)) is not bool:
        raise ClientError('promptHelper must have the form {"enable": false}.')
    if "seed" in params:
        check_seed(params["seed"])
    if "strength" in params and (type(params["strength"]) not in (int, float) or not 0 < params["strength"] <= 1):
        raise ClientError("strength must be greater than 0 and at most 1.")
    for index, item in enumerate(params.get("controlNets") or []):
        if not isinstance(item, dict) or item.get("type") not in CONTROLNET_TYPES:
            raise ClientError(f"controlNets item {index + 1} type must be one of " + " / ".join(CONTROLNET_TYPES) + ".")
        if sum(k in item for k in ("mediaFile", "mediaId", "mediaUrl")) != 1:
            raise ClientError(f"controlNets item {index + 1} must specify an image using exactly one of mediaFile, mediaId, or mediaUrl.")
    if "controlNets" in params and not isinstance(params["controlNets"], list):
        raise ClientError("controlNets must be an array.")
    adapter = params.get("ipAdapter")
    if adapter is not None:
        if not isinstance(adapter, dict) or set(adapter) - {"enabled", "referenceImages", "referenceFiles"}:
            raise ClientError("ipAdapter may contain only enabled, referenceImages (array of mediaIds), and referenceFiles (project-local images).")
        if not (adapter.get("referenceImages") or adapter.get("referenceFiles")):
            raise ClientError("Specify at least one reference image in ipAdapter.")
    local_files(root, params)
    if any(k in params for k in ("mediaId", "mediaUrl", "mediaFile")) and "strength" not in params:
        notes.append("i2i strength is not specified; server default strength will be used")
    if params.get("enableTile") and not (params.get("upscale", 1) > 1 and any(k in params for k in ("mediaUrl", "mediaId", "mediaFile"))):
        notes.append("enableTile is effective only when a source image (mediaUrl) is provided and upscale > 1 (official)")
    return notes, unverified


def prepare_request(root: Path, relative: str) -> tuple[dict, list[str], list[str]]:
    return prepare_request_data(root, read_json(project_path(root, relative)))


def prepare_request_data(root: Path, request: dict) -> tuple[dict, list[str], list[str]]:
    """Validate request JSON and fill in defaults. Returns (request, notes, unverified_fields). Build the transmitted payload with send_payload."""
    api = request.get("api")
    if api == "v2":
        if set(request) - {"api", "body", "model_type"} or "body" not in request:
            raise ClientError('A v2 request must have the form {"api": "v2", "body": {...}} (model_type is an optional non-transmitted annotation).')
        return request, prepare_v2(root, request), []
    if api == "v1":
        if set(request) - {"api", "parameters", "model_type"} or "parameters" not in request:
            raise ClientError('A v1 request must have the form {"api": "v1", "parameters": {...}}.')
        notes, unverified = prepare_v1(root, request)
        return request, notes, unverified
    raise ClientError('Request JSON api must be "v2" (standard) or "v1" (i2i, reference images, Hires, etc.).')


def endpoint_of(request: dict) -> str:
    return "/v2/image/create" if request["api"] == "v2" else "/v1/task"


def batch_size(request: dict) -> int:
    return (request["body"] if request["api"] == "v2" else request["parameters"]).get("batchSize", 1)


def summary(request: dict) -> str:
    if request["api"] == "v2":
        body = request["body"]
        width, height = output_size(body)
        model = next((m["label"] for m in MODELS.values() if m["id"] == body["modelVersionId"]), body["modelVersionId"])
        extra = [f"mode {body['mode']}" if "mode" in body else None,
                 f"style {body['style'].get('key', 'custom')}" if "style" in body else None,
                 f"LoRA {len(body.get('loras', []))}" if body.get("loras") else None]
        return (f"v2 / {model} / {body['aspectRatio']} {body['size']} ({width}×{height}px) / {body['batchSize']} img / seed {body['seed']}"
                + "".join(" / " + e for e in extra if e))
    params = request["parameters"]
    model = next((m["label"] for m in MODELS.values() if m["id"] == params["modelId"]), params["modelId"])
    extra = [f"upscale {params['upscale']}" if params.get("upscale", 1) > 1 else None, "ADetailer" if params.get("enableADetailer") else None,
             "i2i" if any(k in params for k in ("mediaId", "mediaUrl", "mediaFile")) else None,
             f"ControlNet {len(params['controlNets'])}" if params.get("controlNets") else None,
             "IP-Adapter" if params.get("ipAdapter") else None, f"LoRA {len(params.get('lora', {}))}" if params.get("lora") else None]
    return (f"v1 / {model} / {params['width']}×{params['height']}px / {params['batchSize']} img"
            + (f" / seed {params['seed']}" if "seed" in params else "") + "".join(" / " + e for e in extra if e))


# ---------------------------------------------------------------- Uploads (reference and i2i images)

def read_uploads(root: Path) -> dict:
    path = root / UPLOADS
    try:
        data = json.loads(path.read_text(encoding="utf-8-sig")) if path.is_file() else {}
    except (OSError, ValueError):
        data = {}
    return data if isinstance(data, dict) else {}


def upload(root: Path, key: str, relative: str, reuse: bool = True) -> str:
    """Upload a project-local image via POST /v1/media/upload and return its mediaId. Reuses the recorded mediaId for identical content (SHA-256)."""
    path = project_path(root, relative)
    data = path.read_bytes()
    kind = image_kind(data[:16])
    if kind is None or kind[0] == "image/gif":
        raise ClientError(f"Uploadable image formats are PNG, JPEG, and WebP: {relative}")
    digest = hashlib.sha256(data).hexdigest()
    uploads = read_uploads(root)
    if reuse and isinstance(uploads.get(digest), dict) and re.fullmatch(r"[0-9]{1,30}", str(uploads[digest].get("mediaId", ""))):
        return uploads[digest]["mediaId"]
    result = api_json(key, "POST", "/v1/media/upload", payload=data, content_type=kind[0], timeout=180)
    media_id = str(result.get("id", ""))
    if not re.fullmatch(r"[0-9]{1,30}", media_id):
        raise ClientError("[Invalid API response] Upload response did not contain a mediaId.")
    uploads[digest] = {"mediaId": media_id, "file": relative, "uploadedAt": now()}
    (root / UPLOADS).parent.mkdir(parents=True, exist_ok=True)
    write_record(root / UPLOADS, uploads)
    return media_id


def send_payload(root: Path, key: str | None, request: dict) -> tuple[dict, dict]:
    """Return the payload to transmit and the mapping of replaced project-local images (path -> mediaId). When key is None, return the mapping without uploading."""
    if request["api"] == "v2":
        return dict(request["body"]), {}
    params = json.loads(json.dumps(request["parameters"]))
    replaced = {}

    def media(relative: str) -> str:
        if relative not in replaced:
            replaced[relative] = upload(root, key, relative) if key else "(upload on send)"
        return replaced[relative]

    for local, target in LOCAL_FILE_KEYS.items():
        if local in params:
            params[target] = media(params.pop(local))
    for item in params.get("controlNets") or []:
        if "mediaFile" in item:
            item["mediaId"] = media(item.pop("mediaFile"))
    adapter = params.get("ipAdapter")
    if isinstance(adapter, dict):
        files = adapter.pop("referenceFiles", [])
        adapter["referenceImages"] = list(adapter.get("referenceImages") or []) + [media(f) for f in files]
        adapter.setdefault("enabled", True)
    return {"parameters": params}, replaced


# ---------------------------------------------------------------- Cost confirmation & generation

def check_cost(args, request: dict, unverified: list[str]) -> None:
    if not args.cost_note or not args.cost_note.strip():
        raise ClientError("Execution requires --cost-note documenting the basis for cost confirmation (credits, membership plan, and permitted scope).")
    if not args.confirm_credits:
        raise ClientError("Credit consumption is unconfirmed. Pass --confirm-credits only when the user has explicitly authorized PixAI credit consumption. "
                          "Because no official API queries balance or cost, this script cannot verify zero-cost execution.")
    if unverified and not args.allow_unverified:
        raise ClientError("Request contains field(s) not in the current official documentation: " + ", ".join(unverified)
                          + ". These fields come from official client type definitions and their behavior/cost is unverified. Pass --allow-unverified only when testing them intentionally.")


def candidate_paths(first: Path, count: int) -> list[Path]:
    match = re.fullmatch(r"(.*?)(\d+)", first.stem)
    if count == 1:
        return [first]
    if not match:
        return [first.with_name(f"{first.stem}-{i + 1}.png") for i in range(count)]
    prefix, number = match.group(1), match.group(2)
    return [first.with_name(f"{prefix}{int(number) + i:0{len(number)}d}.png") for i in range(count)]


def record_path_for(output: Path) -> Path:
    return output.with_name(output.stem + ".pixai.json")


def wait_task(key: str, task_id: str, timeout: float, log=print) -> dict:
    """Poll GET /v1/task/{id} with increasing intervals. Retries up to 3 transient read errors (never resends generation)."""
    deadline = time.monotonic() + timeout
    interval, failures, last = 3.0, 0, None
    while True:
        time.sleep(interval)
        try:
            task = api_json(key, "GET", f"/v1/task/{task_id}", timeout=30)
            failures = 0
        except ClientError:
            failures += 1
            if failures >= 3:
                raise
            task = None
        if task is not None:
            status = task.get("status")
            if status != last:
                log(f"  Task {task_id}: {status}")
                last = status
            if status in TERMINAL:
                return task
        if time.monotonic() >= deadline:
            raise TimeoutError
        interval = min(interval * 1.3, 10.0)


def media_url(key: str, media_id: str) -> str | None:
    data = api_json(key, "GET", f"/v1/media/{media_id}", timeout=30)
    for item in data.get("urls") or []:
        if isinstance(item, dict) and item.get("variant") == "PUBLIC" and isinstance(item.get("url"), str):
            return item["url"]
    return None


def save_outputs(root: Path, key: str, task: dict, outputs: list[Path], record: dict) -> list[Path]:
    """Save images from a completed task in order. Record any slots that failed to save while preserving the rest."""
    found = task.get("outputs") or {}
    ids = found.get("mediaIds") or []
    urls = found.get("mediaUrls") or []
    saved, problems = [], []
    for index, output in enumerate(outputs):
        url = urls[index] if index < len(urls) and isinstance(urls[index], str) else None
        media_id = ids[index] if index < len(ids) and isinstance(ids[index], str) else None
        if output.exists():
            saved.append(output)
            continue
        try:
            if url is None and media_id:
                url = media_url(key, media_id)
            if url is None:
                raise ClientError("Image URL is missing (mediaUrls is null).")
            png, original = as_png(download(url))
            png_size(png)
            with output.open("xb") as stream:
                stream.write(png)
            record.setdefault("outputs", []).append({"path": output.relative_to(root).as_posix(), "mediaId": media_id,
                                                     "sha256": hashlib.sha256(png).hexdigest(), "originalType": original})
            saved.append(output)
        except ClientError as error:
            problems.append(f"{output.name}: {error}")
    record["missingOutputs"] = problems
    if len(ids) and len(ids) < len(outputs):
        record["missingOutputs"].append(f"Task produced {len(ids)} image(s) (requested {len(outputs)})")
    return saved


def finish(root: Path, key: str, task: dict, outputs: list[Path], record: dict, record_path: Path) -> list[Path]:
    status = task.get("status")
    record["task"] = {k: task.get(k) for k in ("id", "status", "createdAt", "startedAt", "endAt", "mediaSafetyLevel", "textSafetyLevel")
                      if task.get(k) is not None}
    if status != "completed":
        record.update(status=f"task-ended ({status}) / no-image", finishedAt=now())
        write_record(record_path, record)
        output = outputs[0]
        folder = reject_to_failed(root, output, record_path, f"PixAI ended the task with status {status} (no image)")
        raise ClientError(f"Task ended with status {status}. No image was produced. Moved record to {folder.relative_to(root).as_posix()}. "
                          "Check credit consumption on PixAI.")
    saved = save_outputs(root, key, task, outputs, record)
    if not saved:
        record.update(status="completed-save-failed (recoverable via taskId)", finishedAt=now())
        write_record(record_path, record)
        raise ClientError("Task completed but images could not be saved: " + " / ".join(record["missingOutputs"])
                          + ". Re-fetch with fetch (images are not stored indefinitely).")
    record.update(status="png-saved" if not record["missingOutputs"] else "partial-png-saved", finishedAt=now())
    write_record(record_path, record)
    if record["missingOutputs"]:
        raise ClientError(f"Saved {len(saved)} image(s), but some images could not be retrieved. Run fetch to retrieve the remaining outputs (does not resend generation).")
    return saved


def execute_generation(root: Path, request: dict, output_relative: str, args, unverified: list[str] | None = None,
                       log=print) -> list[Path]:
    """After cost confirmation, create a single task, wait for completion, and save images and the execution record. Never resends task creation."""
    unverified = unverified or []
    check_cost(args, request, unverified)
    key, source = load_key(root)
    if key in json.dumps(request, ensure_ascii=False) or key in args.cost_note:
        raise ClientError("Do not include credentials in requests or cost notes.")
    output = project_path(root, output_relative)
    if not output.is_relative_to(root / "output") or output.suffix.lower() != ".png":
        raise ClientError("Output must be a PNG under output/.")
    outputs = candidate_paths(output, batch_size(request))
    record_path = record_path_for(output)
    body_path = output.with_name(output.stem + ".request-body.json")
    readable_path = output.with_name(output.stem + ".request.json")
    if any(p.exists() for p in [*outputs, record_path, body_path, readable_path]):
        raise ClientError("An image or execution record with this name already exists. Check the record instead of resending.")
    output.parent.mkdir(parents=True, exist_ok=True)
    record = {"schemaVersion": 1, "status": "ready-to-send", "startedAt": now(), "api": request["api"],
              "endpoint": endpoint_of(request), "request": request, "credentialSource": source,
              "costMode": "credits_authorized", "costNote": args.cost_note, "unverifiedParameters": unverified,
              "reservedOutputs": [p.relative_to(root).as_posix() for p in outputs], "output": output.relative_to(root).as_posix(),
              "taskId": None, "actualCreditCost": None}
    with readable_path.open("x", encoding="utf-8") as stream:
        json.dump(request, stream, ensure_ascii=False, indent=2)
        stream.write("\n")
    # Block concurrent runs targeting the same output before sending.
    with record_path.open("x", encoding="utf-8") as stream:
        json.dump(record, stream, ensure_ascii=False, indent=2)
    try:
        body, uploaded = send_payload(root, key, request)
    except (ClientError, OSError) as error:
        record.update(status="upload-failed (task-not-created)", error=str(error)[:500], finishedAt=now())
        write_record(record_path, record)
        reject_to_failed(root, output, record_path, "Failed to upload reference / i2i image (no task created)")
        raise
    if uploaded:
        record["uploadedFiles"] = uploaded
        log("  Uploaded: " + ", ".join(f"{p} -> {m}" for p, m in uploaded.items()))
    try:
        payload = json.dumps(body, ensure_ascii=False, sort_keys=True, allow_nan=False).encode("utf-8")
        record["requestSha256"] = hashlib.sha256(payload).hexdigest()
        record["sentRequestFiles"] = {"body": body_path.relative_to(root).as_posix(), "readable": readable_path.relative_to(root).as_posix()}
        with body_path.open("xb") as stream:
            stream.write(payload)
        record["status"] = "sending"
        write_record(record_path, record)
        task = api_json(key, "POST", endpoint_of(request), payload=payload, timeout=120)
    except RejectedError:
        record.update(status="rejected (task-not-created)", finishedAt=now())
        write_record(record_path, record)
        reject_to_failed(root, output, record_path, "PixAI rejected the request without creating a task (HTTP 4xx)")
        raise
    except (ClientError, OSError, ValueError, TypeError):
        record["status"] = "incomplete-send-result-unknown (check PixAI generation history and credits before retrying)"
        try:
            write_record(record_path, record)
        except OSError:
            pass
        raise
    task_id = str(task.get("id", ""))
    if not re.fullmatch(r"[0-9]{1,30}", task_id):
        record["status"] = "incomplete-missing-taskId (check PixAI generation history and credits)"
        write_record(record_path, record)
        raise ClientError("[Invalid API response] Task creation response did not include an id. Check PixAI before retrying.")
    record.update(taskId=task_id, status="waiting", createdTask={k: task.get(k) for k in ("id", "status", "createdAt")})
    write_record(record_path, record)
    log(f"  Task created: {task_id} (waiting for completion; polling every 3s to 10s)")
    try:
        task = wait_task(key, task_id, getattr(args, "timeout", 900), log)
    except (TimeoutError, ClientError) as error:
        record["status"] = "interrupted-while-waiting (recoverable via taskId)"
        write_record(record_path, record)
        reason = "Timed out waiting for completion" if isinstance(error, TimeoutError) else str(error)
        raise ClientError(f"{reason}. Task {task_id} has already been created. Do not resend; retrieve it with fetch.") from None
    return finish(root, key, task, outputs, record, record_path)


def reject_to_failed(root: Path, output: Path, record_path: Path, note: str) -> Path:
    """Move an imageless transmission record to failed/ to free up the candidate number (without deleting)."""
    folder = output.parent / "failed" / f"{datetime.now():%Y%m%d-%H%M%S}-{output.stem}-{secrets.token_hex(3)}"
    folder.mkdir(parents=True)
    for path in output.parent.glob(output.stem + ".*"):
        if path.is_file() and path.name != output.name:
            path.replace(folder / path.name)
    write_record(folder / "moved.json", {"action": "rejected", "files": sorted(p.name for p in folder.iterdir()),
                                         "moved_at": datetime.now().isoformat(timespec="seconds"), "note": note})
    return folder


def fetch(root: Path, record_relative: str, log=print) -> list[Path]:
    """Query a task by the taskId in its execution record and save any unsaved images if completed. Never resends generation."""
    record_path = project_path(root, record_relative)
    if not record_path.name.endswith(".pixai.json") or not record_path.is_file():
        raise ClientError("Specify a candidate folder rNNN.pixai.json file to re-fetch.")
    record = read_json(record_path)
    task_id = str(record.get("taskId") or "")
    if not re.fullmatch(r"[0-9]{1,30}", task_id):
        raise ClientError("This record has no taskId (the creation response was not received). Check generation history and credits on PixAI, "
                          "and move it to failed/ with move-unknown if no image was created.")
    outputs = [project_path(root, p) for p in record.get("reservedOutputs") or [record["output"]]]
    key, _ = load_key(root)
    task = api_json(key, "GET", f"/v1/task/{task_id}", timeout=30)
    log(f"  Task {task_id}: {task.get('status')}")
    if task.get("status") not in TERMINAL:
        raise ClientError(f"Task is still {task.get('status')}. Wait a moment and run fetch again.")
    record["refetchedAt"] = now()
    return finish(root, key, task, outputs, record, record_path)


def run(args, root: Path) -> None:
    if args.command in {"key-status", "status"}:
        key, source = load_key(root)
        print("Key loaded (value hidden): " + source)
        if args.command == "status":
            print(auth_check(key))
            print("No official API endpoint queries credit balance or consumption. Check your credits on the PixAI screen.")
        return
    if args.command == "fetch":
        for path in fetch(root, args.record):
            print("Saved: " + path.relative_to(root).as_posix())
        return
    if args.command == "upload":
        if not args.execute:
            file_reference(root, args.file, "--file")
            print("Not sent. Uploading requires --execute (sends the image to PixAI).")
        else:
            key, _ = load_key(root)
            print("mediaId: " + upload(root, key, args.file, not args.no_reuse))
        return
    request, notes, unverified = prepare_request(root, args.request)
    print("Request: " + summary(request))
    for note in notes:
        print("  [Note] " + note)
    if unverified:
        print("  [Unverified fields] " + ", ".join(unverified) + " (requires --allow-unverified to send)")
    if not args.execute:
        print("Not sent. Execution requires --execute and cost confirmation flags.")
        return
    for path in execute_generation(root, request, args.output, args, unverified):
        print("Saved: " + path.relative_to(root).as_posix())
    print("Actual credit consumption is unverified; actualCreditCost remains null in the execution record.")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, epilog=KEY_SETUP_GUIDE, formatter_class=argparse.RawDescriptionHelpFormatter)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("key-status", help="Check only the key source (no network)", epilog=KEY_SETUP_GUIDE,
                        formatter_class=argparse.RawDescriptionHelpFormatter)
    commands.add_parser("status", help="Verify connection and authentication (no image generation)", epilog=KEY_SETUP_GUIDE,
                        formatter_class=argparse.RawDescriptionHelpFormatter)
    generate = commands.add_parser("generate", help="Single-task generation (dry-run validation by default)")
    generate.add_argument("--request", required=True, help="Generation request JSON inside the project")
    generate.add_argument("--output", default="output/pixai/test-001.png")
    generate.add_argument("--execute", action="store_true", help="Send a user-requested generation once")
    generate.add_argument("--confirm-credits", action="store_true", help="User has explicitly authorized credit consumption for these settings")
    generate.add_argument("--allow-unverified", action="store_true", help="User has agreed to test fields not in current official docs (i2i, reference images, etc.)")
    generate.add_argument("--cost-note", help="Verification method, timestamp, and authorized scope (do not include credentials)")
    generate.add_argument("--timeout", type=float, default=900, help="Maximum time to wait for completion (seconds)")
    again = commands.add_parser("fetch", help="Re-fetch results by taskId from an execution record (does not resend generation)")
    again.add_argument("--record", required=True, help="Candidate folder rNNN.pixai.json")
    send = commands.add_parser("upload", help="Upload a project-local image and print its mediaId")
    send.add_argument("--file", required=True)
    send.add_argument("--execute", action="store_true")
    send.add_argument("--no-reuse", action="store_true", help="Upload again even if a record for the same image exists")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    try:
        if not (root / "project.json").is_file():
            raise ClientError("Create and open a manga project first, then run the project's scripts.")
        run(args, root)
    except ClientError as error:
        print("Error: " + str(error), file=sys.stderr)
        return 1
    except (OSError, ValueError, UnicodeError):
        print("Error: Failed to process file or configuration. Keys and raw responses are hidden; check the execution record.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
