# Bundled English comic examples

Completed 2026-09-30 for **0.4.1-en-US.2**. The [example gallery](../../examples/README.md) now presents 29 comic pages for US English reading. The source remains the author's Japanese kit 0.4.1 and its recorded source commit; this is a new English adaptation, not a claim that the historical Japanese production used English.

| Example | Comic pages | Adopted treatment |
| --- | --- | --- |
| 01 — After School, Side by Side | 2 | English title/dialogue; reordered reaction panels; question before reply without swapping the characters |
| 02 — magic tournament | 3 | English announcement/banner on page 1; wordless pages 2–3 retain simultaneous action and established ice/fire geography |
| 03 — A Promise on a Rainy Day | 4 | Title and three panel-order edits; wordless page 3 retained; pictorial speech stays pictorial |
| 04 — In Our Slightly Lonely World | 0 locally | Three text-free character references retained; the linked Japanese comic is external |
| 05 — An Incident in the Old Forest | 8 | English dialogue/captions/SFX and LTR panels; repeated uncanny lines remain identical and unexplained |
| 06 — The Sumeragi Detectives | 12 | English title/dialogue/signs/SFX and LTR panels; bookmark clues, silent beats, cookie quantities, and jokes retained |

Total: **26 edited pages, three unchanged wordless pages, and six unchanged text-free reference images**. The [image manifest](example-localization.json) records every source/output path, SHA-256, actual dimensions, and disposition. The original images are preserved byte-for-byte in the ignored local backup and traceable to [the source manifest](source-manifest.json).

## Editing method and records

All creative raster edits used **built-in imagegen**, under the imagegen skill. Existing pages were supplied as editing targets. Full panels were repositioned for left-to-right sequencing without intentionally reflecting their contents. Balloons were moved or resized for horizontal, word-wrapped English, including vertically separated questions and answers where the source character positions otherwise invite reversed reading.

The [exact prompt record](example-edit-prompts.json) preserves all 34 successful generation prompts, including corrections, and three reviewed source/English scripts. It is an editing specification and audit trail, not a promise of deterministic regeneration. Original filenames and PNG/JPEG formats were preserved; JPEG outputs were exported at quality 98. PNG/JPEG ancillary metadata was removed before adoption. The 26 edited pages use their actual generated dimensions: 24 are 1024 × 1536, one is 1060 × 1484, and one is 1059 × 1485. Source and output sizes are recorded separately in the image manifest; these are web-viewing assets, not certified print-resolution masters.

Generated edits can alter fine lines, faces, framing, or texture. They are not pixel-identical lettering overlays, and no English layered PSD is supplied. Example 05's first title was rendered in capitals with a terminal period; its title meaning is unchanged. Small textbook/background strokes that were illegible in the source were treated as image texture rather than invented dialogue.

## Meaning and visual review

An independent sub-agent compared all proposed narrative lettering with all 29 source pages and reconstructed the Japanese meaning. Five precision corrections were applied. See the [dialogue review](REVIEW-example-dialogue.md) for the actual translations, ambiguity boundaries, and repeated-line checks.

Each editing agent inspected every selected output. An additional independent visual review covers the six edited pages in examples 01–03 and the first six pages of example 06; the coordinator also inspected key later pages. See [image review](REVIEW-example-images.md) for exact scope and limits. Automated format/hash checks establish file integrity, not narrative accuracy.

The Japanese school setting stays Japanese; school years are not converted into US grades or invented ages. Name readings and spellings are provisional. Two source balloons in example 06 have ambiguous attribution; the English preserves the source cues instead of inventing a new speaker. These items are in [the Japanese hearing sheet](HEARING-SHEET.ja.md) and do not block the completed adaptation.

The external comic linked under example 04 and the external Japanese PSD library remain original Japanese materials, explicitly labeled in the gallery. They were not edited or republished. No commit, push, or external publication was performed.

Future source changes follow [the update workflow](UPDATE-WORKFLOW.md). Update the reviewed text, actual image, prompt record, image manifest, and English state together; a translated gallery description alone does not update embedded lettering.
