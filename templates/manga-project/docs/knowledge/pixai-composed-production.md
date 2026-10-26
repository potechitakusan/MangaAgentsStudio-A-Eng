# Standard Procedure for PixAI Asset Generation + Codex Typesetting

Read this when starting comic production with PixAI. For API specifications, cost confirmation, and transmission records, see [PixAI API Connection Procedure](pixai-api.md); for parameter acceptance and observed effects, see [Verification results from live generation](pixai-api.md#results). Because generation conditions vary by model and API version, re-verify immediately before sending. **LoRA effectiveness is unverified.**

**Keeping character consistency (production proposal)**: Under the conditions observed in testing, v2 (Tsubaki.2) with identical appearance wording written every time preserved character features most reliably. Use this as the primary approach, and convert prompts into `.env.pixai` variables only when requested by the user. When working from reference images alone, combine Tsubaki.2 with IP-Adapter and short color cues (such as `navy blue and red`), and add `sepia, yellow tint` to the negative prompt to suppress color casts. Haruka v2's IP-Adapter copies design motifs strongly but is prone to color casts and ignoring prompt actions, so limit it to character trials or key single illustrations.

## Starting production and choosing a style

1. Check the project's `OPTION.md`, any existing art-style instructions, and `config/pixai-production-policy.json`. Project-specific instructions take precedence.
2. **Choose a model.** The default is Tsubaki.2 (DiT; officially described as strong at prompt understanding, anatomy, and multiple characters). Choose Haruka v2 when prioritizing stable coloring and accurate hands, or Hoshino v2 for a style popular in Japan (both SDXL). Fifteen official PixAI models are pre-registered in `config/pixai-models.json` and can be selected simply via `--model <name>` without looking up version IDs (list them with `python -X utf8 scripts/pixai_models.py list`; see [Model list and characteristics](pixai-api.md#models)). Tsubaki.3 (`--model tsubaki3`) defaults to `mode` `pro` (`standard` and `lite` are rejected) and takes over 1 minute per image ([Verification results](pixai-api.md#results)). If the user specifies a model not in the catalog, get its model page URL and register it in the project catalog with `python -X utf8 scripts/pixai_models.py add <name> --url <URL>` (uses neither API key nor credits). Share the usage terms displayed at registration (commercial use, online sharing) with the user so they can confirm whether publication is permitted. If embedded data cannot be read, ask the user to click the version tab on the model page, copy that URL, and specify `--model-version-id` and `--model-type`.
3. **Choose an art style.** On the Tsubaki.2 and Tsubaki.3 family, use an official style preset (`--style-preset`, 35 presets; list with `python -X utf8 scripts/pixai_compose.py --list-styles`) or a style description (`--style`). On SDXL models, style presets are ignored, so define the look with a style description and style LoRAs. If no style is specified yet, present candidate models and preset names for the user to choose from and wait for their selection before generating artwork. Visual differences across models and style presets can be compared in the kit's `resources/pixai-model-samples/index.html` (15 official models and 35 style presets on Tsubaki.2, one image each using essentially the same prompt). When pointing the user to it, resolve the path from `sourceKitRelativePath` in `project.json` and show only the existence-verified absolute path (do not copy sample images into the project). Regenerating samples consumes credits, so do so only with explicit user permission. Never use the names of specific artists or manga creators. The `flat-anime-pastel` (Pastel Flat) style preset tends to draw an unprompted **halo above the head** (a motif reminiscent of existing IP), even when `halo` is in the negative prompt. Either avoid using it in published works or erase any halo that appears using `pixai_edit.py inpaint --no-style` (which redraws with Tsubaki.3) and inspect the result.
4. Standardize the chosen model, style, negative prompt, character appearance wording, LoRAs, and core generation settings (aspect ratio, resolution, `mode`) across the project, changing only action, camera angle, and background per panel. Do not rely on seed alone for consistency.

## Expressive capabilities available in PixAI (features supported by this kit)

| Feature | When to use | Status |
| --- | --- | --- |
| **Character LoRA** (v2 `loras`, up to 5) | Keep a character's face, hair, and outfit consistent across all panels. Put the version ID of a character LoRA published or created on the PixAI model market into `PIXAI_LORA_…` in `.env.pixai` and reference it from requests as `${PIXAI_LORA_MIO}`. Weight is `0`–`1` (default `1`). When trigger words are omitted, the model's default trigger words are used. Before use, run `python -X utf8 scripts/pixai_models.py lora --url <LoRA-page-URL>` once to record its base model and usage terms in `config/pixai-loras.json` (already-recorded entries do not need to be fetched again). Pre-send checks warn if the generation model and LoRA base model types differ | Verified in official docs; visual effect unverified |
| **Style LoRA** | Unify linework and coloring across the work. Up to 5 LoRAs total combined with character LoRAs | Same as above |
| **Style presets** (`style`) | Switch linework and coloring direction with a single key on the Tsubaki.2 / Tsubaki.3 family (`hard-line-monochrome-accent`, `pencil-sketch`, `retro-tv-anime`, etc.) | Verified in official docs; ignored on SDXL |
| **`mode`** (`lite`, `standard`, `pro`, `ultra`) | Quality and speed tiers on the Tsubaki.2 / Tsubaki.3 family. Tsubaki.2 accepts all 4 (`pro` and `ultra` shift toward soft, warm coloring). Tsubaki.3 accepts only `pro` and `ultra` (`standard` and `lite` are rejected). Credit differences across modes are unverified | Verified in official docs & [live generation](pixai-api.md#unverified-results) |
| **11 aspect ratios & `1.5k`** | Generate assets tailored to wide or tall panels. `1:3` and `3:1` work for vertical or horizontal strip panels | Verified in official docs |
| **`batchSize` 4** | Generate 4 candidates in a single task and compare them before adopting. **Use as the default for complex panels (2+ characters or inpainting) and retakes** (see "Batch size and cost" below) | Acceptance verified; see "[Batch size and cost](#batch-size)" below |
| **Hires Fix** (v1 `upscale`) & **ADetailer** (v1 `enableADetailer`) | Increase resolution on key panels (`1.5`× outputs 1272×1920 with finer detail). ADetailer's effect is subtle | Verified in official docs & [live generation](pixai-api.md#unverified-results) |
| **i2i** (v1 `mediaFile` + `strength`) | Redraw from a rough sketch, a previous panel, or an edited image. On Haruka v2, `strength` `0.6` makes small changes while keeping composition, and `0.9` makes larger changes while preserving composition and pose | Undocumented parameter; [acceptance & effect verified](pixai-api.md#unverified-results); requires `--allow-unverified` |
| **Inpainting** (v1 `--i2i` + `--mask`) | Redraw only a masked region (swapping props, adding details, erasing unwanted elements) while preserving everything outside the mask ([Inpainting](#inpaint)) | Undocumented parameter; [acceptance & effect verified](pixai-api.md#unverified-results); requires `--allow-unverified` |
| **`latentCouple`** (v1 region prompts) | Separate hair and outfits for left and right characters (SDXL), though an extra person may appear | Undocumented parameter; effect verified on SDXL, extra-person issue unresolved; requires `--allow-unverified` |
| **ControlNet** (v1 `controlNets`) | Transfer composition from a source image. From normal illustrations, `canny` (lines/shapes) and `depth` (depth/orientation) are effective; `openpose` does not work from normal illustrations, and `scribble` fails. Use on SDXL (`haruka2`, etc.; unsupported on Tsubaki.2) | Undocumented parameter; [`canny` & `depth` effect verified](pixai-api.md#unverified-results); requires `--allow-unverified` |
| **IP-Adapter** (v1 `ipAdapter.referenceFiles`) | **Character / style reference image.** Make a character without a LoRA resemble an adopted character-trial image | Undocumented parameter; acceptance verified; requires `--allow-unverified`. Official "PixAI Reference Pro" is not supported by the API |

Undocumented features (i2i, inpainting, ControlNet, `latentCouple`, IP-Adapter)—even those whose acceptance and effect have been [verified](pixai-api.md#unverified-results)—may change or stop working without notice. Use them only when the user agrees (`--allow-unverified`), test on a single panel and open the image to verify the result before scaling up, and record the outcome (acceptance, effect, credits) in the project's `docs/production/PIXAI-BATCH.md`. Never assume consistency or quality improvement merely because an undocumented feature was enabled.

## Asset generation and typesetting

Design panel layouts and reading order in Codex, and use PixAI to generate textless, borderless illustrations for typesetting. Generate compositions with enough margin around the figure so panels can be rotated, zoomed, and cropped during placement. Decide which contact points, faces, and hands must be visible—and where speech balloons will sit—before generating. When using image-conditioned panel generation (i2i, ControlNet, reference images), also follow `manga-external-panel-i2i` and [Shared external-panel i2i procedure](external-panel-i2i.md).

### Pre-production character trials

Before generating story panels, generate a character trial for each main character (such as `--id chara-mio`; you may use `batchSize 4` to compare candidates). Check the generated image against the text storyboard and character design sheet (hair length and color, glasses, layering order of hoodie/jacket over uniform, left/right placement of accessories), and adjust the appearance wording or LoRA weight before starting main production if anything differs. Adopted trial images can also serve as IP-Adapter reference images (undocumented feature; acceptance verified). Record trials and adjustments in the production log.

### Generation dimensions and panel placement

PixAI v2 determines dimensions by **aspect ratio and resolution tier** rather than raw pixel width and height ([Resolution table](pixai-api.md#official-specification-verified-facts)). Generate each panel asset **wider than the final cropped panel**, then reveal only the needed region using the panel frame and mask on the page.

- Choose the aspect ratio closest to the panel shape (`3:2` or `16:9` for wide panels, `2:3` or `9:16` for tall panels, `1:3` or `3:1` for strip panels). If `--aspect-ratio` is omitted, `pixai_compose.py` selects the ratio closest to `generationCanvas` in `config/page-layout.json`. See `panel_aspect_examples` in `config/pixai-production-policy.json` for examples.
- Actual generated pixel dimensions (for example, `2:3` at `1k` is 848×1280px) are saved in the execution record. When generating a full page as a single image, match the panel frames and final PNG dimensions to the actual pixel size ([Page layout settings](page-layout.md)).
- Control how the asset sits inside the panel via `focus` (the point in the image placed at the panel center), `zoom`, and `rotation` in the page manifest JSON. Zooming heavily into a wide establishing shot destroys the sense of space; regenerate with a true wide composition instead.

<a id="prompt-writing"></a>

### Assembling request prompts

Translate each storyboard panel into **visually observable** terms before writing the prompt. PixAI models read Danbooru-style tags and natural phrases (official example: `1girl, green hair, masterpiece, best quality, solo, standing, flower`). The guidelines below are kit production proposals; their isolated effect on PixAI has not been separately benchmarked.

1. **Order**: Headcount and primary subject (`1girl, solo` / `no humans`) → character appearance → visible posture, action, and expression → camera angle, shot size, and screen position → location landmarks → time of day and lighting → art style → quality tags. `pixai_compose.py` concatenates sections in this order.
2. **Use only parentheses for emphasis**: Write `(smile:1.2)`. Square brackets, curly braces, and NovelAI-style `1.2::word::` weights are not supported (per v1 official documentation; `generate` warns if present).
3. **Do not put negative words in the positive prompt**: Phrases like `not smiling`, `no people`, or `without glasses` can trigger the very element you want to avoid. Put unwanted elements in `negativePrompt`, and use the `no humans` tag for scenes without characters.
4. **Describe visible states rather than intent or mid-transition processes**: Write `eyes half closed, shoulders dropped, looking aside` instead of `about to sigh`; write `an unfolded sheet of paper with fold creases, held open in both hands` instead of `unfolding a paper airplane`.
5. **Specify whose body appears in close-ups**: Write `1boy, lower body, standing, school shoes, a paper airplane on the ground at his feet` or `1girl, hands only, …`.
6. **Two-character panels**: PixAI has no per-character prompt fields or coordinate pins. First consider whether the beat can be split into single-character panels (with the other person off-panel or over the shoulder). When drawing two characters together, place their shared posture and spatial relationship (`sitting side by side, girl on the left, boy on the right, facing each other`) *before* their individual appearances, and keep appearance tags to the minimum needed for identification. Although official docs note that Tsubaki.2 improves multi-character depiction, always inspect the generated image for swapped features. When using two character LoRAs simultaneously, check that their appearances do not bleed together.
7. **Choose camera angles from the storyboard**: `from above`, `from below`, and `from behind` are options, not mandatory prefixes for every panel. `generate` warns if the exact same angle repeats across 3 consecutive panels.
8. **Include identifying features in every request**: Write each character's signature features (hair color and length, glasses shape, clothing layering order, key accessories) using identical wording every time. Even when using a LoRA, write out the clothing and props that must be visible in that panel. If you register features in `input/pixai/characters.json` and list appearing characters under `cast` for each request, `generate` warns about missing feature terms when `PIXAI_CHECK_IDENTITY=1` is set (see example below; this check is string matching, not image recognition).
9. **Avoid numeric ages and `man` / `woman`**: Numeric ages rarely control visual appearance, and `man` or `woman` can cause an extra person to appear. Terms like `teenage`, `high school student`, and `adult` are fine.
10. **Keep `promptHelper` disabled**: PixAI's official default is `enable`, which automatically rewrites your prompt before sending. To preserve alignment with the text storyboard, this kit defaults to `disable`. If you enable it, record the reason (`generate` will display a warning).

```json
{
  "characters": {
    "mio": {"name_ja": "Mio Hinata", "features": {
      "hair": "light brown short bob hair", "outer": "open yellow hoodie worn over navy blazer"}}
  },
  "cast": {"p01-01": {"mio": "all"}, "p01-03": {"mio": ["outer"]}}
}
```

### Expanding scene relationships and continuity into each request

Rather than listing bare character and prop names, expand the text storyboard into each panel's visible state in the following order before writing the request:

1. **Pin down the instantaneous relationship**: Identify the primary subject and who is doing what to whom or what. Specify required contact points, held items, manipulations, actor and counterpart, posture, body orientation, gaze direction, and reader-facing left/right/top/bottom positions, narrowing down 1–3 conditions that distinguish this panel from another action.
2. **Carry over continuing states from the preceding panel**: Check clothing and colors, held props, which hand holds them, posture/orientation, and left/right positions and distance between characters. Update only what changed, and explicitly re-state any continuing state that remains visible in this panel (the previous panel's request is not carried over to the next generation call).
3. **Merge into a single prompt with explicit subjects**: Because PixAI has no separate per-character inputs, write explicit subjects for each action—for example, `girl on the left holding an open notebook toward the boy, boy on the right looking down at the notebook`. Never include character terms in a `no humans` panel.

**Never pass dialogue, lettering, or speech balloons to PixAI.** Do not include dialogue lines or positive tags such as `speech bubble` or `english text` / `japanese text` in the prompt, and do not ask the model to draw panel borders. Use `text, speech bubble, panel border, watermark` in the negative prompt. `pixai_compose.py` attaches those four terms by default when `PIXAI_NEGATIVE_PROMPT` in `.env.pixai` is unset (setting `PIXAI_NEGATIVE_PROMPT` replaces the default across all requests). Keep dialogue, in-world text, and sound effects in the typesetting specification.

<a id="prompt-content-check"></a>

### Pre-send content verification

When creating or inspecting prompts in `manga-ai-production`, read the expanded prompt, negative prompt, LoRAs, and reference images together and verify them against the text storyboard. Record the check in [PixAI Batch Generation Log](../production/PIXAI-BATCH.md).

| Check | What to verify |
| --- | --- |
| Relationships | Can the primary subject, actor/counterpart, and required contact, holding, or manipulation be identified from the sent prompt text? |
| Continuity | Are unchanged clothing, held items, hands, orientation, and positions from the previous panel preserved in this request? |
| Assignment & non-contradiction | Do subjects match their appearances and actions? Do LoRA / reference-image characters match the characters in the prompt? |
| Text separation | Are positive text/balloon tags absent, with negative tags and later typesetting specifications in place? |

`pixai_batch.py generate` inspects prompts before sending for negative words in positive prompts, expressions of intent, numeric ages, unanchored body parts, 2+ characters, bracket syntax, `promptHelper`, and 3-in-a-row camera angles, displaying warnings. If warnings remain, either revise the prompt or record the reason for keeping it before sending with `--accept-warnings`. Automated linting is keyword detection and does not replace human/agent content verification.

<a id="batch"></a>

### Request JSON, batch generation, adoption, and page rebuilding (reproducible by humans)

So that a human can regenerate individual pages or all pages, choose which candidate images to adopt, and rebuild pages with identical placement, keep all requests and page manifests in files and run generation, adoption, and rebuilding with the bundled `scripts/pixai_batch.py`.

| Path | Contents |
| --- | --- |
| `input/pixai/requests/p01-03.json` | One request JSON per panel ([Format](pixai-api.md#request-json-shape)). Named `p{2-digit-page}-{2-digit-panel}`; variants use `p01-03b.json`, character trials use `chara-mio.json`, etc. |
| `output/pixai/candidates/p01-03/r001.png` | Generated candidate. Increments sequentially on each run without overwriting. Saved alongside execution record `.pixai.json` (`taskId`, sent payload, cost-confirmation note). `batchSize` 4 saves `r001`–`r004` |
| `input/pixai/adopted.json` | Adopted candidate per request (recorded via `adopt`) |
| `input/typeset/page-01.json` | Typesetting specification (speech balloons, dialogue, in-world text, protected regions). See [Typesetting script](japanese-manga-readability.md#typeset-script) |
| `input/pages/page-01.json` | Page manifest: `layout.json`, typesetting spec, per-panel adopted image (`request` looks up `input/pixai/adopted.json`; `source` points to a file directly), `focus` / `zoom` / `rotation`, and SFX/other `overlays` |
| `output/build/page-01/v001/` | Rebuild output in a new folder per version: `page-01.png`, optional `page-01.psd`, `build.json`, and typesetting check results |

```json
{
  "schema_version": 1,
  "layout": "output/layout/page-001-v1/layout.json",
  "typeset": "input/typeset/page-01.json",
  "panels": [
    {"panel": 1, "request": "p01-01", "focus": [0.5, 0.4]},
    {"panel": 2, "request": "p01-02", "focus": [0.5, 0.5], "zoom": 1.1},
    {"panel": 3, "source": "output/fixed/p01-03-fix.png", "original_source": "output/pixai/candidates/p01-03/r002.png"}
  ],
  "overlays": [{"name": "SFX PAT", "source": "templates/onomatopoeia/images/burst-pata.webp", "center": [700, 1300], "scale": 0.6, "rotation": -10}]
}
```

```powershell
# Inspect content, dimensions, seed, and planned uploads without sending
python -X utf8 scripts/pixai_batch.py generate --page 1
# Generate page 1 sequentially one task at a time (all pages: --all; specific panels: --ids p01-02,p01-04)
python -X utf8 scripts/pixai_batch.py generate --page 1 --execute --accept-warnings --confirm-credits --cost-note 'Verified balance, approved scope, and timestamp'
# Re-fetch records whose completion polling was interrupted (does not re-send generation)
python -X utf8 scripts/pixai_batch.py fetch --page 1
# Compare candidates and adopt
python -X utf8 scripts/pixai_batch.py list --page 1
python -X utf8 scripts/pixai_batch.py adopt p01-02 --candidate 3
python -X utf8 scripts/pixai_batch.py adopt-latest --page 1
# Rebuild with identical page/panel placement (add --write-psd when also creating a PSD)
python -X utf8 scripts/pixai_batch.py build --page 1
```

- `generate` uses the request seed on the first run and random seeds on subsequent runs (`--seed request` fixes it; if a v1 request has no seed, a random seed is not added). Sends one task at a time and waits for completion, with a default 3-second interval between tasks and a default limit of 30 tasks per run. **Verifies cost confirmation and undocumented parameters across all target requests before sending the first task.** If any task fails, stops without sending the remaining tasks and never retries automatically.
- Default completion timeout is 900 seconds per task (`--timeout`). On models such as Tsubaki.3 `pro` that take over 1 minute per image, running `generate` across multiple tasks may exceed the execution environment's command timeout; use the environment's background/continuation mechanism and monitor progress via a log file (e.g., `output/pixai/gen-p1.log`). Use `fetch` to recover any records whose polling was interrupted.
- Do not regenerate panels that have an execution record without an image. If the record has a `taskId`, recover it with `fetch`. If it has no `taskId`, check generation status and credits in the PixAI web UI, then move the record to `failed/` with `move-unknown --ids <request-ID> --confirm-checked --note 'What was verified'`. Records where no task was created (HTTP 4xx) or where the task ended in `failed` or `cancelled` are moved to `failed/` automatically by the script.
- `adopt-latest` adopts the highest-numbered PNG in each target folder. Because an earlier highest-numbered candidate will be chosen if a new generation failed, always check generation results and inspect the images.
- `build` stops if any panel's adopted image has not been selected. To place an image created by another method (such as NovelAI) on the same page, specify its file path in `source` rather than `request`.
- When comparing prompt phrasing, create a variant request (`p01-03b.json`, etc.) with the same seed, run with `--seed request`, and keep all settings other than the changed wording identical. Do not draw conclusions from a pair whose unchanged control failed.
- When a human wants to work in a browser UI, start the WebUI following `.agents/skills/pixai-batch-webui/SKILL.md` and provide only the URL (do not launch a browser).
- Codex uses this same workflow from the initial artwork pass onward and records per-page commands in [PixAI Batch Generation Log](../production/PIXAI-BATCH.md). Present PNGs produced by `build` to the user.

<a id="batch-size"></a>

### Batch size and cost (when to default to `batchSize` 4)

**For complex panels (2+ characters or inpainting) and retakes (regenerating a panel that already has candidates), generate 4 images per task (`batchSize` 4) and compare the 4 candidates before adopting.** On Tsubaki.3 `pro` `1k`, 1 image costs 4,000 credits while 4 images cost 7,000 credits (1,750 per image), making a 4-image batch cheaper than running 1 image twice (verified by the user in PixAI usage history). For rough credit estimates on other models, see [Costs](pixai-api.md#costs).

- `pixai_compose.py` defaults to `batchSize` 4 when there are 2+ characters, when `--mask` (inpainting) is set, or when the request ID already has candidates (override to 1 image with `--batch-size 1`).
- `pixai_batch.py generate` sends panels that already have candidates (retakes) with a batch size of 4 (`--batch-size auto` by default; override with `--batch-size 1` or `4`). Check the dry-run summary line (`Total: N tasks, M images`) and verify that the user's approved credit scope covers the 4-image batches.
- A single-character simple panel only needs 1 image on its first run.
- A 4-image batch is saved sequentially (e.g., `r005` through `r008`), and the WebUI groups them together as "4 images from the same generation" so you can compare and adopt from them.

<a id="inpaint"></a>

### Inpainting and i2i (fixing generated panels with `scripts/pixai_edit.py`)

Creates an **inpaint** request (redrawing only the masked region) or an **i2i** request (redrawing the entire image) from an adopted image (or candidate). Carries over the original request's prompt, negative prompt, model, style preset, `mode`, LoRAs, and seed, prepends the desired fix (`--add`) to the prompt, and saves under a variant ID (such as `p04-01b`). Leaves the original request and candidates untouched and makes no network calls.

```powershell
# Fix only part of an image: also creates the mask (white = redraw) and overlay preview input/pixai/masks/<ID>.preview.png. Defaults to 4 images
python -X utf8 scripts/pixai_edit.py inpaint p04-01 --add "girl with cat ears on top of head" --ellipse 300,40,260,180
# Redraw the whole image: strength 0.6 keeps composition with small changes; 0.9 keeps composition/pose with larger changes (Haruka v2 example)
python -X utf8 scripts/pixai_edit.py i2i p04-01 --add "snowy park, winter, snow" --strength 0.6
# Dry-run check → send (requires --allow-unverified because these use undocumented parameters)
python -X utf8 scripts/pixai_batch.py generate --ids p04-01b
# Adopt (compare the redrawn region side-by-side with the original image at native resolution, then adopt the variant file into the original panel)
python -X utf8 scripts/pixai_batch.py adopt p04-01 --file output/pixai/candidates/p04-01b/r002.png
```

- Uses the adopted image as the source by default, or the latest candidate if none is adopted (specify `--candidate N` to pick a specific candidate). `1.5k` images that exceed v1 dimension limits (512–1280px) cannot be edited via v1 i2i/inpaint.
- When the source image came from a model that does not support inpainting (such as Tsubaki.2, marked `inpaint: false` in `config/pixai-models.json`), omitting `--model` redraws with Tsubaki.3. This blends well for backgrounds and small props (succeeded in 3 of 4 images when erasing a background halo).
- When a style preset caused the unwanted artifact (such as the overhead halo in `flat-anime-pastel`), pass `--no-style` so the preset is not carried over. Add extra negative terms with `--negative`.
- Specify mask regions with `--ellipse` or `--rect` (`left,top,width,height`; repeatable). Warns if the mask covers more than 20% of the canvas. To build masks separately, use `scripts/pixai_mask.py`; to assemble a request from scratch, use `pixai_compose.py --i2i <image> --mask <mask> --strength 0.75` (which sets request dimensions from the source image and rejects masks with mismatched dimensions).
- Write `--add` with an explicit subject for what you want drawn (e.g., `both girls have cat ears`, `girl wearing a red beret`).
- Include both the item being added and the empty space it will occupy (for ears, the background above the head) inside the mask, while keeping shapes you do not want redrawn outside the mask. **Making the mask too large causes faces, expressions, ribbons, and props inside the mask to change as well** (and does not improve the success rate of adding items). Keep masks off the face whenever possible.
- Omitting the subject can cause terms like `cat ears` to combine with the added item and draw something unintended (such as a "small cat wearing a beret").
- Prop replacement (cup → apple) and removal (clasping hands) are reliable with a small mask. Adding items (hats, ears) succeeds in roughly 2 out of 4 images, so generate 4 candidates and choose the best one.
- **Inspect results by comparing the redrawn region side-by-side with the original image at full native resolution** (scaled-down previews make it easy to misjudge small additions).
- Because inpainting and i2i fields (`mediaId`, `maskMediaId`, `strength`) are undocumented, sending requires `--allow-unverified`, and support may change without notice.
- For test details, see [PixAI API Connection Procedure](pixai-api.md#inpaint-results).

<a id="layout-control"></a>

### Transferring composition (ControlNet) and left/right separation (`latentCouple`)

Both are undocumented v1 parameters used with SDXL models (`haruka2`, etc.; Tsubaki.2 does not support ControlNet and ignores `latentCouple`). For verification details, see [PixAI API Connection Procedure](pixai-api.md#unverified-results).

- **ControlNet**: Transfers composition from a rough sketch or existing illustration. From normal illustrations, `canny` (lines and shapes; strongest transfer) and `depth` (depth and orientation) are effective. `openpose` does not work from normal illustrations (skeleton stick-figure images untested), and `scribble` fails. Assemble with `pixai_compose.py --model haruka2 --controlnet canny:input/rough/p01-04.png[:weight]`.
- **`latentCouple`**: Divides the canvas into rectangles to separate left and right character hair and clothing. It separates attributes as specified, **but may add a third person**. When using it, write the request JSON by hand (example below) and pick a candidate with the right headcount out of 4 images. Until the extra-person issue is resolved, keep `--layout` plus inpainting fixes as the standard approach for two-character panels.

```json
{"api": "v1", "parameters": {"prompts": "2girls, side by side, park AND girl, long red hair, green dress AND girl, short blue hair, yellow raincoat",
  "modelId": "1861558740588989558", "width": 1280, "height": 848, "batchSize": 4,
  "latentCouple": {"type": "rect", "divisions": ["1:1", "1:2", "1:2"], "positions": ["0:0", "0:0", "0:1"], "weights": [0.2, 0.8, 0.8]}}}
```

<a id="compose"></a>

### Assembling request JSON from arguments (`scripts/pixai_compose.py`)

**Standard way to assemble requests for PixAI API generation.** Accepts model, art style, background, characters, LoRAs, style preset, and generation settings as arguments and saves the request JSON to `input/pixai/requests/<ID>.json`. Makes no network calls and displays the same dry-run check as `pixai_batch.py generate` after saving. Hands off to transmission only when `--execute` and cost-confirmation flags are passed. Saved request JSON files may be edited by hand.

```powershell
python -X utf8 scripts/pixai_compose.py --id p01-03 --seed 123 `
  --char1-appearance "<appearance>" --char1-action "<pose and action>" `
  --scene "upper body, from below" --background "school rooftop, blue sky" --style "<style>" `
  --style-preset moe-pastel --mode standard --lora '${PIXAI_LORA_MIO}:0.8'
# Two-character panel: place shared posture and spatial relationship before appearance with --layout
python -X utf8 scripts/pixai_compose.py --id p01-05 --layout "girl on the right, boy on the left, facing each other" `
  --char1-appearance "<appearance>" --char2-type boy --char2-appearance "<appearance>" --scene "upper body"
# ControlNet & reference image (v1 undocumented features; use with SDXL models)
python -X utf8 scripts/pixai_compose.py --id p01-04 --model haruka2 --char1-appearance "<appearance>" `
  --reference output/pixai/candidates/chara-mio/r002.png --controlnet canny:input/rough/p01-04.png --adetailer
```

- **Model**: `--model tsubaki2` (default; overridable via `PIXAI_MODEL` in `.env.pixai`), `tsubaki3`, `haruka2`, `hoshino2`, or any name in `config/pixai-models.json`, or `--model-version-id` with `--model-type dit|sdxl`. List models with `--list-models`. Passing `--mode` or `--style-preset` to a model that does not support them (SDXL or first-gen Tsubaki family) raises an error (officially, `mode` is rejected and `style` is ignored outside the Tsubaki.2 / Tsubaki.3 family). When `--mode` is omitted, the model's `default_mode` from the catalog is used, or omitted if none is defined.
- **Order**: Concatenates `headcount tag (derived automatically from characters: solo for 1 character, no humans for 0) → --layout (posture and spatial relationship for multiple characters) → characters (prepends girl / boy to each character when 2+ characters are present) → --scene → --background → --style → quality tags` without rewriting input text.
- **Quality tags**: Defaults to `masterpiece, best quality` (from the official example prompt; visual difference unverified). Skips tags already present in the input. Customize with `--quality-tags`, `--no-quality-tags`, or `PIXAI_QUALITY_TAGS`.
- **Negative prompt**: `PIXAI_NEGATIVE_PROMPT` (`--negative-base`; defaults to `text, speech bubble, panel border, watermark` when neither is set, or disabled when set to an empty string) → `--negative`. Because negative prompts in v1 (`negativePrompts`) are undocumented, no default negative prompt is attached in v1 unless `--negative-base` or `--negative` is explicitly specified.
- **LoRA**: Repeat `--lora ID[:weight[:triggerWords]]` (up to 5 in v2, up to 3 in v1). `ID` is a numeric version ID or `${PIXAI_LORA_…}`. Because v1 has no dedicated trigger-word field, trigger words in v1 are appended to the prompt text.
- **Arguments that switch the request to v1**: `--upscale` and `--adetailer` (official), plus `--i2i` (with `--strength` / `--mask`), `--controlnet type:image[:weight]`, and `--reference image` (undocumented parameters; see [Verification results](pixai-api.md#unverified-results)). Use `pixai_edit.py` when fixing an already-generated panel. Because v1 specifies dimensions via `width` and `height` (512–1280), `--size 1.5k` and `1:3` / `3:1` cannot be used in v1. Negative prompts (`negativePrompts`) and `seed` in v1 are also undocumented parameters (acceptance and seed behavior verified).
- **Settings overridable in `.env.pixai`**: Reads only `PIXAI_MODEL`, `PIXAI_QUALITY_TAGS`, `PIXAI_NEGATIVE_PROMPT`, `PIXAI_PROMPT_HELPER`, and `PIXAI_CHECK_IDENTITY`, and never reads API key lines. Priority is `arguments > environment variables / .env.pixai > defaults`.
- **Style, background, and character text**: Pass the values of `PIXAI_STYLE_`, `PIXAI_BACKGROUND_`, and `PIXAI_CHAR_` from `.env.pixai` directly as arguments. This script does not expand prompt variables and treats `${VARIABLE_NAME}` (except in `--lora`) as an error.
- Only when using character identity-feature checking, copy the cast entry from an existing request with `--cast-from <existing-request-ID>`.

<a id="character-variables"></a>

### Reading characters, styles, backgrounds, and LoRAs from `.env.pixai` (only on request)

So that a human can edit appearances in bulk and regenerate, prompt snippets and LoRA version IDs can be stored as variables in `.env.pixai` at the project root and referenced from request JSON as `${PIXAI_CHAR_MIO}`, `${PIXAI_STYLE_MAIN}`, `${PIXAI_BACKGROUND_CLASSROOM}`, and `${PIXAI_LORA_MIO}`. **Do this only when requested by a human.** Keep API keys and URLs in the shared `.env` file, never in `.env.pixai`.

1. Propose variable names (`PIXAI_CHAR_`, `PIXAI_STYLE_`, `PIXAI_BACKGROUND_`, or `PIXAI_LORA_` + uppercase ASCII letters, digits, and `_`) and their values, and confirm with the user. `PIXAI_LORA_` values must be numeric LoRA version IDs only.
2. Write each variable to `.env.pixai` with `python -X utf8 scripts/pixai_batch.py env-set PIXAI_CHAR_MIO --value-file input/pixai/prompts/mio.txt`. Other lines remain untouched.
3. Preview replacements with `templatize PIXAI_CHAR_MIO --dry-run`, then replace matching strings in request JSON with `templatize PIXAI_CHAR_MIO` (including v1 `lora` keys).
4. Verify registered variable names with `vars`, and record the variable names and affected requests in [PixAI Batch Generation Log](../production/PIXAI-BATCH.md).

From then on, the human can edit values in `.env.pixai` and re-run `generate`. At generation time, the expanded request is saved in the execution record. Never expand API keys or variables outside the four allowed prefixes. Defining the same variable in both environment variables and `.env.pixai` stops execution. For hands-on editing examples, see the [user-facing README](../pixai-prompts/README.md).

### Post-artwork comparison (required before typesetting)

Once adopted images are ready for all panels, **actually open each image** and fill out the "Post-artwork comparison" table in the project's [Storyboard checks](../reviews/NAME-REVIEW.md) panel by panel before typesetting. Under "Plan," write the storyboard's primary subject, action, camera angle, and characters; under "Observed image," describe what is actually drawn in the image. Resolve any mismatch by regenerating, adjusting placement, or revising the plan, and record the adoption decision and reason. Do not proceed to typesetting until this table is complete. For any image whose execution record marks `mediaSafetyLevel` as `nsfw`, judge whether it is acceptable against the target publication's standards (absence of that value does not guarantee safety).

### Typesetting

Typeset speech balloons, horizontal English dialogue, in-world text, and panel frames using the bundled `scripts/typeset_manga.py` (see [Typesetting script](japanese-manga-readability.md#typeset-script)). Attach tails to spoken dialogue balloons pointing toward the speaker's mouth. Never place text over faces, hands, or important props. Depict text written on in-world objects as part of the objects themselves. Do not add unrequested titles, page numbers, logos, or signatures to pages.

Search sound effects in `templates/onomatopoeia/catalog.json` by meaning, wording, use, and intensity, and check `placement_hint_en` (and compatibility alias `placement_hint_ja`) along with [Scene wording](../../templates/onomatopoeia/README.md#select-wording-for-the-scene). When colored lettering is needed, create a recolored copy in the project using `scripts/recolor_onomatopoeia.py` (never write back into the shared template).

When a candidate's overall look is adoptable and only a local detail differs (ears, small props, hand orientation, etc.), **use PixAI inpainting as the first choice** ([Inpainting](#inpaint)). It preserves the composition, expression, and other characters at the same credit cost as regenerating a panel. If inpainting does not resolve the issue, consider local retouching with `imagegen` or regenerating the panel. Always preserve both the original artwork and the edited version.

### Checking PNG previews

After building page PNGs with `pixai_batch.py build`, present them in page order via the WebUI Preview tab or by showing `page-NN-display.png` from each page's latest version folder (the folder with the highest `vNNN` number under `output/build/page-NN/vNNN/`). When creating a page-flipping HTML viewer, use no external libraries or network calls, reference existing PNGs via relative paths, and save it to `output/build/preview.html`. In left-to-right works (the US English default), `→` advances to the next page; in right-to-left works, `←` advances to the next page. **Do not launch a browser**; present the existence-verified absolute path so the user can open it personally.

## Confirming costs

PixAI generation consumes credits (from membership allowances or purchased packs). **Because the official documentation provides no API for querying credit balance or consumption**, the scripts cannot determine whether a run is free.

1. Show the user the planned generation scope (number of tasks, images per task, model, `mode`, resolution, LoRAs, Hires, ADetailer, reference images).
2. Attach `--confirm-credits` **only when the user explicitly authorizes consuming credits for that scope**, and record the verified balance, approved scope, and timestamp in `--cost-note`. Setting up an API key, checking connectivity, or asking to generate does not by itself count as permission for paid credit usage.
3. Obtain fresh permission whenever exceeding the approved scope (adding pages, changing `mode`, resolution, or batch size, or using undocumented features).
4. Actual credit consumption is not measured automatically (`actualCreditCost` in the execution record is `null`). When needed, the user checks usage history in the PixAI web UI and records it in the production log.

Final page dimensions are determined separately from publication or print requirements; you do not need to cram an entire page into a single generation canvas size.

## PSD handoff preserving original artwork

Check the PNG preview first, and create a PSD only after receiving both confirmation that the PNG needs no changes and an instruction to create the PSD ([PSD handoff](psd-handoff.md)). `pixai_batch.py build --write-psd` uses `scripts/export_composed_psd.py` to store uncropped original panel artwork in a hidden layer group and place each positioned panel image on its own layer with a pixel mask hiding only the area outside the panel frame. This preserves the original artwork, placement matrix, and mask for later repositioning (it does not use Photoshop Smart Objects). Actual loading verification in CLIP STUDIO PAINT is still required separately.

## Sources and verification scope

For API specification sources and verification dates, see [PixAI API Connection Procedure](pixai-api.md#sources-and-verification-scope) (2026-10-25). The prompt-writing order, scene-expansion steps, and content-verification checklist are production proposals adapting this kit's comic workflow to PixAI (single-prompt generation without separate per-character inputs); their isolated effect on PixAI has not been separately benchmarked.
