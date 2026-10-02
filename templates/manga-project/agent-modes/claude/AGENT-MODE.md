# Claude mode adaptations

This work was created with `New-MangaProject.ps1 -AgentMode Claude` (`agentMode` in `project.json`). The kit primarily targets Codex with built-in image generation; interpret the following parts of AGENTS.md, OPTION.md, and shared knowledge through this file. All other AGENTS.md rules still apply.

## Names and records

- "Codex" in documents means the agent working on this project (Claude). Apply the same convention in user guidance.
- In progress, checklists, and acceptance records, use the actual agent/model name as reviewer/selector (for example, the configured Claude model), not "Codex." Original Japanese examples included Claude Sonnet 5.5 and Claude Opus 5.5; these examples do not verify model availability.
- Codex-specific tools such as `wait_agent` do not apply. Use the active environment's subagent procedures for delegation.

## Artwork tools

- This Claude mode assumes no built-in image generation. imagegen rules (whole-page generation with numbered references, local/final edits, and OPTION's imagegen generation unit) do not apply. Do not record imagegen use that did not occur.
- Default artwork is NovelAI panel assets followed by composition (`docs/knowledge/novelai-composed-production.md`, `scripts/novelai_batch.py`). Follow that document and AGENTS.md for request JSON, character trials, prompt checks, post-artwork comparison, and rebuilding with `build`.
- If the user specifies another external environment such as ComfyUI or supplied assets, follow that environment's workflow. Do not treat unavailable tools/APIs as available.
- If artwork tools are unavailable, or NovelAI key/style is missing, pause artwork and explain needed settings/options. Independent planning/text/rough storyboards may continue. Do not fabricate finished artwork with substitutes lacking image generation, such as code-drawn illustrations.
- Without local image-editing capabilities, correct via regeneration, placement changes, or plan revision. Disclose unresolved problems when presenting PNGs.

## Image inspection

- Actually open candidate/adopted images and rebuilt PNG pages with Read. Do not fill comparison tables without opening images.
- With many candidates, first open those needed under the text-storyboard plan. Do not base acceptance on unopened candidates.

## Execution environment

- Claude Code permission settings may require confirmation or reject NovelAI network calls through `scripts/novelai_api.py` and `scripts/novelai_batch.py`. If rejected, do not change settings on your own; explain required permission. Connection failure alone is not grounds to recommend changing an API key.
- AGENTS.md's browser launch/control prohibition also applies to Claude.
