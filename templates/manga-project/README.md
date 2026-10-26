# Manga project

This is the project folder for an individual comic work. Open this folder—at the absolute path shown when it was created—in Codex (or your chosen AI agent) and begin comic production in a **new conversation** (reopening from the distribution kit is required).

---

## 1. First production request (getting started)

Provide characters, a synopsis, and a page count to produce all pages of a web comic through PNG previews without extra configuration (one environment capable of generating or editing images is required).

> **Example first request:**
> "Make a 2-page comic with a punchline at the end where two women play a game on their day off. First check what image-generation methods are available, and take it through web PNG previews. No PSD is needed."

- **The AI updates the record files**: The project title and source kit are recorded in `project.json`. At the start of production, the AI agent checks [OPTION.md](OPTION.md) and creates/updates `docs/story/BRIEF.md`, `docs/PLAN.md`, and `docs/PROGRESS.md`, so humans do not need to fill out every file by hand before starting.
- **Changing preferences**: The defaults are single pages, white background, left-to-right reading, and horizontal English lettering. Only when you want to change an item, edit "Current setting" in [OPTION.md](OPTION.md) or state your preference in conversation (unspecified items use defaults; later edits require intent confirmation).
- **If you need help reopening the folder**: Tell Codex your environment (Windows or Mac, app or VS Code), and it will check current official information and explain the steps with source URLs and check date. If you already know how, simply open this folder without replying ([Reopening instructions](docs/knowledge/codex-operation.md#reopen-codex-in-the-project-folder)). No in-kit production exception file is needed in this project folder.

---

## 2. Preparation and editing guides by drawing method

Refer to the following procedures and guides for the drawing method you use (you do not need to configure every service):

| Drawing method | Overview and handling of text and frames | Reference guides (user guides / procedures) |
| --- | --- | --- |
| **Built-in `imagegen`**<br>(available Codex environments) | Supply a numbered layout reference image and each panel's contents, and **generate the whole page at once with text and balloons included** by default. Fit frames and final PNG dimensions to the actual generated image dimensions | [Panel layout workflow](docs/knowledge/panel-layout-policy.md), [Basic-frame settings](docs/knowledge/page-layout.md) |
| **NovelAI API**<br>(per-panel generation + typesetting) | Generate artwork without text or frames, then typeset frames, balloons, and horizontal English dialogue afterward with `scripts/typeset_manga.py`, etc. Set the API key in `.env` or `.secrets/novelai.env` | - Initial setup: [Setup](docs/SETUP.md), [API connection procedure](docs/knowledge/novelai-api.md)<br>- Changing appearance: [Editing and regenerating characters, style, and backgrounds](docs/novelai-prompts/README.md)<br>- Browser UI: [NovelAI WebUI (port 8765)](.agents/skills/novelai-batch-webui/SKILL.md)<br>- Production workflow: [NovelAI production workflow](docs/knowledge/novelai-composed-production.md) |
| **PixAI API**<br>(per-panel generation + typesetting) | Generate artwork without text or frames using the 15 official models, LoRA, etc., then typeset frames, balloons, and horizontal English dialogue afterward. Set the API key in `.env` or `.secrets/pixai.env` (generation requires explicit authorization for credit consumption) | - Initial setup: [Setup](docs/SETUP.md), [PixAI API connection procedure](docs/knowledge/pixai-api.md)<br>- Changing appearance: [Editing and regenerating characters, style, backgrounds, and LoRA](docs/pixai-prompts/README.md)<br>- Browser UI: [PixAI WebUI (port 8775)](.agents/skills/pixai-batch-webui/SKILL.md)<br>- Production workflow: [PixAI production workflow](docs/knowledge/pixai-composed-production.md) |
| **External generation / rough-reference i2i**<br>(ComfyUI / Qwen, etc.) | Supply roughs and character reference images to draw per panel, then typeset frames, balloons, and text afterward | [Per-panel drawing with external generation](docs/knowledge/external-panel-i2i.md), [Qwen-Image 2.1](docs/knowledge/image-generation/qwen-image-2.1.md) |

- **Files bundled in the project vs. kit-side references**: Shared knowledge, skills, and scripts are copied into this project folder, whereas **NovelAI style samples** (`resources/novelai-style-samples/index.html`) and **PixAI model and style samples** (`resources/pixai-model-samples/index.html`) reference the distribution kit (`sourceKitRelativePath` in `project.json`).

---

## 3. PNG review, PSD handoff, and print settings

- **Review and revise with PNG previews first**: Move from the text storyboard to thumbnails and artwork, then review and revise using PNG previews first. Wait for the user's response confirming PNG revisions.
- **Create PSDs only when requested**: Once no PNG revisions remain, check whether PSD creation was requested; if not, ask whether to create one and wait for the answer. If already requested, do not ask again—create, validate, and hand off a manuscript meeting the [PSD requirements](docs/knowledge/psd-handoff.md) (example request: "After PNG confirmation, make a PSD with art, balloons, and text separated").
- **PSD layers and text handling**: A PSD stores the assets that were actually kept separate during production (untouched original art, masked placed images, balloons, and rasterized text layers in NovelAI / PixAI typesetting). An image generated all-in-one with art and text by `imagegen` is not automatically split into part-specific layers or editable text strings. So that lettering can be re-entered in CLIP STUDIO PAINT or similar software, the finalized dialogue text is also saved and handed off in [Dialogue source and placement](docs/production/DIALOGUE.md).
- **Finishing, publication, and print settings**: Normally a human finishes the work in CLIP STUDIO PAINT before external publication, though this is not required if you only want web PNGs. CBZ files are created only on explicit request. Print-only settings are separated into [PRINT-OPTION.md](PRINT-OPTION.md) and need not be filled out for web production.

---

## 4. Optional features (used only when needed)

- **Scene-specific supervision (16 themes)**: Use [Scene supervision](docs/knowledge/supervision/README.md) and [Supervision records](docs/reviews/SUPERVISION.md) for staging consultations and post-PNG improvement suggestions covering humor, appeal, emotion, relationships, and developments.
- **Optional Japanese polishing skills**: [Legacy Japanese polishing skills](docs/knowledge/optional-skills.md) are disabled by default in the English workflow and apply only when selected in [OPTION.md](OPTION.md) for Japanese source text; they are not an English polishing feature. When enabled for that work, installation runs at the first work session in this project. `humanizer-jp` uses Git; ask before installing missing Git. `japanese-natural-writing` uses Gemini, so always confirm permission to transmit text and consume quota before installation even when the environment is available. With silence or refusal, defer installation and continue normal comic production.
- **Registering personal required steps (process checker)**: If there is a step you want to make mandatory from next time onward, say for example, "Register character review after completing the text storyboard as an 'instruction.'" The [process checker](docs/knowledge/process-checker.md) discusses content, conditions, checkpoints, evidence, and carryover scope. An "instruction" is checked during stage reports; a "strong instruction" is also reflected in `AGENTS.md`, with Hooks added if needed (if delegated, Codex chooses details). The distributed list is empty, and an empty list requires no detailed checks. Carryover to the next project happens only when the source project is explicitly named.
- **Feedback records**: Record in `docs/feedback/` following the [Feedback workflow](docs/knowledge/feedback-workflow.md) only when asked to retain feedback.

---

## 5. Agent operating rules and detailed references

- **Browser control prohibition**: Launching, connecting to, or controlling Chrome or Edge and using `chrome:control-chrome` by Codex or other agents is prohibited. Inspect images with image-viewing tools; the human opens supplied local WebUI URLs and sample HTML paths.
- **Know-how index**: [Comic production know-how index](docs/MANGA-KNOWHOW.md) (78 techniques, comic fundamentals, staging and comparison procedures, and record templates; film and television references are consulted only as support where needed).
- **Shared knowledge and skill mapping**: [Production workflow](docs/knowledge/review-workflow.md), [Shared know-how](docs/knowledge/review-workflow.md#common-knowledge)
- **Command to check review settings (optional)**: `.\scripts\Resolve-ReviewProfile.ps1 -Preset 'daily'` (on Linux: `bash scripts/Resolve-ReviewProfile.sh`)
- **Bundled toolkit license**: [MIT License](docs/toolkit-license.txt) (these terms do not automatically apply to the comics you create or the assets you bring in)
