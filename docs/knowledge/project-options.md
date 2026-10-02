# Applying Production Options

Updated: 2026-09-20. Applies at project start, resumption, and setting changes. This operating procedure follows the user's request for editable settings and Web production by default. See [AI Production](ai-production.md#novelai-opus) for NovelAI Opus specifications and sources.

## When to read

Read the project's `OPTION.md` when production starts. On resumption and before panel scripting, thumbnails, drawing, lettering, or delivery, compare file existence and SHA-256 with the previous record. Reread only if changed. No continuous monitoring or per-panel rereading is required. Consult this procedure initially and when needed to handle changes.

Codex interprets `OPTION.md` and applies it to production decisions and related settings. Only editing-skill initialization reads its relevant row directly. Apply adopted values to configuration JSON before running page/layout tools.

## Defaults

Use this table for a missing `OPTION.md`, removed fields, or blanks. Users edit their project's `OPTION.md`. When changing kit defaults, maintain this table and the template together.

| Item | Default |
| --- | --- |
| Publication format | Web single-page comics, left to right and top to bottom; portrait 2:3 as a guide, adapted to the tool |
| Generated image dimensions | Fit the image generator; verify actual dimensions after generation |
| NovelAI Opus generation conditions | No Anlas consumption; one image per request, at most 28 steps; initial steps 23 for V5, 28 for V4.5 and earlier; additional features such as references disabled by default |
| Frame placement dimensions | Actual whole-page image size; choose assembly page size for per-panel generation |
| Final PNG dimensions | Same as frame placement, without enlargement |
| Basic frame margins | Scale with page dimensions; 120 px on each side at 2000 × 3000 px |
| Text-safe margins | Scale with page dimensions; 160 px on each side at the same baseline |
| Border thickness | Scale with page dimensions; 10 px at the same baseline |
| Basic frame guides | Hidden |
| Japanese polishing skill | Do not use; Japanese-source-only optional feature |
| Japanese polishing scope | Japanese dialogue/internal monologue only when enabled |
| Panel layout templates | Use as a rule; custom layouts permitted for artistic needs with recorded reasons |
| imagegen generation unit | Whole page, using a numbered layout reference |
| Lettering and balloons | Include in imagegen generation; add separately after art with other methods |
| Panel-count proportions | 5 panels 60%; 4 panels 15%; 3 panels 15%; 6 panels 10% |
| Three-horizontal-tier repetition | At least 4 intervening pages; at most 3 uses in any 20 consecutive pages, including tilted variants |
| Diagonal five-panel frequency | Aim for at most once in any 20 consecutive pages |
| Dialogue/internal-monologue direction | Horizontal English, left to right |
| Dialogue alignment | Centered within speech balloons; balanced word wrapping and comfortable padding |
| Dialogue/narration punctuation | Natural US English punctuation, including periods and commas where meaning/voice require; no Japanese character-count threshold |
| PSD creation | If not instructed, ask and wait for the answer |
| CBZ creation | Explicit request only |
| Video prototype | Explicit request only |
| Feedback recording | Only when requested |

## Applying options at the start

1. Check `docs/PROGRESS.md` to determine whether production has begun. Production starts with planning/panel scripting in the project, not simply copying the project.
2. Overlay each "Current settings" field in `OPTION.md` onto the defaults. Missing/blank fields revert to defaults. Examples in explanatory sections are not settings. Explicit conversation instructions take precedence; ask only about a field whose removal of a previous instruction is unclear. Do not substitute old JSON values copied from OPTION for missing fields.
3. Explain adopted settings once, including that layout proportions are defaults or revised guidelines when templates are used. Do not require every field to be answered/confirmed. With characters, synopsis, and page count, provisionally choose unspecified details and proceed. Missing style preferences, destination, or print specifications do not prevent starting.
4. Under "Production options" in `docs/PROGRESS.md`, record every effective value and source (default/OPTION/conversation), file existence/SHA-256, application date, and production-started status. Do not copy project-specific settings or records back to the kit.
5. Run [editing-skill initialization](optional-skills.md) at the first working session. It reads the "Japanese polishing skill" row. For a conversation instruction or retained effective value while a change awaits confirmation, pass the effective `-Provider`. Disabled means no retrieval. Obtain explicit permission separately for missing-Git installation and Gemini skill installation/quota use. Deferring this Japanese-source-only feature must not stop normal comic production.

Explain dimensions as "requested generation size / actual generated size → frame placement → final PNG." Mark unverified actual size as undecided; do not present a long-edge value such as 3000 px as a generation specification. Codex may select provisional supported sizes without making extra questions a prerequisite.

When NovelAI is selected and an active Opus subscription is confirmed, use the [Opus default procedure](ai-production.md#novelai-opus) for steps, image count, and additional features, and check costs for every setting including dimensions. Follow common page settings adapted to the tool. Do not ask again if the conversation already specifies Opus. If the plan is unknown, confirm before generation; planning/panel scripting may continue. A template field alone does not authorize NovelAI use, imply an Opus subscription, or authorize paid generation.

Preserve dimensions in the old combined "Publication format / page dimensions" field as the existing finished-page dimensions, not generation dimensions. New individual fields take precedence when specified. Do not silently migrate an existing project to automatic dimensions.

## Changes after production starts

- Compare edits, file additions/deletions, and removed/blank fields reverting to defaults against adopted values. For formatting-only changes, update the verified SHA-256 without asking.
- For a value change, show "before → after" and affected stages, then confirm intent. Ask about edits conflicting with prior conversation too, rather than silently ignoring them. Confirm scope at the same time if finished pages need changes. Until answered, retain adopted values/configuration, defer affected work, and continue unrelated work.
- Do not reconfirm changes explicitly instructed in conversation or edits Codex made to implement those instructions. A file first added after production begins, or missing adopted-value records in an existing production, is not automatically a fresh initial setting: compare progress decisions and confirm intent.
- While awaiting confirmation, separately record current adopted values, pending changes, and checked file state. Do not repeat the same question on every resumption or treat silence as approval. If edited again before an answer, confirm the new difference.
- After approval, update related configuration and adopted values. If unintended, keep previous values and record the response/checked file state. Do not revert the user's file without instructions. Use this record on resumption rather than automatically applying the same unadopted values.

## Applying settings to production

| Target | Application |
| --- | --- |
| Format, generation, placement, final PNG | Record format in `docs/story/BRIEF.md`. In `config/page-layout.json`, `generationCanvas` is requested generation size, `canvas` placement, `exportCanvas` final PNG. `null` means fit tool / actual image size / placement size respectively. Send requested dimensions separately to the actual generator; record actual output and scale factors in handoff specifications. See [Page Settings](page-layout.md) |
| NovelAI Opus | Apply adopted dimensions to `generationCanvas` and the generator. Record steps, image count, and references/additional features in tool settings and production records. Check 0 Anlas and V5 limits before running; wait for quota recovery if insufficient. See [Opus procedure](ai-production.md#novelai-opus) for out-of-range settings/paid use. Do not apply uniformly to other environments or existing projects |
| Margins, borders, guides | Placement automatically scales baseline values. Put only fixed-pixel requests in `fixedPixels`; retain scaling for unspecified edges/strokes. Do not overwrite baselines with converted values. Visible review guides still stay out of published PNGs |
| Japanese polishing skill/scope | Disabled by default. When enabled for Japanese source, install `humanizer-jp` or `japanese-natural-writing` inside the project through [initial installation](optional-skills.md). Gemini needs pre-installation permission regardless of environment availability. Use the [comparison procedure](japanese-manga-readability.md#optional-polish) only on selected Japanese text. Always check typos, speakers, meaning, and source fidelity; do not assume English support |
| Templates: use as a rule | "Use" has the same meaning. Select IDs before page generation. Codex may choose a custom page if templates cannot express the effect adequately; record page, effect, and reason in `docs/production/PANEL-LAYOUT-POLICY.md`. A page exception does not disable OPTION globally and needs no individual approval |
| Templates: required | Use templates within the specified scope; Codex cannot waive them. If a custom layout becomes necessary, consult the user about changing that scope |
| Templates: do not use | Design freely; do not require IDs/validation or template-derived proportions/repetition limits. Continue checking general reading order and pacing |
| imagegen generation unit | Apply to the production plan. Default: actually provide a numbered layout reference and each panel's content, then generate the whole page. Supply a custom-layout reference when templates are disabled. Per-panel generation is permitted when needed with a recorded reason. Follow [layout procedure](panel-layout-policy.md) for references/output comparison. Other environments use their own workflows |
| Lettering and balloons | Choose from the actual method before drawing, briefly explain, and do not ask during new-project creation. imagegen normally includes them; other methods use later typesetting. Separate typesetting remains possible with imagegen when desired/needed. Using imagegen only for references/local corrections does not change the method. See [text finishing](page-layout.md#text-finishing) |
| Proportions | Set `recommended.standardPercent` in `config/panel-layout-policy.json`. Match `standard20PageMix` to a 20-page guideline and resolve rounding in the page plan. Set `hardRules.mostCommonPanelCount` too, or `null` for a tie. Do not fix five panels as always most common |
| Three-tier repetition | Set spacing, window, and maximum in `hardRules.horizontalThree`; "No limit" means `enabled: false`. Count tilted variants unless otherwise specified. Update explanatory `example` too |
| Diagonal five-panel frequency | Set `recommended.diagonalFiveMaximumPer20`; "No limit" means `null` |
| Text direction | Apply to panel scripts, thumbnails, lettering, and readability review. Horizontal English is the default; respect an explicitly adopted alternative |
| Alignment and punctuation | Apply to scripts, approved text, edited text, thumbnails, and PNGs. Record adopted alignment/exceptions in `docs/production/DIALOGUE.md`. Follow [English lettering and punctuation](japanese-manga-readability.md#dialogue-typesetting), use natural sentence punctuation, and wrap at word boundaries |
| PSD | Record "Create" as an instruction in `docs/production/PSD-HANDOFF.md`; create/validate after PNG revision confirmation. Retain "Do not create"/"Deferred" without repeated questions. Under the default, ask if uninstructed and wait |
| CBZ/video | Adopted "Create"/"Prototype" is an explicit request; record scope in the production plan. Defaults/blanks imply no request |
| Feedback | An adopted recording instruction is a request; write only the specified scope/frequency to `docs/feedback/`. External transmission/shared-knowledge incorporation requires a separate request |

Proportions range from 0–100% and total 100%. For partial specifications, fill unspecified panel counts with defaults (1, 2, 7, etc. default to 0%); confirm if the total is wrong. Confirm only affected fields for negative counts, unclear values, or contradictions. Do not silently normalize or replace them with defaults. When templates are disabled, do not delay production over inapplicable proportions/limits.

Consult [layout selection](panel-layout-policy.md) and [PSD handoff](psd-handoff.md) when needed. These settings do not imply authorization for external publication/transmission or confirmation that PNG revisions are complete.

## User-required production steps

When asked to register a continuing requirement, use the [process checker](process-checker.md) to discuss `instruction`/`strong-instruction`, conditions, checkpoints, evidence, and carry-forward scope. Codex decides delegated matters within scope. The authoritative file is `config/process-requirements.json`. Do not automatically turn OPTION edits or ordinary revision requests into permanent requirements. Resolve contradictions against the user's latest intent. Carry forward only from an explicitly named source project.

## Separate print options

Keep print-specific fields/records in root `PRINT-OPTION.md`. Missing, unspecified, or blank means disabled. In normal Web production, do not read print details or ask submission specifications. Initially check only enabled/disabled status and record file state. On change, check whether activation changed and read details only when enabled. Meaningful post-start changes use the same confirmation procedure as OPTION. Do not reconfirm explicit conversation instructions.

`config/page-layout.json` receives adopted numeric settings. If directly edited, compare with adopted values and handle post-start changes as above. Never silently reset it to template values.
