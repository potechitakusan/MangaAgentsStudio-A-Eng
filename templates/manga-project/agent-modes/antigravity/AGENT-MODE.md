# Adaptations for Antigravity mode

This project was created with `New-MangaProject.ps1 -AgentMode Antigravity` or `New-MangaProject.sh --agent-mode Antigravity`. Apply this file only when `project.json` has `agentMode` set to `Antigravity`. `AGENTS.md` is authoritative for common rules; adapt Codex-specific passages as described below. All other rules still apply.

## Naming, starting, and resuming

- “Codex” in the documents means the Antigravity agent handling this project. Reopening guidance becomes “Reopen Antigravity in this folder.”
- Record the actual model name for reviewers and adopters. If unknown, use “Antigravity (model name unconfirmed)”; do not guess a version.
- Read `AGENTS.md`, this file, `project.json`, `docs/PROGRESS.md`, `docs/PLAN.md`, and `OPTION.md` before resuming. Save progress, plans, and adoption records in the project, rather than only in Antigravity Artifacts.
- Use the Bash entry points on Linux and PowerShell entry points on Windows. For initial/resumed optional-skill checks, use `bash scripts/Initialize-OptionalSkills.sh` on Linux or `scripts/Initialize-OptionalSkills.ps1` on Windows. Use the review-profile entry point for the same OS.
- Do not assume Codex-specific tools such as `wait_agent` exist. If delegation is needed, use the actual environment's procedure; the main agent integrates decisions.

## Artwork and composition

- Do not assume Codex imagegen is available. Before artwork, check this session's available generation, editing, and image viewing tools, the selected model, and input method. The Gemini model name alone does not establish image-generation capability.
- Default to NovelAI panel asset generation followed by separate composition. Follow `docs/knowledge/novelai-composed-production.md`, `config/novelai-production-policy.json`, and `scripts/novelai_batch.py`. Do not skip key/style/cost/allowance checks, character prototypes, request JSONs, adopted candidates, post-artwork comparison, or page rebuilding.
- If the user specifies another generation environment or supplied assets, follow that procedure. Do not apply imagegen-specific whole-page generation and lettering rules universally to other environments; add text and balloons after artwork according to the common policy.
- If generation tools or necessary settings are missing, defer artwork and explain the needed setup. Planning, text storyboards, and thumbnails may proceed. Do not substitute code-drawn pictures as finished artwork.
- If image editing is unavailable, use regeneration, placement changes, or plan revision. Report unresolved issues when presenting PNGs.

## Image inspection, browsers, and communication

- Open and inspect candidate images, adopted images, and final page PNGs using actual image viewing tools. Do not mark a comparison as visually reviewed based only on path existence, dimensions, or generation logs.
- If images cannot be displayed, record visual inspection as unperformed, provide PNG paths, and request user inspection. Do not launch a browser to open images.
- The Chrome/Edge launch, connection, and control prohibition also applies to Antigravity. Do not use its built-in browser, browser agents, Playwright, Selenium, CDP, headless execution, or the default browser. Research through search/retrieval without browser control. Give paths/URLs for users to open HTML or similar files.
- If permissions or sandboxing reject communication or commands, follow that environment's permission procedure. Do not change permission settings unilaterally or ask to reset keys merely because an operation failed. Since project destinations are outside the kit, also check the permitted working scope.

## Skills and optional Japanese polishing

- Use production skills in the project's `.agents/skills/`. Do not duplicate them in `.agent/skills/` or a global user store. Actually read the relevant stage's `SKILL.md`; refer to the same authoritative file even if automatic recognition fails.
- Optional Japanese polishing is disabled by default and applies only to Japanese source text, not English prose. Do not use installed skills while disabled. When enabled, explicitly apply only the selected skill to selected targets. Do not assume the implicit-invocation setting in `agents/openai.yaml` works in Antigravity.
- Producing with Antigravity does not authorize installation or additional calls of optional Gemini polishing skills. Follow `docs/knowledge/optional-skills.md` for consent before installation, pinned-version checks, and project-specific consent records.
- If third-party skills require Codex comparison or a specific CLI/model, read their execution contract. Do not silently substitute Gemini self-review, another CLI, or another API. Defer only polishing that lacks its required environment and continue ordinary production.

## Scope and sources

The Japanese source records a check date of 2026-10-03. Distinguish its official-documentation findings from this kit's production proposals; this translation did not repeat external verification.

- [Rules](https://www.antigravity.google/docs/rules/): recognition of `AGENTS.md` and `GEMINI.md`, and content expansion with `@[label](path)`. Ordinary `@filename` does not expand content.
- [Agent skills](https://www.antigravity.google/docs/skills?tab=ide): recognition of project `.agents/skills/` and `SKILL.md`.
- The artwork, permission, and record adaptations above are kit operating policies. Reading rules, displaying images, generation, and optional-skill execution in an actual Antigravity environment remain unverified. Distinguish the source's earlier Debian checks of Linux entry points from verification of Antigravity support.
