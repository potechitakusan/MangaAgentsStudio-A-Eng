# English-edition validation

Validation date: 2026-09-30. Scope: local implementation and documentation for localization 0.4.1-en-US.1, based on source kit 0.4.1.

## Executed checks

| Command / inspection | Result |
| --- | --- |
| `python -m unittest discover -s tests -p "test_*.py"` | 145 tests: 144 passed, one skipped because this Windows environment cannot create symbolic links |
| `powershell -NoProfile -ExecutionPolicy Bypass -File tests/Test-Scaffold.ps1` | 82 checks passed; actual Codex and Claude projects created in ignored `.work/`, including Unicode project names, inheritance boundaries, asset distribution, hashes, and relative paths |
| `powershell -NoProfile -ExecutionPolicy Bypass -File tests/Test-OptionalSkills.ps1` | 54 checks passed; network retrieval mocked, local dummy Git/ZIP sources only, no third-party skills or Gemini calls |
| `python scripts/check_panel_templates.py` | All 79 templates valid, including the five-panel family and six policy boundary cases |
| `python scripts/public_release.py check` | 855 public files and 653 internal links checked; no public-file, metadata, secret-pattern, working-path, Markdown-link, or table-structure errors |
| `python scripts/record_localization_state.py --check` | Recorded source/English mappings and hashes match the completed files |
| `git diff --check` | No whitespace errors after final normalization |

The Python suite includes six added localization regressions: every layout reads left to right within its row; growing/shrinking timing panels follow that direction; English words and punctuation survive wrapping; legacy Japanese requirement values retain their constraints; source comparison reports additions/modifications/deletions without modifying input; and all 114 English SFX assets match their catalog hashes, dimensions, transparency, grayscale channels, and editable SVG sources. A publication regression also distinguishes ordinary English “prototype” prose from a hardcoded legacy folder path.

The Windows optional-skill test initially failed because the restricted token prevented Git's local shell child from creating a signal pipe. The same offline test passed when run with normal process permissions. Its Git URL is replaced by a local test repository; ZIP retrieval is also mocked. No real service request or charge was made.

## Visual inspection

The primary agent opened a rendered contact sheet of representative panel layouts and English sound effects, and an English lettering preview. The inspected layouts include ordinary rows, changing panel sizes for elapsed time, and character-breakout guides. Numbers follow the new reading direction; the preview uses horizontal English text, normal punctuation, centered speech balloons, and a left-aligned caption. The preview reported zero errors and zero warnings. The local diagnostic images are retained under `.work/localization/` and are not release assets.

All 158 panel PNGs (79 transparent frames and 79 numbered previews), corresponding JSON/SVG guides, and all 114 SFX WebP/SVG pairs were generated locally. No browser automation or image-generation API was used for those reusable assets. The later example-image adaptation below used built-in imagegen.

## Issues found and resolved

- English message changes required updating test expectations, while preserving Japanese compatibility fixtures.
- The English optional-skill default initially contained explanatory prose in a machine-read value. It now uses `none`, with scope explained in the adjacent notes cell.
- The project packager now permits editable SFX SVGs only in their designated asset directory.
- Release-link resolution now recognizes knowledge documents physically owned by the project template as well as knowledge copied from the kit.
- The old folder-name check no longer rejects the ordinary English word “prototype”; explicit legacy folder paths still fail.
- Stale translated heading fragments were corrected. Catalog galleries were refreshed from the actual localized metadata.
- Normal inherited-permission test workspaces avoid unreadable temporary folders under this Windows restricted token.

## Limits

These checks do not verify current vendor pricing, product availability, live NovelAI/Gemini/ComfyUI behavior, remote service terms, actual CLIP STUDIO PAINT import, printer output, or browser-gallery rendering. Historical product observations retain their source dates and caveats. Revision 1 did not edit the comic examples; revision 2 uses generated image edits as documented below. External Japanese comic and PSD downloads were not modified. Fine linework and framing can differ from the original art; tiny illegible background marks were not independently transcribed.

Independent semantic review is recorded separately in [Back-translation review](BACK-TRANSLATION-REVIEW.md). Tests and hashes are not proof that every sentence or every image received independent human review.

## Revision 0.4.1-en-US.2 — bundled comic images

The earlier runtime test results above apply to revision 1. This continuation changed example images, their records, documentation, the localization version, and image dispositions in the state recorder; the full runtime/scaffold suites were not repeated.

- All 29 source comic pages and all proposed narrative text were included in the independent [dialogue review](REVIEW-example-dialogue.md). Five precision corrections were applied before image editing.
- Every one of the 26 edited pages was visually inspected by its editing agent. Twelve received an additional independent edited-image review, with coordinator spot checks of later clues and the final pages. See [image review](REVIEW-example-images.md) for exact scopes and fidelity limits.
- All 35 original-image backup hashes match the frozen Japanese source manifest. All 35 adopted/retained output hashes, dimensions, and PNG/JPEG formats match the example manifest. The three wordless pages and six references are byte-identical to their originals.
- Every metadata-stripped edited image decodes to the same RGB pixels as its staged PNG or quality-98 JPEG export. This checks that metadata removal itself did not alter the artwork; it does not assert equivalence between generated edits and Japanese source art.
- The exact prompt record matches all 26 adopted output hashes and contains 34 successful generation prompts and three reviewed scripts. One failed source-image transport attempt produced no candidate and is not counted as a generation.
- Final integration: `python scripts/public_release.py check` checked **860 public files and 682 internal links**, with no public-file, image-metadata, secret-pattern, working-path, Markdown-link, or table errors. `python scripts/record_localization_state.py --check` confirmed all current mappings/hashes, and `git diff --check` reported no whitespace errors.

Built-in imagegen was used for these image edits. No browser, separately configured image API, NovelAI/Gemini request, Git commit/push, or external publication was used. External Japanese comic/PSD downloads remain outside this localization.

## Revision 0.4.1-en-US.3 — meaning and source identities

The [2026-10-03 follow-up review](REVIEW-2026-10-03.md) records the new independent comparison and exact scope. Read-only hash verification confirmed all 400 Japanese snapshot files unchanged, 398 tracked snapshot files matching the source manifest, all 35 Japanese image backups matching source hashes, and all 35 English/retained images matching the unchanged example manifest. Original citation label/URL pairs and the 23 complete supervision source records were verified; historical dates were preserved. The two modified Python files passed syntax parsing.

The full runtime/scaffold suites and publication check were not repeated. This pass changed prose, import guidance, runtime error wording, and localization version metadata; it did not regenerate or inspect raster artwork. The final English state was refreshed after the reviewed edits. Earlier results above retain their original dates and scope.
