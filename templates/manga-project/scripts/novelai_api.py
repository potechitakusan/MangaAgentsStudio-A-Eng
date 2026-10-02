"""Load a NovelAI key, check the subscription, and generate one image. Python 3.10+, no extra dependencies."""

from __future__ import annotations

import argparse
import base64
import binascii
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
from urllib.error import HTTPError, URLError
from urllib.request import HTTPRedirectHandler, Request, build_opener
import zipfile
import zlib


# Pin the authentication-header destination. Do not follow redirects.
API_ROOT = "https://image.novelai.net"
MAX_RESPONSE = 64 * 1024 * 1024
KEY_FILES = (".secrets/novelai.env", ".secrets/.env", ".env")
KEY_SETUP_GUIDE = (
    "Add this line to the project file .secrets/novelai.env:\n"
    "NOVELAI_API_KEY=YOUR_ACTUAL_TOKEN\n"
    "NOVELAI_API_KEY on the left is a public setting name. The token on the right is secret.\n"
    "Replace the right side with your Persistent API token, without Bearer. Do not enter a token-only line.\n"
    "Do not paste the actual value in conversation. After setup, key-status checks its source."
)
PLAIN_PARAMETERS = {
    "width", "height", "steps", "n_samples", "seed", "sampler", "scale",
    "negative_prompt", "noise_schedule", "params_version", "cfg_rescale",
    "qualityToggle", "ucPreset", "sm", "sm_dyn", "dynamic_thresholding",
    "legacy", "legacy_v3_extend", "deliberate_euler_ancestral_bug",
    "prefer_brownian", "skip_cfg_above_sigma", "v4_prompt", "v4_negative_prompt",
    "image_format", "prompt", "tag_hint_qt", "tag_hint_uc_preset",
    "tag_hint_transparent_background", "straight_alpha",
}


class ClientError(Exception):
    """User-facing error without keys, input bodies, or HTTP response bodies."""


def project_path(root: Path, relative: str) -> Path:
    path = Path(relative)
    if path.is_absolute() or path.drive or ".." in path.parts:
        raise ClientError("Use a relative path inside the project root.")
    resolved = (root / path).resolve()
    if not resolved.is_relative_to(root):
        raise ClientError("Links resolving outside the project are not allowed.")
    return resolved


def read_json(path: Path) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, UnicodeError, ValueError):
        raise ClientError("Cannot read JSON. Check its location and format.") from None
    if not isinstance(value, dict):
        raise ClientError("The top-level JSON value must be an object.")
    return value


def load_key(root: Path) -> tuple[str, str]:
    value = os.environ.get("NOVELAI_API_KEY", "").strip()
    source = "Environment variable NOVELAI_API_KEY"
    diagnostics = [source + (": Empty value" if "NOVELAI_API_KEY" in os.environ else ": Not configured")]

    def invalid(location: str, reason: str) -> ClientError:
        # Use only a fixed source location, never input lines, secrets, or exception contents.
        return ClientError(f"[Configuration error] {location}: {reason}\n{KEY_SETUP_GUIDE}")

    if not value:
        for relative in KEY_FILES:
            path = project_path(root, relative)
            if not path.exists():
                diagnostics.append(relative + ": File not found")
                continue
            if not path.is_file():
                raise invalid(relative, "Invalid format (not a regular configuration file)")
            try:
                lines = path.read_text(encoding="utf-8-sig").splitlines()
            except UnicodeError:
                raise invalid(relative, "Invalid format (not readable as UTF-8 text)") from None
            except OSError:
                raise invalid(relative, "Read failed (check file permissions)") from None
            matches = []
            for line in lines:
                match = re.match(r"^\s*(?:export\s+)?NOVELAI_API_KEY\s*=\s*(.*?)\s*$", line)
                if not match and re.match(r"^\s*(?:export\s+)?NOVELAI_API_KEY\b", line):
                    raise invalid(relative, "Invalid format (separate setting name and value with ASCII =)")
                if match:
                    candidate = match.group(1)
                    if candidate.startswith(("'", '"')):
                        quote = candidate[0]
                        end = candidate.find(quote, 1)
                        if end < 0 or (candidate[end + 1:].strip() and not candidate[end + 1:].lstrip().startswith("#")):
                            raise invalid(relative, "Invalid format (unclosed quotes or extra trailing characters)")
                        candidate = candidate[1:end]
                    else:
                        candidate = "" if candidate.startswith("#") else re.split(r"\s+#", candidate, maxsplit=1)[0].strip()
                    matches.append(candidate)
            if len(matches) > 1:
                raise invalid(relative, "Invalid format (duplicate NOVELAI_API_KEY lines)")
            if not matches:
                diagnostics.append(relative + ": Missing setting (a NOVELAI_API_KEY= line is required)")
            elif not matches[0].strip():
                diagnostics.append(relative + ": Empty value (token required after =)")
            else:
                value, source = matches[0], relative
                break
    if not value:
        raise ClientError("[Configuration error] No readable key was found.\n"
                          + "\n".join(diagnostics) + "\n" + KEY_SETUP_GUIDE)
    # Do not output values or lengths. No dotenv variable expansion or command execution.
    if not re.fullmatch(r"[A-Za-z0-9._~+/=-]+", value) or value.lower() in {"your_api_key", "your_token", "replace_me"}:
        raise invalid(source, "Invalid format (invalid characters, whitespace, or an unreplaced example value)")
    return value, source


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def api_request(key: str, endpoint: str, *, payload: bytes | None = None,
                correlation_id: str | None = None) -> tuple[bytes, str]:
    if endpoint not in {"/user/subscription", "/ai/generate-image"}:
        raise ClientError("Unsupported API.")
    headers = {"Authorization": "Bearer " + key, "Accept": "application/json",
               "User-Agent": "MangaAgentsStudio-NovelAI/1"}
    if payload is not None:
        headers["Content-Type"] = "application/json"
    if correlation_id:
        headers["x-correlation-id"] = correlation_id
    request = Request(API_ROOT + endpoint, data=payload, headers=headers)
    retry_note = ("No image generation was requested. No automatic retry was made." if payload is None else
                  "No automatic retry was made. Check generation results and consumption before retrying.")
    try:
        with build_opener(NoRedirect()).open(request, timeout=180 if payload else 30) as response:
            body = response.read(MAX_RESPONSE + 1)
            content_type = response.headers.get_content_type()
    except HTTPError as error:
        status = error.code
        error.close()
        explanations = {
            401: "[Authentication failed] The request was not authenticated. Check the key source and token validity.",
            402: "[Insufficient balance] Not enough Anlas.",
            403: "[Access denied] The server rejected the request. This does not prove the key is wrong. Check access rights and connection restrictions.",
            429: "[Usage limit] The usage limit was reached.",
        }
        fallback = "[Server error] The remote server encountered an error." if status >= 500 else "[API response error] The request could not be completed."
        raise ClientError(f"HTTP {status}: " + explanations.get(status, fallback) + " " + retry_note) from None
    except (URLError, OSError, HTTPException):
        raise ClientError("[Connection failure] API communication did not complete after loading the key. "
                          "This result alone does not establish whether the key is valid. "
                          "Check network, proxy, and execution-environment connection restrictions. " + retry_note) from None
    if len(body) > MAX_RESPONSE:
        raise ClientError("API response exceeded the storage limit. Check results and consumption before regenerating.")
    return body, content_type


def subscription(key: str) -> dict:
    body, _ = api_request(key, "/user/subscription")
    try:
        data = json.loads(body)
    except (ValueError, UnicodeError):
        raise ClientError("[Invalid API response] Subscription response is not JSON. This is distinct from a missing key.") from None
    if not isinstance(data, dict) or type(data.get("active")) is not bool or type(data.get("tier")) is not int:
        raise ClientError("[Invalid API response] Unrecognized subscription response format. This is distinct from a missing key.")
    # Never display or save email addresses, payment information, or undefined response fields.
    safe = {"active": data["active"], "tier": data["tier"]}
    if type(data.get("expiresAt")) is int:
        safe["expiresAt"] = data["expiresAt"]
    steps = data.get("trainingStepsLeft")
    if isinstance(steps, dict):
        safe["trainingStepsLeft"] = {name: steps[name] for name in
                                     ("fixedTrainingStepsLeft", "purchasedTrainingSteps")
                                     if type(steps.get(name)) is int}
    usage = data.get("usage")
    if isinstance(usage, dict):
        safe["usage"] = {name: usage[name] for name in ("percent", "timeUntilNextPercent")
                         if type(usage.get(name)) is int}
        if type(usage.get("isNegative")) is bool:
            safe["usage"]["isNegative"] = usage["isNegative"]
    return safe


def prepare_request(root: Path, relative: str) -> tuple[dict, bytes]:
    return prepare_request_data(root, read_json(project_path(root, relative)))


def prepare_request_data(root: Path, request: dict) -> tuple[dict, bytes]:
    if set(request) != {"action", "input", "model", "parameters"} or request.get("action") != "generate":
        raise ClientError("The request must contain exactly action=generate, input, model, and parameters.")
    if not isinstance(request["input"], str) or not request["input"].strip():
        raise ClientError("Set the generation prompt in input.")
    if not isinstance(request["model"], str) or not re.fullmatch(r"nai-diffusion-[a-z0-9.-]+", request["model"]):
        raise ClientError("Set model to an ID verified against official specifications.")
    params = request["parameters"]
    if not isinstance(params, dict):
        raise ClientError("parameters must be an object.")
    if "width" in params or "height" in params:
        # Generate assets beyond panel bounds; show selected areas with panel frames and masks.
        # Prefer request dimensions; they need not match full-page generation dimensions.
        for dimension in ("width", "height"):
            size = params.get(dimension)
            if type(size) is not int or size < 64 or size % 64:
                raise ClientError("Request width and height must both be multiples of 64, at least 64.")
    else:
        layout = read_json(root / "config/page-layout.json")
        canvas = layout.get("generationCanvas")
        if not isinstance(canvas, dict):
            raise ClientError("Specify width and height in the request or set generationCanvas in config/page-layout.json.")
        for dimension in ("width", "height"):
            size = canvas.get(dimension)
            if type(size) is not int or size < 64 or size % 64:
                raise ClientError("Requested dimensions must be multiples of 64, at least 64.")
            params[dimension] = size
    params.setdefault("n_samples", 1)
    if type(params["n_samples"]) is not int or params["n_samples"] != 1:
        raise ClientError("Generate exactly one image per request.")
    params.setdefault("steps", 23 if request["model"].startswith("nai-diffusion-5") else 28)
    if type(params["steps"]) is not int or not 1 <= params["steps"] <= 50:
        raise ClientError("steps must be an integer from 1 to 50. The Opus default is at most 28.")
    params.setdefault("image_format", "png")
    if params["image_format"] != "png":
        raise ClientError("Only PNG output is supported.")
    if type(params.get("seed")) is not int or not 0 <= params["seed"] <= 4294967295:
        raise ClientError("Fix seed to an integer from 0 to 4294967295.")
    if not isinstance(params.get("sampler"), str) or not params["sampler"].strip():
        raise ClientError("Set a sampler verified against official specifications.")
    if type(params.get("scale")) not in (int, float) or not math.isfinite(params["scale"]) or params["scale"] <= 0:
        raise ClientError("scale must be a positive finite number.")
    if request["model"].startswith(("nai-diffusion-4", "nai-diffusion-5")):
        params.setdefault("v4_prompt", {"caption": {"base_caption": request["input"], "char_captions": []},
                                        "use_coords": False, "use_order": True})
        params.setdefault("v4_negative_prompt", {"caption": {"base_caption": params.get("negative_prompt", ""),
                                                            "char_captions": []}})
    try:
        payload = json.dumps(request, ensure_ascii=False, sort_keys=True, allow_nan=False).encode("utf-8")
    except (ValueError, TypeError):
        raise ClientError("The request contains a value that cannot be transmitted as JSON.") from None
    return request, payload


def check_cost(args, request: dict) -> None:
    if not args.cost_note or not args.cost_note.strip():
        raise ClientError("Execution requires --cost-note documenting cost verification for every setting in this run.")
    if not (args.confirm_zero_anlas or args.allow_anlas):
        raise ClientError("Cost unverified. Verify 0 Anlas or obtain explicit user authorization for paid use.")
    if args.confirm_zero_anlas:
        params = request["parameters"]
        if params["steps"] > 28 or params["width"] * params["height"] > 1048576:
            raise ClientError("This request exceeds the dimensions/steps eligible as Opus zero-consumption candidates in this kit.")
        if set(params) - PLAIN_PARAMETERS:
            raise ClientError("Extra features or unverified parameters prevent sending this as zero-consumption generation.")
        if request["model"].startswith("nai-diffusion-5") and not args.confirm_v5_allowance:
            raise ClientError("V5 also requires verification of sufficient Opus allowance for this generation.")


def image_bytes(body: bytes, content_type: str) -> bytes:
    try:
        if content_type in {"application/zip", "application/x-zip-compressed"} or body.startswith(b"PK\x03\x04"):
            # Extract one PNG in memory without using archive paths.
            with zipfile.ZipFile(BytesIO(body)) as archive:
                members = [item for item in archive.infolist() if not item.is_dir() and item.filename.lower().endswith(".png")]
                if len(members) != 1 or members[0].file_size > MAX_RESPONSE:
                    raise ClientError("Unexpected PNG count or size in the generation response.")
                return archive.read(members[0])
        data = json.loads(body)
        images = data.get("images") if isinstance(data, dict) else None
        if not isinstance(images, list) or len(images) != 1 or not isinstance(images[0], dict):
            raise ClientError("Unrecognized images format in the generation response.")
        return base64.b64decode(images[0]["image"], validate=True)
    except (ValueError, TypeError, KeyError, binascii.Error, zipfile.BadZipFile, RuntimeError, NotImplementedError):
        raise ClientError("Cannot extract PNG from the response. No automatic regeneration was made.") from None


def png_size(data: bytes) -> tuple[int, int]:
    if len(data) < 33 or data[:16] != b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR":
        raise ClientError("Generated result is not PNG.")
    width, height = struct.unpack(">II", data[16:24])
    if not width or not height:
        raise ClientError("Invalid generated PNG dimensions.")
    offset, has_pixels = 8, False
    while offset + 12 <= len(data):
        length = struct.unpack(">I", data[offset:offset + 4])[0]
        end = offset + 12 + length
        if end > len(data):
            break
        kind = data[offset + 4:offset + 8]
        expected = struct.unpack(">I", data[end - 4:end])[0]
        if zlib.crc32(data[offset + 4:end - 4]) & 0xFFFFFFFF != expected:
            raise ClientError("Generated PNG CRC mismatch. No automatic regeneration was made.")
        has_pixels = has_pixels or kind == b"IDAT"
        if kind == b"IEND":
            if length == 0 and end == len(data) and has_pixels:
                return width, height
            break
        offset = end
    raise ClientError("Generated PNG is truncated or structurally invalid.")


def write_record(path: Path, data: dict) -> None:
    temporary = path.with_suffix(".tmp")
    with temporary.open("x", encoding="utf-8") as stream:
        json.dump(data, stream, ensure_ascii=False, indent=2)
        stream.write("\n")
    temporary.replace(path)


def run(args, root: Path) -> None:
    if args.command in {"key-status", "status"}:
        key, source = load_key(root)
        print("Key loaded (value hidden): " + source)
        if args.command == "status":
            result = subscription(key)
            print("Subscription lookup succeeded (no image generation).")
            print(json.dumps(result, ensure_ascii=False, indent=2))
            print("Subscription lookup alone does not verify generation cost or remaining V5 allowance.")
        return
    request, payload = prepare_request(root, args.request)
    digest = hashlib.sha256(payload).hexdigest()
    params = request["parameters"]
    print(f"Request: {request['model']} / {params['width']}×{params['height']}px / {params['steps']} steps / one image")
    print("Request SHA-256: " + digest)
    if not args.execute:
        print("Not sent. Execution requires --execute and cost confirmation.")
        return
    execute_generation(root, request, payload, args.output, args)


def execute_generation(root: Path, request: dict, payload: bytes, output_relative: str, args) -> Path:
    """Send once after cost/subscription checks; save PNG and execution record. Never retry automatically."""
    digest = hashlib.sha256(payload).hexdigest()
    check_cost(args, request)
    key, source = load_key(root)
    # Do not send or save keys accidentally pasted into requests or cost notes.
    if key in payload.decode("utf-8") or key in args.cost_note:
        raise ClientError("Do not include credentials in requests or cost notes.")
    state = subscription(key)
    if args.confirm_zero_anlas and (state["active"] is not True or state["tier"] != 3):
        raise ClientError("Stopped zero-consumption generation because an active Opus subscription could not be verified.")
    if args.confirm_zero_anlas and request["model"].startswith("nai-diffusion-5"):
        usage = state.get("usage", {})
        if usage.get("isNegative") is True or ("percent" in usage and usage["percent"] <= 0):
            raise ClientError("Subscription lookup indicates insufficient V5 allowance. Wait for recovery.")
    output = project_path(root, output_relative)
    if not output.is_relative_to(root / "output") or output.suffix.lower() != ".png":
        raise ClientError("Output must be a PNG under output/.")
    record_path = output.with_suffix(".novelai.json")
    if output.exists() or record_path.exists() or record_path.with_suffix(".tmp").exists():
        raise ClientError("An image or execution record already exists with this name. Check the record instead of resending.")
    output.parent.mkdir(parents=True, exist_ok=True)
    correlation_id = "".join(secrets.choice("abcdefghijklmnopqrstuvwxyz0123456789") for _ in range(6))
    record = {"schemaVersion": 1, "status": "ready-to-send", "startedAt": datetime.now(timezone.utc).isoformat(),
              "correlationId": correlation_id, "requestSha256": digest, "request": request,
              "credentialSource": source, "subscriptionBefore": state,
              "costMode": "zero_anlas_confirmed" if args.confirm_zero_anlas else "paid_authorized",
              "costNote": args.cost_note, "v5AllowanceConfirmed": args.confirm_v5_allowance,
              "actualAnlasCost": None, "output": output.relative_to(root).as_posix()}
    # Stop concurrent runs targeting the same output before sending.
    with record_path.open("x", encoding="utf-8") as stream:
        json.dump(record, stream, ensure_ascii=False, indent=2)
    try:
        body, content_type = api_request(key, "/ai/generate-image", payload=payload, correlation_id=correlation_id)
        png = image_bytes(body, content_type)
        width, height = png_size(png)
        with output.open("xb") as stream:
            stream.write(png)
        record.update(status="png-saved", actualCanvas={"width": width, "height": height},
                      finishedAt=datetime.now(timezone.utc).isoformat())
        write_record(record_path, record)
    except (ClientError, OSError):
        record["status"] = "incomplete-check-result-and-consumption-before-retry"
        try:
            write_record(record_path, record)
        except OSError:
            pass
        raise
    print("Saved: " + output.relative_to(root).as_posix())
    print(f"Actual generation: {width}×{height}px. Apply to frames and final PNG according to page settings.")
    print("Actual Anlas consumption is unverified; actualAnlasCost remains null in the execution record.")
    return output


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, epilog=KEY_SETUP_GUIDE,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("key-status", help="Check only the key source (no network)",
                        epilog=KEY_SETUP_GUIDE, formatter_class=argparse.RawDescriptionHelpFormatter)
    commands.add_parser("status", help="Look up subscription (no generation)",
                        epilog=KEY_SETUP_GUIDE, formatter_class=argparse.RawDescriptionHelpFormatter)
    generate = commands.add_parser("generate", help="Generate one image; default is an unsent request check")
    generate.add_argument("--request", required=True, help="Generation request JSON inside the project")
    generate.add_argument("--output", default="output/novelai/test-001.png")
    generate.add_argument("--execute", action="store_true", help="Send a human-requested generation once")
    costs = generate.add_mutually_exclusive_group()
    costs.add_argument("--confirm-zero-anlas", action="store_true", help="All settings for this run verified as 0 Anlas")
    costs.add_argument("--allow-anlas", action="store_true", help="User explicitly authorized Anlas consumption for these settings")
    generate.add_argument("--confirm-v5-allowance", action="store_true", help="Verified sufficient allowance for this V5 generation")
    generate.add_argument("--cost-note", help="Verification method, date/time, and authorized scope; never credentials")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    try:
        if not (root / "project.json").is_file():
            raise ClientError("Create and reopen a work project, then use its script.")
        run(args, root)
    except ClientError as error:
        print("Error:" + str(error), file=sys.stderr)
        return 1
    except (OSError, ValueError, UnicodeError):
        print("Error: File or configuration processing failed. Keys and response bodies are hidden. Check the execution record.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
