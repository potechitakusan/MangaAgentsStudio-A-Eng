# Maintaining the US English edition

This checkout is the US English localization of the author's Japanese Comic Production Kit 0.5.4. The current localization revision is **0.5.4-en-US.1**, adding PixAI API and WebUI production workflows, the NovelAI WebUI, standard request composition (`novelai_compose.py` and `pixai_compose.py`), the three-way `.env` / `.env.novelai` / `.env.pixai` configuration split, NovelAI subscription check caching, the 11-style V5 Curated gallery, and the 15-model / 35-preset PixAI sample gallery to the earlier 0.5.0 features. The English examples retain their original 0.4.1-en-US.2 image provenance. The edition has horizontal English lettering and left-to-right, top-to-bottom reading order. Original Japanese source identities are retained in citations.

| Record | Purpose |
| --- | --- |
| [Plan](PLAN.md) | Scope and completion criteria |
| [Progress](PROGRESS.md) | Completed work and remaining owner preferences |
| [Translation policy](TRANSLATION-POLICY.md) | Terminology, US comic conventions, and source fidelity |
| [Back-translation review](BACK-TRANSLATION-REVIEW.md) | Independent review scope, findings, and corrections |
| [2026-10-03 follow-up review](REVIEW-2026-10-03.md) | Further meaning corrections, original Japanese citations, and source preservation |
| [Example localization](EXAMPLE-LOCALIZATION.md) | Bundled comic pages, editing prompts, and image provenance |
| [Validation](VALIDATION.md) | Executed checks and practical limits |
| [0.5.4 update](UPDATE-0.5.4.md) | Changed source files (0.5.2–0.5.4), English adaptations, and verification scope |
| [0.5.4 review](REVIEW-0.5.4.md) | Independent semantic comparison of the 0.5.4 changes, findings resolved, and adaptations |
| [0.5.0 update](UPDATE-0.5.0.md) | Earlier update: changed source files, English adaptations, and verification scope |
| [0.5.0 review](REVIEW-0.5.0.md) | Semantic comparison of the 0.5.0 changes, its limits, and open items |
| [0.4.2 update](UPDATE-0.4.2.md) | Earlier update: changed source files, English adaptations, and verification scope |
| [Update workflow](UPDATE-WORKFLOW.md) | Maintaining the English edition when Japanese upstream changes |
| [Japanese owner questionnaire](HEARING-SHEET.ja.md) | Preferences to confirm without blocking the completed localization |
| [Source manifest](source-manifest.json) | Japanese source revision and exact file hashes |
| [English state](translation-state.json) | Source-to-English mapping and current file hashes |

The reusable panel and sound-effect assets and the 29 bundled comic pages support English production and reading. Twenty-six comic pages were edited; three wordless pages and six text-free references retain their originals after visual inspection. External Japanese comic and PSD links remain labeled original editions.

No commit, push, or remote publication has been performed. Built-in imagegen was used for the example-image edits; no NovelAI/Gemini request or separately configured image API was used in this localization. Publish from this checkout when requested, following [the publication procedure](../publication.md).
