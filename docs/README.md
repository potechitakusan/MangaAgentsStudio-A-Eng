# Documentation Guide

This folder maintains and distributes the production kit. First run `scripts/New-MangaProject.ps1` to create a project outside the kit, then reopen Codex in the folder at the displayed absolute path. In that project, follow the [Production workflow](knowledge/manga/08-workflow-review.md) from planning through PNG review and any requested PSD handoff. Do not begin production inside the kit until the [README exception procedure](../README.md#exception-producing-a-comic-inside-the-kit) is satisfied.

| Purpose | Reference |
| --- | --- |
| Capabilities and first steps | [Repository overview](../README.md) |
| English translation, review, and Japanese-source updates | [Localization records](localization/README.md) |
| Workflow and confirmation order | [Comic production workflow](knowledge/manga/08-workflow-review.md) |
| Make web PNGs without extra settings, or change margins | [Page dimensions and basic frames](knowledge/page-layout.md), [Options](../templates/manga-project/OPTION.md) |
| Configure print only when needed | [Print options](../templates/manga-project/PRINT-OPTION.md) |
| Install optional Japanese prose-polishing skills for a Japanese-language project | [Selection, first installation, and Gemini authorization](knowledge/optional-skills.md) |
| Select knowledge and templates | [Know-how index](../templates/manga-project/docs/MANGA-KNOWHOW.md) |
| Create a project folder | [Architecture and distribution](architecture.md) |
| Reopen Codex in the destination | [After creation and help with reopening](knowledge/codex-operation.md#reopen-codex-in-the-project-folder) |
| Choose review priorities | [Review workflow](knowledge/review-workflow.md) |
| Select common knowledge and skills | [Character, information, readability, and endings](knowledge/review-workflow.md#common-knowledge) |
| Supervise humor, appeal, emotion, relationships, and developments in a scene | [Supervision knowledge](knowledge/supervision/README.md), [Supervision skill](../skills/manga-supervision/SKILL.md) |
| Check included content and distribution | [Architecture and distribution](architecture.md) |
| Consider image-production environments and consistency | [AI image production](knowledge/ai-production.md) |
| Edit and regenerate NovelAI characters, style, and backgrounds | [Beginner README](../templates/manga-project/docs/novelai-prompts/README.md) |
| Supply roughs and references to external tools for individual panels | [Common procedure](knowledge/external-panel-i2i.md), [Qwen-Image 2.1](knowledge/image-generation/qwen-image-2.1.md), [Evidence and limits](knowledge/image-generation/production-evidence.md) |
| Proceed from PNG review to PSD | [PSD handoff](knowledge/psd-handoff.md) |
| Make an optional video prototype | [Video previsualization](knowledge/video-previsualization.md), [Video tools](knowledge/video-tools.md) |
| Check sources and scope | [Source register](SOURCES.md), [Screenwriting references](knowledge/manga-sources.md) |
| Verify before committing from this folder | [Publication procedure](publication.md) |

The English edition uses US English, left-to-right and top-to-bottom reading, and horizontal English lettering. English-edition maintenance records and update guidance are in `docs/localization/`; Japanese source references retain their original provenance.
