# Using Panel Layout Templates

Updated and checked: 2026-09-20. Consult when planning page shapes and pacing for US English page comics, read left to right and top to bottom. The English edition localizes the original Japanese reading direction; it does not establish a universal rule for all comics.

## When this applies

Use when moving from a panel script to page layouts or reviewing repetitive arrangements. Detailed sources and catalogs are unnecessary for planning discussions or dialogue-only revisions.

At production start, follow [Applying Project Options](project-options.md) and explain once the template proportions adopted from `OPTION.md`. If templates are disabled, template-derived proportions, repetition limits, and ID validation do not apply. These are kit defaults, not universal quality criteria. Prioritize user instructions; do not apply them uniformly to short stories, four-panel strips, vertical scrolling, or deliberate repetition.

## Default use and page-level exceptions

The default "Use as a rule" and "Use" settings instruct template use. Select each applicable page's template ID before generating page art.

If existing templates cannot adequately express the intended effect, Codex may design a custom layout. Record the page, intended effect, and exception reason in the per-page records of `docs/production/PANEL-LAYOUT-POLICY.md`. No separate approval is needed, and the project-wide OPTION remains unchanged. Forgetting to select a template or receiving a different generated layout is not a retroactive artistic justification.

Do not use this exception for a scope marked "Required." With "Do not use," design freely without requiring reasons why templates are insufficient on every page. In either case, plan layout and reading order before generation and compare afterward.

## Selection and review

1. Determine panel count from emotional changes, highlights, and necessary events.
2. Consult the relevant [project panel layout policy](../production/PANEL-LAYOUT-POLICY.md) section and [catalog](../../templates/panel-templates/index.html). Narrow the 79 choices by purpose and panel count.
3. Record the ID or custom layout/reason per page. Read individual JSON only when coordinates are needed. Do not expand all of `catalog.json` into the conversation; use scripts to extract necessary candidates/fields.
4. Plans using templates on every page can be checked with `scripts/validate_panel_plan.py` against project settings. It requires an existing ID on every page and does not support custom layouts. Review mixed plans against their records and actual layouts; do not invent IDs or remove exception pages and renumber the remainder. Do not report unrun checks as passed. A plan JSON is not mandatory for every brief discussion or partial revision.
5. Assign events, acting, and dialogue by reading-order number, then place art and the full intended text volume. Check reading order, face size, breathing room, and adjacent pacing. Numbers alone do not establish readability.

Check actual panel counts and pacing across all pages, including custom layouts. Count repeated shapes such as three horizontal tiers by actual geometry and original page numbers; do not evade limits by labeling a layout "custom." Record artistic reasons for proportion adjustments. Project-wide "Do not use" disables template-derived proportions and limits.

## Inputs to imagegen and comparison after generation

Whole-page generation is the imagegen default. Templates do not imply separate generation per panel. Per-page preparation is unnecessary for non-page work such as character references.

1. Finalize layout and left-to-right, top-to-bottom reading order before generating page art. `templates/panel-templates/previews/ID.png` can be a numbered reference. If dimensions, margins, or placement change, reposition according to [Page Settings](page-layout.md) and create a numbered image of that arrangement. Render custom layouts as numbered images too.
2. Visually verify that numbers/layout match the panel script and actually provide the image to imagegen with image-input support. A prompt containing an ID/path does not attach it. Distinguish layout references from character references.
3. Specify the scene, acting, and approved dialogue for each number. Generate one comic page preserving panel count, placement, and reading order. State that numbers, color coding, and guides are explanatory and must not appear in finished art. Borders, balloons, and lettering may be generated together. Prioritize instructions for later lettering or separate PSD elements.
4. Compare actual dimensions, panel count, arrangement, reading order, content, characters, exact dialogue, and stray numbering against the output image. Fix deviations/typos; attachment alone does not prove reproduction. Overlaying borders on art with misplaced divisions does not repair the layout.

Record the selected ID/custom layout, intended effect and exception reason, numbered reference, panel script, generation method, output image, and comparison result per page using relative paths. Choose per-panel generation when needed and record why. Do not uniformly require imagegen's whole-page/reference-image method for NovelAI or other environments; follow their workflows and cost conditions.

Manage page dimensions, basic frame, and text-safe area under [Page Settings](page-layout.md), separately from panel subdivision. Defaults retain existing asset placement. Adjust margins/guides to preference; exclude guides and catalog numbers from final PNGs.

Proportion/limit values are centralized in [project settings](../../config/panel-layout-policy.json); explanations of forms/effects are in the [project panel layout policy](../production/PANEL-LAYOUT-POLICY.md).

## Evidence and scope

- Source: user-provided production feedback, received 2026-09-15; no public URL. Individual project data, verbatim evaluations, and production history are excluded; only general selection procedures are distributed.
- Operating instruction: the user's 2026-09-20 instruction established default use, artistic page-level exceptions, and whole-page imagegen generation with numbered references. No public URL. This is a kit procedure, not a guarantee of general model capability.
- Production suggestion: prepare layout candidates and review repeated page shapes. Default proportions are starting points for adjustment.
- Unverified: improved reader evaluation from these proportions or exact generated adherence to references. Geometric checks, output-image comparison, and reader evaluation are separate activities.
