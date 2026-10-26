"""Local WebUI for operating NovelAI batch production (novelai_batch.py) from a browser.

Launch from a work project (a project root containing project.json and scripts/novelai_batch.py).

  python -X utf8 .agents/skills/novelai-batch-webui/novelai_webui.py            # http://127.0.0.1:8765/?token=…
  python -X utf8 .agents/skills/novelai-batch-webui/novelai_webui.py --port 8800 --root <project-root>

Capabilities
  - View, edit, and add character, style, and background variables (NOVELAI_CHAR_, NOVELAI_STYLE_, NOVELAI_BACKGROUND_)
    in .env.novelai; run templatize; migrate variables placed in .env in earlier versions (env-migrate)
  - Edit prompts, per-character captions, placement pins, negative prompts, dimensions, and seed in request JSON
    (input/novelai/requests/); duplicate alternate variants; inspect payloads after variable expansion
  - Run generation (dry-run check / execute), compare and adopt candidates, and batch-adopt the latest candidates
  - Edit page manifests (input/pages/) and typesetting specs (input/typeset/) as JSON, run build (PSD only when requested),
    and page through built previews
  - Check API key loading (key-status) and query subscription status (status)

Rules
  - Generation, adoption, rebuilding, and writing .env.novelai call the project's scripts/novelai_batch.py and novelai_api.py directly.
    Cost confirmation, execution records, and stopping without automatic retry remain governed by the scripts. The WebUI does not expose paid generation (--allow-anlas).
  - Never read or display API keys (variables use only prefixes permitted by novelai_batch.read_variables).
  - Listen only on 127.0.0.1 and reject API calls without the per-launch token. Never open a browser automatically.
  - Before saving JSON, keep the previous contents under output/webui/history/.
Runs on Python 3.10+ using only the standard library (build requires Pillow from the project's existing requirements).
"""
from __future__ import annotations

import argparse
from datetime import datetime
import json
import mimetypes
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import re
import secrets
import shutil
import subprocess
import sys
import threading
from urllib.parse import parse_qs, urlparse

IMAGE_TYPES = {".png", ".jpg", ".jpeg", ".webp"}
SERVE_DIRS = ("output/", "input/", "templates/onomatopoeia/")
HERE = Path(__file__).resolve().parent
SETTINGS = "output/webui/settings.json"
LORA_OUTPUT = "output/lora"
MAX_LIMIT = 1000  # Upper limit for generate --max (novelai_batch.py default is 30)
PAGE_FILE = re.compile(r"page-(\d{2,3})\.json")


def find_root(start: Path) -> Path:
    for path in [start, *start.parents]:
        if (path / "project.json").is_file() and (path / "scripts" / "novelai_batch.py").is_file():
            return path
    raise SystemExit("Project root (project.json and scripts/novelai_batch.py) not found. Specify it with --root.")


class Project:
    def __init__(self, root: Path):
        self.root = root
        sys.path.insert(0, str(root / "scripts"))
        import novelai_batch  # noqa: E402  Use the project's bundled script
        self.batch = novelai_batch
        self.job: dict | None = None
        self.lock = threading.Lock()
        import importlib.util
        spec = importlib.util.spec_from_file_location("lora_run", HERE / "lora_run.py")
        self.lora_runner = importlib.util.module_from_spec(spec)
        sys.modules["lora_run"] = self.lora_runner  # Required for dataclass resolution
        spec.loader.exec_module(self.lora_runner)
        self.lora = self.lora_check()

    # ------------------------------------------------------------ LoRA application mode
    def settings(self) -> dict:
        path = self.root / SETTINGS
        try:
            return json.loads(path.read_text(encoding="utf-8")) if path.is_file() else {}
        except (OSError, json.JSONDecodeError):
            return {}

    def lora_check(self) -> dict:
        """Verify lora_apply.py readiness (READY, apply, and check()). Disables any saved ON state if not ready."""
        ready, message, name = self.lora_runner.readiness(self.root)
        mode = bool(self.settings().get("lora_mode")) and ready
        return {"ready": ready, "message": message, "name": name, "mode": mode}

    def set_lora_mode(self, on: bool) -> dict:
        self.lora = self.lora_check()
        if on and not self.lora["ready"]:
            raise ValueError("Cannot turn ON LoRA Mode because setup is incomplete. " + self.lora["message"] +
                             " Implement processing in .agents/skills/novelai-batch-webui/lora_apply.py for this project and set READY to True.")
        data = self.settings()
        data["lora_mode"] = bool(on)
        path = self.root / SETTINGS
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        self.lora = self.lora_check()
        return self.lora

    def lora_results(self, request_id: str) -> list[str]:
        folder = self.root / LORA_OUTPUT / request_id
        found = [p for p in folder.glob("l*.png") if re.fullmatch(r"l\d{3,}\.png", p.name)] if folder.is_dir() else []
        return [self.rel(p) for p in sorted(found, key=lambda p: int(p.stem[1:]))]

    # ------------------------------------------------------------ Paths
    def rel(self, path: Path) -> str:
        return path.resolve().relative_to(self.root.resolve()).as_posix()

    def inside(self, relative: str) -> Path:
        path = (self.root / relative).resolve()
        if not path.is_relative_to(self.root.resolve()):
            raise ValueError("Path is outside the project root")
        return path

    def backup(self, path: Path) -> None:
        if path.is_file():
            stamp = datetime.now().strftime("%Y%m%d-%H%M%S-%f")
            target = self.root / "output" / "webui" / "history" / f"{path.parent.name}-{path.stem}-{stamp}{path.suffix}"
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, target)

    def write_json(self, path: Path, data) -> None:
        self.backup(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary = path.with_suffix(path.suffix + ".tmp")
        temporary.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        temporary.replace(path)

    # ------------------------------------------------------------ Reading state
    def variables(self) -> list[dict]:
        try:
            found = self.batch.read_variables(self.root)
        except Exception as error:  # Duplicate definitions, etc.
            return [{"error": str(error)}]
        return [{"name": n, "value": v, "source": s} for n, (v, s) in sorted(found.items())]

    def pages(self) -> list[dict]:
        result = []
        manifests = self.root / self.batch.PAGES_DIR
        numbers = sorted({int(m.group(1)) for p in manifests.glob("page-*.json") if (m := PAGE_FILE.fullmatch(p.name))}) if manifests.is_dir() else []
        for page in numbers:
            folder = self.root / self.batch.BUILD_DIR / f"page-{page:02d}"
            versions = sorted((p for p in folder.glob("v[0-9][0-9][0-9]") if p.is_dir()), key=lambda p: p.name) if folder.is_dir() else []
            latest = None
            if versions:
                v = versions[-1]
                files = {k: v / f"page-{page:02d}{suffix}" for k, suffix in
                         (("png", ".png"), ("display", "-display.png"), ("check", "-check-overlay.png"), ("psd", ".psd"))}
                latest = {"version": v.name, **{k: self.rel(p) for k, p in files.items() if p.is_file()}}
                build = v / "build.json"
                if build.is_file():
                    info = json.loads(build.read_text(encoding="utf-8"))
                    latest["summary"] = info.get("typeset_summary")
                    latest["notes"] = info.get("placement_notes")
            result.append({"page": page, "versions": [v.name for v in versions], "latest": latest})
        return result

    def state(self) -> dict:
        adopted = self.batch.load_adopted(self.root)["adopted"]
        requests = []
        for request_id, path in self.batch.request_files(self.root).items():
            text = path.read_text(encoding="utf-8-sig")
            requests.append({
                "id": request_id, "page": self.batch.page_of(request_id),
                "candidates": [self.rel(p) for p in self.batch.candidates(self.root, request_id)],
                "lora": self.lora_results(request_id),
                "adopted": adopted.get(request_id, {}).get("path"),
                "vars": sorted(set(self.batch.PLACEHOLDER.findall(text))),
            })
        return {"project": json.loads((self.root / "project.json").read_text(encoding="utf-8-sig")).get("name", self.root.name),
                "requests": requests, "pages": self.pages(), "variables": self.variables(), "job": self.job_view(),
                "lora": self.lora}

    def request(self, request_id: str) -> dict:
        path = self.batch.request_files(self.root).get(request_id)
        if not path:
            raise ValueError("Request JSON not found: " + request_id)
        raw = json.loads(path.read_text(encoding="utf-8-sig"))
        try:
            resolved, used = self.batch.resolved_request(self.root, request_id, self.batch.read_variables(self.root))
            lint = self.batch.lint_prompt(resolved)
        except Exception as error:
            resolved, used, lint = None, set(), [f"Cannot expand variables: {error}"]
        return {"id": request_id, "raw": raw, "resolved": resolved, "used": sorted(used), "lint": lint}

    def save_request(self, request_id: str, data: dict, new: bool = False) -> None:
        if not self.batch.REQUEST_ID.fullmatch(request_id):
            raise ValueError("Use ASCII letters, digits, -, or _ for request IDs (e.g. p01-03b)")
        if not isinstance(data, dict) or not isinstance(data.get("parameters"), dict) or not isinstance(data.get("input"), str):
            raise ValueError("Request JSON is missing required fields (input and parameters)")
        path = self.root / self.batch.REQUESTS_DIR / f"{request_id}.json"
        if new and path.exists():
            raise ValueError("A request with the same ID already exists: " + request_id)
        self.write_json(path, data)

    def page(self, number: int) -> dict:
        manifest = self.root / self.batch.PAGES_DIR / f"page-{number:02d}.json"
        data = {"page": number, "manifest": None, "typeset": None, "typeset_path": None}
        if manifest.is_file():
            data["manifest"] = json.loads(manifest.read_text(encoding="utf-8-sig"))
            typeset = data["manifest"].get("typeset")
            if typeset and self.inside(typeset).is_file():
                data["typeset_path"] = typeset
                data["typeset"] = json.loads(self.inside(typeset).read_text(encoding="utf-8-sig"))
        return data

    def save_page(self, number: int, manifest: dict | None, typeset: dict | None) -> None:
        if manifest is not None:
            if manifest.get("schema_version") != 1 or not isinstance(manifest.get("panels"), list):
                raise ValueError("Page manifest requires schema_version 1 and a panels list")
            self.write_json(self.root / self.batch.PAGES_DIR / f"page-{number:02d}.json", manifest)
        if typeset is not None:
            current = self.page(number)["manifest"] or manifest or {}
            target = current.get("typeset")
            if not target:
                raise ValueError("Page manifest has no typeset path")
            if typeset.get("schema_version") != 1:
                raise ValueError("Typesetting specification requires schema_version 1")
            self.write_json(self.inside(target), typeset)

    # ------------------------------------------------------------ Execution (calls existing project scripts)
    def command(self, action: str, body: dict) -> list[str]:
        script = ["scripts/novelai_batch.py"]
        ids = [i for i in body.get("ids", []) if i]
        for i in ids:
            if not self.batch.REQUEST_ID.fullmatch(i):
                raise ValueError("Invalid request ID: " + i)
        pages = [int(p) for p in body.get("pages", [])]
        target: list[str] = []
        if body.get("all"):
            target = ["--all"]
        elif ids:
            target = ["--ids", ",".join(ids)]
        elif pages:
            for p in pages:
                target += ["--page", str(p)]
        if action == "generate":
            if not target:
                raise ValueError("Specify a target (IDs, pages, or all pages)")
            args = script + ["generate", *target, "--seed", body.get("seed", "auto")]
            if body.get("seed") not in ("auto", "request", "random"):
                raise ValueError("Invalid seed option")
            limit = int(body.get("max") or 30)
            if not 1 <= limit <= MAX_LIMIT:
                raise ValueError(f"Specify max requests between 1 and {MAX_LIMIT}")
            if limit != 30:
                args += ["--max", str(limit)]
            if body.get("execute"):
                note = str(body.get("cost_note", "")).strip()
                if not body.get("confirm_zero_anlas") or not note:
                    raise ValueError('Execution requires confirming 0 Anlas and providing a confirmation note (cost-note). The WebUI does not perform paid generation.')
                args += ["--execute", "--confirm-zero-anlas", "--cost-note", note]
                if body.get("confirm_v5_allowance"):
                    args.append("--confirm-v5-allowance")
                if body.get("accept_warnings"):
                    args.append("--accept-warnings")
            return args
        if action == "adopt":
            if len(ids) != 1 or not str(body.get("candidate", "")).isdigit():
                raise ValueError("Adopting requires a single request ID and candidate number")
            return script + ["adopt", ids[0], "--candidate", str(int(body["candidate"]))]
        if action == "adopt-latest":
            if not target:
                raise ValueError("Specify a target")
            return script + ["adopt-latest", *target] + (["--dry-run"] if body.get("dry_run") else [])
        if action == "build":
            if not (body.get("all") or pages):
                raise ValueError("Specify one or more pages")
            return script + ["build", *(["--all"] if body.get("all") else [a for p in pages for a in ("--page", str(p))])] + \
                (["--write-psd"] if body.get("write_psd") else [])
        if action == "list":
            return script + ["list"]
        if action == "templatize":
            name = str(body.get("name", ""))
            if not self.batch.VAR_NAME.fullmatch(name):
                raise ValueError("Invalid variable name")
            return script + ["templatize", name] + (["--dry-run"] if body.get("dry_run") else [])
        if action == "env-migrate":
            return script + ["env-migrate"] + (["--dry-run"] if body.get("dry_run") else [])
        if action == "env-set":
            name, value = str(body.get("name", "")), str(body.get("value", ""))
            if not self.batch.VAR_NAME.fullmatch(name):
                raise ValueError("Variable name must be " + self.batch.VAR_HELP)
            return script + ["env-set", name, "--value", value]
        if action == "adopt-file":
            path = str(body.get("path", ""))
            if len(ids) != 1 or not path.startswith(LORA_OUTPUT + "/") or not self.inside(path).is_file():
                raise ValueError("Adopting requires a request ID and an image under output/lora/")
            return script + ["adopt", ids[0], "--file", path]
        if action == "lora":
            self.lora = self.lora_check()
            if not self.lora["mode"]:
                raise ValueError("LoRA Mode is not ON (" + self.lora["message"] + ")")
            if not target:
                raise ValueError("Specify a target (panels, pages, or all pages)")
            if body.get("input", "adopted") not in ("adopted", "latest"):
                raise ValueError("Invalid source image option")
            runner = (HERE / "lora_run.py").resolve()
            runner = runner.relative_to(self.root.resolve()).as_posix() if runner.is_relative_to(self.root.resolve()) else str(runner)
            return [runner, *target, "--input", body.get("input", "adopted"), "--root", str(self.root)] + (["--adopt"] if body.get("adopt") else [])
        if action in ("key-status", "status"):
            return ["scripts/novelai_api.py", action]
        raise ValueError("Unsupported action: " + action)

    def start(self, action: str, body: dict) -> dict:
        args = self.command(action, body)
        with self.lock:
            if self.job and self.job["state"] == "running":
                raise ValueError("A previous operation is still running. Wait for it to finish.")
            shown = ["python", "-X", "utf8", *args]
            self.job = {"id": secrets.token_hex(4), "action": action, "command": " ".join(quote(a) for a in shown),
                        "state": "running", "log": "", "code": None, "started": datetime.now().isoformat(timespec="seconds")}
            job = self.job
        threading.Thread(target=self.run, args=(job, args), daemon=True).start()
        return self.job_view()

    def run(self, job: dict, args: list[str]) -> None:
        try:
            # -u: Receive output line by line without buffering so progress ([3/39] p01-03, etc.) streams into the log while running.
            process = subprocess.Popen([sys.executable, "-u", "-X", "utf8", *args], cwd=self.root, stdout=subprocess.PIPE,
                                       stderr=subprocess.STDOUT, text=True, encoding="utf-8", errors="replace")
            job["process"] = process
            for line in process.stdout:
                job["log"] += line
            job["code"] = process.wait()
        except OSError as error:
            job["log"] += f"Failed to start process: {error}\n"
            job["code"] = -1
        job["state"] = "done" if job["code"] == 0 else "failed"
        log = self.root / "output" / "webui" / "logs" / f"{datetime.now():%Y%m%d-%H%M%S}-{job['action']}.log"
        log.parent.mkdir(parents=True, exist_ok=True)
        log.write_text(job["command"] + "\n\n" + job["log"], encoding="utf-8")

    def job_view(self) -> dict | None:
        return {k: v for k, v in self.job.items() if k != "process"} if self.job else None

    def stop(self) -> dict | None:
        """Stop a running operation. If stopped while sending a generation request, that record remains with an unknown result (handled under Organize Execution Records below)."""
        job = self.job
        if not job or job["state"] != "running" or not job.get("process"):
            raise ValueError("No operation is currently running.")
        job["log"] += "\n[WebUI] Stop requested. Any generation request being sent will leave an unknown-result record (check it under Organize Execution Records).\n"
        job["process"].kill()
        return self.job_view()

    # ------------------------------------------------------------ Organize execution records (move to subfolders without deleting)
    def kinds(self, request_id: str) -> dict:
        if not self.batch.REQUEST_ID.fullmatch(request_id):
            raise ValueError("Invalid request ID: " + request_id)
        return {"novelai": (self.root / self.batch.CANDIDATES_DIR / request_id, "r", "novelai.json"),
                "lora": (self.root / LORA_OUTPUT / request_id, "l", "lora.json")}

    def records(self, request_id: str) -> dict:
        adopted = self.batch.load_adopted(self.root)["adopted"].get(request_id, {}).get("path")
        result = {"id": request_id, "exists": request_id in self.batch.request_files(self.root), "adopted": adopted}
        for kind, (folder, prefix, record_suffix) in self.kinds(request_id).items():
            items, moved = {}, []
            if folder.is_dir():
                for path in folder.iterdir():
                    m = re.fullmatch(prefix + r"(\d{3,})\.(.+)", path.name)
                    if path.is_file() and m:
                        items.setdefault(int(m.group(1)), []).append(path)
                for sub in ("failed", "discarded"):
                    for batch_dir in sorted((folder / sub).glob("*")) if (folder / sub).is_dir() else []:
                        names = sorted(p.name for p in batch_dir.iterdir()) if batch_dir.is_dir() else []
                        moved.append({"where": sub, "folder": self.rel(batch_dir), "files": names})
            entries = []
            for number, paths in sorted(items.items()):
                png = folder / f"{prefix}{number:03d}.png"
                record_path = folder / f"{prefix}{number:03d}.{record_suffix}"
                info = {}
                if record_path.is_file():
                    try:
                        data = json.loads(record_path.read_text(encoding="utf-8"))
                        info = {k: data.get(k) for k in ("status", "startedAt", "started_at", "finishedAt", "finished_at", "correlationId", "error", "costMode")}
                    except (OSError, json.JSONDecodeError):
                        info = {"status": "Cannot read record"}
                rel_png = self.rel(png) if png.is_file() else None
                entries.append({"n": number, "png": rel_png, "unknown": rel_png is None, "adopted": bool(rel_png and rel_png == adopted),
                                "files": sorted(p.name for p in paths), "record": {k: v for k, v in info.items() if v is not None}})
            result[kind] = {"folder": self.rel(folder) if folder.is_dir() else None, "entries": entries, "moved": moved}
        return result

    def scan_unknown(self) -> list[dict]:
        found = []
        ids = set(self.batch.request_files(self.root))
        for base in (self.root / self.batch.CANDIDATES_DIR, self.root / LORA_OUTPUT):
            ids |= {p.name for p in base.iterdir() if p.is_dir()} if base.is_dir() else set()
        for request_id in sorted(i for i in ids if self.batch.REQUEST_ID.fullmatch(i)):
            data = self.records(request_id)
            for kind in ("novelai", "lora"):
                for e in data[kind]["entries"]:
                    if e["unknown"]:
                        found.append({"id": request_id, "kind": kind, "n": e["n"], "status": e["record"].get("status")})
        return found

    def move(self, body: dict) -> dict:
        # Serialize generation start and record organization so the idle check and file move happen atomically.
        with self.lock:
            return self._move(body)

    def _move(self, body: dict) -> dict:
        if self.job and self.job["state"] == "running":
            raise ValueError("An operation is currently running. Wait for it to finish before organizing records.")
        request_id, kind, action = str(body.get("id", "")), body.get("kind"), body.get("action")
        folder, prefix, _ = self.kinds(request_id).get(kind, (None, None, None))
        if folder is None:
            raise ValueError("Invalid record kind")
        stamp = datetime.now().strftime("%Y%m%d-%H%M%S-%f")
        if action == "restore":
            source = self.inside(str(body.get("folder", "")))
            if not source.is_dir() or source.parent.parent != folder or source.parent.name != "discarded":
                raise ValueError("Only folders inside discarded/ can be restored")
            files = [p for p in source.iterdir() if p.name != "moved.json"]
            clash = [p.name for p in files if (folder / p.name).exists()]
            if clash:
                raise ValueError("Cannot restore because files with the same name already exist: " + ", ".join(clash))
            for path in files:
                shutil.move(str(path), str(folder / path.name))
            # Archive moved.json in history instead of restoring it into the candidate folder, where it would collide on future restores.
            record = source / "moved.json"
            if record.is_file():
                history = self.root / "output" / "webui" / "history" / "records"
                history.mkdir(parents=True, exist_ok=True)
                shutil.move(str(record), str(history / f"{request_id}-{kind}-{source.name}-{secrets.token_hex(4)}.json"))
            source.rmdir()
            self.note(f"restore {self.rel(source)} → {self.rel(folder)}")
            return self.records(request_id)
        number = int(body.get("n", -1))
        files = [p for p in folder.glob(f"{prefix}{number:03d}.*") if p.is_file()] if folder.is_dir() else []
        if not files:
            raise ValueError("No matching files found")
        png = folder / f"{prefix}{number:03d}.png"
        if action == "move-unknown":
            if png.is_file():
                raise ValueError("An image exists, so the result is not unknown (use Discard if unwanted)")
            if not body.get("confirmed"):
                raise ValueError("Check the box confirming that you verified external results and consumption (NovelAI, etc.)")
            target = folder / "failed" / f"{stamp}-{prefix}{number:03d}-{secrets.token_hex(4)}"
        elif action == "discard":
            if not png.is_file():
                raise ValueError("No image exists (move unknown-result records to failed/)")
            adopted = self.batch.load_adopted(self.root)["adopted"].get(request_id, {}).get("path")
            if adopted == self.rel(png):
                raise ValueError("Cannot discard the currently adopted image. Adopt another candidate first")
            target = folder / "discarded" / f"{stamp}-{prefix}{number:03d}-{secrets.token_hex(4)}"
        else:
            raise ValueError("Invalid action")
        target.mkdir(parents=True)
        for path in files:
            shutil.move(str(path), str(target / path.name))
        (target / "moved.json").write_text(json.dumps({"action": action, "request_id": request_id, "kind": kind, "number": number,
                                                        "files": [p.name for p in files], "moved_at": datetime.now().isoformat(timespec="seconds"),
                                                        "note": body.get("note", "")}, ensure_ascii=False, indent=2), encoding="utf-8")
        self.note(f"{action} {request_id} {kind} {prefix}{number:03d} → {self.rel(target)}")
        return self.records(request_id)

    def note(self, text: str) -> None:
        path = self.root / "output" / "webui" / "logs" / "records.log"
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as stream:
            stream.write(f"{datetime.now().isoformat(timespec='seconds')} {text}\n")


def quote(arg: str) -> str:
    return arg if re.fullmatch(r"[\w./,:=+-]+", arg) else "'" + arg.replace("'", "''") + "'"


def make_handler(project: Project, token: str, port: int):
    hosts = {f"127.0.0.1:{port}", f"localhost:{port}"}

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):  # Suppress routine access logs
            pass

        def send(self, status: int, body: bytes, kind: str) -> None:
            self.send_response(status)
            self.send_header("Content-Type", kind)
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.end_headers()
            self.wfile.write(body)

        def reply(self, data, status: int = 200) -> None:
            self.send(status, json.dumps(data, ensure_ascii=False).encode("utf-8"), "application/json; charset=utf-8")

        def allowed(self, query: dict) -> bool:
            if self.headers.get("Host") not in hosts:
                return False
            given = self.headers.get("X-Token") or (query.get("token") or [""])[0]
            return secrets.compare_digest(given, token)

        def do_GET(self):
            url = urlparse(self.path)
            query = parse_qs(url.query)
            if not self.allowed(query):
                return self.send(403, "Token required. Open the URL displayed at startup.".encode("utf-8"), "text/plain; charset=utf-8")
            try:
                if url.path == "/":
                    return self.send(200, PAGE.replace("__TOKEN__", token).encode("utf-8"), "text/html; charset=utf-8")
                if url.path == "/api/state":
                    return self.reply(project.state())
                if url.path == "/api/records":
                    return self.reply(project.records(query["id"][0]))
                if url.path == "/api/records/scan":
                    return self.reply(project.scan_unknown())
                if url.path == "/api/lora":
                    project.lora = project.lora_check()
                    return self.reply(project.lora)
                if url.path == "/api/job":
                    return self.reply(project.job_view())
                if url.path == "/api/request":
                    return self.reply(project.request(query["id"][0]))
                if url.path == "/api/page":
                    return self.reply(project.page(int(query["n"][0])))
                if url.path == "/file":
                    relative = query["path"][0]
                    path = project.inside(relative)
                    if not project.rel(path).startswith(SERVE_DIRS) or path.suffix.lower() not in IMAGE_TYPES or not path.is_file():
                        return self.send(404, b"not found", "text/plain")
                    return self.send(200, path.read_bytes(), mimetypes.guess_type(path.name)[0] or "application/octet-stream")
            except (ValueError, KeyError, OSError, json.JSONDecodeError) as error:
                return self.reply({"error": str(error)}, 400)
            self.send(404, b"not found", "text/plain")

        def do_POST(self):
            url = urlparse(self.path)
            if not self.allowed({}) or self.headers.get("Content-Type", "").split(";")[0] != "application/json":
                return self.reply({"error": "Forbidden"}, 403)
            try:
                body = json.loads(self.rfile.read(int(self.headers.get("Content-Length", "0"))).decode("utf-8") or "{}")
                if url.path == "/api/request":
                    project.save_request(body["id"], body["data"], bool(body.get("new")))
                    return self.reply({"ok": True})
                if url.path == "/api/page":
                    project.save_page(int(body["page"]), body.get("manifest"), body.get("typeset"))
                    return self.reply({"ok": True})
                if url.path == "/api/lora":
                    return self.reply(project.set_lora_mode(bool(body.get("on"))))
                if url.path == "/api/records":
                    return self.reply(project.move(body))
                if url.path == "/api/job/stop":
                    return self.reply(project.stop())
                if url.path == "/api/run":
                    return self.reply(project.start(body.get("action", ""), body))
            except (ValueError, KeyError, TypeError, OSError, json.JSONDecodeError) as error:
                return self.reply({"error": str(error)}, 400)
            self.reply({"error": "not found"}, 404)

    return Handler


PAGE = r"""<!doctype html>
<html lang="en">
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>NovelAI Production Panel</title>
<style>
:root{--bg:#f6f5f2;--panel:#fff;--ink:#1f1d1a;--sub:#6b665e;--line:#ddd8cf;--accent:#c2410c;--ok:#15803d;--warn:#b45309;--ng:#b91c1c}
@media (prefers-color-scheme:dark){:root{--bg:#171614;--panel:#211f1c;--ink:#ece8e1;--sub:#a39d93;--line:#3a3631;--accent:#fb923c;--ok:#4ade80;--warn:#fbbf24;--ng:#f87171}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:14px/1.5 system-ui,"Yu Gothic UI",sans-serif}
header{display:flex;gap:1rem;align-items:center;padding:.5rem 1rem;border-bottom:1px solid var(--line);background:var(--panel);position:sticky;top:0;z-index:5}
header h1{font-size:15px;margin:0}nav{display:flex;gap:.25rem;flex-wrap:wrap}nav button.on{background:var(--accent);color:#fff;border-color:var(--accent)}
button,select,input,textarea{font:inherit;color:inherit;background:var(--panel);border:1px solid var(--line);border-radius:6px;padding:.3rem .6rem}
button{cursor:pointer}button:hover{border-color:var(--accent)}button.primary{background:var(--accent);color:#fff;border-color:var(--accent)}
textarea{width:100%;font-family:ui-monospace,Consolas,monospace;font-size:12.5px}
main{display:grid;grid-template-columns:260px 1fr;gap:0;height:calc(100vh - 49px)}
aside{border-right:1px solid var(--line);overflow:auto;padding:.5rem;background:var(--panel)}
section.view{overflow:auto;padding:1rem}
.item{display:flex;gap:.5rem;align-items:center;padding:.25rem;border-radius:6px;cursor:pointer}.item:hover,.item.on{background:var(--bg)}
.item img{width:44px;height:44px;object-fit:cover;border-radius:4px;background:var(--line)}
.muted{color:var(--sub);font-size:12px}.row{display:flex;gap:.5rem;align-items:center;flex-wrap:wrap;margin:.4rem 0}
.card{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:.8rem;margin-bottom:1rem}
.card h3{margin:0 0 .5rem;font-size:14px}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(180px,1fr));gap:.6rem}
.cand{border:2px solid transparent;border-radius:8px;padding:.3rem;background:var(--bg)}.cand.adopted{border-color:var(--ok)}
.cand img{width:100%;height:170px;object-fit:contain;cursor:zoom-in}
.chars .char{border:1px dashed var(--line);border-radius:8px;padding:.5rem;margin:.4rem 0}
.lint{color:var(--warn)}.err{color:var(--ng)}.ok{color:var(--ok)}
pre.log{white-space:pre-wrap;background:var(--bg);border:1px solid var(--line);border-radius:8px;padding:.6rem;max-height:50vh;overflow:auto;font-size:12px}
dialog{border:1px solid var(--line);border-radius:12px;background:var(--panel);color:var(--ink);max-width:640px}
#zoom{max-width:95vw;max-height:95vh;padding:0}#zoom img{max-width:94vw;max-height:90vh;display:block}
.pageimg{max-width:100%;max-height:75vh;border:1px solid var(--line);background:#fff}
label.chk{display:flex;gap:.4rem;align-items:flex-start;margin:.3rem 0}
#jobbar{margin-left:auto;font-size:12px}
.toggle{display:flex;gap:.35rem;align-items:center;border:1px solid var(--line);border-radius:999px;padding:.2rem .7rem;font-size:12.5px;cursor:pointer;white-space:nowrap}
.toggle.on{border-color:var(--accent);color:var(--accent);font-weight:600}.toggle.unready{color:var(--sub)}
.range input{width:4.5em}
@media (max-width:800px){main{grid-template-columns:1fr;height:auto}aside{max-height:40vh}}
</style>
<header>
  <h1 id="title">NovelAI Production Panel</h1>
  <nav id="tabs">
    <button data-tab="panels" class="on">Panels (Prompts, Generate, Adopt)</button>
    <button data-tab="pages">Pages (Manifest, Typeset, Build)</button>
    <button data-tab="vars">Variables (.env.novelai)</button>
    <button data-tab="preview">Preview</button>
    <button data-tab="log">Execution Log &amp; Connection</button>
  </nav>
  <label class="toggle unready" id="loraToggle" title="Mode for applying LoRAs via project-specific external processing (lora_apply.py)"><input type="checkbox" id="loraMode"><span id="loraLabel">LoRA Mode (Not configured)</span></label>
  <span id="jobbar" class="muted"></span>
</header>
<main>
  <aside id="side"></aside>
  <section class="view" id="view"></section>
</main>
<dialog id="gen">
  <form method="dialog" id="genform">
    <h3 id="gentitle">Generate</h3>
    <p class="muted">Requests are sent by the project's novelai_batch.py generate command. Do not check boxes for items you have not verified. Paid generation (--allow-anlas) is not available from the WebUI.</p>
    <div class="row">seed: <select name="seed"><option value="auto">auto (request seed on first run, random afterward)</option><option value="request">request (fixed to request seed)</option><option value="random">random</option></select></div>
    <div class="row">Max requests per run (--max): <input type="number" name="max" min="1" max="1000" value="30" style="width:7em"><span class="muted">Default 30. Increase this for targets over 30 (such as all pages). Request interval (default 3s) and stop-on-failure behavior remain the same</span></div>
    <label class="chk"><input type="checkbox" name="confirm_zero_anlas">Confirmed that all current settings (model, dimensions, steps, count, and extra features) cost 0 Anlas (--confirm-zero-anlas)</label>
    <label class="chk"><input type="checkbox" name="confirm_v5_allowance">Confirmed sufficient remaining V5 allowance (required when using V5; --confirm-v5-allowance)</label>
    <label class="chk"><input type="checkbox" name="accept_warnings">Reviewed dry-run warnings and recorded the reason for keeping them (--accept-warnings)</label>
    <div>Verification method and timestamp (--cost-note)<textarea name="cost_note" rows="2"></textarea></div>
    <p class="muted">Checkboxes and max request count are remembered while opened with this URL (token). Restarting the server and opening a new URL clears them.</p>
    <div class="row"><button value="cancel">Cancel</button><button value="dry">Dry run (no send)</button><button value="exec" class="primary">Generate</button></div>
  </form>
</dialog>
<dialog id="loradlg">
  <form method="dialog" id="loraform">
    <h3 id="loratitle">Apply LoRA</h3>
    <p class="muted" id="loraname"></p>
    <p class="muted">Runs the project-specific external hook (.agents/skills/novelai-batch-webui/lora_apply.py) one panel at a time. Costs and terms of use follow that implementation. Results are saved in output/lora/ without modifying NovelAI candidates. Stops on failure without running remaining panels.</p>
    <div class="row">Source image: <select name="input"><option value="adopted">Adopted image (or latest candidate if unadopted)</option><option value="latest">Latest candidate</option></select></div>
    <label class="chk"><input type="checkbox" name="adopt">Adopt result (same as adopt --file; can switch back to a candidate later)</label>
    <div class="row"><button value="cancel">Cancel</button><button value="run" class="primary">Apply LoRA</button></div>
  </form>
</dialog>
<dialog id="zoom"><img alt=""></dialog>
<script>
const TOKEN = "__TOKEN__";
const $ = (s, el = document) => el.querySelector(s);
const h = (tag, attrs = {}, ...kids) => { const e = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs)) { if (k === 'class') e.className = v; else if (k.startsWith('on')) e[k] = v; else if (v !== undefined && v !== null) e.setAttribute(k, v); }
  for (const k of kids.flat()) if (k !== null && k !== undefined) e.append(k instanceof Node ? k : document.createTextNode(String(k))); return e; };
const img = (path, attrs = {}) => h('img', {src: '/file?path=' + encodeURIComponent(path) + '&token=' + TOKEN + '&t=' + Date.now(), loading: 'lazy', ...attrs});
async function api(path, body) {
  const opt = body === undefined ? {headers: {'X-Token': TOKEN}} : {method: 'POST', headers: {'X-Token': TOKEN, 'Content-Type': 'application/json'}, body: JSON.stringify(body)};
  const r = await fetch(path + (path.includes('?') ? '&' : '?') + 'token=' + TOKEN, opt); const j = await r.json();
  if (!r.ok || (j && j.error)) throw new Error(j && j.error || r.statusText); return j; }
function store(k, v) { try { if (v === undefined) return localStorage.getItem(k); localStorage.setItem(k, v); } catch (e) { return null; } }
let S = null, tab = 'panels', sel = {panel: null, page: null}, lastJob = null, renderSeq = 0;

async function refresh() { S = await api('/api/state'); $('#title').textContent = 'NovelAI Production Panel — ' + S.project; renderLora(); render(); }
// ---------------------------------------------------------------- LoRA Mode (can be enabled only when readiness checks pass)
const loraOn = () => !!(S && S.lora && S.lora.mode);
function renderLora() { const L = S.lora || {}, t = $('#loraToggle'); $('#loraMode').checked = !!L.mode;
  $('#loraLabel').textContent = !L.ready ? 'LoRA Mode (Not configured)' : L.mode ? 'LoRA Mode: ON (' + L.name + ')' : 'LoRA Mode: OFF';
  t.className = 'toggle' + (L.mode ? ' on' : !L.ready ? ' unready' : ''); t.title = L.ready ? 'Hook: ' + L.name : L.message || ''; }
$('#loraMode').onchange = async e => { const on = e.target.checked;
  try { S.lora = await api('/api/lora', {on}); } catch (err) { alert(err.message); try { S.lora = await api('/api/lora'); } catch (e2) {} }
  renderLora(); render(); };
function loraDialog(target, label) { if (!loraOn()) return alert('LoRA Mode is not ON.');
  const d = $('#loradlg'), f = n => $('#loraform').elements.namedItem(n); $('#loratitle').textContent = 'Apply LoRA: ' + label;
  $('#loraname').textContent = 'Hook: ' + S.lora.name; d.returnValue = ''; d.showModal();
  d.onclose = () => { if (d.returnValue === 'run') run('lora', {...target, input: f('input').value, adopt: f('adopt').checked}); }; }
// Page range (from start page to end page)
function pageNumbers() { return [...new Set(S.requests.map(r => r.page).filter(p => p !== null))].sort((a, b) => a - b); }
function rangeControl() { const nums = pageNumbers(); if (!nums.length) return null;
  const a = h('input', {type: 'number', min: nums[0], max: nums[nums.length - 1]}), b = a.cloneNode(); a.value = store('rangeFrom') || nums[0]; b.value = store('rangeTo') || nums[nums.length - 1];
  const pick = () => { const x = +a.value, y = +b.value; store('rangeFrom', a.value); store('rangeTo', b.value); const lo = Math.min(x, y), hi = Math.max(x, y);
    const pages = nums.filter(n => n >= lo && n <= hi); if (!pages.length) { alert('No pages with requests in that range.'); return null; } return {pages, label: `Pages ${lo}–${hi} (${S.requests.filter(r => pages.includes(r.page)).length} requests)`}; };
  return h('div', {class: 'row range'}, 'Pages', a, '–', b,
    h('button', {onclick: () => { const r = pick(); if (r) generateDialog({pages: r.pages}, r.label); }}, 'Generate range…'),
    loraOn() ? h('button', {onclick: () => { const r = pick(); if (r) loraDialog({pages: r.pages}, r.label); }}, 'Apply LoRA to range…') : null); }
function zoom(path) { const d = $('#zoom'); $('img', d).src = '/file?path=' + encodeURIComponent(path) + '&token=' + TOKEN + '&t=' + Date.now(); d.showModal(); d.onclick = () => d.close(); }
async function run(action, body = {}) {
  try { const j = await api('/api/run', {action, ...body}); showJob(j); poll(); } catch (e) { alert(e.message); } }
function showJob(j) { lastJob = j; const step = j ? [...j.log.matchAll(/\[(\d+)\/(\d+)\] (\S+)/g)].pop() : null;
  $('#jobbar').textContent = j ? `${j.action}: ${{running: 'Running…', done: 'Done', failed: 'Failed'}[j.state]}` + (step ? ` ${step[1]}/${step[2]} ${step[3]}` : '') + ' (click for log)' : '';
  $('#jobbar').className = j && j.state === 'failed' ? 'err' : j && j.state === 'done' ? 'ok' : 'muted'; if (tab === 'log') render(); }
async function poll() { const j = await api('/api/job'); showJob(j); if (j && j.state === 'running') setTimeout(poll, 1200); else { await refresh(); if (j && j.state === 'failed' && tab !== 'log') { if (confirm('Operation failed. Open the log?')) { tab = 'log'; tabs(); render(); } } } }
// Remember generation dialog checkboxes and max count per launch token (opening a new URL clears old tokens).
const CHECKS = ['confirm_zero_anlas', 'confirm_v5_allowance', 'accept_warnings'], GEN_KEY = 'genOptions:' + TOKEN;
try { for (let i = localStorage.length - 1; i >= 0; i--) { const k = localStorage.key(i); if (k.startsWith('genOptions:') && k !== GEN_KEY) localStorage.removeItem(k); } } catch (e) {}
function generateDialog(target, label) {
  const d = $('#gen'), f = n => $('#genform').elements.namedItem(n); $('#gentitle').textContent = 'Generate: ' + label;
  let saved = {}; try { saved = JSON.parse(store(GEN_KEY) || '{}'); } catch (e) {}
  f('cost_note').value = store('costNote') || ''; CHECKS.forEach(n => f(n).checked = !!saved[n]); f('max').value = saved.max || 30;
  d.returnValue = ''; d.showModal();
  d.onclose = () => { const v = d.returnValue; if (v !== 'dry' && v !== 'exec') return;
    const options = {max: +f('max').value || 30}; CHECKS.forEach(n => options[n] = f(n).checked); store(GEN_KEY, JSON.stringify(options));
    const body = {...target, seed: f('seed').value, max: options.max};
    if (v === 'exec') { Object.assign(body, options, {execute: true, cost_note: f('cost_note').value}); store('costNote', f('cost_note').value); }
    run('generate', body); }; }

// ---------------------------------------------------------------- Panels
function sidePanels() {
  const side = $('#side'); side.replaceChildren(h('div', {class: 'row'}, h('span', {class: 'muted'}, 'Requests (input/novelai/requests)'),
    h('button', {onclick: () => generateDialog({all: true}, 'All pages (' + S.requests.filter(r => r.page !== null).length + ' requests; check max limit)')}, 'Generate all pages…'), h('button', {onclick: () => confirm('Adopt the latest (highest-numbered) candidate for every panel across all pages? (Stops without changes if any panel has no candidates)') && run('adopt-latest', {all: true})}, 'Adopt latest for all pages'),
    loraOn() ? h('button', {onclick: () => loraDialog({all: true}, 'All pages')}, 'Apply LoRA to all pages…') : null), rangeControl());
  const groups = {}; for (const r of S.requests) (groups[r.page ?? 'other'] ||= []).push(r);
  for (const [g, list] of Object.entries(groups)) {
    side.append(h('div', {class: 'row'}, h('b', {}, g === 'other' ? 'Other (character trials, etc.)' : 'Page ' + g),
      g !== 'other' ? h('button', {onclick: () => generateDialog({pages: [+g]}, 'Page ' + g + ' (all panels)')}, 'Generate') : null,
      g !== 'other' ? h('button', {onclick: () => confirm('Adopt the latest candidate for every panel on page ' + g + '?') && run('adopt-latest', {pages: [+g]})}, 'Adopt latest') : null,
      g !== 'other' && loraOn() ? h('button', {onclick: () => loraDialog({pages: [+g]}, 'Page ' + g)}, 'Apply LoRA') : null));
    for (const r of list) side.append(h('div', {class: 'item' + (sel.panel === r.id ? ' on' : ''), onclick: () => { sel.panel = r.id; render(); }},
      r.adopted ? img(r.adopted) : h('img', {alt: ''}), h('div', {}, h('div', {}, r.id), h('div', {class: 'muted'}, `Candidates: ${r.candidates.length}` + (r.lora.length ? ` · LoRA: ${r.lora.length}` : '') + ` · ${r.adopted ? (r.adopted.startsWith('output/lora/') ? 'LoRA adopted' : 'Adopted') : 'Unadopted'}`))));
  } }
async function viewPanel() {
  const v = $('#view'); if (!sel.panel) { v.replaceChildren(h('p', {class: 'muted'}, 'Select a request from the list on the left.')); return; }
  const seq = renderSeq, R = await api('/api/request?id=' + encodeURIComponent(sel.panel)); if (seq !== renderSeq || tab !== 'panels') return; const raw = R.raw, P = raw.parameters, cap = P.v4_prompt?.caption || {}, neg = P.v4_negative_prompt?.caption || {};
  const info = S.requests.find(r => r.id === sel.panel) || {candidates: []};
  const base = h('textarea', {rows: 4}); base.value = raw.input;
  const negative = h('textarea', {rows: 3}); negative.value = P.negative_prompt || '';
  const num = (k) => { const e = h('input', {type: 'number', style: 'width:8em'}); e.value = P[k]; return e; };
  const W = num('width'), H = num('height'), seed = num('seed');
  const coords = h('input', {type: 'checkbox'}); coords.checked = !!P.v4_prompt?.use_coords;
  const chars = (cap.char_captions || []).map((c, i) => { const t = h('textarea', {rows: 3}); t.value = c.char_caption;
    const x = h('input', {type: 'number', step: '0.01', min: 0, max: 1, style: 'width:6em'}), y = x.cloneNode(); x.value = c.centers?.[0]?.x ?? 0.5; y.value = c.centers?.[0]?.y ?? 0.5;
    const n = h('textarea', {rows: 1}); n.value = neg.char_captions?.[i]?.char_caption || '';
    return {t, x, y, n, el: h('div', {class: 'char'}, h('b', {}, 'Character ' + (i + 1)), t, h('div', {class: 'row'}, 'Placement pin x', x, 'y', y, '(0–1, origin at top-left)'), h('div', {class: 'muted'}, 'Per-character negative prompt'), n)}; });
  function collect() { const d = JSON.parse(JSON.stringify(raw)), p = d.parameters;
    d.input = base.value; p.negative_prompt = negative.value; p.width = +W.value; p.height = +H.value; p.seed = +seed.value;
    if (p.v4_prompt) { p.v4_prompt.caption.base_caption = base.value; p.v4_prompt.use_coords = coords.checked;
      chars.forEach((c, i) => { const cc = p.v4_prompt.caption.char_captions[i]; cc.char_caption = c.t.value; cc.centers = [{x: +c.x.value, y: +c.y.value}];
        if (p.v4_negative_prompt?.caption?.char_captions?.[i]) { p.v4_negative_prompt.caption.char_captions[i].char_caption = c.n.value; p.v4_negative_prompt.caption.char_captions[i].centers = [{x: +c.x.value, y: +c.y.value}]; } }); }
    if (p.v4_negative_prompt) p.v4_negative_prompt.caption.base_caption = negative.value; return d; }
  async function save(id = sel.panel, isNew = false) { try { await api('/api/request', {id, data: collect(), new: isNew}); sel.panel = id; await refresh(); return true; } catch (e) { alert(e.message); return false; } }
  const varsInfo = S.variables.filter(x => x.name).map(x => x.name);
  const resolved = h('pre', {class: 'log'}, R.resolved ? JSON.stringify({input: R.resolved.input, char_captions: (R.resolved.parameters.v4_prompt?.caption?.char_captions || []).map(c => c.char_caption)}, null, 2) : 'Cannot expand variables');
  const cands = h('div', {class: 'grid'}, ...info.candidates.slice().reverse().map(p => { const n = +p.match(/r(\d+)\.png$/)[1];
    return h('div', {class: 'cand' + (info.adopted === p ? ' adopted' : '')}, img(p, {onclick: () => zoom(p)}),
      h('div', {class: 'row'}, 'r' + String(n).padStart(3, '0'), info.adopted === p ? h('span', {class: 'ok'}, 'Adopted') : h('button', {onclick: () => run('adopt', {ids: [sel.panel], candidate: n})}, 'Adopt'),
        info.adopted === p ? null : h('button', {title: 'Move to discarded/ (not deleted)', onclick: () => discard(sel.panel, 'novelai', n)}, 'Discard'))); }));
  v.replaceChildren(
    h('div', {class: 'card'}, h('h3', {}, 'Prompt for ' + sel.panel),
      h('div', {class: 'muted'}, 'Shared scene prompt (saved to both input and base_caption). ${VAR_NAME} expands from .env.novelai. Available variables: ' + (varsInfo.join(', ') || 'none')), base,
      h('div', {class: 'chars'}, chars.map(c => c.el)),
      h('label', {class: 'chk'}, coords, 'Use placement pins (use_coords)'),
      h('div', {class: 'muted'}, 'Negative prompt (negative_prompt and v4_negative_prompt base_caption)'), negative,
      h('div', {class: 'row'}, 'Width', W, 'Height', H, 'seed', seed, h('span', {class: 'muted'}, `steps ${P.steps} · ${raw.model}`)),
      R.lint.length ? h('div', {class: 'lint'}, 'Prompt check warnings: ' + R.lint.join(' / ')) : h('div', {class: 'muted'}, 'No prompt check warnings (term detection only; verify content separately)'),
      h('div', {class: 'row'}, h('button', {class: 'primary', onclick: () => save()}, 'Save'),
        h('button', {onclick: async () => { if (await save()) generateDialog({ids: [sel.panel]}, sel.panel); }}, 'Save & generate…'),
        loraOn() ? h('button', {onclick: () => loraDialog({ids: [sel.panel]}, sel.panel)}, 'Apply LoRA to this panel…') : null,
        h('button', {onclick: () => { const id = prompt('ID for alternate variant (e.g. ' + sel.panel + 'b)', sel.panel + 'b'); if (id) save(id, true); }}, 'Duplicate as alternate variant'))),
    h('div', {class: 'card'}, h('h3', {}, 'Candidates (newest first)'), info.candidates.length ? cands : h('p', {class: 'muted'}, 'No candidates yet.')),
    (info.lora || []).length ? h('div', {class: 'card'}, h('h3', {}, 'LoRA Results (newest first; output/lora/)'), h('div', {class: 'grid'}, ...info.lora.slice().reverse().map(p =>
      h('div', {class: 'cand' + (info.adopted === p ? ' adopted' : '')}, img(p, {onclick: () => zoom(p)}),
        h('div', {class: 'row'}, p.split('/').pop(), info.adopted === p ? h('span', {class: 'ok'}, 'Adopted') : h('button', {onclick: () => run('adopt-file', {ids: [sel.panel], path: p})}, 'Adopt')))))) : null,
    h('details', {class: 'card'}, h('summary', {}, 'Payload after variable expansion (saved version)'), resolved)); }

// ---------------------------------------------------------------- Pages
function sidePages() { const side = $('#side');
  side.replaceChildren(h('div', {class: 'row'}, h('b', {}, 'Pages'), h('button', {onclick: () => confirm('Rebuild PNGs for all pages?') && run('build', {all: true})}, 'All pages PNG'),
    h('button', {onclick: () => confirm('Build PSDs for all pages? (Also builds same-version PNGs; use after PNG review when requested)') && run('build', {all: true, write_psd: true})}, 'All pages PSD'), h('button', {onclick: () => confirm('Adopt the latest (highest-numbered) candidate for every panel across all pages? (Stops without changes if any panel has no candidates)') && run('adopt-latest', {all: true})}, 'Adopt latest for all pages'),
    loraOn() ? h('button', {onclick: () => loraDialog({all: true}, 'All pages')}, 'Apply LoRA to all pages…') : null), rangeControl());
  for (const p of S.pages) side.append(h('div', {class: 'item' + (sel.page === p.page ? ' on' : ''), onclick: () => { sel.page = p.page; render(); }},
    p.latest?.display ? img(p.latest.display) : h('img', {alt: ''}), h('div', {}, h('div', {}, 'Page ' + p.page), h('div', {class: 'muted'}, p.latest ? 'Latest ' + p.latest.version : 'Not built')))); }
async function viewPage() { const v = $('#view'); if (!sel.page) { v.replaceChildren(h('p', {class: 'muted'}, 'Select a page from the list on the left.')); return; }
  const seq = renderSeq, D = await api('/api/page?n=' + sel.page); if (seq !== renderSeq || tab !== 'pages') return; const info = S.pages.find(p => p.page === sel.page), L = info.latest;
  const man = h('textarea', {rows: 14}), ts = h('textarea', {rows: 18}); man.value = JSON.stringify(D.manifest, null, 2); ts.value = D.typeset ? JSON.stringify(D.typeset, null, 2) : '';
  const rows = (D.manifest?.panels || []).map(p => { const f = (k, d, step) => { const e = h('input', {type: 'number', step, style: 'width:6em'}); e.value = k === 'fx' ? (p.focus?.[0] ?? .5) : k === 'fy' ? (p.focus?.[1] ?? .5) : (p[k] ?? d); e.dataset.k = k; return e; };
    const tr = h('tr', {}, h('td', {}, 'Panel ' + p.panel), h('td', {}, p.request || p.source || ''), h('td', {}, f('fx', .5, .01)), h('td', {}, f('fy', .5, .01)), h('td', {}, f('zoom', 1, .05)), h('td', {}, f('rotation', 0, 1))); tr.dataset.panel = p.panel; return tr; });
  function applyRows() { const m = JSON.parse(man.value); for (const tr of rows) { const p = m.panels.find(x => x.panel === +tr.dataset.panel); const g = k => +tr.querySelector(`[data-k=${k}]`).value;
      p.focus = [g('fx'), g('fy')]; if (g('zoom') !== 1) p.zoom = g('zoom'); else delete p.zoom; if (g('rotation')) p.rotation = g('rotation'); else delete p.rotation; } man.value = JSON.stringify(m, null, 2); }
  async function save(build) { try { applyRows(); await api('/api/page', {page: sel.page, manifest: JSON.parse(man.value), typeset: ts.value.trim() ? JSON.parse(ts.value) : null});
      if (build) run('build', {pages: [sel.page], write_psd: build === 'psd'}); else refresh(); } catch (e) { alert(e.message); } }
  v.replaceChildren(
    h('div', {class: 'card'}, h('h3', {}, 'Page ' + sel.page + ' ' + (L ? '(Latest ' + L.version + ')' : '(Not built)')),
      h('div', {class: 'row'}, h('button', {class: 'primary', onclick: () => save('png')}, 'Save & build PNG'),
        h('button', {onclick: () => confirm('Build PSD? (Also builds the same-version PNG; use after PNG review when requested)') && save('psd')}, 'Save & build PSD'),
        h('button', {onclick: () => generateDialog({pages: [sel.page]}, 'Page ' + sel.page + ' (all panels)')}, 'Generate this page…'),
        loraOn() ? h('button', {onclick: () => loraDialog({pages: [sel.page]}, 'Page ' + sel.page)}, 'Apply LoRA to this page…') : null,
        h('button', {onclick: () => confirm('Adopt the latest candidate for each panel?') && run('adopt-latest', {pages: [sel.page]})}, 'Adopt latest')),
      L ? h('div', {class: 'muted'}, `Typesetting check: ${L.summary?.error ?? '?'} errors · ${L.summary?.warning ?? '?'} warnings` + (L.notes && Object.keys(L.notes).length ? ' / Placement notes: ' + JSON.stringify(L.notes) : '')) : null,
      L ? h('div', {class: 'row'}, L.display ? img(L.display, {class: 'pageimg', onclick: () => zoom(L.png)}) : null, L.check ? img(L.check, {class: 'pageimg', style: 'max-width:45%', onclick: () => zoom(L.check)}) : null) : null),
    h('div', {class: 'card'}, h('h3', {}, 'Panel Framing (focus = image point placed at panel center, zoom, rotation)'),
      h('table', {}, h('tr', {}, ...['Panel', 'Image', 'focus x', 'focus y', 'zoom', 'rotation'].map(t => h('th', {}, t))), ...rows)),
    h('div', {class: 'card'}, h('h3', {}, 'Page Manifest JSON (input/pages)'), man, h('h3', {}, 'Typesetting Spec JSON (' + (D.typeset_path || 'none') + ')'),
      h('div', {class: 'muted'}, 'Speech balloons (balloons: center, tail, text, size), keep-out zones (keep_out), and in-art lettering (inserts). Coordinates are in page px.'), ts,
      h('div', {class: 'row'}, h('button', {onclick: () => save(false)}, 'Save only'), h('button', {class: 'primary', onclick: () => save('png')}, 'Save & build PNG'), h('button', {onclick: () => confirm('Build PSD?') && save('psd')}, 'Save & build PSD')))); }

// ---------------------------------------------------------------- Variables
// Variables tab guidance (matches the Step 0 example request in docs/novelai-prompts/README.md).
const VARS_GUIDE = 'To set up this tab so you can batch-adjust character appearances, outfits, and background prompts, ask your AI agent in the project folder:', VARS_EXAMPLE = '"Based on the existing prompts, please set up character, style, and background variables in .env.novelai so I can edit them myself. Do not generate images yet—just prepare the files."';
function viewVars() { $('#side').replaceChildren(h('p', {class: 'muted'}, 'Edit character, style, and background variables in .env.novelai (shared API key and URL settings stay in .env). API keys are never displayed or modified.'),
    h('div', {class: 'card'}, h('p', {}, VARS_GUIDE), h('p', {class: 'muted'}, VARS_EXAMPLE)));
  const v = $('#view'); const list = S.variables;
  const blocks = list.map(x => { if (x.error) return h('div', {class: 'card'}, h('p', {class: 'err'}, x.error), x.error.includes('env-migrate') ? h('div', {class: 'row'},
      h('button', {onclick: () => run('env-migrate', {dry_run: true})}, 'Preview lines to migrate'),
      h('button', {class: 'primary', onclick: () => confirm('Migrate variables and auxiliary settings from legacy locations (.env and .secrets) to .env.novelai? (Leaves API keys and other lines intact)') && run('env-migrate')}, 'Migrate to .env.novelai (env-migrate)')) : null); const t = h('textarea', {rows: 3}); t.value = x.value;
    const used = S.requests.filter(r => r.vars.includes(x.name)).map(r => r.id);
    return h('div', {class: 'card'}, h('h3', {}, x.name + ' (' + x.source + ')'), t, h('div', {class: 'muted'}, 'Used by requests: ' + (used.join(', ') || 'none')),
      h('div', {class: 'row'}, h('button', {class: 'primary', onclick: () => run('env-set', {name: x.name, value: t.value.replace(/\s*\n\s*/g, ' ')})}, 'Save (env-set)'),
        used.length ? h('button', {onclick: () => generateDialog({ids: used}, used.length + ' panels using ' + x.name)}, 'Generate panels using this variable…') : null,
        h('button', {onclick: () => run('templatize', {name: x.name, dry_run: true})}, 'Check replacement matches'),
        h('button', {onclick: () => confirm('Replace matching text in request JSON files with ${' + x.name + '}?') && run('templatize', {name: x.name})}, 'Apply to requests (templatize)'))); });
  const name = h('input', {placeholder: 'NOVELAI_CHAR_NAME', style: 'width:22em'}), val = h('textarea', {rows: 2});
  const empty = !list.some(x => !x.error) ? h('div', {class: 'err', style: 'font-weight:bold'}, h('p', {}, VARS_GUIDE), h('p', {}, VARS_EXAMPLE)) : null;
  v.replaceChildren(...blocks, ...(empty ? [empty] : []), h('div', {class: 'card'}, h('h3', {}, 'Add Variable'), h('div', {class: 'muted'}, 'Uppercase ASCII letters, digits, and _ starting with NOVELAI_CHAR_, NOVELAI_STYLE_, or NOVELAI_BACKGROUND_. Single-line value. After adding, click "Apply to requests" to convert matching text in existing requests into variable references.'),
    name, val, h('div', {class: 'row'}, h('button', {class: 'primary', onclick: () => run('env-set', {name: name.value.trim(), value: val.value.replace(/\s*\n\s*/g, ' ')})}, 'Add (env-set)')))); }

// ---------------------------------------------------------------- Preview
function viewPreview() { $('#side').replaceChildren(h('p', {class: 'muted'}, 'Latest build of each page (display-width review image). Use ← for the next page.'));
  const pages = S.pages.filter(p => p.latest?.display); let i = 0; const v = $('#view');
  if (!pages.length) { v.replaceChildren(h('p', {class: 'muted'}, 'No built pages yet.')); return; }
  const im = h('img', {class: 'pageimg', style: 'max-height:82vh'}), info = h('span');
  const show = k => { i = Math.max(0, Math.min(pages.length - 1, k)); const p = pages[i]; im.src = '/file?path=' + encodeURIComponent(p.latest.display) + '&token=' + TOKEN; im.onclick = () => zoom(p.latest.png); info.textContent = `Page ${p.page} (${p.latest.version}) ${i + 1}/${pages.length}`; };
  v.replaceChildren(h('div', {class: 'row'}, h('button', {onclick: () => show(i + 1)}, '← Next'), info, h('button', {onclick: () => show(i - 1)}, 'Prev →')), im); show(0);
  document.onkeydown = e => { if (tab !== 'preview') return; if (e.key === 'ArrowLeft') show(i + 1); if (e.key === 'ArrowRight') show(i - 1); }; }

// ---------------------------------------------------------------- Log
async function discard(id, kind, n) { if (!confirm(`Move ${kind === 'lora' ? 'l' : 'r'}${String(n).padStart(3, '0')} of ${id} to discarded/? (Files are not deleted and can be restored from Organize Execution Records)`)) return;
  try { await api('/api/records', {action: 'discard', id, kind, n}); await refresh(); } catch (e) { alert(e.message); } }
// Organize execution records: move records into subfolders (failed/ or discarded/) without deleting files.
function recordsPane() { const id = h('input', {placeholder: 'Request ID (e.g. p07-03)', list: 'reqids', style: 'width:12em'}), out = h('div');
  id.value = store('recordsId') || '';
  const list = h('datalist', {id: 'reqids'}, ...S.requests.map(r => h('option', {value: r.id})));
  async function show() { const v = id.value.trim(); if (!v) return; store('recordsId', v);
    try { draw(await api('/api/records?id=' + encodeURIComponent(v))); } catch (e) { out.replaceChildren(h('p', {class: 'err'}, e.message)); } }
  async function act(body) { try { draw(await api('/api/records', body)); refresh(); } catch (e) { alert(e.message); } }
  function draw(D) { const kids = [h('div', {class: 'muted'}, `${D.id}: ${D.exists ? 'Request exists' : 'No request JSON'} / Adopted: ${D.adopted || 'none'}`)];
    for (const [kind, label, pre] of [['novelai', 'NovelAI Candidates', 'r'], ['lora', 'LoRA Results', 'l']]) { const K = D[kind];
      if (!K.entries.length && !K.moved.length) { kids.push(h('div', {class: 'muted'}, label + ': none')); continue; }
      kids.push(h('h3', {}, label + ' (' + (K.folder || '') + ')'));
      for (const e of K.entries) { const name = pre + String(e.n).padStart(3, '0'), rec = e.record;
        if (e.unknown) { const ok = h('input', {type: 'checkbox'});
          kids.push(h('div', {class: 'card'}, h('b', {class: 'err'}, name + ': Unknown result (no image)'),
            h('div', {class: 'muted'}, `Status: ${rec.status || 'no record'} / Started: ${rec.startedAt || rec.started_at || '?'}` + (rec.correlationId ? ` / Correlation ID: ${rec.correlationId}` : '') + (rec.error ? ` / ${rec.error}` : '') + ` / Files: ${e.files.join(', ')}`),
            h('div', {class: 'muted'}, kind === 'novelai' ? 'Check NovelAI image history and Anlas consumption. If an image was created, save it as ' + K.folder + '/' + name + '.png to use it as a candidate (no need to move it).' : 'Check whether the external hook (lora_apply.py) produced an output.'),
            h('label', {class: 'chk'}, ok, kind === 'novelai' ? 'Verified NovelAI results and consumption (no image was created, or it is not needed)' : 'Verified external processing result'),
            h('button', {class: 'primary', onclick: () => act({action: 'move-unknown', id: D.id, kind, n: e.n, confirmed: ok.checked})}, 'Move to failed/')));
        } else kids.push(h('div', {class: 'row'}, img(e.png, {style: 'width:64px;height:64px;object-fit:cover', onclick: () => zoom(e.png)}), name,
            e.adopted ? h('span', {class: 'ok'}, 'Adopted') : h('button', {onclick: () => confirm('Move ' + name + ' to discarded/?') && act({action: 'discard', id: D.id, kind, n: e.n})}, 'Discard'),
            h('span', {class: 'muted'}, rec.status || ''))); }
      for (const m of K.moved) kids.push(h('div', {class: 'row muted'}, (m.where === 'failed' ? 'Moved as unknown result: ' : 'Discarded: ') + m.folder + ' (' + m.files.filter(f => f !== 'moved.json').join(', ') + ')',
        m.where === 'discarded' ? h('button', {onclick: () => act({action: 'restore', id: D.id, kind, folder: m.folder})}, 'Restore') : null)); }
    out.replaceChildren(...kids); }
  async function scan() { try { const L = await api('/api/records/scan');
      out.replaceChildren(L.length ? h('div', {}, h('b', {}, 'Unknown-result records'), ...L.map(x => h('div', {class: 'row'}, `${x.id} (${x.kind === 'lora' ? 'LoRA' : 'NovelAI'} ${x.kind === 'lora' ? 'l' : 'r'}${String(x.n).padStart(3, '0')}: ${x.status || '?'})`,
        h('button', {onclick: () => { id.value = x.id; show(); }}, 'Open')))) : h('p', {class: 'ok'}, 'No unknown-result records found.')); } catch (e) { alert(e.message); } }
  if (id.value) setTimeout(show, 0);
  return h('div', {class: 'card', id: 'recpane'}, h('h3', {}, 'Organize Execution Records'),
    h('div', {class: 'muted'}, 'Use when generation stops due to execution records with unknown results or when cleaning up unwanted candidates. Files are never deleted; they are moved to failed/ or discarded/ in the same folder (logged in output/webui/logs/records.log).'),
    h('div', {class: 'row'}, id, list, h('button', {class: 'primary', onclick: show}, 'Inspect'), h('button', {onclick: scan}, 'Scan all panels for unknown results')), out); }
function viewLog() { const before = $('#view pre.output'), kept = before ? before.scrollTop : 0, auto = store('logAutoScroll') !== '0';
  const follow = h('input', {type: 'checkbox'}); follow.checked = auto;
  follow.onchange = () => { store('logAutoScroll', follow.checked ? '1' : '0'); if (follow.checked) toBottom(); };
  const toBottom = () => { const out = $('#view pre.output'); if (out) out.scrollTop = out.scrollHeight; };
  $('#side').replaceChildren(h('p', {class: 'muted'}, 'Executed commands and output. Logs are also saved under output/webui/logs/.'),
    h('div', {class: 'card'}, h('h3', {}, 'API Connection'), h('div', {class: 'row'}, h('button', {onclick: () => run('key-status')}, 'Check API key loading (no network)')),
      h('div', {class: 'row'}, h('button', {onclick: () => confirm('Call the subscription status API once (no image generation)?') && run('status')}, 'Subscription status (status)')),
      h('div', {class: 'muted'}, 'The script also queries subscription status automatically roughly every 10 generations. Avoid calling it excessively.'), h('div', {class: 'row'}, h('button', {onclick: () => run('list')}, 'List requests (list)'))),
    lastJob && lastJob.state === 'running' ? h('div', {class: 'card'}, h('h3', {}, 'Running Operation'), h('div', {class: 'muted'}, 'Use only if an operation stops responding. Stopping while a generation request is being sent leaves an unknown-result record (verify and move it under Organize Execution Records on the right).'),
      h('button', {onclick: async () => { if (confirm('Stop the running operation?')) try { showJob(await api('/api/job/stop', {})); } catch (e) { alert(e.message); } }}, 'Stop')) : null);
  // Keep the Organize Execution Records pane intact across log refreshes so user input is preserved
  if (!$('#view #recpane')) $('#view').replaceChildren(h('div', {id: 'jobpane'}), recordsPane());
  const j = lastJob; $('#jobpane').replaceChildren(j ? h('div', {class: 'card'}, h('h3', {}, `${j.action} (${j.started}): ${{running: 'Running', done: 'Done', failed: 'Failed'}[j.state]}${j.code !== null ? ' · Exit code ' + j.code : ''}`),
    h('div', {class: 'muted'}, 'Equivalent terminal command (run at the project root):'), h('pre', {class: 'log'}, j.command),
    h('label', {class: 'chk'}, follow, 'Auto-scroll (scroll to the bottom of output on every update while ON)'), h('pre', {class: 'log output'}, j.log || '(no output)')) : h('p', {class: 'muted'}, 'No operations run yet.'));
  if (auto) toBottom(); else { const out = $('#view pre.output'); if (out) out.scrollTop = kept; } }

function tabs() { document.querySelectorAll('#tabs button').forEach(b => b.classList.toggle('on', b.dataset.tab === tab)); }
function render() { if (!S) return; tabs(); renderSeq++;
  if (tab === 'panels') { sidePanels(); viewPanel(); } else if (tab === 'pages') { sidePages(); viewPage(); } else if (tab === 'vars') viewVars(); else if (tab === 'preview') viewPreview(); else viewLog(); }
document.querySelectorAll('#tabs button').forEach(b => b.onclick = () => { tab = b.dataset.tab; render(); });
$('#jobbar').style.cursor = 'pointer'; $('#jobbar').onclick = () => { tab = 'log'; render(); };
refresh().then(() => api('/api/job')).then(j => { showJob(j); if (j && j.state === 'running') poll(); }).catch(e => alert(e.message));
</script>
</html>
"""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--root", help="Project root (defaults to searching upward from the current directory)")
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()
    root = find_root(Path(args.root).resolve() if args.root else Path.cwd().resolve())
    project = Project(root)
    token = secrets.token_urlsafe(16)
    server = ThreadingHTTPServer(("127.0.0.1", args.port), make_handler(project, token, args.port))
    print(f"Project: {root}")
    print(f"Open in your browser: http://127.0.0.1:{args.port}/?token={token}")
    print("Press Ctrl+C to stop. This URL changes on every launch.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
