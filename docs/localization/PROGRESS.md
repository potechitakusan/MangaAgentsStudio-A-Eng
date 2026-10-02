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
