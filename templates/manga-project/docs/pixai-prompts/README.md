# Edit and Regenerate PixAI Characters, Styles, Backgrounds, and LoRAs

This guide explains how to change character appearances, art styles, backgrounds, and LoRAs, regenerate images, and rebuild pages in a **project where PixAI requests (`input/pixai/requests/`) are already set up**. Work inside the existing project folder.

> [!NOTE]
> Settings files are split into three files:
>
> | File | Contents | Edited in this guide? |
> | --- | --- | --- |
> | `.env` | Shared settings such as API keys (`PIXAI_API_KEY`, etc.) and URLs | No |
> | `.env.novelai` | Prompt variables for NovelAI | No |
> | `.env.pixai` | **PixAI character, style, background, and LoRA variables and helper settings** | **Yes** |
>
> `.env.pixai.example` is a sample file; editing it has no effect. API keys can also be placed in `.secrets/pixai.env` or environment variables in addition to `.env`.

> [!IMPORTANT]
> PixAI generation **consumes credits**. Because there is no API for querying credit balance, the scripts cannot determine whether a run is free. Before generating, check your credit balance and scope yourself, and explicitly tell the AI agent something like: "You may consume credits to generate this page up to N images total with this model and these settings." Asking for preparation, inspection, or generation alone does not count as permission to spend credits.

---

## [Quick Start] Change Only a Character's Appearance

### [First Time Only] Step 0. Ask the AI Agent to Prepare the Environment

> 🤖 **Sample prompt for the AI:**
> "Based on the existing PixAI requests, please set things up so I can edit characters, styles, and backgrounds myself from `.env.pixai`. If character LoRAs are used, please make their IDs variables too. Do not generate any images this time—just do the preparation."

The AI agent will propose variable names and values, and after your confirmation, write them to `.env.pixai` and replace matching values in the request JSON files with `${VARIABLE_NAME}` references.

### Step 1. Edit `.env.pixai`

Open `.env.pixai` in the root of your project folder in a text editor, edit the right-hand side (inside `"`) of the target line, and save it (UTF-8, single line without line breaks):

```dotenv
PIXAI_CHAR_MIO="light brown short bob hair, yellow hairclip, yellow hoodie over navy blazer"
PIXAI_STYLE_MAIN="clean lineart, soft colors"
PIXAI_BACKGROUND_CLASSROOM="classroom, desks, windows, daylight"
PIXAI_LORA_MIO="1234567890123456789"
```

- Keep the variable name to the left of `=` unchanged and edit **only the text inside the quotation marks on the right**.
- The value of `PIXAI_LORA_` must be **only the final number (the version ID)** from the PixAI LoRA page URL (`https://pixai.art/model/<modelId>/<versionId>`). The LoRA weight (`weight`, `0`–`1`) is specified in the request JSON.
- Write emphasis using parentheses `(smile:1.2)`. Square brackets and curly braces are not supported.
- Saving the file applies your changes immediately.

If you prefer to apply changes from a text file, use the following commands (other lines in `.env.pixai` remain untouched):

```powershell
python -X utf8 scripts/pixai_batch.py env-set PIXAI_CHAR_MIO --value-file input/pixai/prompts/mio.txt
python -X utf8 scripts/pixai_batch.py vars
```

### Step 2. Dry-Run Check Without Sending

```powershell
python -X utf8 scripts/pixai_batch.py generate --page 1 --batch-size 1
```

Makes no network calls and does not read your API key; displays each panel's model, aspect ratio, output pixel dimensions, image count, seed, variables used, and any prompt warnings. This example uses 1 image per panel (5 images total for a 5-panel page). With the default `--batch-size auto`, regenerating a panel that already has candidates defaults to 4 images per panel. If you want to compare 4 candidates per panel, pass `--batch-size 4` to both the dry-run check and the execution command, and authorize credit consumption for the displayed total image count. Note that `--cost-note` is a text record and does not automatically cap the number of images generated.

### Step 3. Regenerate Images (Only Within Approved Scope)

```powershell
python -X utf8 scripts/pixai_batch.py generate --page 1 --batch-size 1 --execute --accept-warnings --confirm-credits --cost-note 'Balance XX; approved consuming credits for 5 images total (1 image each across 5 panels on page 1) with verified model and settings on 2026-10-25'
```

- `--confirm-credits` is your declaration that you have authorized credit consumption for this scope; the script itself cannot verify whether generation is free.
- Creates one task per panel, waits for completion, and saves candidates such as `output/pixai/candidates/p01-02/r003.png`. If a task fails mid-run, the script stops without sending the remaining tasks and does not automatically retry.
- If completion polling is interrupted mid-way (due to a network drop, cancellation, etc.), you can re-fetch the result without re-sending generation by running `python -X utf8 scripts/pixai_batch.py fetch --page 1`. Because PixAI does not store generated images indefinitely, fetch them promptly.

### Step 4. Adopt Candidates and Rebuild the Page

```powershell
python -X utf8 scripts/pixai_batch.py list --page 1
python -X utf8 scripts/pixai_batch.py adopt p01-02 --candidate 3      # Compare and pick a specific candidate
python -X utf8 scripts/pixai_batch.py adopt-latest --page 1           # Or adopt the latest candidate for every panel at once
python -X utf8 scripts/pixai_batch.py build --page 1                  # Add --write-psd when also creating a PSD
```

The output is saved to `output/build/page-01/vNNN/page-01.png` (and `page-01-display.png` for viewing).

---

## Work in the Browser (WebUI)

Instead of using the terminal, you can edit `.env.pixai` variables and requests (aspect ratio, `mode`, style preset, LoRAs), run generation, re-fetch interrupted tasks, adopt candidates, build PNG/PSD files, and flip through page previews in a browser UI.

```powershell
python -X utf8 .agents/skills/pixai-batch-webui/pixai_webui.py
```

Open the displayed `http://127.0.0.1:8775/?token=…` URL in your browser (the AI agent does not control a browser and only provides the URL). Press Ctrl+C to stop. See `.agents/skills/pixai-batch-webui/SKILL.md` for details.

---

## Helper Settings (`.env.pixai`)

`PIXAI_MODEL`, `PIXAI_QUALITY_TAGS`, `PIXAI_NEGATIVE_PROMPT`, and `PIXAI_PROMPT_HELPER` are used when assembling requests with `pixai_compose.py`. Changing them does not automatically modify existing request JSON files; to apply them to existing requests, edit or re-assemble those requests. `PIXAI_CHECK_IDENTITY` is used during pre-generation checks.

```dotenv
# Model (tsubaki2, tsubaki3, haruka2, hoshino2, or a model version ID)
PIXAI_MODEL="tsubaki2"
# Full quality-tag string (leave empty to disable; defaults to masterpiece, best quality)
PIXAI_QUALITY_TAGS="masterpiece, best quality"
# Default negative prompt attached to all requests (defaults to these 4 terms if unset; leave empty to disable)
PIXAI_NEGATIVE_PROMPT="text, speech bubble, panel border, watermark"
# Pre-send automatic prompt rewriting (defaults to disable; setting enable may cause divergence from the storyboard)
PIXAI_PROMPT_HELPER="disable"
# Automatic character identity-feature check (1 = enabled; uses input/pixai/characters.json)
PIXAI_CHECK_IDENTITY=1
```

Use `scripts/pixai_compose.py` when creating or re-assembling request JSON files (see examples in [PixAI Production Procedure](../knowledge/pixai-composed-production.md#compose)). List available style presets with `python -X utf8 scripts/pixai_compose.py --list-styles`.

---

## Troubleshooting Common Errors

| Message / Situation | Primary Cause | Solution |
| --- | --- | --- |
| **Invalid variable name (`Invalid variable:`)** | Variable name does not match naming rules | Start with `PIXAI_CHAR_`, `PIXAI_STYLE_`, `PIXAI_BACKGROUND_`, or `PIXAI_LORA_`, using only uppercase ASCII letters, digits, and `_` |
| **Variable X is missing in `.env.pixai` (`Variable ... not found in .env.pixai`)** | Variable is not set | Check whether the line exists in `.env.pixai` or whether `env-set` was run |
| **Duplicate variable across multiple sources (`Duplicate variable in multiple sources:`)** | Defined in both `.env.pixai` and environment variables | Keep the definition in only one place |
| **`PIXAI_LORA_` value must be a LoRA version ID (`PIXAI_LORA_ value must be a LoRA version ID`)** | Non-numeric characters in the LoRA value | Write only the final number from the LoRA page URL |
| **Cost is unconfirmed (`Credit consumption is unconfirmed`)** | Missing `--confirm-credits` | Check your credit balance and scope, and attach `--confirm-credits` only when authorizing credit usage |
| **Request contains parameters not in current official docs (`Contains parameters not in the current official documentation:`)** | Request uses i2i, inpainting, ControlNet, reference images, v1 seed, etc. | Attach `--allow-unverified` only if you agree to use them. Even for parameters verified in this kit (`docs/knowledge/pixai-api.md`), behavior may change without notice |
| **Execution record without an image (`Execution records without images exist:`)** | Polling was interrupted mid-wait, or transmission outcome is unknown | First try `fetch --ids p01-02`. If there is no `taskId` and it cannot be fetched, check generation status and credits in the PixAI web UI, then move the record to `failed/` with `move-unknown --ids p01-02 --confirm-checked --note 'What was verified'` (nothing is deleted) |
| **`HTTP 400` [Input error]** | Request parameter was rejected (e.g., sending `mode` to an SDXL model) | Inspect the response message and fix the request. No task was created, and the record is automatically moved to `failed/` |
| **`HTTP 429` [Rate / queue limit]** | Reached 10 concurrent waiting tasks or hit a rate limit | Wait briefly before sending again |
| **Changed settings, but the image did not change** | Regeneration, adoption, or `build` has not been completed | Verify in order: `generate` → `adopt` / `adopt-latest` → `build` |

- **Canonical procedures**: [PixAI Production Procedure](../knowledge/pixai-composed-production.md#character-variables), [PixAI API Connection Procedure](../knowledge/pixai-api.md)
- **Per-project commands and adoption records**: [PixAI Batch Generation Log](../production/PIXAI-BATCH.md)
