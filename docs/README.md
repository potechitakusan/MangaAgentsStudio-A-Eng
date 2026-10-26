# Documentation Guide

This folder maintains and distributes the production kit. First run `scripts/New-MangaProject.ps1` (on Linux, `scripts/New-MangaProject.sh`) to create a project outside the kit, then reopen Codex (or the specified AI agent) in the folder at the displayed absolute path. In that project, follow the [Production workflow](knowledge/manga/08-workflow-review.md) from planning through PNG review and any requested PSD handoff. Do not begin production inside the kit until the [README exception procedure](../README.md#exception-producing-a-comic-inside-the-kit) is satisfied.

## 1. First-time user and creator guides

| Purpose | Reference | Audience / distribution |
| --- | --- | --- |
| Learn capabilities, required environment, and first request examples | [Repository overview](../README.md), [Public examples](../examples/README.md) | First-time users and creators (examples are kept in the kit only) |
| First steps and API key setup in a created project folder | [Project environment setup (SETUP)](../templates/manga-project/docs/SETUP.md), [Project README](../templates/manga-project/README.md) | Shared by users and agents (bundled into new projects) |
| Reopen Codex in the destination folder | [After creation and help with reopening](knowledge/codex-operation.md#reopen-codex-in-the-project-folder) | Shared by users and agents (bundled into new projects) |
| Make web PNGs without extra settings, or change dimensions and margins | [Page dimensions and basic frames](knowledge/page-layout.md), [Options](../templates/manga-project/OPTION.md) | Shared by users and agents (bundled into new projects) |
| Edit and regenerate NovelAI characters, style, and backgrounds via variables | [NovelAI prompt editing README](../templates/manga-project/docs/novelai-prompts/README.md) | For users (bundled into new projects) |
| Edit and regenerate PixAI characters, style, backgrounds, and LoRA via variables | [PixAI prompt editing README](../templates/manga-project/docs/pixai-prompts/README.md) | For users (bundled into new projects) |
| Edit, generate, adopt, and build in a browser UI (local WebUI) | [NovelAI WebUI (port 8765)](../skills/novelai-batch-webui/SKILL.md), [PixAI WebUI (port 8775)](../skills/pixai-batch-webui/SKILL.md) | Shared by users and agents (bundled into project `.agents/skills/`) |
| Configure print specifications only when printing | [Print options](../templates/manga-project/PRINT-OPTION.md) | For users who want print output (bundled into new projects; disabled by default) |

## 2. Drawing tools, production stages, and agent execution procedures

| Purpose | Reference | Audience / distribution |
| --- | --- | --- |
| Workflow and confirmation order, from PNG review to PSD handoff | [Comic production workflow](knowledge/manga/08-workflow-review.md), [PSD handoff](knowledge/psd-handoff.md) | Shared by agents and users (bundled into new projects) |
| Choose a drawing environment and follow Opus cost and consistency rules | [AI image production](knowledge/ai-production.md), [Panel layout policy](knowledge/panel-layout-policy.md) | Shared by agents and users (bundled into new projects) |
| Connect, assemble requests, batch-generate, and typeset with the NovelAI API | [NovelAI workflow](../templates/manga-project/docs/knowledge/novelai-composed-production.md), [NovelAI API connection procedure](knowledge/novelai-api.md) | Shared by agents and users (bundled into new projects; style samples `resources/novelai-style-samples/index.html` are referenced from the kit) |
| Connect, select models, assemble requests, batch-generate, and typeset with the PixAI API | [PixAI workflow](../templates/manga-project/docs/knowledge/pixai-composed-production.md), [PixAI API connection procedure](knowledge/pixai-api.md) | Shared by agents and users (bundled into new projects; model and style samples `resources/pixai-model-samples/index.html` are referenced from the kit) |
| Supply roughs and references to external tools (ComfyUI / Qwen, etc.) for individual panels | [Common procedure](knowledge/external-panel-i2i.md), [Qwen-Image 2.1](knowledge/image-generation/qwen-image-2.1.md), [Evidence and limits](knowledge/image-generation/production-evidence.md) | Shared by agents and users (bundled into new projects) |
| Select knowledge, techniques, and record templates | [Know-how index](../templates/manga-project/docs/MANGA-KNOWHOW.md) | Shared by agents and users (bundled into new projects) |
| Choose review priorities, common knowledge, and skills | [Review workflow](knowledge/review-workflow.md), [Character, information, readability, and endings](knowledge/review-workflow.md#common-knowledge) | For agents (bundled into new projects) |
| Supervise humor, appeal, emotion, relationships, and developments in a scene | [Supervision knowledge](knowledge/supervision/README.md), [Supervision skill](../skills/manga-supervision/SKILL.md) | Shared by agents and users (manifest-listed items bundled) |
| Use optional Japanese prose-polishing skills, the process checker, or video previsualization | [Polishing skills](knowledge/optional-skills.md), [Process checker](knowledge/process-checker.md), [Video previsualization](knowledge/video-previsualization.md), [Video tools](knowledge/video-tools.md) | Used only on request (procedures bundled into new projects) |

## 3. Kit architecture, sources, maintenance, and publication references

| Purpose | Reference | Audience |
| --- | --- | --- |
| Check how project folders are created and distinguish copied files from kit-side references | [Architecture and distribution](architecture.md) | Users and kit maintainers |
| Check English translation, review, and Japanese-source updates | [Localization records](localization/README.md) | Kit maintainers and reviewers |
| Check sources, access dates, and scope | [Source register](SOURCES.md), [Screenwriting references](knowledge/manga-sources.md) | Users and kit maintainers |
| Check licensing and third-party material handling | [Terms of use and third-party materials](RIGHTS.md) | Users and kit maintainers |
| Verify before committing from this folder to Git | [Publication procedure](publication.md) | Kit maintainers |

The English edition uses US English, left-to-right and top-to-bottom reading, and horizontal English lettering. English-edition maintenance records and update guidance are in `docs/localization/`; Japanese source references retain their original provenance.
