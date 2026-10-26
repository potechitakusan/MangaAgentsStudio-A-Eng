# Localization progress

## 2026-09-30

- Inventoried 721 tracked source files and saved SHA-256 hashes and source commit metadata locally.
- Preserved Japanese text/code under `.work/localization/source-ja/` for comparison.
- Completed English documentation, all ten bundled skills, project templates, prompts, configuration descriptions, runtime messages, asset interfaces, and test descriptions.
- Rebuilt all 79 panel layouts for left-to-right reading, including 158 frame/preview PNGs and their SVG/JSON guides. Time-growing and time-shrinking panels retain their narrative sequence in the new reading direction.
- Adapted lettering to horizontal English with word wrapping, standard punctuation, and centered balloon text. Kept explicitly requested legacy Japanese support and compatibility identifiers.
- Replaced all 114 reusable sound-effect images with English lettering, with editable SVG sources, consistent catalog metadata, and English gallery guidance.
- Revision 1 translated the example descriptions while temporarily retaining Japanese images. Revision 2, below, completes the bundled image localization.
- Three sub-agents translated separate scopes and independently reviewed another translator's work against the frozen Japanese baseline. Corrected semantic ambiguities and configuration/document synchronization issues; see the review records for actual coverage and limitations.
- Verified Python tests (144 passed, one environment skip), project scaffolding (82 checks), optional-skill handling (54 checks), panel geometry, release links, asset metadata, and visual samples. See [Validation](VALIDATION.md).
- Added source-delta reporting and an English state recorder, plus a repeatable [update workflow](UPDATE-WORKFLOW.md). These tools do not automatically merge Japanese changes over US-specific adaptations.
- Preserved local Japanese snapshots, original sound-effect images, and pre-existing private example archives under ignored `.work/localization/`. These local records are not included in the public scope.
- During revision 1, no Git commit, push, external publication, browser automation, or image-generation API call was made. Owner preferences remain in [the Japanese hearing sheet](HEARING-SHEET.ja.md); they did not block this completed kit localization.

## 2026-09-30 — example images, revision 0.4.1-en-US.2

- Completed the remaining bundled examples following the owner's continuation request. The optional preference question received no answer; the original instruction to complete the English edition supplied the scope, and silence was not recorded as approval.
- Preserved all 35 original images byte-for-byte in the ignored local backup. Localized 26 of 29 comic pages using built-in imagegen; retained three compatible wordless pages and six text-free reference images after inspection.
- Converted Japanese narrative lettering to horizontal English and repositioned whole panels for LTR reading. Corrected generated balloon-order and panel-order failures before adoption. No art was intentionally mirrored.
- An independent sub-agent reviewed every proposed narrative line against all 29 source pages and reconstructed its Japanese meaning. Five precision corrections were applied before the affected pages were edited. See [dialogue review](REVIEW-example-dialogue.md).
- Authors inspected every edited page. A separate agent additionally inspected the six edited pages of examples 01–03 and the six opening pages of example 06; the coordinator spot-checked later clues, cookie counts, and the forest ending. See [image review](REVIEW-example-images.md) for actual coverage and limits.
- Saved reviewed scripts, exact prompts, and source/output image hashes for subsequent Japanese updates. The adoption step preserved filenames/formats and removed PNG/JPEG metadata. See [example localization](EXAMPLE-LOCALIZATION.md).
- Provisional spellings and two source speaker ambiguities remain in the Japanese hearing sheet; the translation preserves the uncertainty. External Japanese comic and PSD links remain explicitly labeled originals.
- No commit, push, or publication was performed. Image generation can alter fine drawing details; the English images are adaptations rather than pixel-identical lettering replacements.

## 2026-10-03 — source fidelity, revision 0.4.1-en-US.3

- Completed the owner's requested follow-up back-translation comparison with three independent sub-agents. Scope includes all general knowledge and story/supervision guidance, all ten skills, principal project templates and operating rules, selected script messages, and saved dialogue for 29 comic pages. Detailed coverage and limits are recorded in the [follow-up review](REVIEW-2026-10-03.md).
- Corrected further meaning drift and ambiguous instructions, restored the Claude rules import, and synchronized stale publication guidance with the delivered English comic examples.
- Restored 211 external citation labels in 21 files and the 23 complete supervision source identity records from the Japanese baseline. Restored the external Japanese comic title, an unlinked source title, and the original Japanese CC0 summary reference. Added a policy exception requiring original-language source identities in future updates.
- Retained source URLs, dates, compatibility identifiers, licensing boundaries, English lettering, and LTR reading order. The source baseline and original image backups remain unchanged. Unchanged image and exact-prompt records retain revision-2 provenance.
- No image regeneration, browser automation, external source retrieval, Git staging/commit/push, or publication was performed. Saved bilingual dialogue was compared; actual lettering in the raster images was not freshly reviewed in this pass.

### README provenance clarification

At the owner's request, the root README now explains that this edition originated as an automated AI translation of a kit designed for Japanese-speaking readers, with later localization and review, and that Japanese manga conventions may remain. The example README explicitly identifies its English-lettered pages as originally Japanese-generated images whose dialogue and other lettering Codex subsequently replaced with English. An independent sub-agent checked both additions against the owner's Japanese intent and the documented image dispositions.

## 2026-10-03 — Japanese 0.4.2, localization 0.4.2-en-US.1

- Compared the clean Japanese 0.4.2 checkout against the recorded 0.4.1 source hashes: 12 additions, 19 modifications, no deletions or image changes.
- Translated every changed prose section and all new runtime messages/help; integrated portable creation/review/optional-skill entry points, Antigravity files, NovelAI V5 observations, E4/E5 evidence, V15, and upstream regression tests.
- Retained English reading/lettering defaults. Added en-US/ltr/localization metadata and English SFX SVG support to the portable creator; the optional-skill reader recognizes both English fields and legacy Japanese fixtures.
- Updated source version/commit/hashes and localization version. Existing examples and image-edit prompts retain their earlier provenance.
- Independent comparison is recorded in [0.4.2 review](REVIEW-0.4.2.md); update scope and verification limits are in [the update record](UPDATE-0.4.2.md). No runtime, scaffold, shell, or publication tests were run. No external calls, staging, commit, or publication.

## 2026-10-05 — Japanese 0.5.0, localization 0.5.0-en-US.1

- Compared the clean Japanese checkout (`b7a06f7`, version file 0.5.0) against the recorded 0.4.2 source hashes and the real Git diff from `b6a958a`: 1 addition, 13 modifications, no deletions, no image or asset changes. The final upstream commit is labeled 0.5.1 but leaves the version file at 0.5.0; this edition follows the version file.
- Translated the new editing README and every changed prose section; ported the batch-script changes (three variable types, numeric candidate names of three or more digits, `adopt-latest`) with English messages and the five new upstream tests. Position pins, scene-state expansion, and pre-send verification are integrated with their source dates and unverified-effect statements.
- Retained English reading/lettering defaults and original-language citation labels. Two linguistic adaptations are recorded (reading-order wording in position pins; "plain prose" for the relationship step).
- Updated the version file, README header and version FAQ, localization version in project creation, the state recorder, and the portable scaffold test, the source manifest, and the English state.
- Review is recorded in [0.5.0 review](REVIEW-0.5.0.md) and scope in [the update record](UPDATE-0.5.0.md). The review was by the integrating translator, not an independent sub-agent; that step remains open. No unit, scaffold, publication, or state-check run was performed. No external calls, generation, staging, commit, or publication.

## 2026-10-26 — Japanese 0.5.4 (0.5.2–0.5.4), localization 0.5.4-en-US.1

- Compared the clean Japanese 0.5.4 checkout (`ad50dd0`, version file `0.5.4`) against the recorded 0.5.0 source hashes (`b7a06f7`): 81 additions, 46 modifications, no deletions. Updated `scripts/localization_sync.py` so `.env.novelai.example` and `.env.pixai.example` are inventoried alongside `.env.example`.
- Translated all modified and new documentation, configuration files, NovelAI/PixAI scripts, WebUI skills (`novelai-batch-webui` and `pixai-batch-webui`), resource catalogs (`novelai-style-samples` with 11 styles / 17 samples and `pixai-model-samples` with 15 models / 35 style presets), and unit/scaffold tests into US English while preserving LTR reading order and horizontal English lettering defaults.
- Copied the 17 updated/added NovelAI WebP previews and 50 added PixAI JPEG previews byte-for-byte from the clean upstream checkout and refreshed offline HTML gallery indexes with `scripts/refresh_asset_indexes.py`. Generated equivalent US English gallery READMEs (`resources/novelai-style-samples/README.md` and `resources/pixai-model-samples/README.md`) matching the viewer and catalog data.
- Conducted an independent sub-agent semantic and back-translation review ([0.5.4 review](REVIEW-0.5.4.md)) and resolved all nine findings (including exact upstream schema restoration for `pixai-request.example.json`, `pixai-models.json`, `pixai-production-policy.json`, and `.env.pixai.example`). Integrated follow-up upstream commits `38755f5` and `8d5becb` (`Sample.env.txt`, gallery READMEs, `.gitignore`). Scope and adaptations are recorded in [0.5.4 update](UPDATE-0.5.4.md).
- Refreshed `source-manifest.json` (`8d5becb`, `0.5.4`) and `translation-state.json` (`0.5.4-en-US.1`). Verified Python syntax via `ast.parse` and statically verified all 967 public files, 961 internal links/anchors, table column counts, and image metadata without errors. Prepublication test suites passed when authorized by owner.
