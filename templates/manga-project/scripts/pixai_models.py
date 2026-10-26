"""Display the PixAI model catalog (config/pixai-models.json) and register models or LoRAs from their PixAI page URLs.

  python -X utf8 scripts/pixai_models.py list                                   # List registered models (no network)
  python -X utf8 scripts/pixai_models.py info --url <model-page-URL>            # Show versionId, type, and terms of use (does not register)
  python -X utf8 scripts/pixai_models.py add <name> --url <model-page-URL>      # Register into the project's model catalog
  python -X utf8 scripts/pixai_models.py lora --url <LoRA-page-URL>             # Record a LoRA's base model and terms of use in the project

LoRA records (config/pixai-loras.json) are cached once fetched (pass --refresh to re-fetch).
pixai_api.py uses only this local record during pre-send validation to check LoRA and generation model compatibility (no network).

The URL can be https://pixai.art/model/<modelId>, a version tab URL https://pixai.art/model/<modelId>/<versionId>,
or just the numeric modelId. If no version is specified, the latest version shown on the page is used.
Performs only a single GET request to the public model page (never sends API keys, logs in, generates images, or consumes credits).
Embedded page data is not an official PixAI API; if the page format changes and cannot be parsed, ask the user to copy the URL
after clicking the version tab on the model page and pass --model-version-id and --model-type to pixai_compose.py.
"""
from __future__ import annotations

import argparse
from datetime import date
import json
from pathlib import Path
import re
import sys
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

sys.path.insert(0, str(Path(__file__).resolve().parent))
import pixai_api as api  # noqa: E402

PAGE_ROOT = "https://pixai.art"
MAX_PAGE = 8 * 1024 * 1024
MODEL_URL = re.compile(r"(?:https://pixai\.art(?:/[a-z]{2}(?:-[A-Za-z]{2,4})?)?/model/)?([0-9]{6,30})(?:-[^/?#]*)?(?:/([0-9]{6,30}))?/?(?:[?#].*)?")
NAME = re.compile(r"[a-z0-9][a-z0-9.-]{0,40}")


class ModelError(Exception):
    pass


def parse_url(value: str) -> tuple[str, str | None]:
    match = MODEL_URL.fullmatch(value.strip())
    if not match:
        raise ModelError("Specify https://pixai.art/model/<modelId>[/<versionId>] or a numeric modelId.")
    return match.group(1), match.group(2)


def fetch_page(model_id: str, version_id: str | None) -> str:
    url = f"{PAGE_ROOT}/model/{model_id}" + (f"/{version_id}" if version_id else "")
    request = Request(url, headers={"User-Agent": "MangaAgentsStudio-PixAI/1", "Accept": "text/html"})
    try:
        with urlopen(request, timeout=30) as response:
            body = response.read(MAX_PAGE + 1)
    except HTTPError as error:
        raise ModelError(f"Could not fetch model page (HTTP {error.code}). Check the URL and whether the model is public.") from None
    except (URLError, OSError):
        raise ModelError("Could not connect to the model page. Check your network and environment connection restrictions.") from None
    if len(body) > MAX_PAGE:
        raise ModelError("Model page is larger than expected and will not be read.")
    return body.decode("utf-8", errors="replace")


def page_data(html: str) -> dict:
    """Reconstruct React Router turbo-stream data (an array of cross-referenced indexed entries)."""
    match = re.search(r'streamController\.enqueue\((".*?")\);', html, re.S)
    if not match:
        raise ModelError("The page format may have changed (embedded data not found). "
                         "Ask the user to copy the URL after clicking the version tab on the model page.")
    flat = json.loads(json.loads(match.group(1)))
    memo: dict[int, object] = {}

    def hydrate(index):
        if not isinstance(index, int) or index < 0:
            return None
        if index in memo:
            return memo[index]
        value = flat[index]
        if isinstance(value, dict):
            out: dict = {}
            memo[index] = out
            for key, item in value.items():
                name = flat[int(key[1:])] if key.startswith("_") else key
                out[name] = hydrate(item) if isinstance(item, int) else item
            return out
        if isinstance(value, list):
            out_list: list = []
            memo[index] = out_list
            if value and isinstance(value[0], str) and value[0] in ("D", "P", "S", "Y", "R", "E"):
                return value  # Special tagged values such as dates are not needed
            out_list.extend(hydrate(item) if isinstance(item, int) else item for item in value)
            return out_list
        return value

    root = hydrate(0)
    for data in (root or {}).get("loaderData", {}).values():
        if isinstance(data, dict) and isinstance(data.get("generationModel"), dict):
            return data
    raise ModelError("Model information was not found on the page. Check that the URL points to a model page.")


def model_info(html: str, version_id: str | None) -> dict:
    data = page_data(html)
    model = data["generationModel"]
    version = data.get("generationModelVersion") if version_id else model.get("latestAvailableVersion")
    if not isinstance(version, dict) or (version_id and version.get("id") != version_id):
        raise ModelError("The specified version was not found on the page. Use the URL from clicking the version tab.")
    extra = model.get("extra") if isinstance(model.get("extra"), dict) else {}
    vextra = version.get("extra") if isinstance(version.get("extra"), dict) else {}
    compat = vextra.get("compatibility") if isinstance(vextra.get("compatibility"), dict) else {}
    permissions = extra.get("permissions") if isinstance(extra.get("permissions"), dict) else {}
    return {"title": model.get("title"), "modelId": model.get("id"), "id": version.get("id"), "versionName": version.get("name"),
            "pixaiType": model.get("type") or "", "status": version.get("status"), "permittedUse": model.get("permittedUse"),
            "permissions": permissions, "isNsfw": model.get("isNsfw"), "negativePrompt": compat.get("negativePrompt", True),
            "loraBaseModelType": version.get("loraBaseModelType"), "loraBaseModelId": version.get("loraBaseModelId"), "triggerWords": vextra.get("triggerWords") or extra.get("triggerWords") or ""}


def catalog_entry(info: dict) -> dict:
    """Build a catalog entry from page info. Determines mode and style support from the official rule (Tsubaki.2 / Tsubaki.3 families only)."""
    kind = info["pixaiType"]
    if "LORA" in kind:
        raise ModelError(f"This is a LoRA ({kind}). Put version ID {info['id']} into PIXAI_LORA_... in .env.pixai.")
    if kind == "SDXL_MODEL":
        entry = {"type": "sdxl", "mode": False, "style": False}
    elif kind.startswith("MMDIT26"):  # Tsubaki.2 (MMDIT26A) and Tsubaki.3 (MMDIT26B) families
        entry = {"type": "dit", "mode": True, "style": True}
    elif "DIT" in kind:
        entry = {"type": "dit", "mode": False, "style": False}
    else:
        raise ModelError(f"Unsupported type for an image generation base model ({kind or 'unknown'}).")
    commercial = info["permittedUse"] == "COMMERCIAL" or bool(info["permissions"].get("commercialUses"))
    return {"label": f"{info['title']} {info['versionName']}".strip(), "modelId": info["modelId"], "id": info["id"],
            "versionName": info["versionName"], "pixaiType": kind, **entry, "negativePrompt": bool(info["negativePrompt"]),
            "commercialUse": commercial, "permissions": info["permissions"], "api": "unverified", "checked_on": date.today().isoformat(),
            "strengths_ja": "Registered from model page (pixai_models.py add)"}


def show(info: dict) -> None:
    perms = info["permissions"]
    print(f"Model: {info['title']} (modelId {info['modelId']}, type {info['pixaiType']})")
    print(f"Version: {info['versionName']} (versionId {info['id']}, status {info['status']})")
    print("Terms of use: " + ("commercial allowed" if info["permittedUse"] == "COMMERCIAL" or perms.get("commercialUses") else "non-commercial")
          + " / online sharing " + ("allowed" if perms.get("shareImagesOnline") else "unknown/disallowed")
          + (" / author credit required" if perms.get("shouldCreditAuthor") else "")
          + (" / NSFW" if info["isNsfw"] else ""))
    if "LORA" in info["pixaiType"]:
        print(f"LoRA base model type: {info['loraBaseModelType'] or 'unknown'}. Trigger words: {info['triggerWords'] or 'none'}")


def lora_record(info: dict) -> dict:
    if "LORA" not in info["pixaiType"]:
        raise ModelError(f"This is not a LoRA ({info['pixaiType'] or 'unknown type'}). Register base models with add.")
    perms = info["permissions"]
    return {"title": f"{info['title']} {info['versionName']}".strip(), "modelId": info["modelId"], "versionName": info["versionName"],
            "pixaiType": info["pixaiType"], "baseModelType": info["loraBaseModelType"], "baseModelId": info["loraBaseModelId"],
            "commercialUse": info["permittedUse"] == "COMMERCIAL" or bool(perms.get("commercialUses")), "permissions": perms,
            "triggerWords": info["triggerWords"], "checked_on": date.today().isoformat(), "source": "model page (pixai_models.py lora)"}


def save_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(".json.tmp")
    temp.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temp.replace(path)


def lora(root: Path, url: str, refresh: bool, fetch=None) -> tuple[str, dict, bool]:
    """Return (versionId, record, was_fetched). Does not make a network call if already recorded."""
    path = root / api.LORAS_FILE
    data = json.loads(path.read_text(encoding="utf-8-sig")) if path.is_file() else {"schema_version": 1, "loras": {}}
    records = data.setdefault("loras", {})
    model_id, version_id = parse_url(url)
    known = version_id if version_id in records else \
        (next((v for v, r in records.items() if r.get("modelId") == model_id), None) if not version_id else None)
    if known and not refresh:
        return known, records[known], False
    info = model_info((fetch or fetch_page)(model_id, version_id), version_id)
    records[info["id"]] = lora_record(info)
    save_json(path, data)
    return info["id"], records[info["id"]], True


def read_catalog(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig")) if path.is_file() else {"schema_version": 1, "models": {}}


def add(root: Path, name: str, info: dict, force: bool) -> dict:
    if not NAME.fullmatch(name):
        raise ModelError("Name must use lowercase ASCII letters, digits, ., or - (e.g. my-model2).")
    path = root / api.MODELS_FILE
    catalog = read_catalog(path)
    models = catalog.setdefault("models", {})
    if name in models and not force:
        raise ModelError(f"{name} is already registered. Pass --force to replace it.")
    same = [n for n, m in models.items() if m.get("id") == info["id"] and n != name]
    if same:
        raise ModelError(f"This versionId is already registered as {same[0]}.")
    entry = catalog_entry(info)
    models[name] = entry
    save_json(path, catalog)
    return entry


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="List and register PixAI models")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("list", help="Display the model catalog (no network)")
    info_cmd = sub.add_parser("info", help="Display versionId, type, and terms of use from a model page (does not register)")
    info_cmd.add_argument("--url", required=True)
    add_cmd = sub.add_parser("add", help="Register a model from its model page into the project's catalog")
    add_cmd.add_argument("name", help="Short name for --model (lowercase ASCII letters, digits, ., -)")
    add_cmd.add_argument("--url", required=True)
    add_cmd.add_argument("--force", action="store_true", help="Replace an existing entry with the same name")
    lora_cmd = sub.add_parser("lora", help="Record a LoRA's base model and terms of use in the project (no network if already recorded)")
    lora_cmd.add_argument("--url", required=True)
    lora_cmd.add_argument("--refresh", action="store_true", help="Re-fetch the page even if already recorded")
    opts = parser.parse_args(argv)
    root = Path(__file__).resolve().parents[1]
    try:
        if opts.command == "list":
            for name, model in read_catalog(root / api.MODELS_FILE).get("models", {}).items():
                use = "commercial allowed" if model.get("commercialUse") else "non-commercial"
                print(f"{name}: {model['label']} ({model['type'].upper()}, modelVersionId {model['id']}, {use})"
                      f" {model.get('strengths_ja', '')} / API: {model.get('api', 'not recorded')}")
            return 0
        if opts.command == "lora":
            if not (root / "project.json").is_file():
                raise ModelError("Run from scripts/ inside a manga project.")
            version_id, record, fetched = lora(root, opts.url, opts.refresh)
            print(("Recorded" if fetched else "Already recorded (page not re-fetched; pass --refresh to update)") + f": {api.LORAS_FILE}")
            print(f"LoRA: {record['title']} (versionId {version_id}, checked {record['checked_on']})")
            print(f"Base model: type {record['baseModelType'] or 'unknown'}" + (f", modelId {record['baseModelId']}" if record.get("baseModelId") else ""))
            print("Terms of use: " + ("commercial allowed" if record["commercialUse"] else "non-commercial (confirm publishing and sales terms with the user)"))
            print(f"Trigger words: {record['triggerWords'] or 'none'}")
            print(f".env.pixai example: PIXAI_LORA_<NAME>=\"{version_id}\"")
            return 0
        model_id, version_id = parse_url(opts.url)
        info = model_info(fetch_page(model_id, version_id), version_id)
        show(info)
        if opts.command == "add":
            if not (root / "project.json").is_file():
                raise ModelError("Run from scripts/ inside a manga project.")
            entry = add(root, opts.name, info, opts.force)
            print(f"Registered {opts.name} in {api.MODELS_FILE} (API: unverified). Use with --model {opts.name}.")
            if not entry["commercialUse"]:
                print("Warning: Commercial use is not permitted. Confirm publishing and sales terms on the model page with the user.")
            if entry["mode"]:
                print("Warning: mode acceptance is unverified. No mode is sent by default (uses server default).")
        return 0
    except ModelError as error:
        print(error, file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
