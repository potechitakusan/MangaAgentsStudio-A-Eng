# Panel templates and selection policy

Source policy updated 2026-09-20; localized for US English left-to-right page comics. Initial settings and asset specifications; read only needed sections when selecting layouts.

Adapt proportions/restrictions to the work. Apply settings received through [OPTION.md](../../OPTION.md) to configuration JSON under [Applying options](../knowledge/project-options.md). With templates disabled, do not require template-derived distributions/restrictions. User choices prevail; short works need not reproduce exact ratios. Do not directly apply this distribution to different formats such as four-panel strips or vertical scroll.

## Per-page selection and generation records

Use templates as a rule; when existing shapes cannot express staging adequately, record reasons and use a custom layout. Prioritize "required" and "do not use." For imagegen, default to full-page generation with an actually supplied numbered layout image and panel contents. Follow [Panel workflow](../knowledge/panel-layout-policy.md) for decisions, references, and mixed-layout checks.

Record selections below before page-art generation. Write "custom layout," never a fictitious template ID. Paths are project-relative. Add post-generation comparisons to the same row.

| Page | Template ID / custom layout | Staging intent / reason for custom layout | Numbered reference image / text storyboard | Generation method / reason for separate panels | Output / comparison |
| --- | --- | --- | --- | --- | --- |
| | | | | | |

## Entry points

- [Template browser](../../templates/panel-templates/index.html): filter by count, basic/diagonal/special layout, and purpose. Select an image to enlarge reading order and description.
- [Full JSON catalog](../../templates/panel-templates/catalog.json): shapes, uses, order, asset paths.
- [Project settings](../../config/panel-layout-policy.json): validation constraints and target proportions; canonical configuration when changed.
- [20-page example](../../templates/panel-templates/plan-example-20.json): ordinary 20-page plan.

## The 79 layouts

| Category | Count | Contents |
| --- | ---: | --- |
| Three panels | 9 | 2 above/1 below, 1 above/2 below and left/right diagonals; three horizontal tiers with both boundary slopes |
| Four panels | 3 | Two tiers of two with upper-left/lower-right wider, reversed wider pair, or 2-1-1 tiers |
| Five panels | 54 | Three arrangements × three width patterns × two height patterns × straight/diagonal A/diagonal B |
| Six panels | 3 | Three tiers of two with staggered vertical divisions |
| Two panels / splash | 6 | Full page; top square/lower wide; top wide/lower square; equal halves; two unequal top/bottom variants |
| Character breakout | 2 | Five-panel base with right/left overlapping character region |
| Time passage | 2 | Replace a five-panel layout's wide panel with three changing-size white panels; seven actual panels |
| Total | **79** | Initial browser view shows the 18 basic five-panel layouts |

### Five-panel combinations

- Top-to-bottom arrangements: `2-1-2`, `1-2-2`, `2-2-1`.
- Widths: equal pairs; first pair wider right/next wider left; first wider left/next wider right. No variants with both right sides or both left sides wider.
- Heights: roughly one-third each, or wide tier 24% and each paired tier 38%, before subtracting gutters.
- Vertical divisions: 18 straight layouts; diagonal A/B variants for all 18 produce 36 diagonals. A/B reverse the directions of both slants.
- Width division reference positions are 43% and 57% from the left; slopes change width at top/bottom edges. English localization changes reading-order numbering while preserving actual geometry.

### Two-panel combinations

- Top square/bottom wide (`P2-top-square`): top square 880 × 880 coordinate units, bottom wide. Establish a character/key subject in the square, then situation/dialogue below.
- Top wide/bottom square (`P2-bottom-square`): situation/landscape above, emotion or key image in the lower 880 × 880 square.
- Equal top/bottom (`P2-half`): two wide halves for scene contrast or quiet passage of time.
- Unequal top/bottom (`P2-large-bottom`, `P2-large-top`): wide panels at 0.3/0.7 proportions for quiet aftermath or strong spatial contrast.

## Default validated constraints

These are kit defaults; use configuration values after project changes.

1. **After three horizontal tiers, leave at least four intervening pages.** Page-number difference at least five; p1 permits next use at p6 or later.
2. **At most three three-horizontal-tier pages in any 20 consecutive pages.** Check p2–21, p3–22, etc., not only fixed p1–20/p21–40 blocks.
3. Sloped variants share `horizontal-three`; changing slope/ID does not evade frequency limits.
4. **Five panels should be most common.** For plans at least 20 pages long, automated validation requires five-panel pages to outnumber each other count.

The four-page gap is not mandatory for other identical layouts. Still avoid consecutive repetitions and judge surrounding pages. Consecutive spread pages are one two-page composition.

## Selection proportions

At startup explain these default targets once and that they can change with the work/preferences. Exact numerical matching is not an acceptance criterion.

| Panels | Target in ordinary 20 pages | Share |
| --- | ---: | ---: |
| Five | 12 | **60%** |
| Four | 3 | 15% |
| Three | 3 | 15% |
| Six | 2 | 10% |
| Splash / two | Adjust to staging | - |

- Of three three-panel pages in 20, aim for two horizontal-tier layouts; use layouts with a half-page large panel for the other.
- Aim for at most one diagonal five-panel page in any 20. More available variants do not imply more uses.
- Breakouts, time passage, and two-panel pages serve staging; they are not mandatory quotas.
- Uniform random selection from all templates overuses diagonals. Choose count/purpose first, then width/height.

Apply changes in `config/panel-layout-policy.json`: proportions in `recommended.standardPercent`; horizontal tiers in `hardRules.horizontalThree` gap/window/limit; dominant count in `hardRules.mostCommonPanelCount`. Disable horizontal checks with `enabled: false`, dominance with `mostCommonPanelCount: null`. Record decisions in normal progress; do not repeat explanations at every resumption. Browser HTML/examples show distribution defaults and do not automatically reflect project changes.

## Breakouts and time passage

### Character entrance

`FX-breakout-right` and `FX-breakout-left` preserve the five-panel base order and indicate candidate regions for a character spanning tiers, e.g. a full figure beside a building or before a door.

Orange dashed outlines indicate planned character occupancy, not a separate chronological panel. After placing the character, remove only frame lines overlapping its silhouette. Do not crowd backgrounds, faces, and dialogue into the same area or reveal later events early through a large foreground character. Frame PNGs are the underlying frames before removal.

### Time passage

`FX-time-grow` and `FX-time-shrink` replace the middle wide panel with three white panels, growing/shrinking **left to right** in this edition. Actual count becomes seven, so do not count these as five-panel pages.

Whether blank space conveys time depends on surrounding art. Add minimal change if needed—light on the same object, steam, fingertips. Panel size alone does not fix elapsed seconds.

## Artwork and files

| Format | Use |
| --- | --- |
| `svg/ID.svg` | Editable transparent frames, one polygon per panel. See guide SVG for effect regions |
| `png/ID.png` | 2000 × 3000 px transparent frame asset; no numbers/color fills; overlay on artwork |
| `guides/ID.svg` | Reading-order numbers, tier colors, effect regions; selection/rough-storyboard use |
| `previews/ID.png` | 2000 × 3000 px numbered review image; imagegen layout reference if matching the plan. Not generation/final-size requirements |
| `json/ID.json` | One layout's summary, coordinates, use, asset paths |

Coordinate system: 1000 × 1500, origin upper-left, frames inset 60 on each side. Values are SVG user units, doubled in transparent PNGs; they do not specify print format/dpi.

2000 × 3000 px is source-asset size, not default generation/export size. Scale frames, margins, and strokes to actual layout dimensions under [Page settings](../knowledge/page-layout.md).

SVG/PNG does not directly create CLIP STUDIO PAINT frame-border folders. Actual CSP import is unverified. Individual SVG polygons and JSON allow regeneration at needed manuscript dimensions.

## Reading JSON

Filter `catalog.json`'s `templates` by purpose/count in scripts; do not load the entire catalog into conversation. With an ID, read only `json/ID.json`. Resolve asset paths relative to catalog directory `templates/panel-templates/`, also for individual JSON.

| Field | Meaning |
| --- | --- |
| `id` / `name` / `summary` | Stable ID, English name, shape/purpose summary |
| `panelCount` / `rows` | Actual panel count; counts per tier from top |
| `rowHeightRatios` / `splitPositionsFromLeft` | Tier heights and vertical split positions |
| `widthPattern` / `shortWidePanel` | Width combination; reduced-height wide-tier variant |
| `verticalTilt` / `horizontalTilt` | Coordinate difference, not degrees |
| `usage` / `frequency` | Purpose and frequency class (mainstay, sparing, etc.) |
| `restrictionGroup` | Shared counting group for horizontal-tier restrictions |
| `panels[].order` / `polygon` | Reading order and four-vertex coordinates; lettering order designed separately |
| `baseTemplateId` / `modifiers` | Base template and modification conditions for breakout/time effects |
| `coordinateSystem` / `assets` | Individual JSON coordinate system and relative SVG/PNG paths |

All-template plan JSON lists `page` and `templateId` under `pages`. For custom-layout plans use the per-page table above, never fictitious IDs in template-only validation JSON.

## Validate assignments

For plans entirely using existing templates, run from project root:

```powershell
python scripts/validate_panel_plan.py <plan.json>
```

This compares assignments with settings. Separately inspect readability in PNGs after art/text placement.

Custom-layout plans are outside this script's scope. Removing exception pages and renumbering changes gap/repetition results; compare original page numbers, actual shapes, and counts with per-page records. Do not report unrun automated checks as passed.
