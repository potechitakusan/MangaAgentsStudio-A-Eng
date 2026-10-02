# PSD handoff specifications and validation

Review/revise PNG previews first; create PSD after confirmation that no revisions remain. If creation has not been instructed, ask and wait; do not re-ask an existing instruction. Requested PSD completion includes creation, validation, and handoff. Humans finish in CLIP STUDIO PAINT before external publication. CBZ requires explicit request. See [PSD requirements](../knowledge/psd-handoff.md).

## PNG confirmation and PSD instructions

- Current stage: not started (awaiting PNG confirmation / revising PNG / awaiting PSD answer / PSD unnecessary or deferred / creating and validating PSD / PSD handed off).
- Latest PNG preview: path, version, pages, presentation time.
- Revisions, implementation, and re-presentation:
- Confirmation latest PNG needs no revisions: unverified (record user answer, time, version).
- PSD creation instruction: none (record existing answer, time, pages if instructed).
- Question/answer about PSD creation: not asked (unnecessary if already instructed).

Silence is neither "no revisions" nor a creation instruction. PNG acceptance alone does not start PSD creation; verify its instruction too. Record current stage in progress.

## Shared PNG/PSD specifications

Use relevant fields even for PNG-only work. Print specifications/checks belong in [PRINT-OPTION.md](../../PRINT-OPTION.md) and are not mandatory for Web work.

- Episode/pages and page order:
- Requested generation dimensions / actual file dimensions: undecided / unverified (width × height; full-page or per-panel):
- Frame-layout dimensions: default actual full-page image size; destination page size for panel generation.
- Final PNG dimensions: default frame-layout size; record actual width × height.
- Generation → layout → PNG transformations: source/destination dimensions, scale, method. Unverified dimensions or unperformed conversion are not complete.
- Basic frame / text-safe area / stroke: reference/fixed values in `config/page-layout.json`, scaled values in per-page `layout.json`.
- Color/profile: white background, RGB/sRGB baseline; record actual export settings.
- Publication destination/display size: if unspecified, inspect single pages and smartphone-sized reductions.
- Guides: absent from publication PNG; separate hidden layers in PSD.
- Specification sources/check dates / provisional items:
- CLIP STUDIO PAINT version:
- Layer-organization policy:
- CBZ: none (record request/scope only if explicit).
- External publication: decided by a human after finishing.

## Per-page handoff

| Page | PSD file | Review image | Layers and editable scope | Merged elements / text embedded in art | Human finishing |
| --- | --- | --- | --- | --- | --- |
| | | | | | |

Record approved wording in [Dialogue source](DIALOGUE.md). Do not claim line art, characters, and backgrounds are independently editable if they were not separated.

## Validation

| Item | Result / checked scope | Method/version | Time / reason not performed |
| --- | --- | --- | --- |
| Actual files and PSD format for every page | Not performed | | |
| Pixel dimensions, color, no stray guides | Not performed | | |
| PSD reopening and layer list | Not performed | | |
| Recomposition against confirmed PNG, opacity, visibility | Not performed | | |
| Source-text comparison and full read-through | Not performed | | |
| Actual CLIP STUDIO PAINT import | Not performed | | |

- Codex status: not started.
- Missing output, defects, gaps:
- Ordinary finishing left to a human:
- Unverified compatibility:

Requested PSDs are incomplete until created, reopened, and visually checked. Distinguish pending PNG/PSD answers and unnecessary/deferred creation from creation defects. Carry forward any lack of actual CLIP STUDIO PAINT import verification.
