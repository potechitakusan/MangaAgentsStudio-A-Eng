# Initial environment setup (SETUP)

Settings to verify first and preparation steps for each drawing method in this project folder created from the distribution kit.

---

## 1. First-run verification and folder structure

1. **Reopen the agent in the project folder**: From the distribution kit, reopen Codex (or your chosen AI agent) in the project folder at the absolute path displayed during creation and start a new conversation. Confirm that the current working folder contains this project's `project.json` and `AGENTS.md` and that local skills (`.agents/skills/`) are recognized. If you are unsure how to reopen it, tell Codex your environment (Windows or Mac, app or VS Code); only when instructions are requested, Codex follows [Reopening instructions](knowledge/codex-operation.md#reopen-codex-in-the-project-folder), checks current official information for that environment, and explains it.
2. **Folder roles**:
   - `input/`: Project-specific input data, NovelAI / PixAI request JSON files (`input/novelai/requests/` and `input/pixai/requests/`), page layout definitions (`input/pages/`), and typesetting definitions (`input/typeset/`)
   - `assets/characters/`: Character reference images; `assets/references/`: Background, prop, and other references; `assets/fonts/`: Project-specific fonts (optional)
   - `workflows/`: ComfyUI workflows (when using external generation or video previsualization)
   - `output/`: Generated candidate images, page PNG/PSD build outputs, and WebUI logs
   - `docs/`: Planning, text storyboards, thumbnails, reviews, and progress records

---

## 2. Configuration files (3-way split) and API key storage locations

Project configuration files are split into three by purpose (templates are in `.env.example`, `.env.novelai.example`, and `.env.pixai.example`; the `.example` files themselves are never loaded):

| File / location | Role and contents | Loading target and priority |
| --- | --- | --- |
| **`.env`**<br>(recommended first) | **Shared settings** such as API keys (`NOVELAI_API_KEY`, `PIXAI_API_KEY`) and endpoint URLs | Priority 4 for key loading (in order: `environment variable` → `.secrets/<service>.env` → `.secrets/.env` → `.env`) |
| **`.secrets/novelai.env`**<br>**`.secrets/pixai.env`** | Service-specific API-key files (`.secrets/.env` is also supported) | Priority 2 for key loading (`.secrets/.env` is Priority 3) |
| **OS environment variables** | `NOVELAI_API_KEY` / `PIXAI_API_KEY` | Priority 1 (highest) for key loading |
| **`.env.novelai`** | NovelAI character, style, and background prompt variables and helper settings | Used by `novelai_compose.py`, `novelai_batch.py`, and the NovelAI WebUI (do not put API keys here; migrate NovelAI variables placed in `.env` in older versions with `python -X utf8 scripts/novelai_batch.py env-migrate`) |
| **`.env.pixai`** | PixAI character, style, background, and LoRA prompt variables and helper settings | Used by `pixai_compose.py`, `pixai_batch.py`, and the PixAI WebUI (do not put API keys here) |

- **Caution when entering keys**: When configuring in a file, write the complete line **including the setting name on the left and `=`, not just the token or key value**. The setting name on the left is a public name; the value on the right is secret. **Never write actual secret values into conversations, public files, or `.env.example` files.**

---

## 3. Preparation by drawing method (configure only what you use)

### Shared: Preparing the Python environment and dependencies for PNG typesetting and PSD export

API communication, request JSON assembly (text only), and launching the WebUI itself run on the **Python 3.10+** standard library alone, whereas the following image-processing, typesetting, and PSD stages require additional packages:

- **PNG typesetting, mask creation, i2i/inpaint dimension checks, and WebP/JPEG response-to-PNG conversion**: Python 3.10+ and `Pillow`
- **Exporting and reload-verifying composed PSDs (`--write-psd`)**: **Python 3.12+** and the bundled `scripts/requirements-composition.txt` (`Pillow==12.3.0`, `numpy==2.5.3`, `psd-tools==1.19.0`). The required Python version for pinned `numpy==2.5.3` is `>=3.12` ([NumPy 2.5.3の配布情報](https://pypi.org/project/numpy/2.5.3/), checked 2026-10-25; scope is the pinned versions in the bundled dependency file).

> **Example request when asking the AI agent to check and prepare the environment:**
> "Without running generation or API calls, please check and prepare the required Python environment and dependency packages."

To check and install them yourself from a terminal at the project root, run the following (on Linux, replace `python` with `python3`; if you want to keep your existing Python environment separate, activate a virtual environment such as `venv` first):

```powershell
# 1. Check the current Python version and installed packages (no API communication)
python --version
python -c "import PIL; print('Pillow OK')"
python -c "import PIL, numpy, psd_tools; print('PSD dependencies OK')"

# 2A. When using PSD export and reload verification as well (Python 3.12+; installs bundled pinned dependencies)
python -m pip install -r scripts/requirements-composition.txt

# 2B. When using only PNG typesetting, mask creation, and image conversion (Python 3.10+)
python -m pip install Pillow==12.3.0
```

### A. Using Codex built-in image generation (`imagegen`)

No additional API key setup is required. Confirm that the image-generation tool is available in the current Codex session and proceed according to the [Panel layout workflow](knowledge/panel-layout-policy.md) and [Page settings](knowledge/page-layout.md).

### B. Using the NovelAI API

Bundled `scripts/novelai_api.py`, `scripts/novelai_compose.py`, and `scripts/novelai_batch.py` support automatic key loading, subscription lookup, request assembly, batch generation, candidate adoption, and page rebuilding (API communication and generation run on the Python 3.10+ standard library alone; typesetting and PNG `build` use `Pillow`; PSD export follows the shared requirements above and uses Python 3.12+ with `Pillow`, `numpy`, and `psd-tools`). See [NovelAI API connection procedure](knowledge/novelai-api.md) and [NovelAI production workflow](knowledge/novelai-composed-production.md) for details.

1. **Prepare the API key**: Write your Persistent API token on a single line in the project's `.env` or `.secrets/novelai.env` (or the `NOVELAI_API_KEY` environment variable):
   ```dotenv
   NOVELAI_API_KEY=YOUR_ACTUAL_TOKEN
   ```
2. **Check the connection without generation**: Say "I want to use NovelAI" or "Check my NovelAI connection" in the project, or run the following (missing file, missing setting line, empty value, invalid format, and connection failure are reported separately):
   ```powershell
   python -X utf8 scripts/novelai_api.py key-status
   python -X utf8 scripts/novelai_api.py status
   ```
   `key-status` is a local check with no external communication. `status` uses the API key in the authentication header to query subscription status without sending project prompts or images. [Example connection-check prompts](knowledge/novelai-api.md#example-request-for-a-connection-check) are also available.
3. **Assemble requests and verify costs**: As a rule, assemble request JSON files with `scripts/novelai_compose.py` (V5 is default, V4.5 only when specified by the user; see [Standard script usage](knowledge/novelai-api.md#compose-standard)). Generation commands send nothing without `--execute`. With an active Opus subscription, review the [No-Anlas conditions](knowledge/ai-production.md#novelai-opus) and use 1 image per request, 28 steps or fewer (initial value 23 for V5, 28 for V4.5 and earlier), and standard [Page settings](knowledge/page-layout.md) as the baseline. Verify 0 Anlas with the adopted dimensions, model, and extra features as well as remaining V5 allowance, and run paid (Anlas-consuming) generations only within the explicitly instructed scope (a successful subscription lookup alone does not complete cost and allowance verification).
4. **Prompt variable editing and local WebUI**: To edit characters, style, and backgrounds yourself and regenerate, see the [NovelAI prompt-editing README](novelai-prompts/README.md) (variables are created only on request; you can choose between editing `.env.novelai` directly and applying edits from a text file). Once request JSON files and page configurations are ready, you can also run `python -X utf8 .agents/skills/novelai-batch-webui/novelai_webui.py` at the project root to operate from a browser UI (default port `8765`; see [NovelAI WebUI skill](../.agents/skills/novelai-batch-webui/SKILL.md)).

### C. Using the PixAI API

Bundled `scripts/pixai_api.py`, `scripts/pixai_compose.py`, and `scripts/pixai_batch.py` support key loading, authentication checks, request assembly, batch generation, re-fetching (`fetch`), candidate adoption, and page rebuilding. For settings and features (15 official models, LoRA, 35 style presets, mode, and reference images), see [PixAI API connection procedure](knowledge/pixai-api.md) and [PixAI production workflow](knowledge/pixai-composed-production.md).

Ordinary text-only request creation and authentication checks run on the Python 3.10+ standard library. **Creating i2i and inpaint requests** requires `Pillow` to check source-image and mask dimensions. Converting WebP/JPEG responses to PNG, creating masks, and building page PNGs also use `Pillow`. PSD export follows the shared requirements above.

1. **Prepare the API key**: Create a key in [PixAIのAPI設定](https://pixai.art/profile/edit/api) and write it on a single line in the project's `.env` or `.secrets/pixai.env` (or the `PIXAI_API_KEY` environment variable):
   ```dotenv
   PIXAI_API_KEY=YOUR_ACTUAL_KEY
   ```
2. **Check the connection without generation**:
   ```powershell
   python -X utf8 scripts/pixai_api.py key-status
   python -X utf8 scripts/pixai_api.py status
   ```
   `key-status` is a local check with no external communication. `status` uses the API key in the authentication header to verify authentication without sending project prompts or images.
3. **Confirm credit consumption and generate**: Because PixAI generation consumes credits and there is no balance-check API, send with `--confirm-credits` and `--cost-note` only within the scope explicitly permitted by the user (4 candidates per task with `batchSize: 4` generates 4 images' worth). Even if you stop waiting mid-run, a task already created on PixAI continues, so re-fetch with `pixai_batch.py fetch` before regenerating.
4. **Prompt variable editing and local WebUI**: For editing variables, see the [PixAI prompt-editing README](pixai-prompts/README.md). Once request JSON files and page configurations are ready, you can also run `python -X utf8 .agents/skills/pixai-batch-webui/pixai_webui.py` at the project root to operate from a browser UI (default port `8775`; see [PixAI WebUI skill](../.agents/skills/pixai-batch-webui/SKILL.md)).

### D. Using local ComfyUI or external generation

During image work, verify the relative path to local ComfyUI, GPU, models, versions, and startup procedure, and record non-secret details in `docs/experiments/`. Authorization to start an existing environment follows the user's instructions for this project (no initialization step automatically installs models or LoRA). For per-panel drawing steps, see [Per-panel drawing with external generation](knowledge/external-panel-i2i.md).

---

## 4. Optional feature configuration (only when needed)

- **Optional Japanese polishing skills (disabled by default)**: In a project where a Japanese polishing skill is enabled in [OPTION.md](../OPTION.md) for Japanese source text, run `scripts/Initialize-OptionalSkills.ps1` (on Linux: `scripts/Initialize-OptionalSkills.sh`) at the first work session to install it into `.agents/skills/`. If Git is missing for `humanizer-jp`, ask whether to install Git; for `japanese-natural-writing`, which uses Gemini, always obtain **permission to transmit text and consume quota** before installation even when the environment is available. With silence or refusal, continue normal production ([Initial installation procedure](knowledge/optional-skills.md)).
- **Adjusting review priorities (optional)**: Adapt `defaults` in `config/review-profiles.json` to the project and add needed scenes under `scenes`. For resolution examples and meanings, see [Review workflow](knowledge/review-workflow.md).
- **Video previsualization (only on explicit request)**: Only when explicitly asked to test cinematic staging in video, use the `manga-video-previsualization` skill and [Video previsualization workflow](knowledge/video-previsualization.md). Place a verified video workflow in the project's `workflows/` and check model and input mappings before execution (character references go in `assets/characters/`, video and audio in `output/`, and conditions, duration, and adoption decisions in `docs/experiments/`). Do not make this a prerequisite for ordinary comic production.

---

## 5. From PNG review to PSD handoff

Select the needed guidance from the [Know-how index](MANGA-KNOWHOW.md) and proceed with production.

1. **Review and revise with PNG previews**: First create PNG previews to review and revise. Keep separated production assets and the dialogue source text so a PSD can be built later.
2. **Create and verify PSDs only when requested**: Proceed to PSD creation only after no PNG revisions remain. If there is no PSD instruction, ask whether to create one and wait for the answer; if already instructed, do not ask again. When proceeding to PSD creation, check the tools for creating and reloading PSDs and the environment for verifying them in CLIP STUDIO PAINT, and record PNG review answers, PSD instructions, and specifications in [Handoff records](production/PSD-HANDOFF.md) and [Dialogue source](production/DIALOGUE.md) (details in [PSD handoff rules](knowledge/psd-handoff.md)).
3. **Finishing and publication**: Create and verify requested PSDs and hand them off to a human, who normally finishes and publishes the work in CLIP STUDIO PAINT. Create CBZ files only on explicit request.
