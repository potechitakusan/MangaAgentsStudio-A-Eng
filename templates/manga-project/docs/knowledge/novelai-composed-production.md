# Standard workflow: NovelAI assets + Codex composition

Adopted by the user on 2026-09-20. Read when starting NovelAI comic production. Generation conditions vary by time/model; recheck immediately before sending.

## Startup and style

1. Check project OPTION, existing style instructions, and `config/novelai-production-policy.json`. Project-specific instructions prevail.
2. If style is unspecified, go to step 3 and wait for the user's style ID. Do not ask to select again if already specified. If style/sample guidance is requested despite an existing choice, still follow step 3.
3. Samples are in kit `resources/novelai-style-samples/index.html`. Resolve `project.json`'s `sourceKitRelativePath` from the project root and join `kit_sample_library_relative_path` from `config/novelai-style-presets.json`. Check only that the file exists and provide only its absolute path. During style guidance, do not open/read HTML or images, list candidates, describe/summarize features, propose comparisons, or attach images. For older projects without this record, a kit location already known from conversation may be used. If unknown, moved, or absent, report unverified and clarify location; never guess the absolute path. Do not copy sample images into the work.
4. Before selection, do not generate NovelAI/API trials, including 0-Anlas trials. Wait only on style selection and style-dependent artwork; independently requested synopsis work may continue. After the answer, match its ID to `config/novelai-style-presets.json` and record adopted ID/prompt. `default_ids` lists available IDs, not an instruction to explain candidates, blend all styles, or silently choose the first. Do not use specific artist/cartoonist names. `sample_prompt_prefix` sets sample headcount; it does not require two female characters in every panel.
5. Use the same adopted style, negative-prompt and appearance wording, and major generation settings across panels; vary only action, framing, and background per panel. A fixed seed does not guarantee consistency. Send character prompts only for people visible in that scene.

The ten styles are `style-01` through `style-10` in display order (updated 2026-09-21). On that date the user excluded the thin, sharp-line drawing style; former `style-10` (cute color manga) became `style-09`, and former `style-11` (cute monochrome manga) became `style-10`. Sample HTML, catalog, and new-project settings share IDs. Do not reinterpret an old project's IDs as new IDs; compare name and prompt when needed.

## Asset generation and composition

Distinguish text-only t2i from initial/reference-image methods. Only when image-conditioned panel artwork is selected, also use `manga-external-panel-i2i` and [Shared workflow](external-panel-i2i.md); verify input implementation/extra charges in [API instructions](novelai-api.md). Style choice, cost checks, and separating lettering/frames also apply to t2i. Do not transfer Qwen image order/strength to NovelAI.

Codex designs panels and left-to-right reading order; NovelAI supplies illustration assets without text/frames. Generate compositions preserving full bodies and space around the subjects, then rotate, scale, or show portions during placement. Where needed, place only the character in front of frames. Decide visible contact points, faces/hands, and lettering space before generation. Recompose for English reading; do not mirror artwork and reverse handedness, props, or in-world text.

### Character trial before production

Before panel generation, generate one trial for each main character within Opus zero-cost conditions (multiple characters may share one image). Compare appearance to storyboard/settings: hair length/color, glasses, coat/uniform layering, prop sides. Correct appearance prompts for mismatches before production. Record trials and corrections. Honor explicit instructions to omit trials.

### Generation dimensions and placement

Generate panel assets **beyond panel bounds**. Show only needed areas using frames (topmost frame layer covers outside panels with white) and masks. Preserve the entire original in PSD layers for later human position/size adjustment in painting software.

- Set dimensions in request `width`/`height`; these may differ from full-page `generationCanvas`. Near-panel aspect ratios maximize usable area: wide assets for wide panels, tall for tall panels. Examples: `panel_canvas_examples` in `config/novelai-production-policy.json`. Continue checking candidate zero-Anlas pixel/step conditions.
- Set visible placement in page-manifest `focus` (point in the image centered in the panel), `zoom`, and `rotation`.
- Excessive enlargement of a spatial shot such as "wide overhead courtyard" removes the space. Regenerate the wide composition itself.
- After placement use the comparison below to confirm subject, action, characters, and props remain visible. Fix placement if a face is half cut off by a panel edge.

<a id="prompt-writing"></a>

### Constructing request prompts

Translate storyboard content into **visible forms** before prompting. These production suggestions address mismatches seen in a 2026-09-29 comparison (unworn shoes, paper remaining folded, standing instead of sitting); effectiveness remains under evaluation.

1. **Order:** headcount/subject (`1boy, solo` / `no humans`) → visible posture/action/expression → angle, subject size, frame position → location landmarks → time/light → style. Put shared style wording last and panel-specific content first.
2. **Keep negatives out of positive prompts:** `not smiling`, `no people`, `without glasses`, `neither …` may trigger the named concept and produce the opposite. Put unwanted elements in `negative_prompt`; use `no humans` for an empty cast.
3. **Visible form, not intention:** instead of `about to sigh`, `as if starting to reply`, or `awkward`, describe face/hands/body, e.g. `eyes half closed, shoulders dropped, mouth slightly open, looking aside`.
4. **State, not an intermediate action:** `unfolding a paper airplane` may depict an intermediate, still-folded form. If the result matters, specify `an unfolded sheet of paper with fold creases, held open in both hands`—the visible state at that instant.
5. **Identify whose body is close up:** `dark school shoes` alone may show unworn shoes. Describe character, body region, and posture: `1boy, lower body, standing, legs in navy trousers and white lab coat hem, school shoes, a paper airplane on the ground at his feet`. For hands, likewise identify ownership: `1girl, hands only, …`.
6. **Two-character panels:** consecutive appearance descriptions can bury posture and blend traits. First consider separate panels, with the other person offscreen or over a shoulder. If both are needed, put posture and spatial relationships before appearance (`sitting side by side on the floor, knees up, girl on the right`), and keep appearance to essential identifying traits. Before using separate-character functionality such as `char_captions` in `v4_prompt`, verify its format in the official schema.
7. **Choose angles from the storyboard:** `from above`, `from below`, and `from behind` are candidates, not mandatory prefixes for all panels. Choose for what must be shown; include landmarks (`rooftop edge at the top of the frame`, `courtyard far below`) and size (`small in frame`, `upper body`). Verify intent for repeated angles.
8. **Repeat identifying features in every request:** use identical words for hair color/length, glasses shape, clothing layers/inner garments, and accessories whenever that character appears. Do not omit features because an earlier panel mentioned them. The 2026-09-29 comparison found inconsistent hair, glasses, and inner clothing where wording varied. Register features matching the chosen trial in `input/novelai/characters.json`, then list each request's cast and visible features in `cast`.

```json
{
  "characters": {
    "mio": {"name_ja": "Mio Hinata", "features": {
      "hair": "light brown short bob hair", "hairpin": "yellow hairpin on left bangs",
      "outer": "open yellow hoodie worn over navy blazer"}},
    "ren": {"name_ja": "Ren Tsukishima", "features": {
      "hair": "short black hair", "glasses": "thin black rectangular glasses",
      "outer": "white lab coat over navy blazer"}}
  },
  "cast": {
    "p01-01": {"mio": "all"},
    "p01-03": {"mio": ["outer"]},
    "p04-05": {"mio": "all", "ren": "all"}
  }
}
```

`"all"` includes every feature; an array lists only visible features (e.g. a sleeve in a hand close-up). Include feature strings verbatim in prompts, case-insensitively. With `.env` character variables, check expanded wording. The legacy `name_ja` field name remains for compatibility; English display names are valid.

9. **Avoid numeric ages and man/woman:** numeric ages such as `25 years old` or a Japanese numeric-age expression may have little effect on appearance. `man`/`woman` can create another person beside the `1girl`/`1boy` character (user instruction, 2026-09-29). Describe people using `1girl`, `1boy`, `solo`, and appearance. Era/role terms such as `teenage`, `high school student`, and `adult` are allowed. For older/younger appearance also specify build, facial features, and clothing.

`novelai_batch.py generate` checks items 2, 3, 5, 6, 8, 9 and repeated angles before sending. Fix warnings or record retention reasons in [Batch records](../production/NOVELAI-BATCH.md) before sending with `--accept-warnings`. These are term detections, not judgments of prompt quality.

<a id="batch"></a>

### Request JSON, batch generation, adoption, rebuilding (repeatable by humans)

NovelAI results vary. Preserve all requests/manifests so humans can retry a page or all pages several times, choose images, and continue. Use bundled `scripts/novelai_batch.py` to generate, adopt, and rebuild; do not substitute custom generation/composition scripts.

| Location | Contents |
| --- | --- |
| `input/novelai/requests/p01-03.json` | One request per panel, same schema as `novelai_api.py`. Filename `p{two-digit page}-{two-digit panel}`; variants append a suffix, e.g. `p01-03b.json`. Character trials: `chara-mio.json`, etc. |
| `output/novelai/candidates/p01-03/r001.png` | Candidate; increment number each run without overwriting. Adjacent `.novelai.json` execution record |
| `input/novelai/adopted.json` | Selected candidates, recorded by `adopt` |
| `input/typeset/page-01.json` | Balloons, text, in-world text, protected artwork regions; see [Typesetting script](japanese-manga-readability.md#typeset-script) |
| `input/pages/page-01.json` | `layout.json`, typesetting spec, per-panel `request` or direct `source`, `focus`/`zoom`/`rotation`, and sound-effect/other `overlays` |
| `output/build/page-01/v001/` | New folder per rebuild version: `page-01.png`, optional `page-01.psd`, `build.json`, typesetting checks |

Example page manifest (the stable asset ID now contains English lettering):

```json
{
  "schema_version": 1,
  "layout": "output/layout/page-001-v1/layout.json",
  "typeset": "input/typeset/page-01.json",
  "panels": [
    {"panel": 1, "request": "p01-01", "focus": [0.5, 0.4]},
    {"panel": 2, "request": "p01-02", "focus": [0.5, 0.5], "zoom": 1.1},
    {"panel": 3, "source": "output/fixed/p01-03-fix.png", "original_source": "output/novelai/candidates/p01-03/r002.png"}
  ],
  "overlays": [{"name": "SFX FLAP", "source": "templates/onomatopoeia/images/block-bata.webp", "center": [700, 1300], "scale": 0.6, "rotation": -10}]
}
```

Commands from project root:

```powershell
# Inspect content, dimensions, and seed without sending
python -X utf8 scripts/novelai_batch.py generate --page 1
# Generate sequentially (all pages: --all; specific panels: --ids p01-02,p01-04)
python -X utf8 scripts/novelai_batch.py generate --page 1 --execute --confirm-zero-anlas --confirm-v5-allowance --cost-note 'Verified method and time'
# Compare candidates and adopt
python -X utf8 scripts/novelai_batch.py list --page 1
python -X utf8 scripts/novelai_batch.py adopt p01-02 --candidate 3
# Rebuild identical page/panel placement; add --write-psd when requested
python -X utf8 scripts/novelai_batch.py build --page 1
python -X utf8 scripts/novelai_batch.py build --all --write-psd
```

- `generate` uses request seed first, random seeds later (`--seed request` fixes it). Requests run sequentially with a default 3-second interval and a default limit of 30 requests per run. Failure stops remaining requests without automatic retry. Do not regenerate panels with unknown-result records until results are checked and records moved. Cost flags mean the same as `novelai_api.py`; never assert unverified flags.
- `build` stops if images are unselected and warns when placement does not cover a panel. Human-command PSDs are intended for later painting-software adjustment. Codex handoff PSDs still require both PNG revision confirmation and PSD instructions.
- Codex uses this workflow from initial artwork onward and records per-page commands in [Batch records](../production/NOVELAI-BATCH.md). Present PNGs from `build`.

<a id="character-variables"></a>

### Read character prompts from .env (only on request)

To let humans change appearance globally before regenerating, prompts can become project-root `.env` variables referenced as `${NOVELAI_CHAR_MIO}` in request JSON. **Only do this when a human asks.**

1. Propose names (`NOVELAI_CHAR_` plus uppercase ASCII letters, digits, `_`, e.g. `NOVELAI_CHAR_MIO`) and values; confirm with the user.
2. Write with `python -X utf8 scripts/novelai_batch.py env-set NOVELAI_CHAR_MIO --value-file input/novelai/char-mio.txt`. Do not display/change other `.env` lines, including keys.
3. Check replacements with `templatize NOVELAI_CHAR_MIO --dry-run`, then replace matching wording in JSON with `templatize NOVELAI_CHAR_MIO`.
4. Check names with `vars`; record names and requests in [Batch records](../production/NOVELAI-BATCH.md).

Humans can then edit `.env` and rerun `generate`. Execution records contain expanded requests. Never expand API keys or variables outside `NOVELAI_CHAR_`. Duplicate variables in `.env` and `.secrets/` stop execution.

### Post-artwork comparison (required before typesetting)

Once all adopted panel images are ready, **actually open each image** and fill "Post-artwork comparison" in [Storyboard checks](../reviews/NAME-REVIEW.md) before typesetting. "Plan" gives storyboard subject/action/framing/characters; "Observed image" describes actual drawing. Copying the plan or marking an unseen image matched is invalid. Resolve mismatches by regeneration, placement, or plan revision; record acceptance/reasons. Do not typeset until complete.

In the 2026-09-29 comparison, the unchecked workflow retained six mismatches, including a missing landed paper airplane, paper still folded rather than unfolded, and standing instead of sitting.

### Typesetting

Typeset balloons, horizontal English dialogue, in-world text, and frames with bundled `scripts/typeset_manga.py` ([Usage](japanese-manga-readability.md#typeset-script)). Any custom typesetting code must also satisfy these conditions; the standard batch workflow above remains required:

- Give speech balloons tails pointing toward the speaker's mouth. Record reasons for no tail, e.g. off-panel voice.
- Do not place text on faces, hands, or important props. Define protected regions from actual image inspection.
- Show text on questionnaires, letters, screens, and similar objects as depictions of the objects themselves, such as a close-up or paper within a panel. Do not overlay a game-dialogue-style rectangle on the image.
- Do not add unrequested titles, page numbers, logos, or signatures.

Normally select one appropriate angle from `from above`, `from below`, and `from behind`. Use `dutch angle`/`cinematic angle` sparingly as supplements, never all tags every time. Use level/side views only with recorded intent, such as introducing a character with background or tension through stillness. Verify overhead/back views retain crucial expressions/contact points.

This angle priority is adopted NovelAI policy in `config/novelai-production-policy.json`, not a universal external-i2i rule. Judge intent using [Framing/viewpoint](manga/02-visual-direction.md), and check contact, expression, and action continuity after generation/cropping. Variety itself is not the objective.

Search `templates/onomatopoeia/catalog.json` by meaning, duration, intensity, typography, and repetition. Its stable IDs and asset paths now point to English lettering. Use `meaning_en` and `placement_hint_en`; legacy display-field names such as `placement_hint_ja` also hold English compatibility values, while `source_text_ja` records provenance. See [Scene wording](../../templates/onomatopoeia/README.md#select-wording-for-the-scene). Translate audible sound or visible state rather than romanizing syllables: `puru` is TREMBLE, `zawa` MURMUR, `wai` CHATTER, `doki` THUMP; `pata` PAT fits light contact, while `bata` FLAP fits fluttering where appropriate. Repeat for actual duration or successive beats, not mechanically twice for every asset. Repeated assets already contain whole English words. Place continuing effects along left-to-right reading order and inspect PNGs. The original repetition policy came from the user's 2026-09-21 instruction; this edition preserves its duration/rhythm purpose in English.

If no suitable asset exists, make a separate transparent English asset and inspect alpha, spelling, and repeat count. Legacy four-through-seven-repeat IDs now contain that many whole English words. Default dialogue is horizontal with centered lines and natural English punctuation; separate frames, effects, balloons, and text. Place sound effects at the sounding moment, not a landing sound during flight.

Use imagegen for local corrections when overall appearance is acceptable and only a part differs. Preserve original and edited versions. For whole-composition, headcount, or action mismatches, revisit generation or composition. Do not turn a past session's "at most five regenerations" into a permanent limit for new works; follow each request's limit.

## Opus cost checks

As a rule use one image, ordinary-size candidate pixel counts, and at most 28 steps. Adopted sample settings 1344 × 704 = 946,176 pixels and 24 steps are within candidate ranges, but those numbers alone do not establish free use. Check actual request costs including model, subscription, allowance, input images, and reference features. Send as free-allowance generation only with verified 0 Anlas and remaining allowance. If unknown/paid, stop and clarify; never silently switch to paid use. [契約条件](https://docs.novelai.net/en/subscription/), [使用枠](https://docs.novelai.net/en/faq/) (checked 2026-09-20).

V5 has a replenishing usage limit; do not describe Opus as unlimited. Check image inputs, upscaling, and outpainting separately. First generate within free conditions; if needed preserve originals before enlargement/additional drawing. Upscaling does not guarantee new detail; outpainting requires checking new content/style.

Choose final page dimensions separately for publication/printing. The entire page need not fit one generation size. 1600 × 2400 was a prior comparison's composition size, not a required value or Opus limit. Determine dpi/bleed separately.

## Sound-effect recoloring

Keep only transparent monochrome originals in templates. Use unchanged for monochrome; for color, run `scripts/recolor_onomatopoeia.py` with black/white endpoint colors interpolated by source luminance. Alpha is unchanged. Save color derivatives in project `output/`, never back in templates. Use imagegen only for complex redrawing. This also works with non-NovelAI transparent monochrome assets.

```powershell
python scripts/recolor_onomatopoeia.py --input templates/onomatopoeia/images/block-baan.webp --output output/onomatopoeia-colored/bang.png --ink-color '#C02030' --white-color '#FFF2D6'
```

The example input is the bundled transparent monochrome BANG! asset under its stable upstream ID.

## PSDs preserving source artwork

Review PNGs first; create PSDs after both the no-revision answer and creation instruction. Do not skip existing handoff rules.

`scripts/export_composed_psd.py` stores complete untouched originals in a hidden group, places full transformed images on separate layers, and hides only outside-panel areas with pixel masks. Pre-imagegen NovelAI originals may also be specified. Never delete source pixels. Placement rotation/scaling is rasterized, not a smart object or reversible transform. Preserved originals, matrices, and masks support repositioning.

Default output is PNG plus record JSON; `--write-psd` explicitly adds PSD. Validate source SHA-256, RGBA pixels, masks, English layer names, and recomposited PNG. Raster lettering is not editable text. Actual CSP import requires separate verification.
