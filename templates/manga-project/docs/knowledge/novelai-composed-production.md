# Standard workflow: NovelAI assets + Codex composition

Adopted by the user on 2026-09-20. Read when starting NovelAI comic production. Generation conditions vary by time/model; recheck immediately before sending.

## Startup and style

1. Check project OPTION, existing style instructions, and `config/novelai-production-policy.json`. Project-specific instructions prevail.
2. If style is unspecified, go to step 3 and wait for the user's style ID. Do not ask to select again if already specified. If style/sample guidance is requested despite an existing choice, still follow step 3.
3. Samples are in kit `resources/novelai-style-samples/index.html`. Resolve `project.json`'s `sourceKitRelativePath` from the project root and join `kit_sample_library_relative_path` from `config/novelai-style-presets.json`. Check only that the file exists and provide only its absolute path. During style guidance, do not open/read HTML or images, list candidates, describe/summarize features, propose comparisons, or attach images. For older projects without this record, a kit location already known from conversation may be used. If unknown, moved, or absent, report unverified and clarify location; never guess the absolute path. Do not copy sample images into the work.
4. Before selection, do not generate NovelAI/API trials, including 0-Anlas trials. Wait only on style selection and style-dependent artwork; independently requested synopsis work may continue. After the answer, match its ID to `config/novelai-style-presets.json` and record adopted ID/prompt. `default_ids` lists available IDs, not an instruction to explain candidates, blend all styles, or silently choose the first. Do not use specific artist/cartoonist names. `sample_prompt_prefix` sets sample headcount; it does not require two female characters in every panel.
5. Use the same adopted style, negative-prompt and appearance wording, and major generation settings across panels; vary only action, framing, and background per panel. A fixed seed does not guarantee consistency. Send character prompts only for people visible in that scene.

The eleven styles are `style-01` through `style-11` in display order (updated 2026-10-06; `style-11` was added by the user on that date, includes quality terms in its style prompt, and uses the script default for its sample negative prompt). As of 2026-09-21 there were ten styles: on that date the user excluded the thin, sharp-line drawing style, so former `style-10` (cute color manga) became `style-09`, and former `style-11` (cute monochrome manga) became `style-10`. Sample HTML, catalog, and new-project settings share IDs. Do not reinterpret an old project's IDs as new IDs; compare name and prompt when needed.

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

<a id="position-pins"></a>

### Position pins (Character Positions)

A NovelAI feature for guiding the on-screen position of characters and objects. It makes concrete the existing procedure for per-character prompts and coordinates, and it is a separate specification from panel-frame placement and the post-generation `focus`. Do not apply it to production with tools other than NovelAI.

**Specifications confirmed in official documentation (2026-10-04):** Per-character input is supported from V4 onward. V5 supports up to 22 targets and free placement; V4 supports up to 6 targets; placement in V4 and V4.5 is limited to a 5×5 grid. In the UI, prepare at least one per-character input, change the position from `AI’s Choice` to `Custom`, and set positions on the `Character Positions` canvas. Pins work for objects as well as characters, but objects may need careful description and reinforcement in natural language. Do not let the order of per-character inputs contradict their positions; reinforcing positions in natural language is also recommended. Source: [NovelAI公式の人物別入力・位置指定](https://docs.novelai.net/en/image/multiplecharacters/). Codex does not operate the browser; the user performs UI operations.

**Production proposal in this kit:**

1. Consider pins for panels where placement must be legible: left/right positions of two characters, characters separated vertically, or where a prop sits. Do not use them in panels where automatic placement already conveys the intent.
2. Put the number of characters in Base and each character's appearance and action in the corresponding Character. Order the per-character inputs top to bottom and left to right to match the position settings, and keep natural-language phrases such as `on the left` and `on the right` consistent. Do not copy the panel or balloon reading order directly into the Character input order (the Japanese mode reads right to left; this edition's default reads left to right).
3. In the API, use the structure in [Position-pin requests](novelai-api.md#position-pins). For V4 and V4.5, do not reuse precise coordinates intended for free placement; check the grid and its correspondence for the model in use. Record the targets, positions, and intent in the existing request JSON and in the [batch records](../production/NOVELAI-BATCH.md).
4. Pins specify positions across the whole generated asset. Do not pass page coordinates directly; choose positions where faces, hands, and contact points remain after cropping, enlarging, and rotating. Pins alone do not guarantee posture, gaze, contact between hand and prop, or front-to-back depth, so specify the necessary relationships in text as well.
5. Before adopting an image, actually open it and check for swapped characters, left/right and up/down, relationships with objects, and how it looks after cropping. If a position changes, recheck the Character order and the position wording.

**Unverified:** No generation was performed in this survey. Positional accuracy of pins, object placement, with/without comparisons at the same seed, API acceptance by model, and effects on the contract or extra charges are unconfirmed. Do not treat attaching a pin as placement agreement, quality improvement, or 0 Anlas; follow the existing cost checks and image comparison.

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
8. **Repeat identifying features in every request:** use identical words for hair color/length, glasses shape, clothing layers/inner garments, and accessories whenever that character appears. Do not omit features because an earlier panel mentioned them. The 2026-09-29 comparison found inconsistent hair, glasses, and inner clothing where wording varied. Register features matching the chosen trial in `input/novelai/characters.json`, then list each request's cast and visible features in `cast`. Automatic identity-feature checking (warnings) in `generate` is **disabled by default**; it runs only when `NOVELAI_CHECK_IDENTITY=1` is specified in `.env.novelai` or the environment (user instruction in the project "NAIプロンプト検証", 2026-10-05; even when the automatic check is disabled, write identifying features in identical words in every request).

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

`"all"` includes every feature; an array lists only visible features (e.g. a sleeve in a hand close-up). Include feature strings verbatim in prompts, case-insensitively. With `.env.novelai` character variables, check expanded wording. The legacy `name_ja` field name remains for compatibility; English display names are valid.

9. **Avoid numeric ages and man/woman:** numeric ages such as `25 years old` or a Japanese numeric-age expression may have little effect on appearance. `man`/`woman` can create another person beside the `1girl`/`1boy` character (user instruction, 2026-09-29). Describe people using `1girl`, `1boy`, `solo`, and appearance. Era/role terms such as `teenage`, `high school student`, and `adult` are allowed. For older/younger appearance also specify build, facial features, and clothing.

10. **Check character/object relationships separately from names.** Listing people and objects can lose relationships such as holding, touching, or putting something inside. Define one to three image-verifiable conditions distinguishing the panel from a different action, then write only relevant conditions. The English examples below are not additions required in every panel.

| Aspect | Example content |
| --- | --- |
| Contact and possession | Holding (`water bottle in her hand`), contact with the face, hand shape (`cupped hands`, `palms pressed together`) |
| Operation | Hands tying, adjusting, or fastening; each hand handling a different end |
| Inside/outside, above/below, distance | Putting something into a bag, `close to the ground`, on a stand |
| Gaze target | `smiling at each other`, lowering eyes toward a page |
| Viewpoint and direction | Going to school seen from behind, position relative to the destination |

When shortening, read the main prompt, character prompts, coordinates, and negative prompts together and check whether the same meaning remains elsewhere. Do not assume two individually safe removals remain safe together. Evidence comes from V5 Full ordinary t2i ([E4](image-generation/production-evidence.md#e4), [V5 N1](image-generation/novelai-v5.md#n1)); effects with other versions or image inputs are unverified.

<a id="scene-state"></a>

### Expanding scene relationships and continuing state into each request

A production procedure adopted 2026-10-03. Do not merely list the names of characters and objects: expand the text storyboard, in the following order, into the visible state of each panel before writing the request. Keep per-panel generation and later typesetting of text.

1. **Fix the relationships at that instant:** Decide the main subject and who is doing what to what. In plain prose before converting to prompt terms, make concrete the necessary contact, possession, and operation; actor and other party; posture; body orientation; gaze target; and left/right and up/down as the reader sees them. Narrow the conditions that distinguish this panel from a different action to one to three items; do not add every item, including parts that are not visible. Do not stop at an emotion name or a list of objects.
2. **Carry over the state continuing from before:** From the same scene's text storyboard and the previous panel, check current clothing and colors, belongings, the holding hand, posture and orientation, characters' left/right positions and distances, and the positions of doorways and tools. Update only the items specified to change, and restate in the request the continuing state visible in this panel. Sending the previous panel's request does not carry its state into this generation. Do not invent events or characters absent from the surrounding material. Decide missing placement as a proposal consistent with existing settings, record it, and distinguish it from established facts. Do not fill with guesses a gap that changes the story's meaning.
3. **Assign scene-wide and per-character content:** Assign headcount, location, light, shared objects, and overall positional relationships to the scene-wide text (Base), and each person's fixed appearance, posture, assigned action, hands, orientation, and gaze to the per-character text (Character). For multiple characters, use per-character input confirmed for the supporting model and the official schema. Write an action toward another person so that both the actor and the recipient are identifiable. Where a corresponding action tag exists, `source#`, `target#`, and `mutual#` are aids; do not attach them mechanically to arbitrary action sentences. The text may combine short natural sentences and tags, and tagging must not drop the contact point or subject.
4. **Expand into the actual request:** Make the scene-wide text match `input` and `v4_prompt.caption.base_caption`, and put per-character text into the corresponding `char_captions`. When using coordinates, keep each character's left/right and front/back wording consistent with them. Follow the [API procedure](novelai-api.md) to confirm the exact JSON format and available fields. For a model without per-character input, merge the text into the body with explicit subjects and record that constraint. Do not add per-character text to a panel without characters.

Example: for a panel showing a notebook, first decide "The girl on the left sits at a desk and holds out an open notebook in both hands to the boy on the right. The boy stands and lowers his eyes to the notebook. The notebook is between them." Example distribution into the text (not the API request JSON itself):

| Destination | Example content |
| --- | --- |
| Scene-wide | `1girl, 1boy, classroom, a desk between the two students, an open notebook between them` + adopted angle, light, and style |
| Girl | adopted fixed appearance + `sitting on the left, holding an open notebook in both hands and extending it toward the boy on the right` |
| Boy | adopted fixed appearance + `standing on the right, looking down at the notebook held by the girl` |

If the boy receives it in the next panel, update the holder and hand state. If he does not, maintain the state in which the girl holds it. When a close-up puts one person offscreen, send only the visible person and do not add an invisible face or full body.

**Do not pass dialogue, lettering, or balloons to NovelAI.** The speaker or emotion may be converted into instructions for body, gaze, and expression, but do not put dialogue text, `Text:`, or positive specifications such as `speech bubble`, `japanese text`, or drawn lettering into Base or Character. Do not generate frames either. For the negative text, use examples such as `text, speech bubble, panel border`; if you specify `v4_negative_prompt` explicitly, keep it consistent with the negative text. Keep dialogue, in-image text, and sound effects in the typesetting specification. A position left open for text may be specified as composition, but do not have an empty balloon drawn.

<a id="prompt-content-check"></a>

### Pre-send content verification

When creating or checking prompts with `manga-ai-production`, read the body text, per-character text, coordinates, and negative text together after variable expansion, and verify the following against the text storyboard. Check right after creation and again before sending a revised request. Consolidate the record into the existing per-request records in [Batch records](../production/NOVELAI-BATCH.md); do not make a separate copy of every prompt.

| Check | What to determine |
| --- | --- |
| Relationships | Whether the sent text identifies the main subject, actor and other party, and the necessary contact, possession, and operation, and has not shrunk to names only |
| Continuing state | Whether clothing, belongings, hands, orientation, and positions unchanged from before remain in this request, and only changed items are updated. When swapping, whether the connection to the next panel was also checked |
| Assignment and contradiction | Whether fixed appearance and action correspond to the same character, and whether the body text, per-character text, coordinates, and negative text avoid conflicts in left/right, posture, object form, and so on |
| Text separation | Whether there are no dialogue text, `Text:`, or positive specifications of lettering or balloons, and whether exclusions for text, balloons, and frames and a later typesetting specification are present |

Fix mismatches in the request. Record insufficient material as unconfirmed with its target and reason, and do not send the affected request until the required action and connection to adjacent panels are decided. Do not turn this into a procedure that asks the user for a batch of additional settings. The check record can take the form "request ID / required relationship / continuing and changed state / verification result and reason for revision." The absence of warnings from automatic checking does not substitute for this content verification.

`novelai_batch.py generate` checks items 2, 3, 5, 6, 9 and repeated angles before sending and displays warnings (item 8's identity features are checked only when `NOVELAI_CHECK_IDENTITY=1` is set). Fix warnings or record retention reasons in [Batch records](../production/NOVELAI-BATCH.md) before sending with `--accept-warnings`. These are term detections that do not judge relationships, continuing state, or text separation by meaning. Do not use `--accept-warnings` to skip the content verification.

Sources and scope: this makes concrete, as a procedure for expanding into generation requests, the relationship descriptions in the existing [production evidence E4](image-generation/production-evidence.md#e4) and [spatial continuity V13](manga/02-visual-direction.md#v13). Per-character input, reinforcing positions in natural language, and action tags: [NovelAI公式文書](https://docs.novelai.net/en/image/multiplecharacters/); correspondence between natural language and Japanese: [V5公式発表](https://journal.novelai.net/novelai-diffusion-v5-release-jp-343211a45664/) (checked 2026-10-03).

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
python -X utf8 scripts/novelai_batch.py generate --page 1 --execute --accept-warnings --confirm-zero-anlas --confirm-v5-allowance --cost-note 'Verified method and time'
# Compare candidates and adopt
python -X utf8 scripts/novelai_batch.py list --page 1
python -X utf8 scripts/novelai_batch.py adopt p01-02 --candidate 3
# To use the highest-numbered PNG for each panel, adopt them all at once (--dry-run to check only)
python -X utf8 scripts/novelai_batch.py adopt-latest --page 1
# Rebuild identical page/panel placement; add --write-psd when requested
python -X utf8 scripts/novelai_batch.py build --page 1
python -X utf8 scripts/novelai_batch.py build --all --write-psd
```

- `generate` uses request seed first, random seeds later (`--seed request` fixes it). Requests run sequentially with a default 3-second interval and a default limit of 30 requests per run. Failure stops remaining requests without automatic retry. Do not regenerate panels with unknown-result records until results are checked and records moved. To move them, first check NovelAI's image history and Anlas consumption, then run `move-unknown --ids <request-ID> --confirm-checked --note 'What was verified'` (moves records to `failed/<timestamp>-rNNN/` without deleting them; omitting `--confirm-checked` only displays the targets). Cost flags mean the same as `novelai_api.py`; never assert unverified flags.
- The generation and regeneration examples include `--accept-warnings`. Remove it if you want to check warnings and stop sending when any remain. Warnings are still displayed when it is included, and cost confirmation and error validation are not skipped.
- `adopt-latest` adopts the highest-numbered PNG in each target folder (`--all` for all pages, `--ids` for specific panels). If a target has no candidate PNG, it stops without changing the selection record. For a panel whose new generation failed, an earlier highest number is chosen, so check the generation results and the images. Details: [editing and regeneration README](../novelai-prompts/README.md#adopt-the-highest-numbered-image-in-each-folder-at-once).
- `build` stops if images are unselected and warns when placement does not cover a panel. Human-command PSDs are intended for later painting-software adjustment. Codex handoff PSDs still require both PNG revision confirmation and PSD instructions.
- Keep the previously adopted request separate from alternatives such as `p01-03b.json`. Set both requests' `parameters.seed` to the same value and generate with `--seed request`; change seed values to make multiple pairs. Record settings other than the changed wording, whether the unchanged control succeeded, and all attempts including failed seeds. Do not conclude a phrase is necessary or unnecessary from a pair whose control failed. This is a recommended method, not a mandatory trial count for every panel. Evidence: [E4](image-generation/production-evidence.md#e4).
- Codex uses this workflow from initial artwork onward and records per-page commands in [Batch records](../production/NOVELAI-BATCH.md). Present PNGs from `build`.

<a id="compose"></a>

### Assemble request JSON from arguments (`scripts/novelai_compose.py`)

**Standard way to assemble requests for NovelAI API generation.** The model defaults to V5 (`nai-diffusion-5-curated`; Full produces overly dense detail that is less suited to comics, so it is not the default), and V4.5 is used only when specified by the user. It accepts style, background, per-character text, position pins, and generation settings as arguments and saves the request JSON to `input/novelai/requests/<ID>.json`. It makes no network calls and displays the same dry-run check as `novelai_batch.py generate` after saving. Sending, cost confirmation, and execution records continue to be handled by `novelai_batch.py`, and are handed off to that same pipeline only when `--execute` and cost-confirmation flags are passed. Saved request JSON files may be edited by hand, and JSON written directly without arguments can also be sent through the same `generate` command. When modifications are needed for additional features such as i2i or references or for specification changes, modify and use this script as the base (verify fees and format for additional features in [API procedure](novelai-api.md#compose-standard) first). The script was created and verified in the project "NAIプロンプト検証" (user instruction, 2026-10-05).

```powershell
python -X utf8 scripts/novelai_compose.py --id p01-03 --seed 123 `
  --scene "standing side by side, upper body, eye level" --background "city street, daylight" --style "<style>" `
  --char1-appearance "<appearance>" --char1-action "<pose and action>" --char1-pos 0.3,0.5 `
  --char2-appearance "<appearance>" --char2-action "<pose and action>" --char2-pos 0.7,0.5
```

- **Order**: Base follows `headcount tag (derived automatically from characters, or no humans when empty) → --scene → --background → --style → quality tags`. Per-character text follows `girl/boy/other (no number) → appearance → pose and action`. Negative text follows `preset → --negative`. Input text is concatenated as-is (including spaces and commas) without rewriting. Sources: [タグの順序](https://docs.novelai.net/en/image/tags/), [複数人物](https://docs.novelai.net/en/image/multiplecharacters/), [品質タグ](https://docs.novelai.net/en/image/qualitytags/), and [除外プリセット](https://docs.novelai.net/en/image/undesiredcontent/) (checked 2026-10-05).
- **Model**: `--model` selects `nai-diffusion-5-curated` (default), `nai-diffusion-5-full` (only when specified), or `nai-diffusion-4-5-curated` (only when specified). Quality tags, UC presets, Guidance (7.0 for V5, 5.0 for V4.5), and sent parameters match the Web UI defaults for each model. V4.5 supports up to 6 characters and snaps position pins to the centers of the 5×5 grid; V5 supports up to 22 characters. The basis for each setting is displayed at run time. **V5 Curated, V5 Full, and V4.5 Curated have been verified to match Web UI PNGs pixel-for-pixel at the same seed and input** (1 run each; see [Web UI parity observations](novelai-api.md#compose-standard) for conditions and limits). The V5 Full Web UI prepends `nsfw, ` to the negative prompt, but per user instruction the script does not add it (pass the full string including `nsfw, …` to `--uc-preset-text` for an exact Web UI match). For presets not verified against Web UI PNGs—such as `light` and `human` on V4.5—specify the full string with `--uc-preset-text`.
- **Quality tags**: Automatically appends the Web UI quality tags to the end. If the input (Base or per-character) already contains the same tag, it is not added a second time (weighted tags such as `-0.8::feet::` count as duplicates only when the weight also matches). `--allow-duplicate-quality` reproduces the Web UI's duplicate behavior. The `no text` quality tag is exempted from `generate`'s "negative word in positive prompt" warning.
- **Settings overridable in `.env.novelai`**: Reads only the following four settings and never reads API key lines. Priority is `arguments > environment variables / .env.novelai > defaults`: `NOVELAI_QUALITY_TAGS` (full quality-tag string; empty disables adding them; argument `--quality-tags`), `NOVELAI_UC_PRESET` (`heavy` or `none`, plus `light` and `human` on V5 Curated; argument `--uc-preset`), `NOVELAI_UC_PRESET_TEXT` (full UC preset string; argument `--uc-preset-text`), and `NOVELAI_CHECK_IDENTITY` (`1` enables identity-feature checking).
- **Characters**: `--charN-type`, `--charN-appearance`, `--charN-action`, `--charN-pos`, and `--charN-negative` (`N` is sequential starting at 1), or `--chars-json` to pass an array. Position pins are used and set `use_coords` to `true` only when specified for all characters (`--coords on|off|auto`). When omitted, `use_coords: false` (`AI’s Choice`) is used. **Even with `use_coords: false`, `centers` values affected the generated image in observed testing.** To reproduce the exact Web UI image, pass the Web UI coordinates with `--coords off` and `--charN-pos`. Web UI PNG fields `tag_hint_qt` and `tag_hint_uc_preset` did not affect the image and are not sent.
- **Style, background, and character text**: Pass the values of `NOVELAI_STYLE_`, `NOVELAI_BACKGROUND_`, and `NOVELAI_CHAR_` from `.env.novelai` directly as arguments. This script does not read prompt-variable values and treats unexpanded `${VARIABLE_NAME}` references as an error (it reads only the four helper settings above; requests with variable references use the `novelai_batch.py` mechanism in the next section).
- **Generation setting defaults**: Steps default to 23 for V5 and 28 for V4.5 (matching `novelai_api.py`; pass the Web UI value when reproducing a Web UI image). Uses `k_euler_ancestral`, `karras`, `prefer_brownian: true`, and `deliberate_euler_ancestral_bug: false` (omitting those two boolean flags causes the API defaults to differ from the Web UI). Dimensions use `--width` and `--height`, falling back to `generationCanvas` in `config/page-layout.json`, or the Web UI default 832 × 1216 when unset. Displays a notice when settings exceed the Opus no-Anlas candidate limits (1,048,576 pixels and 28 steps).
- **Actual sent JSON**: On every submission, saves `r001.request-body.json` (the exact bytes sent) and `r001.request.json` (a formatted copy of the same content) next to the candidate PNG. Because `.request.json` shares the request JSON format, you can copy it to `input/novelai/requests/`, adjust it by hand, and use it as the basis for regeneration.
- Only when using identity-feature checking (`cast` in `characters.json`), use `--cast-from <existing-request-ID>` to copy the registered cast entry.

<a id="character-variables"></a>

### Read characters, style, and backgrounds from `.env.novelai` (only on request)

To let humans change appearance globally before regenerating, character, style, and background prompts can become project-root `.env.novelai` variables referenced as `${NOVELAI_CHAR_MIO}`, `${NOVELAI_STYLE_MAIN}`, and `${NOVELAI_BACKGROUND_CLASSROOM}` in request JSON. **Only do this when a human asks.**

1. Propose names (`NOVELAI_CHAR_`, `NOVELAI_STYLE_`, or `NOVELAI_BACKGROUND_` according to purpose, plus uppercase ASCII letters, digits, `_`) and the prompt for each variable; confirm with the user.
2. Write to `.env.novelai` with `python -X utf8 scripts/novelai_batch.py env-set NOVELAI_CHAR_MIO --value-file input/novelai/char-mio.txt`. Other lines in `.env.novelai` are left unchanged. API keys live in shared `.env` or `.secrets/` and are neither displayed nor modified.
3. Check replacements with `templatize NOVELAI_CHAR_MIO --dry-run`, then replace matching wording in JSON with `templatize NOVELAI_CHAR_MIO`.
4. Check names with `vars`; record names and requests in [Batch records](../production/NOVELAI-BATCH.md).

Humans can then edit `.env.novelai` and rerun `generate`. Execution records contain expanded requests. Never expand API keys or variables other than `NOVELAI_CHAR_*`, `NOVELAI_STYLE_*`, and `NOVELAI_BACKGROUND_*`. A variable defined in both the environment and `.env.novelai` stops execution. If variables or helper settings placed in `.env` or `.secrets/` by an earlier version remain, execution stops and instructs you to migrate them to `.env.novelai` with `python -X utf8 scripts/novelai_batch.py env-migrate` (keeping other lines such as API keys; use `--dry-run` to preview). Source lines are removed only after saving to the destination succeeds; if a save fails mid-way and leaves duplicates in both files, verify the destination value and clean up the duplicate.

Assign style and background to Base (`input` and `v4_prompt.caption.base_caption`), and character features to the corresponding Character. For requests that do not use per-character input, merge them into the body. Only requests that reference a variable are affected by a change, so do not give every panel the same background; use separate background variables for each scene. `templatize` replaces every matching string in the request JSON, so check the targets with `--dry-run` and by reading the diff.

Values in Japanese can be saved and expanded as a single UTF-8 line. There is no translation feature, and the model's interpretation must be checked in the image. The feature check is disabled by default and compares the terms registered in `characters.json` with the expanded request only when `NOVELAI_CHECK_IDENTITY=1` is set (it is not image recognition or semantic understanding). When a character's appearance changes, update that file's features and the specification of visible features (`cast`) as well, and separately verify the assignment to per-character input by content. Do not force the same feature check on style and background.

Actual editing examples, applying edits from text files, dry-run checks, and regeneration, adoption, and PNG/PSD rebuilding are collected in the [user-facing README](../novelai-prompts/README.md). This feature is only for NovelAI batch generation and does not apply to other generation methods.

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

<a id="page-viewer"></a>

### Page-flipping HTML viewer for PNG previews (built by the AI agent)

Once pages are typeset with NovelAI and page PNG previews are built with `novelai_batch.py build`, the AI agent creates an HTML viewer that lets the user flip forward and backward through the pages and presents its path. This is a convenience aid for user review and an operational proposal of the production kit (user instruction, 2026-10-06). Do not apply it to other production methods such as `imagegen`. The HTML file is a review artifact placed in `output/`; it is not used for publication or distribution, and it does not replace visual image inspection or the post-artwork comparison table.

1. **Collect target pages**: Inspect `output/build/page-NN/` in numerical order and collect pages whose **latest version** (the folder with the highest `vNNN` number) contains both `page-NN.png` and `page-NN-display.png` (the review image scaled down to display width). Omit unbuilt pages (missing folders) or numbering gaps from the HTML, and tell the user which pages are missing.
2. **Create the HTML**: Replace `__PAGES__` in the template below with a JSON array of the following form and save it as UTF-8 to `output/build/preview.html`. Paths are relative to the HTML file (relative to `output/build/`):

   ```json
   [{"page": 1, "version": "v002", "display": "page-01/v002/page-01-display.png", "png": "page-01/v002/page-01.png"}]
   ```

3. **Reading direction**: Match `RTL` in the template to the publication format in the project's `OPTION.md`. In this US English edition, left-to-right reading is the default (`RTL = false`, `<nav dir="ltr">`, where `→` advances to the next page and `←` goes to the previous page); if right-to-left reading is selected, set `RTL = true` and `<nav dir="rtl">` (where the "Next page" button sits on the left and `←` advances to the next page).
4. **Rules to follow**: Do not use external libraries or external network calls. Do not copy or embed images; reference the existing PNG files. Page numbers and similar labels belong only in the viewer UI controls—never draw them onto the page images themselves (the rule against adding unrequested page numbers to pages remains in force).
5. **Post-creation check**: Verify that every `display` and `png` path written in the HTML actually exists. **Do not launch a browser.** Present the project-relative path and the existence-verified absolute path so the user can open it personally.
6. **Updating**: Every time pages are revised and rebuilt with `build`, recreate the HTML from step 1. Confirm that it does not point to stale versions (check that every page references its latest `vNNN`) before presenting it again.

Template (ready to save as-is; keyboard navigation, buttons, and page selector verified):

```html
<!doctype html>
<html lang="en">
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Page Preview</title>
<style>
:root{color-scheme:light dark}
body{margin:0;height:100vh;display:flex;flex-direction:column;font:16px/1.5 system-ui,sans-serif}
nav{display:flex;gap:.5rem;align-items:center;justify-content:center;flex-wrap:wrap;padding:.5rem;border-bottom:1px solid #8886}
button,select{font:inherit;padding:.35rem .9rem}
main{flex:1;min-height:0;display:flex;justify-content:center;align-items:center;padding:.5rem}
img{max-width:100%;max-height:100%;object-fit:contain;background:#fff}
</style>
<nav dir="ltr">
<button id="prev">Previous page</button>
<select id="jump" aria-label="Page"></select>
<button id="next">Next page</button>
<span id="info"></span>
<a id="full" target="_blank">Open full-size PNG</a>
</nav>
<main><img id="page" alt=""></main>
<script>
const pages = __PAGES__;
const RTL = false; // false for left-to-right works (US English default); true for right-to-left works
const $ = id => document.getElementById(id), img = $('page'), jump = $('jump');
let index = 0;
pages.forEach((p, k) => { const o = document.createElement('option'); o.value = k; o.textContent = 'Page ' + p.page; jump.append(o); });
function show(k) {
  index = Math.max(0, Math.min(pages.length - 1, k));
  const p = pages[index];
  img.src = p.display; img.alt = 'Page ' + p.page; $('full').href = p.png;
  $('info').textContent = (index + 1) + ' / ' + pages.length + ' (' + p.version + ')';
  jump.value = index; $('prev').disabled = index === 0; $('next').disabled = index === pages.length - 1;
  history.replaceState(null, '', '#' + p.page);
}
$('prev').onclick = () => show(index - 1);
$('next').onclick = () => show(index + 1);
jump.onchange = () => show(Number(jump.value));
addEventListener('keydown', e => {
  const step = e.key === 'ArrowLeft' ? (RTL ? 1 : -1) : e.key === 'ArrowRight' ? (RTL ? -1 : 1) : 0;
  if (step) show(index + step);
});
const start = pages.findIndex(p => '#' + p.page === location.hash);
show(start < 0 ? 0 : start);
</script>
</html>
```

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
