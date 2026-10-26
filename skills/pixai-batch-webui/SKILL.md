---
name: pixai-batch-webui
description: Use when the user wants to operate a PixAI project in progress from a browser screen (editing character, style, background, and LoRA variables in .env.pixai; editing request JSON prompts, aspect ratios, modes, style presets, and LoRAs; running generation, re-fetching interrupted results, adopting candidates, building pages, and previewing). Launches and guides a local WebUI that calls the project's pixai_batch.py and pixai_api.py directly.
---

# PixAI Production WebUI

A browser interface for humans to operate the batch generation workflow (`docs/knowledge/pixai-composed-production.md`: request JSON → `generate` → `adopt` → `build`). All processing is delegated to the project's `scripts/pixai_batch.py` and `scripts/pixai_api.py`. The WebUI performs no independent generation or typesetting of its own.

## Launch (at the project root)

```powershell
python -X utf8 .agents/skills/pixai-batch-webui/pixai_webui.py
# Specify a port or project root if needed
python -X utf8 .agents/skills/pixai-batch-webui/pixai_webui.py --port 8800 --root <project-root>
```

The user opens the displayed `http://127.0.0.1:8775/?token=…` URL in a browser. **AI agents must not launch or operate a browser** (only share the URL). Press Ctrl+C to stop. The URL token changes on every launch. The default port (`8775`) is separate from the other production panel (`8765`) so both can run at the same time.

## What You Can Do on Screen

| Tab | Contents | Commands Called |
| --- | --- | --- |
| Panels | Request list (grouped by page, with adopted image thumbnails, `[v2]` / `[v1]` tags, and counts of records without images). `v2` requests are edited via form fields: prompt, negative prompt, model (`modelVersionId`), aspect ratio and resolution (displays output pixel dimensions), `mode` (Tsubaki.2 / Tsubaki.3 family), style (preset or custom text; Tsubaki.2 / Tsubaki.3 family), LoRA (up to 5: version ID, weight, trigger words; `${PIXAI_LORA_…}` supported), seed, batch size (`1` or `4`), `promptHelper`, and `sampling` (SDXL). `v1` requests (i2i, ControlNet, reference images, Hires, ADetailer) are edited via `prompts` and `parameters` JSON. Duplicate as an alternate variant (`p01-03b`, etc.). View variable-expanded payloads and prompt lint checks. Compare, zoom, adopt, or discard candidates (moves to `discarded/`). Candidates from a 4-image task (`batchSize` 4) are grouped together as "4 images from the same generation" for selection. Choose images per panel in the generation dialog (Auto = 4 images for regenerations, 4 images, or 1 image). Panels with image-less records show "Re-fetch from PixAI". Generate by page, all pages, or a page range, and batch-adopt the latest candidates. | `generate` (`--max`, `--batch-size`), `fetch`, `adopt`, `adopt-latest` |
| Pages | Latest build and annotated check image, with typesetting check counts. Table of `focus`, `zoom`, and `rotation` within each panel; JSON editors for page manifest and typesetting specification. Separate "PNG" and "PSD" build buttons for a single page or all pages (building a PSD also creates the same version's PNG). | `build`, `build --write-psd` (`--page` / `--all`) |
| Variables | View, edit, and add `PIXAI_CHAR_`, `PIXAI_STYLE_`, `PIXAI_BACKGROUND_`, and `PIXAI_LORA_` in `.env.pixai`; list requests using each variable; generate those requests; run `templatize` (dry run / apply). On the left, displays an example request to give an AI agent for setting up batch prompt adjustment, and also shows it in bold red above "Add variable" when no variables exist yet. | `env-set`, `templatize` |
| Preview | Page through the latest build of each page (`←` advances to the next page). | — |
| Execution Log & Connection | Command and output of the most recent operation (updated every 1.2 seconds while running, including task states `waiting` and `running`), stop a running operation, **organize execution records** (see below), check API key loading, verify connection (no image generation), and run `list`. | `key-status`, `status`, `list` |

Each operation prints the equivalent terminal command in the log (and saves it under `output/webui-pixai/logs/`).

## Organizing Execution Records (Execution Log & Connection Tab)

Enter a request ID (e.g., `p07-03`) and click "Inspect", or click "Scan all panels for records without images". **Files are never deleted; they are moved into a subfolder within the same directory** (recording the operation in `moved.json` and logging it to `output/webui-pixai/logs/records.log`). Records cannot be organized while an operation is running.

| State | Action |
| --- | --- |
| Record without an image that has a `taskId` (interrupted or stopped while waiting for completion, or image download failed) | Click "Re-fetch from PixAI (`fetch`)". Queries the task and saves the image if completed without resending generation. Because PixAI does not retain generated images indefinitely, fetch them promptly. |
| Record without an image and without a `taskId` (no response was received when sending) | Check generation and credit consumption on the PixAI screen, check the "Confirmed" box, and move the record to `failed/`. If an image was created, save it as `rNNN.png` in the same folder so it is treated as a valid candidate. |
| Unwanted candidate | Click "Discard" to move it to `discarded/`. Currently adopted images cannot be discarded. Click "Restore" on a `discarded/` entry to move it back (blocked if a file with the same name already exists). |
| Unresponsive operation | Click "Stop". Any task already created continues on PixAI and leaves a record without an image (retrieve it with `fetch` above). If you stop a build, inspect and clean up any incomplete version folder (missing `build.json`). |

When PixAI rejects a request without creating a task (HTTP 4xx) or a task ends in `failed` or `cancelled`, `pixai_api.py` automatically moves the record to `failed/` (freeing the candidate number). From the terminal, you can perform the same actions with `python -X utf8 scripts/pixai_batch.py fetch --ids <request-ID>` and `move-unknown --ids <request-ID> --confirm-checked --note 'What was verified'`.

## Rules to Follow

- **Never skip generation cost confirmation.** Because the official PixAI documentation does not provide an API to query credit balance or consumption, the scripts cannot determine whether a run is free. Clicking "Generate" requires checking the box confirming that **the user explicitly authorized credit consumption for this scope** (`--confirm-credits`) and filling in the confirmation note (`--cost-note`). AI agents must never instruct users to check this box without explicit user permission.
- For requests using fields not in the current official documentation (`v1` i2i, ControlNet, IP-Adapter, `seed`, negative prompts, etc.), check the "Unverified parameters" box (`--allow-unverified`) only when the user has agreed to test them.
- Generation dialog checkboxes and the max request count are **remembered in the browser per launch token (URL)**. Restarting the server and opening the new URL clears memories from old tokens. Because remembered checkboxes still represent a confirmation declaration, uncheck and re-verify them whenever the scope changes (task count, batch size, model, mode, resolution, LoRA, or extra features).
- The default limit per run is 30 tasks (`pixai_batch.py` default). A 4-image task uses 4 images' worth of credits. Request intervals (default 3 seconds), polling intervals (3 to 10 seconds; official limit is at most once per 1.5 seconds), and stopping on failure without automatic retry remain governed by `pixai_batch.py`. Only one operation runs at a time.
- Never read or display API keys (variables handle only prefixes permitted by `pixai_batch.read_variables`). Serve images only from `output/`, `input/`, and `templates/onomatopoeia/`.
- Listen only on `127.0.0.1` and verify both the launch token and `Host` header. Never expose the server to other devices.
- Every time JSON is saved, back up the previous file under `output/webui-pixai/history/`. Validate JSON structure before saving (`api` and `body.prompt` for `v2`; `api` and `parameters.prompts` for `v1`; `schema_version` and `panels` for page manifests).
- Editing in the WebUI does not replace the project's production workflow (assembling request prompts, pre-send content checks, post-artwork comparison tables, post-typesetting inspection, and PNG review before PSD creation). Always open and verify generated images afterward.
- Templatizing prompts into `.env.pixai` should be performed after confirming variable names and values when requested by a human according to the project workflow.

## Prerequisites and Limitations

- Runs on Python 3.10+ using only the standard library. `build` and converting WebP/JPEG responses to PNG use the project's existing requirement (Pillow).
- Compatible with distribution 0.5.x `pixai_batch.py` (functions such as `read_variables`, `request_files`, `candidates`, `unknown_records`, `load_adopted`, `resolved_request`, and `lint_prompt`, and commands `list`, `vars`, `env-set`, `templatize`, `generate`, `fetch`, `adopt`, `adopt-latest`, and `build`). Startup fails if function names differ.
- Creating new requests from scratch, switching between `v2` and `v1`, and adding or removing characters are not exposed in the UI (compose with `pixai_compose.py` or edit the JSON directly).
- A `request` entry in a page manifest uses the adopted image from `input/pixai/adopted.json`. For panels on the same page that place images created by other means (such as NovelAI), specify the image path in `source` rather than `request`.
