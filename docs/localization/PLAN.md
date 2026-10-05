# US English edition plan

Source: Japanese kit 0.4.1, captured 2026-09-30. This is a localization of the production kit, including its scaffold, knowledge, scripts, layout library, and asset catalogs.

- [x] Preserve the source baseline and inventory tracked files.
- [x] Translate distributed prose, prompts, UI, configuration descriptions, and runtime messages while retaining technical identifiers and provenance.
- [x] Adapt layout ordering, horizontal English lettering, wrapping, punctuation, and preview assets for US readers.
- [x] Translate asset selection interfaces and supply English sound-effect assets.
- [x] Localize all bundled comic pages for English reading, preserve source images, and review dialogue meaning and visual sequence.
- [x] Independently audit meaning against the source, resolve findings, and verify the changed scaffold and rendering behavior.
- [x] Record reproducible update instructions, source hashes, validation evidence, and unresolved owner preferences in Japanese.

Publication itself is not part of this work. The existing checkout is the English edition; no separate release folder or archive is created.

## Japanese 0.4.2 update — 2026-10-03

The completed 0.4.1 plan above is historical. The 0.4.2 update covers all 12 added and 19 modified upstream files, portable script adaptation, Antigravity mode, NovelAI V5 production guidance, and corresponding tests/provenance. Preserve English defaults and existing image provenance. Record independent semantic review separately from automated tests; runtime/publication tests are not authorized by the translation request.

## Japanese 0.5.0 update — 2026-10-05

The 0.5.0 update covers the 1 added and 13 modified upstream files (NovelAI character/style/background variables, position pins, pre-send verification, `adopt-latest`, and the new editing README) between Japanese `b6a958a` and `b7a06f7`. No image or asset changes. Preserve English defaults, existing image provenance, and original-language citation labels. Record the integrating translator's review separately from an independent sub-agent review (still open) and from automated tests (not authorized by the request).
