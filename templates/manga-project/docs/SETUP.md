# Initial environment setup

On first project work resolve OPTION's Japanese polishing setting and run `scripts/Initialize-OptionalSkills.ps1`. It is disabled by default in English work and applies only to explicitly selected Japanese source text. Install into project `.agents/skills/` only if enabled. Ask before installing missing Git; before installing a Gemini variant obtain quota-consumption permission even if the environment is available. With silence/refusal, continue normal production. See [Initial installation](knowledge/optional-skills.md).

Reopen Codex from the distribution kit into the work folder at the absolute path displayed during creation before setup. If unsure, tell Codex your environment (Windows/Mac, app/VS Code). Only if instructions are requested, Codex follows [Reopening](knowledge/codex-operation.md#reopen-codex-in-the-project-folder), checks current official information for the environment, and explains it. Confirm current folder contains this work's `project.json` and `AGENTS.md`.

The title is recorded in `project.json`. Adapt `config/review-profiles.json` defaults and add needed scene overrides. Examples/meaning: `knowledge/review-workflow.md`.

Store project inputs in `input/`, character references in `assets/characters/`, background/other references in `assets/references/`, ComfyUI workflows in `workflows/`, and outputs in `output/`. Keep instructions, acceptance, and validation in `docs/`.

For image work, verify local ComfyUI relative path, GPU, models/versions, and startup procedure; record nonsecret details in `docs/experiments/`. Startup authorization follows the user's instructions for this work. No initialization automatically installs models or LoRA.

For explicit requests to test cinematic staging with video, use optional `manga-video-previsualization` and [Video workflow](knowledge/video-previsualization.md). Put a verified workflow in project `workflows/` and check model/input mapping before execution. References go in `assets/characters/`, video/audio in `output/`, and conditions/timing/acceptance in `docs/experiments/`. This is not a prerequisite for ordinary comic work.

Bundled `scripts/novelai_api.py` supports key loading, subscription lookup, and single-image generation. Python 3.10+; no additional packages. See [NovelAI API setup](knowledge/novelai-api.md). Set actual keys in `NOVELAI_API_KEY` environment variable or project `.secrets/novelai.env`, never `.env.example`. First run `python -X utf8 scripts/novelai_api.py key-status` to check source, then `python -X utf8 scripts/novelai_api.py status` for subscription lookup without generation. Even generation commands send nothing without `--execute`.

For file setup, write this complete line in `.secrets/novelai.env`, **including the name and `=`, not just the token**:

```dotenv
NOVELAI_API_KEY=YOUR_ACTUAL_TOKEN
```

The left-hand `NOVELAI_API_KEY` is a public setting name; the right-hand token is secret. Replace `YOUR_ACTUAL_TOKEN` with your Persistent API token. Do not paste it into conversation. Say "I want to use NovelAI" or "Check my NovelAI connection" for guidance. Missing file, missing setting, empty value, and invalid format are reported separately; connection failure is distinct from key configuration trouble.

Before execution check official specifications and available allowance. With active Opus, review [No-Anlas conditions](knowledge/ai-production.md#novelai-opus): one image, at most 28 steps (V5 initial 23, V4.5 and earlier 28). Generation dimensions follow tool-appropriate shared [Page settings](knowledge/page-layout.md). Verify 0 Anlas with adopted dimensions/model/extras and remaining V5 allowance. Successful subscription lookup alone does not establish cost/allowance confirmation. [Connection request prompts](knowledge/novelai-api.md#example-request-for-a-connection-check) are also available.

To edit NovelAI characters, style, and backgrounds yourself and regenerate, read the [prompt-editing README](novelai-prompts/README.md). Variables are created only on request; you can edit `.env` directly or apply edits from a text file.

Open the project root in a new Codex session and confirm AGENTS.md and local skills are recognized. Bundled skills work with this project's shared knowledge.

Choose needed references from [Know-how](MANGA-KNOWHOW.md). Review/revise PNG first, then proceed to PSD after no revisions remain. If no PSD instruction, ask and wait; do not re-ask existing instructions. Preserve separated assets/source dialogue for later PSD. Before PSD work, check creation/reopening tools and the environment for CLIP STUDIO PAINT verification; record PNG answers, PSD instructions, and specifications in [Handoff](production/PSD-HANDOFF.md). Create/validate requested PSDs and hand them to a human for finishing/publication. CBZ only on explicit request.
