# Architecture and Distribution

This kit is maintained for distribution; ordinary comic production takes place in separate projects outside it. Do not write a work directly into `templates/manga-project/`; copy it into a project with `scripts/New-MangaProject.ps1`. Production inside the kit requires an explicit user instruction and verification of `特別な理由でこのフォルダの中で漫画を作ります.txt`, created personally by the user in the root. See the [Exception procedure](../README.md#exception-producing-a-comic-inside-the-kit). The Japanese marker filename is retained for compatibility.

## File responsibilities

| Location | Purpose | Included in new projects |
| --- | --- | --- |
| `docs/knowledge/manga/` | Comic workflows and techniques, including integrated general knowledge of character, information, performance, and payoff | Copied to the same relative path |
| Files directly in `docs/knowledge/` | Detailed perspectives such as readability, common review, and operations for PSD, settings, and tools | Copied to the same relative path |
| `docs/knowledge/image-generation/` | Model/version/environment-specific image inputs and observations, plus anonymized production evidence summaries | Copied to the same relative path; no project original art or logs |
| `docs/knowledge/supervision/` | Scene-specific supervision knowledge, sources, and procedures | Explicitly listed documents and manifest included |
| `skills/` | Master copies of role-based skills | Copied to `.agents/skills/` |
| `templates/manga-project/` | Project settings, record templates, and panel-layout assets | Copied to the project root |
| `templates/manga-project/docs/knowledge/novelai-composed-production.md` | Master procedure for NovelAI style selection, asset generation, and lettering | Copied from the template to `docs/knowledge/novelai-composed-production.md` |
| `resources/novelai-style-samples/` | Kit-only visual samples of NovelAI style options | Bundled only with the kit; not copied into projects |
| `templates/manga-project/OPTION.md` | Initial choices for purpose and preferences, based on web production | Copied to the project root; application procedure in `docs/knowledge/project-options.md` |
| `templates/manga-project/PRINT-OPTION.md` | Settings, specifications, and verification records used only when printing is selected | Copied to the project root; disabled by default |
| `templates/manga-project/config/page-layout.json` | Requested generation size, frame placement, final PNG dimensions, scaling bases for margins/lines, and fixed overrides | Copied to the same path. Version 2 fits actual generation dimensions; placement processing also reads version 1 fixed sizes |
| `templates/manga-project/config/optional-skills.json` | Sources, pinned versions, and hashes for optional polishing skills | Copied to the same path; no third-party skill text |
| `templates/manga-project/config/process-requirements.json` | Empty template for personal required steps | Only an empty array is distributed; explicit carryover from another project is handled separately during creation |
| `scripts/process_checker.py` | Register requirements, manage evidence, reflect strong instructions in AGENTS, and support optional hooks | Copied to `scripts/` |
| `templates/manga-project/scripts/novelai_api.py` | Read a project's NovelAI key, query subscription without generating, and generate one image only on explicit execution | Copied to `scripts/`; Python standard library only; no credentials distributed |
| `templates/manga-project/scripts/novelai_batch.py` | Sequential generation of per-panel request JSON by page or all pages, candidate adoption, expansion of per-character prompt variables (`NOVELAI_CHAR_*` in `.env`), and rebuilding page PNG/PSD from adopted images, placement, and lettering in a human-repeatable form | Copied to `scripts/`; uses `novelai_api.py` for generation, `typeset_manga.py` for lettering, and `export_composed_psd.py` for PSD |
| `templates/manga-project/scripts/typeset_manga.py` | Transparent layers for balloons, horizontal English dialogue, in-art text, and panel borders; checks punctuation, tails, overlaps, and reading order. Does not alter artwork | Copied to `scripts/`; uses Pillow. Fonts are not bundled; use project `assets/fonts/` or OS fonts |
| `templates/manga-project/config/novelai-request.example.json` | Generation request example with model and prompt unset | Copied to the same path; create actual request JSON in the project after selection |
| `scripts/New-MangaProject.ps1` | Create projects; `-AgentMode` (`Codex` default, `Claude`, or `Antigravity`) selects extra agent-specific files | Not copied |
| `templates/manga-project/agent-modes/claude/` | Claude-mode `CLAUDE.md` (loads AGENTS and adaptations) and `AGENT-MODE.md` (adapts Codex assumptions) | Excluded from the default bulk copy; copied to the project root only with `-AgentMode Claude` |
| `scripts/Resolve-ReviewProfile.ps1` | Resolve review priorities | Copied to `scripts/` |
| `scripts/Initialize-OptionalSkills.ps1` | Install enabled polishing skills at the first project work session; Gemini variant only after authorization | Copied to `scripts/`; not run during project creation |
| `scripts/validate_panel_plan.py` | Validate panel-plan rules | Copied to `scripts/` |
| `scripts/prepare_page_layout.py` | Scale borders, margins, and line widths to actual generated PNG dimensions or specified dimensions; record dimensional relationships and export guides separately | Copied to `scripts/`; Python standard library only. Image generation, resizing, and final PNG saving are separate production operations |
| `scripts/build_panel_templates.py`, `scripts/render_panel_templates.py`, `scripts/render_panel_templates.cjs`, `scripts/check_panel_templates.py` | Generate and inspect frame assets for kit maintenance. Python/Pillow renders from catalog geometry; the CJS compatibility wrapper invokes Python without a browser | Not copied |
| `scripts/video/` | Optional video generation and editing support | Copied to the same relative path |
| `tests/` | Distribution and video-editing verification | Not copied |
| `examples/` | Public example PNG/JPEG images and descriptions in Git | Not copied |
| `backup/`, `.work/` | Private backups and verification outputs | Excluded from publication and distribution |
| `特別な理由でこのフォルダの中で漫画を作ります.txt` | Created by the user only for exceptional production inside the kit | Excluded from publication and distribution |

Maintain templates, common knowledge, and skills separately, then assemble them into one project at creation. Production knowledge and scripts are bundled in the project. Direct users to the kit's HTML location for NovelAI style samples. Record the version and each file's SHA-256 in `docs/distribution-snapshot.json`; record project name, creation date, distribution version, and copy source in `project.json`. Its `sourceKitRelativePath` is the path from project root to kit, calculated from actual locations by the creation script. To direct users to samples, resolve it, append the configured `kit_sample_library_relative_path`, and verify existence only. If movement breaks the path or an older project lacks the record, ask for the location; do not guess. Store working paths relatively.

### Authoritative sources for per-panel image generation

Use `manga-ai-production` to select the generation method and `skills/manga-external-panel-i2i/SKILL.md` for image-conditioned panel art. Consolidate shared judgments in `docs/knowledge/external-panel-i2i.md`, model-specific symptoms and input examples in `docs/knowledge/image-generation/`, and connections and costs in existing documents such as `docs/knowledge/novelai-api.md`. Do not add a separate skill merely for each model name.

Common and model documents are distributed through recursive knowledge copying; skills through skill copying. Keep the NovelAI composition master in the template path above, without a duplicate in the kit's knowledge directory. Its links and the know-how index use `docs/knowledge/` as assembled in the project. In the kit, refer to the master listed above.

The 2026-09-26 integration moved common stages from the existing Qwen skill into a shared skill and organized inputs and observations into the Qwen document and evidence summary. The kit does not duplicate the old skill name or automatically replace `manga-qwen-reference-production` already installed personally or in existing projects. For updates, compare the project's usage restrictions and actual input records. Keep pending NovelAI verification in the kit's private `docs/PLAN.md`; do not copy it into new project plans.

## Create a new project

In version 0.3.2, `manga-supervision` covers existing comedy guidance plus 15 experimental themes, for script consultation and image review. Procedures belong in the skill, knowledge in thematic `docs/knowledge/supervision/` documents, and the 15 themes' sources in that directory's `sources.md`. The main agent integrates acceptance decisions; a continuously running independent agent is not required.

Integrate general knowledge into existing documents with the same purpose and distribute it as ordinary knowledge. Use [Common knowledge and skill mapping](knowledge/review-workflow.md#common-knowledge) as the entry point, organizing by purpose and review perspective. Only supervision knowledge is controlled by the explicit `docs/knowledge/supervision/distribution.json` list: exclude `supervision/` from ordinary copying, then include it once. When adding or changing supervision documents, align the list, allowed paths, and `.gitignore`. Do not run distribution or publication tests after every edit. When the user requests pre-commit checks, confirm targets and scope under the [Publication procedure](publication.md) before running them.

Run from the repository root; the folder name is not fixed.

```powershell
.\scripts\New-MangaProject.ps1 -ProjectName 'My Comic' -WhatIf
.\scripts\New-MangaProject.ps1 -ProjectName 'My Comic'
# Use an existing parent folder by relative path
.\scripts\New-MangaProject.ps1 -ProjectName 'Another Comic' -DestinationParent '..'
```

The kit primarily targets Codex with its available built-in image generation. Only `-AgentMode Claude` adds the two `agent-modes/claude/` files to the project root and records `agentMode` in `project.json`. Do not rewrite the main `AGENTS.md`, `OPTION.md`, or common knowledge; adapt Codex-specific assumptions such as imagegen, naming, and `wait_agent` through `AGENT-MODE.md`. The default `Codex` mode creates neither file. Do not duplicate common knowledge for Claude or automatically generate Claude Code permissions. Keep scope notes in private work records.

The default destination is `../My Comic/`. Ordinary production destinations remain outside the kit even with a different `-DestinationParent`. Names may contain Japanese characters, English letters, digits, spaces, hyphens, and underscores. Paths and Windows reserved names are not allowed as names. Existing folders are not overwritten; `-WhatIf` creates no files.

On success, show the absolute destination path and instructions to reopen Codex. The returned `Path` is relative to the caller; `AbsolutePath` is for user display. Do not store absolute paths in `project.json` or `docs/distribution-snapshot.json`. Codex verifies the actual destination and provides both a clickable Markdown link and the same absolute path as copyable text, adding: “If you need help, tell me your environment (Windows or Mac, app or VS Code), and I can explain the steps.” Do not research reopening instructions after every creation; only when requested, consult current official information for the user's environment and include source URLs and check date. See [Reopening instructions](knowledge/codex-operation.md#reopen-codex-in-the-project-folder).

Begin production after opening a new Codex conversation in the project. Merely changing directory from a conversation in the kit does not complete the project switch. The distributed `AGENTS.md` contains project rules and does not require the kit's exception marker.

The creation script locates masters relative to itself. It uses resolved paths internally to check destinations without embedding a specific machine or folder name. Before distribution, it rejects names used for secrets, unexpected formats, and links that lead outside the source. Partial folders from a failed run remain for investigation.

## Personal required steps

The [Process checker](knowledge/process-checker.md) uses `skills/manga-process-checker/` and the project's `config/process-requirements.json`. The authoritative standard workflow remains `docs/knowledge/manga/08-workflow-review.md`; do not maintain a duplicate. Add only requirements the user asks to register. With zero entries, do not perform detailed requirement matching.

Store them in the project. On resume, reread that same authoritative file and `.work/process-checker/` records. Only when creation specifies `-ProcessRequirementsFrom`, copy instructions marked `carryForward: true` from the named source project. Reflect strong instructions in the new AGENTS.md and record the actual hashes of the two changed files in the creation snapshot. Store the source in `project.json` as the relative `processRequirementsSourceRelativePath`.

Do not copy the source project's implementation records, assets, hook configuration, trust, or external-service permissions. Preserve requests for hooks as instructions and configure/review them separately in the new environment. New projects without a named source begin with an empty list. Do not automatically migrate existing projects or synchronize between projects or with user-wide settings. Creation and publication inspections reject personal instructions, check records, or hooks in distribution templates. Track the empty master in the kit's Git; at creation, append exclusion of the personal master to the project's `.gitignore` and record that file's updated hash too.

## Updates and feedback

The initial public release was `0.1.0`. Later releases update `distribution-version.txt`. Existing projects do not synchronize automatically; compare against their local changes when an update is needed.

Version `0.3.1` placed general knowledge in `docs/knowledge/manga/` and existing documents directly under knowledge, and comedy supervision in `docs/knowledge/supervision/gag/`. Version `0.3.2` bundles 15 scene-supervision themes and their source register. Themes are listed in `docs/knowledge/supervision/README.md`; allowed files in `distribution.json`. Older projects remain usable with their own arrangement and skills. When migrating one, check its referenced skills, documents, and distribution records together with the knowledge.

Record project feedback only when the user asks for it. Do not ask whether to record it or prepare routine feedback candidates. Continue ordinary progress, production decisions, and delivery verification as needed. See [Feedback workflow](knowledge/feedback-workflow.md).

English-edition maintenance guidance is kept in `docs/localization/`. Preserve source provenance and distinguish translation updates from changes in production behavior.

## Portable entry points and Antigravity mode (0.4.2)

| Source | Role | Distribution |
| --- | --- | --- |
| `scripts/New-MangaProject.sh`, `scripts/new_manga_project.py` | Create projects through Bash using Python 3.10+ and the standard library without PowerShell | Kit only |
| `scripts/Resolve-ReviewProfile.sh`, `scripts/resolve_review_profile.py` | Resolve review priorities on Linux; JSON output | Copy to project `scripts/` |
| `scripts/Initialize-OptionalSkills.sh`, `scripts/initialize_optional_skills.py` | Optional-skill installation with existing consent and pinned-version checks | Copy to project `scripts/`; do not execute at creation |
| `templates/manga-project/agent-modes/antigravity/` | `GEMINI.md` entry point and `AGENT-MODE.md` adaptations | Exclude from bulk template copy; add only with `-AgentMode Antigravity` or `--agent-mode Antigravity` |

Both PowerShell and the portable Python creator support `Codex` (default), `Claude`, and `Antigravity`. Explicit Antigravity selection adds only `GEMINI.md` and its dedicated `AGENT-MODE.md` to the project root and records the mode in `project.json` and the distribution snapshot. `GEMINI.md` refers to the common `AGENTS.md` as authoritative and expands adaptations with `@[label](path)`. Skills retain `.agents/skills/`; do not duplicate common knowledge or skill bodies. Codex defaults, imagegen production, and Claude branching remain in effect. Do not distribute Antigravity credentials, permissions, or global user rules. Sources, check dates, and limits of actual-environment verification are in its adaptations.
