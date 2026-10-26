---
name: novelai-batch-webui
description: Use when the user wants to operate a NovelAI project in progress from a browser screen (editing character, style, and background variables in .env.novelai; editing request JSON prompts and placement pins; running generation, adopting candidates, building pages, and previewing) or when applying LoRAs through project-specific external processing (implementing lora_apply.py). Launches and guides a local WebUI that calls the project's novelai_batch.py and novelai_api.py directly.
---

# NovelAI Production WebUI

A browser interface for humans to operate the batch generation workflow (`docs/knowledge/novelai-composed-production.md`: request JSON → `generate` → `adopt` → `build`). All processing is delegated to the project's `scripts/novelai_batch.py` and `scripts/novelai_api.py`. The WebUI performs no independent generation or typesetting of its own.

## Launch (at the project root)

```powershell
python -X utf8 .agents/skills/novelai-batch-webui/novelai_webui.py
# Specify a port or project root if needed
python -X utf8 .agents/skills/novelai-batch-webui/novelai_webui.py --port 8800 --root <project-root>
```

The user opens the displayed `http://127.0.0.1:8765/?token=…` URL in a browser. **AI agents must not launch or operate a browser** (only share the URL). Press Ctrl+C to stop. The URL token changes on every launch.

## What You Can Do on Screen

| Tab | Contents | Commands Called |
| --- | --- | --- |
| Panels | Request list (grouped by page, with adopted image thumbnails). Edit shared scene text (saves `input` and `base_caption` together), per-character captions, placement pins (`x`, `y`, `use_coords`), per-character negative prompts, negative prompt text, width, height, and seed. Duplicate as an alternate variant (`p01-03b`, etc.). View variable-expanded payloads and prompt lint checks. Compare, zoom, adopt, or discard candidates (moves to `discarded/`). Generate by page, all pages, or a page range, and batch-adopt the latest candidates (by page or all pages). | `generate` (`--max`), `adopt`, `adopt-latest` |
| Pages | Latest build and annotated check image, with typesetting check counts. Table of `focus`, `zoom`, and `rotation` within each panel; JSON editors for page manifest and typesetting specification. Separate "PNG" and "PSD" build buttons for a single page or all pages (building a PSD also creates the same version's PNG). | `build`, `build --write-psd` (`--page` / `--all`) |
| Variables | View, edit, and add `NOVELAI_CHAR_`, `NOVELAI_STYLE_`, and `NOVELAI_BACKGROUND_` in `.env.novelai`; list requests using each variable; generate those requests; run `templatize` (dry run / apply). If variables or auxiliary settings from earlier versions remain in `.env` or `.secrets/`, displays them with a button to migrate them to `.env.novelai`. On the left, displays an example request to give an AI agent for setting up batch prompt adjustment, and also shows it in bold red above "Add variable" when no variables exist yet. | `env-set`, `templatize`, `env-migrate` |
| Preview | Page through the latest build of each page (`←` advances to the next page). | — |
| Execution Log & Connection | Command and output of the most recent operation (updated every 1.2 seconds while running; turn on the auto-scroll checkbox to follow the bottom on each update), stop a running operation, **organize execution records** (see below), check API key loading, query subscription status, and run `list`. Choosing "Open log" after a failure switches to this tab. The status indicator at the top right shows generation progress (e.g., `3/39 p01-03`) and opens the log when clicked. | `key-status`, `status`, `list` |

Each operation prints the equivalent terminal command in the log (and saves it under `output/webui/logs/`).

## Organizing Execution Records (Execution Log & Connection Tab)

Enter a request ID (e.g., `p07-03`) and click "Inspect", or click "Scan all panels for unknown results". **Files are never deleted; they are moved into a subfolder within the same directory** (grouped by timestamp, candidate number, and token, with `moved.json` recording the operation and `output/webui/logs/records.log` logging it). When restoring a candidate, its `moved.json` is archived in `output/webui/history/records/`. Records cannot be organized while an operation is running.

| State | Action |
| --- | --- |
| Unknown result (an execution record exists without an image; `novelai_batch.py` stops with a message to move unknown records to `failed/` first) | Check NovelAI image history and Anlas consumption, check the "Confirmed" box, and move the record to `failed/`. If an image was actually created, save it as `rNNN.png` in the same folder so it is treated as a valid candidate (do not move it). |
| Unwanted candidate | Click "Discard" to move it to `discarded/`. Currently adopted images cannot be discarded. Click "Restore" on a `discarded/` entry to move it back (blocked if a file with the same name already exists). |
| Failed/interrupted LoRA application (unknown result in `output/lora/`) or unwanted LoRA result | Same actions as NovelAI (`failed/`, `discarded/`, and Restore). |
| Unresponsive operation | Click "Stop" (in the Running Operation card). Stopping while a generation request is being sent leaves that record with an unknown result; verify it using the procedure above. If you stop a build, inspect and clean up any incomplete version folder (missing `build.json`). |

From the terminal, you can move NovelAI unknown-result records to `failed/` in the same way with `python -X utf8 scripts/novelai_batch.py move-unknown --ids <request-ID> --confirm-checked --note 'What was verified'` (omitting `--confirm-checked` only lists the targets).

Files inside `failed/` and `discarded/` are excluded from candidate numbering and listings (`novelai_batch.py` counts only files directly inside the candidate folder).

## LoRA Application Mode

A toggle to the right of the top navigation tabs. Used to apply LoRAs to adopted images or latest candidates via **project-specific external processing** (for example, ComfyUI img2img with a character LoRA).

| File | Role |
| --- | --- |
| `lora_apply.py` | Plug-in hook for external processing. **Empty as distributed** (`READY = False`, and `apply` raises `NotImplementedError`). |
| `lora_run.py` | Calls `lora_apply.apply(job)` sequentially for each specified panel. Writes outputs to `output/lora/<request-ID>/lNNN.png` and execution records to `lNNN.lora.json`. Adopts the result when `--adopt` is passed (same behavior as `novelai_batch.py adopt --file`). Stops on failure without automatic retry. |

- Display: Shows "LoRA Mode (Not configured)" when unimplemented. When toggled ON, the server checks that `READY` is `True`, `apply` is callable, and `check(root)` returns `(True, …)`; it enables the mode only if all checks pass. The state is saved in `output/webui/settings.json` and re-verified on startup and before execution (treated as OFF if readiness is no longer met).
- Only while ON, the UI shows "Apply LoRA to all pages…" (above the panel list and page list), per-page "Apply LoRA" (on each page header in the panel list), "Apply LoRA to this page…" (page view), "Apply LoRA to this panel…" (panel view), and "Apply LoRA to range…" (from start page to end page). The panel view also displays `output/lora/` results and "Adopt" buttons (existing results remain visible even when OFF).
- Choose the source image between "Adopted image (or latest candidate if unadopted)" and "Latest candidate". NovelAI candidates and execution records are not modified.

### When an AI Agent Implements `lora_apply.py`

Do this only when requested by the user (e.g., "I want to use a LoRA in ComfyUI").

1. Confirm the environment with the user (ComfyUI URL and workflow, checkpoint model, LoRA filename and strength, img2img denoise strength, and how prompts should be used) along with any costs and terms of use. Use paid services only within the scope explicitly permitted by the user.
2. Implement `apply(job)` following the contract in the `lora_apply.py` docstring (`job.source_image`, `job.request` with `.env.novelai` variables already expanded, saving the output image to `job.output`, logging via `job.log`, and returning a `dict` to store in the execution record). In `check(root)`, verify only connection/file availability (never run generation or incur charges there).
3. Never write credentials to files, logs, or execution records (read them from environment variables or `.secrets/`). Never overwrite source images.
4. Test on a single panel, open and inspect the resulting image, and then set `READY = True`. Record the implementation details, defaults, and verification results in the project's `docs/production/`.
5. Do not copy project-specific implementations (URLs, LoRA names, etc.) back into the distribution kit. Keep `lora_apply.py` in the distribution kit as an empty template.

## Rules to Follow

- **Never skip generation cost confirmation.** Clicking "Generate" requires checking the 0 Anlas confirmation box and filling in the confirmation note (`--cost-note`). The V5 allowance check is required when using V5. The WebUI does not offer paid generation (`--allow-anlas`); paid runs must be executed from the terminal under explicit user instruction. Checkboxes record the user's confirmation declaration—neither the WebUI nor the script guarantees that a request is free.
- Generation dialog checkboxes (0 Anlas, V5 allowance, warning acceptance) and the max request count are **remembered in the browser per launch token (URL)**. Restarting the server and opening the new URL clears memories from old tokens. Because remembered checkboxes still represent a confirmation declaration, uncheck and re-verify them whenever conditions change (model, dimensions, steps, extra features) or remaining allowance is low.
- The default limit per run is 30 requests (`novelai_batch.py` default). For targets exceeding 30 requests (such as all pages), increase "Max requests per run" (`--max`, 1–1000) in the generation dialog. Request intervals (default 3 seconds), stopping on failure without automatic retry, and handling of unknown-result records remain governed by `novelai_batch.py`. Only one operation runs at a time.
- Never read or display API keys (variables handle only prefixes permitted by `novelai_batch.read_variables`). Serve images only from `output/`, `input/`, and `templates/onomatopoeia/`.
- Listen only on `127.0.0.1` and verify both the launch token and `Host` header. Never expose the server to other devices.
- Every time JSON is saved, back up the previous file under `output/webui/history/`. Validate JSON structure before saving (`input` and `parameters` for requests; `schema_version` and `panels` for page manifests).
- Editing in the WebUI does not replace the project's production workflow (assembling request prompts, pre-send content checks, post-artwork comparison tables, post-typesetting inspection, and PNG review before PSD creation). Always open and verify generated images afterward.
- Templatizing prompts into `.env.novelai` should be performed after confirming variable names and values when requested by a human according to the project workflow.

## Prerequisites and Limitations

- Runs on Python 3.10+ using only the standard library. `build` uses the project's existing requirement (Pillow).
- Compatible with distribution 0.5.x `novelai_batch.py` (functions such as `read_variables`, `request_files`, `candidates`, `load_adopted`, `resolved_request`, and `lint_prompt`, and commands `list`, `vars`, `env-set`, `templatize`, `generate`, `adopt`, `adopt-latest`, and `build`). Startup fails if function names differ.
- Adding or removing characters in request JSON, per-character inputs on requests without `v4_prompt`, and changing `steps` or `model` are not exposed in the UI (edit the JSON directly or re-compose with `novelai_compose.py`).
