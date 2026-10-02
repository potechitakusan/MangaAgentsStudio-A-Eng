# Production Rules for PSD Handoff

Updated and official sources checked: 2026-09-13. Applies when Codex creates comic pages for a person to finish in CLIP STUDIO PAINT.

## Scope and starting conditions

**Review and revise PNG previews before creating an instructed PSD.** PSD creation takes time: before it is requested, ask whether the user wants it rather than creating it. "Finish the comic" alone is not a PSD instruction. When requested, Codex's completion scope covers PSD creation, validation, and handoff. A person normally finishes in CLIP STUDIO PAINT before external publication. Create CBZ only on explicit request. Neither PSD completion nor a CBZ request authorizes external publication.

## Moving from PNG review to PSD creation

An adopted "Create" setting in `OPTION.md` counts as an instruction. Retain adopted "Do not create"/"Deferred" choices and do not repeat creation questions without another instruction. Confirm the intent of later file edits through [Applying Project Options](project-options.md).

1. Create, inspect, and present PNG previews for target pages. Export from production assets rather than creating PSDs to obtain previews. Retain separately created art, text, balloons, and exact dialogue for possible PSD assembly.
2. Apply revisions, present PNGs again, and confirm no further changes are needed to the latest version. Silence or elapsed time is not "no revisions."
3. Without a PSD instruction, identify the reviewed PNGs/pages and ask "Would you like me to create PSDs from this version?" Wait for an answer. PNG "no revisions" alone is not a PSD instruction. If already instructed, proceed after PNG revision confirmation without asking again.
4. Create PSDs only for pages with no outstanding revisions and an instruction to create them; validate and hand over below. If declined/deferred, retain PNGs/assets and record scope/status.

In `docs/production/PSD-HANDOFF.md` and progress, record PNG paths, versions, target pages, revision-confirmation response, and PSD instruction/scope. Distinguish "Awaiting PNG review," "Revising PNGs," "Awaiting PSD decision," "PSD not needed/deferred," "Creating/validating PSDs," and "PSD handoff complete." Waiting for confirmation is valid; do not resolve it by creating unrequested PSDs. Finish PNG-only requests when their scope is complete.

## Specifications to retain and check before PSD creation

Record target pages, pixel dimensions, basic frame/text-safe area, color handling, page order, CLIP STUDIO PAINT version, and layer policy in `docs/production/PSD-HANDOFF.md`. Use [Page Settings](page-layout.md) for Web defaults and proceed through PNG even if the destination platform is undecided. Only for print, record print specifications/validation in `PRINT-OPTION.md`. Reuse confirmed specifications without asking again.

Example: "After reviewing the PNGs, also make PSDs with separate art, balloons, and text." Truly separate layers can move/be replaced, but moving rasterized lettering differs from editing its string. Provide original text separately and describe only what reopening verified. PSD is not required to produce/receive Web PNGs.

## Initial proposal for an editable structure

| Content | Example layer names | Handoff material |
| --- | --- | --- |
| Text | Dialogue Placement, Internal Monologue Placement | Approved text by page, panel, and speaker; identify rasterized text |
| Balloons and borders | Balloons, Panel Borders | Separate from text where possible for movement/replacement |
| Art | Panel 01 Art, Panel 02 Art, Background | Units actually made separately; line art/characters/backgrounds only if preserved separately |
| Effects | Sound Effects, Effect Lines, Solid Blacks, Tones | Separate layers for separately made assets; identify merged areas |
| Paper and helpers | Paper, Sketch, Guides | Sketches/guides normally hidden; exclude from review images |

Use ordered filenames such as `output/psd/page-001.psd`. Use English layer names/descriptions. Do not mandate a fixed layer count; honestly preserve the available separation. A PSD containing one flattened image must be labeled "PSD with one flattened art layer," without claiming independent element editing. Keep areas needing easy revision separate from the start.

## Confirmed format-compatibility information

CLIP STUDIO's official documentation describes preserving text layers in PSD export, but also text rasterization on PSD import and text effects not preserved. **A PSD text layer does not establish that text formatting, vertical text, or ruby remain editable in CLIP STUDIO PAINT.** See the [公式のPSD文字出力解説](https://tips.clip-studio.com/ja-jp/articles/6549). Its scope is that article's import/export behavior; verify the actual version/file. English projects normally use horizontal lettering, but editability still requires checking.

Save approved dialogue and speaker/page/panel mappings in `docs/production/DIALOGUE.md`; normally consider provisional lettering separate from art so a person can re-letter in CLIP STUDIO PAINT. This is a project production suggestion. Identify any lettering baked into original art and needed replacement.

## Codex validation and completion criteria

1. Confirm PSD existence for every requested page and matching page order, names, dimensions, and color settings. Check print specifications only when print is selected. An extension change is not PSD creation.
2. Reopen with a PSD reader; inspect layers, visibility, opacity, and composite. Save success alone is insufficient.
3. Visually compare the composite to the latest user-reviewed PNG, thumbnails, and exact dialogue. Read for missing letters, wrong speakers, missing layers, stray guides, panel order, and continuity.
4. Record review images, file list, editable scope, merged areas, human finishing work, and verification methods/results.
5. Open in CLIP STUDIO PAINT if an environment is available. Otherwise record "Actual import into CLIP STUDIO PAINT has not been verified." PSD structure, reopening, and visual checks complete Codex's side; do not claim application compatibility was tested when it was not.

Once PSD work begins with both instruction and PNG revision confirmation, inability to create/reopen PSDs or missing requested pages means unfinished production. Investigate available methods and continue. Record any remaining blocking condition and intermediate results. Distinguish normal human finishing, waiting/deferred creation, and uncompleted requested deliverables.
