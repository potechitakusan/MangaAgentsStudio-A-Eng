# PixAI API Connection Procedure

Applies to the project-bundled `scripts/pixai_api.py` (single-task generation), `scripts/pixai_compose.py` (request assembly), and `scripts/pixai_batch.py` (per-panel batch generation, adoption, and page rebuilding). Authentication checks, normal text-to-image request creation, and API communication run on the Python 3.10+ standard library. Checking source image and mask dimensions when creating i2i or inpaint requests, converting WebP/JPEG responses to PNG, and running `build` for page PNGs use Pillow. Exporting PSDs as well with the pinned dependencies in `scripts/requirements-composition.txt` requires Python 3.12+ and Pillow, numpy, and psd-tools. Do not launch or control a browser. Requires the project's `project.json`; do not run inside the kit template.

If asked in a project to "use PixAI" or "check the PixAI connection," Codex guides the user with this procedure. Show the key-format example below when key setup is needed; do not ask the user to re-enter it if already configured. For the production workflow (prompt assembly, LoRA, reference images, adoption, and typesetting), see [PixAI Production Procedure](pixai-composed-production.md).

## Prepare the key

Use a PixAI API key. Create the key in [PixAIのプロフィールのAPI設定](https://pixai.art/profile/edit/api) (issued immediately on membership plans; email applications require review per the official FAQ). Never pass an email address, login password, or browser token. Do not paste the key into conversations, prompts, or generation request JSON; instead, the user sets it in one of the following places:

- Environment variable `PIXAI_API_KEY` visible to Codex or the terminal process
- The project's shared `.env` file or `.secrets/pixai.env`, writing the actual value to the right of `PIXAI_API_KEY=`

```dotenv
PIXAI_API_KEY=YOUR_ACTUAL_KEY
```

**The key name is `PIXAI_API_KEY`, and the secret is the value to the right of `=`.** The script uses the first non-empty value in order: environment variable → `.secrets/pixai.env` → `.secrets/.env` → `.env`. File format handling (UTF-8, quotes, `export`, trailing comments) and never printing secret values or raw input lines in error messages follow the same implementation policy as NovelAI key loading. `.env.example` is a sample of key names and is not loaded. `.secrets/`, `.env`, and `.env.*` (except `.example` files) are Git-ignored.

### How configuration files are split

A project's configuration files are split into three files:

| File | Contents | Sample |
| --- | --- | --- |
| `.env` | Shared settings such as API keys and endpoint URLs (`NOVELAI_API_KEY`, `PIXAI_API_KEY`, `COMFYUI_URL`, etc.) | `.env.example` |
| `.env.novelai` | NovelAI character, style, and background prompt variables and helper settings | `.env.novelai.example` |
| `.env.pixai` | PixAI character, style, background, and LoRA prompt variables and helper settings | `.env.pixai.example` |

API keys can also be placed in `.secrets/` or environment variables in addition to `.env`. `pixai_batch.py` reads only prompt variables and helper settings from `.env.pixai` and environment variables, ignoring API keys and lines in other files.

## Check without generating

```powershell
python -X utf8 scripts/pixai_api.py key-status
python -X utf8 scripts/pixai_api.py status
```

`key-status` makes no network calls. `status` queries a non-existent task ID (`GET /v1/task/0`) once and treats 404 as "authentication succeeded" and 401 as "invalid key" (verified with a live key on 2026-10-25: a valid key returns `404 not found` and an invalid key returns `401 Invalid token`). It does not generate images or consume credits.

**The official documentation provides no API for querying credit balance or consumption.** Check your plan and remaining credits in the PixAI web UI. Because the script cannot determine whether a run is free, sending requests requires explicit user permission (see below).

<a id="official-specification-verified-facts"></a>
<a id="公式仕様確認した事実"></a>

## Official specification (verified facts)

Source: [PixAI API Documentation](https://platform.pixai.art/en/docs) ([llms-full.txt](https://platform.pixai.art/llms-full.txt) and the TypeScript definitions on each page). Retrieved: 2026-10-25.

| Item | Details |
| --- | --- |
| Endpoint & auth | `https://api.pixai.art`, `Authorization: Bearer <key>` on all requests |
| v2 generation | `POST /v2/image/create`. Required: `modelVersionId`, `prompt`. Optional: `negativePrompt`, `aspectRatio` (`1:1`, `2:3`, `3:2`, `3:4`, `4:3`, `3:5`, `5:3`, `9:16`, `16:9`, `1:3`, `3:1`, default `1:1`), `size` (`1k`, `1.5k`, default `1k`), `mode` (`lite`, `standard`, `pro`, `ultra`; Tsubaki.2 and Tsubaki.3 only—other models return `400 INVALID_ARGUMENT`), `style` (`{"type": "preset", "key": …}` with 35 presets or `{"type": "custom", "custom": …}`; Tsubaki.2 and Tsubaki.3 family only, ignored elsewhere), `loras` (up to 5; `modelId` = LoRA version ID, `weight` 0–1 default 1, `triggerWords` defaults to model default when omitted), `seed`, `batchSize` (1 or 4, default 1), `sampling` (`method`, `steps` 1–100, `cfgScale`; SDXL and SD v1 only), `promptHelper` (`enable` or `disable`, **default is `enable`**, which rewrites the prompt before sending), `callbackUrl`. `modelId` is deprecated |
| v1 generation | `POST /v1/task`. `{"parameters": {…}, "callbackUrl"}`. Official `parameters` fields: `prompts` (up to 4096 characters; supports parenthetical emphasis, does not support square or curly brackets), `modelId`, `width` and `height` (512–1280), `lora` (`{versionId: weight}`, `maxProperties` 3, though the prose description also says "up to 10"), `batchSize` (1–4), `inferenceProfile`, `modelStyle` (`key`, `custom`, `styleKeyRef`), `enableTile` (when a source image is present and `upscale > 1`), `upscale` (Hires Fix; keeps the long edge within 2048px), `upscaleSampler`, `enableADetailer` (face refinement), `promptHelper` (`{"enable": bool}`). This page is unlisted from the documentation table of contents (the URL remains active) |
| Task status | `GET /v1/task/{taskId}`. `status` is `waiting`, `running`, `completed`, `failed`, or `cancelled`. On completion: `outputs.mediaIds` and `outputs.mediaUrls` (`null` for unavailable images). `mediaSafetyLevel` and `textSafetyLevel` (`nsfw` or `safe`; absence does not guarantee safety) |
| Media | `GET /v1/media/{mediaId}` (`PUBLIC`, `THUMBNAIL`, etc. in `urls`), `GET /v1/media/{mediaId}/image` (302 redirect to image), `POST /v1/media/upload` (sends the raw image/video binary directly; requires `Content-Type` and an exact `Content-Length`; multipart is not accepted; response `id` is the `mediaId`) |
| Limits | Up to 10 concurrent `waiting` tasks (`running` tasks do not count). No request rate limit, but poll no faster than once every 1.5 seconds and use exponential backoff for retries. Video generation, PixAI Reference Pro, PixAI Edit, and PixAI Edit Lite are not yet supported (in development) |
| Retention | Generated images are not stored indefinitely; fetch them immediately upon completion. API generations are private and do not appear in public generation history |
| Resolutions (v2) | See table below. All dimensions are multiples of 16. `1.5k` has a long edge of 1536px |
| Models | Recommended: Tsubaki.2 (DiT, `1983308862240288769`; strong prompt understanding, anatomy, and multi-character depiction), Haruka v2 (SDXL, `1861558740588989558`; stable, accurate hands), Hoshino v2 (SDXL, `1954632828118619567`; style popular in Japan). All three models support samplers Euler a, Euler, LMS, Heun, DPM2 Karras, DPM2 a Karras, DDIM, DPM++ 2M Karras, DPM++ 2S a Karras, DPM++ SDE Karras, DPM++ 2M SDE Karras, and Restart. For other models and LoRAs, use the final number in `https://pixai.art/model/<modelId>/<versionId>`. Tsubaki.3 is not on the models list page, but the v2 generation documentation lists it as supporting `mode` and `style`. The kit includes 15 official models (see "Model list and adding models" below) |
| Rights | Copyright in images generated via the API belongs to the user (verifying third-party rights and legal compliance is the user's responsibility). Commercial use of official models is permitted for approved users; redistributing model files is prohibited. [利用規約](https://pixai.art/terms) |

| Aspect Ratio | 1k | 1.5k |
| --- | --- | --- |
| 1:1 | 1024×1024 | 1536×1536 |
| 2:3 | 848×1280 | 1024×1536 |
| 3:2 | 1280×848 | 1536×1024 |
| 3:4 | 864×1152 | 1152×1536 |
| 4:3 | 1152×864 | 1536×1152 |
| 3:5 | 768×1280 | 912×1536 |
| 5:3 | 1280×768 | 1536×912 |
| 9:16 | 720×1280 | 864×1536 |
| 16:9 | 1280×720 | 1536×864 |
| 1:3 | 512×1536 | 512×1536 |
| 3:1 | 1536×512 | 1536×512 |

### Undocumented parameters

The v1 TypeScript types in the [公式JavaScriptクライアント](https://github.com/pixai-art/pixai-client-js) (`src/parameters.types.ts`, retrieved 2026-10-25) include the following fields that do not appear in the current official documentation. Because they may stop working without notice, `pixai_api.py` requires `--allow-unverified` on requests that send them and records them under `unverifiedParameters` in the execution record. For acceptance and observed effects, see "[Verification results for undocumented parameters](#unverified-results)" below.

- `negativePrompts`, `seed`, `samplingSteps`, `samplingMethod`, `cfgScale`, `clipSkip`, `vaeModelId`
- i2i: `mediaId` or `mediaUrl` (source image), `strength` (amount of change), `maskMediaId` / `maskMediaUrl` (inpainting)
- `controlNets`: `[{"type": "openpose", etc., "mediaId", "weight"}]`. Types: `dwpose`, `openpose_full`, `canny`, `depth`, `hed`, `mlsd`, `openpose`, `seg`, `normal`, `scribble`
- `ipAdapter`: `{"enabled": true, "referenceImages": [mediaId…]}`. The type comment describes it as transferring style, composition, and facial features from reference images
- `latentCouple` (region-specific prompts), `upscaler`, `upscaleDenoisingSteps`, `upscaleDenoisingStrength`, `enlarge`, `enlargeModel`

<a id="models"></a>

### Model list and adding models (use without looking up version IDs)

The project's `config/pixai-models.json` includes the version IDs, model types, accepted parameters, and usage terms for 15 official PixAI models. You can select one simply with `pixai_compose.py --model <name>` without looking up version IDs. List them with `python -X utf8 scripts/pixai_models.py list`.

Source: Embedded data on the [PixAI公式アカウントのモデル一覧ページ](https://pixai.art/en/@pixai-official/artworks/models) (retrieved 2026-10-25), verified to match the version IDs of the 3 recommended models in the official documentation. PixAI Edit and PixAI Reference Pro are excluded because they are not supported by the API. All official models permit commercial use (`permittedUse` on the page). Usage counts displayed on the page (as of 2026-10-25): roughly 250 million runs for Haruka v2, 110 million for Tsubaki.2, and 30+ million each for Haruka and Tsubaki.

| Name (`--model`) | Model | Type | `mode` & style presets | Key characteristics (page display & official description) |
| --- | --- | --- | --- | --- |
| `tsubaki3` | Tsubaki.3 | DiT (`MMDIT26B_MODEL`) | Supported; default mode `pro` (`standard` is rejected) | Latest model. Color control and strong prompt adherence |
| `tsubaki3-flash` | Tsubaki.3 Flash | DiT (same as above) | Supported (mode not sent by default) | Fast variant (8 steps). Listed as not supporting `negativePrompt` |
| `tsubaki2` | Tsubaki.2 | DiT (`MMDIT26A_MODEL`) | Supported; default mode `standard` | Kit default. Multiple characters, lighting, dynamic poses |
| `tsubaki`, `tsubaki-v1-1`, `tsubaki-flash` | Tsubaki, Tsubaki v1.1, Tsubaki Flash | DiT (`DIT7B_MODEL`) | Not supported (officially Tsubaki.2 & Tsubaki.3 family only) | First-generation family. Natural language, multiple characters |
| `serin` | Serin | DiT (`DIT7B_MODEL`) | Not supported | Korean webtoon / fashion style |
| `haruka2`, `haruka` | Haruka v2, Haruka | SDXL | Not supported | Stable coloring, accurate hands |
| `hoshino2` | Hoshino v2 | SDXL | Not supported | Style popular in Japan, retro anime look |
| `otome2` | Otome v2 | SDXL | Not supported | Tailored for male characters |
| `hinata2`, `nagi`, `crystalize`, `eternal` | Hinata v2, Nagi, Crystalize, Eternal | SDXL | Not supported | Tailored for style reproduction |

For API acceptance and `mode` behavior, see "[Model verification results](#model-results)" below; to compare visual styles across all models and style presets, open the kit-only sample viewer `resources/pixai-model-samples/index.html` (one image per entry using essentially the same prompt).

**Models not in the list** (such as user-created models) can be registered into the project's catalog from their model page URL:

```powershell
python -X utf8 scripts/pixai_models.py info --url https://pixai.art/model/<modelId>/<versionId>   # Display only
python -X utf8 scripts/pixai_models.py add my-model --url https://pixai.art/model/<modelId>/<versionId>
```

- Fetches the public model page once and reads the version ID, model type, negative-prompt support, and usage terms (commercial use, online sharing, creator attribution) from the embedded page data. Does not send your API key, log in, or spend credits. If the URL does not specify a version, the latest version on the page is used.
- Determines whether `mode` and style presets are supported from the model type (only `MMDIT26*` = Tsubaki.2 and Tsubaki.3 family support them). Newly registered models have their `api` status marked as unverified and do not send `mode` by default.
- Passing a LoRA page prints its version ID and declines model registration (write LoRAs under `PIXAI_LORA_…` in `.env.pixai`).
- Displays a warning when registering non-commercial models. Many user-created models permit personal use only (confirmed among top-ranked models on 2026-10-25); the user must verify on the model page whether online publication or sale is permitted.
- Because the embedded page data is not an official PixAI API, format changes may prevent reading it. If it cannot be read, ask the user to click the version tab (e.g., "v1") on the model page, copy that URL, and pass `--model-version-id` and `--model-type dit|sdxl`. Summarizers such as WebFetch may drop the version ID.
- Credit consumption cannot be queried via API. Users check usage history under "Membership & Credits" on their PixAI profile ([User Profile](https://support.pixai.art/en/articles/11822651-user-profile), checked 2026-10-25).

`pixai_api.py` blocks requests before sending if they hit a model's `modes_rejected` (rejected `mode`), `controlnet: false`, or `inpaint: false` in the catalog, and marks any `mode` not in `modes_accepted` as unverified.

The `GET /generationModel/{modelVersionId}/style-keys` and `GET /model/{modelId}/version/{versionId}/inference-profiles` endpoints mentioned in the v1 documentation under `modelStyle` and `inferenceProfile` return a 400 expecting a GraphQL request when queried with a live key (checked 2026-10-25) and are not used by the scripts.

<a id="request-json-shape"></a>
<a id="要求jsonの形"></a>

## Request JSON shape

`input/pixai/requests/<ID>.json` (or any JSON file inside the project for one-off runs). Standard format is v2:

```json
{
  "api": "v2",
  "body": {
    "modelVersionId": "1983308862240288769",
    "prompt": "1girl, solo, ${PIXAI_CHAR_MIO}, standing, upper body, school rooftop, masterpiece, best quality",
    "negativePrompt": "text, speech bubble, panel border, watermark",
    "aspectRatio": "2:3", "size": "1k", "mode": "standard",
    "style": {"type": "preset", "key": "moe-pastel"},
    "loras": [{"modelId": "${PIXAI_LORA_MIO}", "weight": 0.8}],
    "seed": 12345, "batchSize": 1, "promptHelper": "disable"
  }
}
```

v1 uses `{"api": "v1", "parameters": {…}}`. Project-local images are specified as relative paths using kit-specific fields: `mediaFile` (i2i), `maskMediaFile`, `controlNets[].mediaFile`, and `ipAdapter.referenceFiles` (array). At send time, the script uploads them via `POST /v1/media/upload` and replaces those fields with `mediaId`, `maskMediaId`, and `referenceImages`. Images with identical content (SHA-256) reuse the cached `mediaId` in `output/pixai/uploads.json` (remove the corresponding entry from that file if an older ID expires). `model_type` (`dit` or `sdxl`) is an inspection note for unknown models and is not sent to the API.

`pixai_api.py` validation and defaults (kit implementation policy):

- Rejects undocumented v2 fields and `callbackUrl` (completion is polled by the script).
- If `aspectRatio` is omitted, fills in the ratio closest to `generationCanvas` in `config/page-layout.json`. Defaults: `size` is `1k`, `batchSize` is `1`, and `seed` is chosen randomly if omitted (the sent seed is saved in the execution record).
- **`promptHelper` defaults to `disable`** (the official API default is `enable`) to keep prompts aligned with the text storyboard. Set `"enable"` in the request if you intentionally want it (pre-send inspection will display a warning).
- For models in `config/pixai-models.json`, blocks `mode` on models that do not support it (SDXL and first-gen Tsubaki family), blocks known-rejected `mode` values (`standard` and `lite` on Tsubaki.3; `pro` on Tsubaki.3 Flash), and blocks ControlNet or masks on models that do not support them (such as Tsubaki.2). Displays warnings for `style` on models that ignore it, `sampling` on DiT models, `negativePrompt` on models that do not support negative prompts, unverified `mode` values, and `mode` on unlisted DiT models.
- Checks LoRA base-model types against the project's `config/pixai-loras.json` (recorded by `pixai_models.py lora`) and warns locally without network calls if the base model differs from the generation model.
- Does not estimate credit cost automatically.

## Generate after verification

```powershell
python -X utf8 scripts/pixai_api.py generate --request input/pixai-request.json
python -X utf8 scripts/pixai_api.py generate --request input/pixai-request.json --output output/pixai/test-001.png --execute --confirm-credits --cost-note 'Credit balance and approved scope (e.g., 1 image on Tsubaki.2 standard 1k, approved by user on 2026-10-25)'
```

The dry-run step (without `--execute`) neither reads the API key nor makes network calls. Pass `--confirm-credits` **only when the user has explicitly authorized consuming PixAI credits for this specific scope**, and record the verified balance, membership plan, and approved scope in `--cost-note`. Setting up a key, checking connectivity, or asking to generate does not by itself count as permission for paid credit usage. For requests that use undocumented parameters, also pass `--allow-unverified` only after the user agrees to use them.

Transmission flow and execution records (implementation policy):

1. Stops if an image or record with the same name already exists. Creates `rNNN.request.json` (formatted request) and execution record `rNNN.pixai.json` before sending. Never records the API key.
2. Uploads local project images for v1 requests. If an upload fails, stops without creating a task and moves the record to `failed/`.
3. Creates the task (`rNNN.request-body.json` contains the exact bytes sent). **Task creation is never retried automatically.** HTTP 4xx responses mean no task was created, so the record is moved to `failed/`. Network errors, 5xx responses, or invalid responses leave the record as unknown-result (check the PixAI side before taking further action).
4. Polls `GET /v1/task/{id}` starting at 3 seconds and multiplying by 1.3 each time up to a 10-second maximum interval (respecting the official ≥1.5s rule). Retries transient network errors during polling up to 3 times (polling is a read operation, not a generation retry). Default timeout is 900 seconds (`--timeout`). Tsubaki.3 `pro` takes over a minute even for a single image.
5. Upon completion, downloads the image from `mediaUrls` (or `PUBLIC` in `GET /v1/media/{id}` if absent) **without attaching the `Authorization` header** (so the API key is never sent to other hosts). Saves PNGs directly, converts WebP/JPEG responses to PNG via Pillow, and verifies PNG structure, CRC, and dimensions before saving. For `batchSize` 4, saves sequential files such as `r001` through `r004`.
6. If the task ends in `failed` or `cancelled`, moves the record to `failed/` (check credit consumption on the PixAI side). If polling hits the timeout, is interrupted, or image download fails, the record with `taskId` remains in place. Run `python -X utf8 scripts/pixai_api.py fetch --record <rNNN.pixai.json>` (or `pixai_batch.py fetch` for batch) to re-fetch **without re-sending generation**.

If only part of a 4-image batch could be saved, execution also stops so the remaining images can be fetched via the WebUI or `pixai_batch.py fetch` while keeping the already-saved images. Do not move partially saved records to `failed/` to regenerate; run `fetch` first to recover the remaining images.

Because actual credit consumption is not measured automatically, `actualCreditCost` in the execution record is set to `null`. Generated images and request JSON files are production artifacts of the project; strip metadata when publishing.

## Troubleshooting configuration and connection issues

| Message | Meaning and guidance |
| --- | --- |
| Configuration error: missing file / missing line / empty value / invalid format | Fix the `PIXAI_API_KEY=` line following the reported source path and format example |
| Authentication failed: HTTP 401 | The loaded key is invalid. Reissue the key or check the loaded source (`key-status`) |
| Insufficient credits: HTTP 402 | Not enough credits. Check your balance in the PixAI web UI |
| Input error: HTTP 400 / 422 | Request values were rejected. Displays the response `code` and `message` (e.g., sending `mode` to an SDXL model). No task was created. `unknown inferenceProfile` indicates a `mode` unsupported by that model and suggests trying another mode (`pro`, `ultra`, etc.) |
| Rate / queue limit: HTTP 429 | Reached 10 concurrent `waiting` tasks or hit a rate limit. Wait before sending again |
| Network error / server error | If it occurred during task creation, treat as an unknown result and check the PixAI web UI before re-sending |

## Sample prompt to ask for a connection check

```text
Please check the PixAI connection for this project.
Read AGENTS.md, docs/SETUP.md, and docs/knowledge/pixai-api.md.
I have set PIXAI_API_KEY in .env (or in an environment variable / .secrets/pixai.env).
Do not display the contents of secret files or the actual key value.
Run key-status and then status with scripts/pixai_api.py, and tell me the key source and whether authentication succeeded.
I do not authorize image generation or credit consumption this time. Do not launch or control a browser.
```

<a id="results"></a>

## Verification results from live generation

Verified: 2026-10-25, during kit distribution testing and project production. Based on 1 to a few images per condition; reproducibility and behavior after future model updates are not guaranteed.

### Basic generation and records

| Item | Result |
| --- | --- |
| v2 generation | Accepted. Response images are WebP (public URLs in `mediaUrls`), converted to PNG and saved by the script. Aspect ratios `1:1`, `2:3`, `3:4`, `3:5`, `4:3`, `16:9`, `size` `1.5k`, and `batchSize` `4` were accepted |
| `POST /v1/media/upload` (PNG) | Accepted. Response `id` works as `mediaId` |
| v1 `seed` | Two images with the same seed share nearly identical composition, character, and pose, differing only in small details (mean pixel difference 6.7). v2 shows the same tendency (Tsubaki.2, mean difference 19). Not pixel-identical |
| Character consistency | In v2 (Tsubaki.2) using identical appearance wording every time (`.env.pixai` variables), hair, hat ornament, coat pattern, and companion animal were preserved across 14 panels. Using reference images (`ipAdapter`) alone was less reliable at preserving fine clothing details (hat gem, blouse collar) |
| Continuous generation | On models that take over 1 minute per image, the total time for multiple tasks can exceed the execution environment's command timeout. Batch generation uses the environment's background/continuation mechanism |

<a id="model-results"></a>

### Model verification results

| Item | Result |
| --- | --- |
| Acceptance | All 15 models in `config/pixai-models.json` were accepted and completed in v2 at `2:3` and `1k` (models without `mode` support sent without `mode`; Tsubaki.3 Flash sent without `mode` or negative prompt) |
| `mode` (Tsubaki.3) | `pro` and `ultra` accepted (`ultra` produces nearly the same image as `pro`). `standard` and `lite` returned `422 INVALID_INPUT unknown inferenceProfile` (no task created) |
| `mode` (Tsubaki.3 Flash) | Accepted without `mode`. `pro` returned 422. Other modes unverified |
| `mode` (Tsubaki.2) | `lite` (nearly identical to `standard`), `standard`, `pro`, and `ultra` (both shifted hair toward blonde and warm, soft coloring) were all accepted |
| Generation time (creation to completion, 1k, 1 image) | Tsubaki.3 `pro` and `ultra`: over 1 minute. Tsubaki.2: `lite` ~10s, `standard` ~20s, `pro` and `ultra` ~50s. Other models: 15–72s (Haruka v2 ~50s, Tsubaki ~70s) |
| Visual style | Varies substantially by model. Tsubaki.3 and Tsubaki.3 Flash share nearly the same composition. Tsubaki v1.1, Serin, and Eternal barely showed the park background, and Tsubaki and Tsubaki Flash leaned toward a city street |
| Style presets | All 35 presets accepted on Tsubaki.2 (`standard`). `flat-anime-pastel` tended to draw an unprompted **halo above the head** (a motif reminiscent of existing IP) even when `halo` was placed in the negative prompt |
| Samples | Kit-only viewer `resources/pixai-model-samples/index.html` (15 models and 35 style presets; not copied into new projects) |

<a id="unverified-results"></a>

### Verification results for undocumented parameters

Source images were taken from the Tsubaki.3 and Haruka v2 model samples. Sending requires `--allow-unverified`.

| Parameter | Result | Status |
| --- | --- | --- |
| <a id="inpaint-results"></a>**Inpainting** (v1 `mediaId` + `maskMediaId` + `strength` on Tsubaki.3) | **White = redraw.** Replacing a cup with an apple using a small mask (3% of canvas) succeeded 8/8 times (across 1-image, 4-image, `strength` 0.9, and `inferenceProfile` `pro` + `modelStyle` runs). Removing the cup and clasping hands also succeeded. Adding a red beret on the head succeeded in 2/4 runs with a small mask (6%) and 2/4 with a large mask (17%); the 4 misses drew a "small cat wearing a beret" (likely influenced by `cat ears` in the prompt). Outside the mask, the original image remained intact (mean pixel difference 0.006–0.05) | Accepted & effective |
| Inpaint mask size | Large masks (16–17%) and extra-large masks (36%) also succeeded at adding items, but **other areas inside the mask changed too** (chest ribbon shape, neck bell disappearing, and mouth/expression changing with the extra-large mask). On Haruka v2, a large mask overlapping the eyes changed eye color and expression. Restrict masks strictly to the item being added and the empty space it occupies, keeping faces and accessories you want to preserve outside the mask | Observation |
| Inpainting (Haruka v2 / SDXL) | Adding a beret succeeded with both small and large masks, though areas outside the mask shifted slightly across the whole image (mean pixel difference 1.7–2.0, roughly 100× Tsubaki.3) | Accepted & effective |
| Inpainting (Tsubaki.2) | Returned `400 40000000 This feature is not yet supported for this model` (no task created). `pixai_api.py` blocks sending inpaint requests to models marked `inpaint: false` in the catalog. To retouch a Tsubaki.2 image, inpaint with Tsubaki.3 (succeeded in 3 of 4 images when erasing a background halo while keeping the unmasked area intact) | Unsupported |
| Inpainting time | 1–2 minutes per task (see "[Costs](#costs)" below for credits) | Verified fact |
| i2i (`mediaId` + `strength`, changing a park to a snowy park via prompt) | Haruka v2: `0.3` stays almost unchanged; `0.6` preserves composition while adding snow to ground and trees; `0.9` preserves composition and pose while turning the scene into winter snow (changing sleeves to long sleeves). Tsubaki.3 at `0.6` produced only minor falling snow | Accepted & effective |
| **latentCouple** (`{"type": "rect", "divisions": ["1:1","1:2","1:2"], "positions": ["0:0","0:0","0:1"], "weights": [0.2,0.8,0.8]}`, separating prompt sections with ` AND `: overall `AND` left `AND` right) | Haruka v2: without it, hair and clothing swapped (red hair + yellow raincoat), whereas with it, "red hair + green dress" appeared on the left and "blue hair + yellow raincoat" on the right, and swapping `positions` swapped left and right. **However, a third person was added.** Lowering the global weight to `0.05` or omitting the global region increased extra people and outfit mixing. Accepted on Tsubaki.2 but had no effect | Accepted & effective on SDXL; extra-person issue unresolved |
| ControlNet (source image: normal illustration; Haruka v2) | `canny`: strongly preserved stairs, hairstyle, bag, and pose from the source composition. `depth`: preserved stair railing and back-facing composition (lines slightly rougher). `openpose`: collapsed into a torso close-up at weight 1.0 and only loosely leaned toward a back view at 0.5 (does not work as pose control from a normal illustration; skeleton stick-figure input untested). `scribble`: created a task but failed after ~2 seconds (no image) | `canny` & `depth` effective |
| ControlNet (Tsubaki.2) | Returned `403 40300044 This model cannot be used with ControlNets.` (no task created). The model page compatibility table also marks Tsubaki.2, first-gen Tsubaki family, and Hinata v2 as `controlnet: false`. `pixai_api.py` blocks sending ControlNet to models with `controlnet: false` | Unsupported |
| Hires (`upscale` 1.5) | Output at 1272×1920 with finer facial and line detail (~30s) | Accepted & effective |
| ADetailer (`enableADetailer`) | Only slight change in facial detail (compared at the same seed) | Accepted; minor effect |
| `clipSkip` 2 (v1, Haruka v2) | Indistinguishable from the same-seed image without it (mean difference 6.7, equal to normal seed variance) | Accepted; no observable effect |
| v2 `sampling` (Haruka v2) | `steps` 12 caused a minor change. `cfgScale` 10 increased color saturation and altered pose and eye color | Accepted & effective |
| v1 `ipAdapter` (reference image) | Accepted on Tsubaki.2 and Haruka v2. **Haruka v2** strongly copies design elements from the reference image (proportions, staff shape, earrings, props) but is prone to color casts from the reference background and ignoring prompt actions, expressions, and backgrounds. **Tsubaki.2** (combined with a `modelStyle` preset) keeps natural colors and follows prompt actions, reflecting reference design elements partially (such as hat color and staff shape). Passing reference images for two characters in one request mixes elements of both | Accepted & effective |
| v1 `inferenceProfile` + `modelStyle` (Tsubaki.3) | `pro` + preset `paper-watercolor` produced a distinctly watercolor-styled image. Style presets work in v1 as well | Accepted & effective |
| v1 `negativePrompts` | Accepted | Accepted |

<a id="costs"></a>

### Costs (credits)

Because credits cannot be queried via API, `actualCreditCost` in execution records is `null`. Users verify credit usage under "Membership & Credits" in their PixAI profile.

| Model & conditions | Credits per task | Basis |
| --- | --- | --- |
| Tsubaki.3, `pro`, `1k` (new generation or inpainting) | 4,000 for 1 image; 7,000 for 4 images | Verified by user in usage history |
| Tsubaki.2, `standard`, `1k` (with style preset) | ~2,700 for 1 image | Estimated from partial usage history |
| Haruka v2, v1, 1280×848 | ~1,200–1,500 for 1 image | Estimated from partial usage history |
| Other conditions | Unverified | — |

<a id="sources-and-verification-scope"></a>
<a id="出典確認範囲"></a>

## Sources and verification scope

Verified: 2026-10-25. Verified facts come from the official pages above (Docs, FAQ, Limits, Models, Supported Resolutions, Webhook, Copyright, createImage, createGenerationTask, getTask, getMedia, uploadMedia), live-key responses for `GET /v1/task/0` and `GET /v1/media/1` (404), invalid key (401), `style-keys` and `inference-profiles` (400), and the "[Verification results from live generation](#results)" section above. **LoRA effectiveness and credit consumption for conditions outside the table above are unverified.** Default values, file-saving rules, cost-confirmation flags, and polling intervals are kit implementation policies. Because the PixAI API is in beta and even official documentation pages have discrepancies between versions (such as the maximum number of LoRAs in v1), re-verify against the official documentation immediately before sending.
