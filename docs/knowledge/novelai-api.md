# NovelAI API Connection Procedure

Applies to the project's `scripts/novelai_api.py`, using only Python 3.10+ standard library. It does not launch/control a browser. Requires the project's `project.json`; do not run in the kit template.

If asked to use NovelAI or check its connection in a project, Codex follows this procedure without requiring a detailed diagnostic prompt from the user. Show the key-format example when setup is needed; do not request re-entry if already configured.

## Prepare the key

Use a NovelAI Persistent API token, never an email/login password. Do not paste the key into conversations, prompts, or request JSON. The user places it in either:

- `NOVELAI_API_KEY` in an environment visible to Codex/the terminal process.
- The project's `.secrets/novelai.env`, placing the value after `NOVELAI_API_KEY=`.

The file requires the setting name on the left too. Replace the placeholder below with the actual Persistent API token; do not put a bare token on a line.

```dotenv
NOVELAI_API_KEY=YOUR_ACTUAL_TOKEN
```

**The setting name is `NOVELAI_API_KEY`; the secret is the token to the right of `=`.** Mentioning the name in explanations/conversation does not expose a secret. There is no need to paste the token into conversation.

The first nonempty value wins in this order: environment → `.secrets/novelai.env` → `.secrets/.env` → `.env`. Files use UTF-8 (BOM allowed) and a one-line `NOVELAI_API_KEY=value` format. Quotes, leading `export`, and whitespace followed by a `#` comment are supported. No variable expansion/command execution occurs. Duplicate keys in one file and links outside the project are errors.

`.env.example` demonstrates field names and is not loaded. `.secrets/`, `.env`, and `.env.*` (excluding `.example` files) are Git-excluded. Project configuration files are split into `.env` for shared settings such as API keys and URLs, `.env.novelai` for NovelAI prompt variables and helper settings, and `.env.pixai` for PixAI. The key-loading order above remains unchanged. An old environment key overrides a newly edited file key; inspect the source using `key-status`. No full/partial key or key length is shown.

## Check without generation

Run from the project root. The script resolves its project from its own location; another working directory will not make it search another project's `.env`.

```powershell
python -X utf8 scripts/novelai_api.py key-status
python -X utf8 scripts/novelai_api.py status
```

`key-status` does not communicate externally. `status` calls official image API `GET /user/subscription` once and displays only active state, tier, expiry, and numeric balances returned. It does not output the full response, payment details, or email, request generation, or automatically save connection results.

This implementation identifies Opus with `active=true` and `tier=3`. A different plan or changed response format stops generation under the no-consumption path. Balance field names remain as returned by the API. It also displays `usage.percent`, `usage.isNegative`, and `usage.timeUntilNextPercent`; if they indicate insufficient V5 allowance, no-Anlas generation stops regardless of confirmation flags. A positive balance may still be insufficient for this request. Subscription lookup alone does not establish 0 Anlas for all settings or the number of available generations.

## Configuration and connection problems

Errors and `--help` include the setup example. Errors show only fixed source identifiers/status, never secret values, input lines, or raw communication-exception text.

| Displayed condition | Meaning and action |
| --- | --- |
| Configuration: file missing | Configure the environment or `.secrets/novelai.env` |
| Configuration: setting line missing | File exists without a `NOVELAI_API_KEY=` line; a bare token also produces this condition |
| Configuration: empty value | Setting exists with an empty right-hand side; enter the token |
| Configuration: invalid format | Delimiters, quotes, duplicate lines, or value characters are invalid; follow the displayed reason/example |
| Configuration: read failed | File cannot be read; check permissions |
| Authentication failed: HTTP 401 | The loaded key was not authenticated; check source and token validity |
| Access denied: HTTP 403 | Endpoint refused the request; check access/network restrictions rather than assuming a bad key |
| Communication failure | Communication did not complete after key loading; check network, proxy, and execution-environment restrictions |
| Server error / invalid API response | Server problem/unexpected response, distinct from missing key configuration |

Empty/unset sources continue to the next candidate. If no valid key is found, each candidate's status is listed. An invalid value format stops at that source. The script never edits the secret file automatically.

Do not recommend replacing/re-entering a key solely for communication failure. If environment restrictions may be responsible, explain and follow environment permission procedures. Do not automatically switch to unrestricted execution or browser control. Retrying subscription lookup differs from resending generation; never resend generation with unknown result/cost.

## Prepare one image request

1. Complete the project's style selection and verify chosen model/sampler/features against official specifications. Do not even generate a style-unspecified test.
2. **As a rule, assemble request JSON with the [standard script `novelai_compose.py`](#compose-standard).** When writing by hand, copy `config/novelai-request.example.json` to the project's `input/novelai-request.json`; set `input` to the prompt and `model` to the verified model ID. Review sampler/scale for that model. Example model/prompt are blank and cannot be sent unchanged.
3. If both `width` and `height` are in the request, use them: each at least 64 and a multiple of 64. Per-panel assets may be wider than their final crop and differ from whole-page requested dimensions. If absent, fill from `generationCanvas` in `config/page-layout.json` under [Page Settings](page-layout.md). Bundled 2000 × 3000 px frames are not default generation dimensions. This replaced rejection of a `generationCanvas` mismatch under a 2026-09-29 user instruction.
4. Default missing steps to 23 for V5, otherwise 28. Limit `n_samples` to one; `seed` is random when omitted (or fixed when specified; the sent value is saved in the output JSON and execution record). If V4/V5 `v4_prompt` and `v4_negative_prompt` are absent, derive a structure without per-character prompts from the main text. Preserve supplied per-character structures. The local client does not validate model-specific additional requirements or sampler compatibility.

```powershell
python -X utf8 scripts/novelai_api.py generate --request input/novelai-request.json
```

This stage neither reads the key nor communicates. It displays dimensions, steps, count, model, and SHA-256 of the full prospective request. Do not send a test before verifying cost.

For panel assets, save one request JSON per panel in `input/novelai/requests/` and use `scripts/novelai_batch.py` to generate page/all-page assets sequentially, one image at a time. Validation, cost confirmation, records, and no-resend handling are the same. See [NovelAI production procedure](novelai-composed-production.md#batch). Official API guidance requires human-initiated generation and prohibits excessive automated load: start batches on human instruction and preserve default intervals/count limits. Compliance of this workflow with service terms is unverified; users must check current terms.

<a id="compose-standard"></a>

## Standard script: `novelai_compose.py` (V5 default; V4.5 only when specified)

As a rule, assemble requests for NovelAI API generation with the project's `scripts/novelai_compose.py`. The model defaults to **V5 (`nai-diffusion-5-curated`; Full produces overly dense detail that is less suited to comics, so it is not the default)**. Use **V4.5 (`nai-diffusion-4-5-curated`) only when specified by the user**. Models earlier than V4 and V4.5 Full are not supported. This operational rule was adopted under a user instruction (2026-10-05) and is based on the script created and verified in feedback (`FB-2026-10-05-novelai-ui-parity`) from the project "NAIプロンプト検証".

- **Role**: Assembles request JSON from arguments for style, background, per-character text, position pins, and generation settings, and saves it to `input/novelai/requests/<ID>.json`. Does not communicate over the network. After saving, displays the same dry-run check as `novelai_batch.py generate`. Sending, cost confirmation, execution records, adoption, and page rebuilding continue to be handled by `novelai_batch.py` (or `novelai_api.py` for single runs), and are handed off to that same pipeline only when `--execute` and cost-confirmation flags are passed.
- **i2i, references, and other additional features**: When customization is needed, modify and use this script as the base (including V4.5 features). Check the format, supported models, and additional charges for any added parameters against the official schema and the [Opus procedure](ai-production.md#novelai-opus) first, and never send before confirming. Even when customized, preserve the request JSON structure (`action`, `input`, `model`, `parameters`) and submission through `generate` in `novelai_batch.py` and `novelai_api.py` (cost confirmation and execution records). Image-input implementation and costs remain unverified (see "Remaining verification units" below); do not carry t2i parity findings over to image inputs.
- **Usage, arguments, and `.env.novelai` helper settings**: See [NovelAI production procedure](novelai-composed-production.md#compose).
- **Defaults**: Steps (23 for V5, 28 for V4.5) match `novelai_api.py`. Dimensions use `--width` and `--height`, falling back to `generationCanvas` in `config/page-layout.json`, or the Web UI default 832 × 1216 when unset. Pass the Web UI values as arguments only when reproducing the exact same image as the Web UI.

### Matching Web UI generation

Even with the same text, images generated in the Web UI and via the API can differ because the Web UI appends quality tags, undesired-content (UC) presets, Guidance, and internal parameters to the input, whereas the API uses only what is sent. In the project "NAIプロンプト検証" (distribution version 0.5.0), we compared API output against the metadata (`Comment`, `Description`, `Source`) of PNGs generated in the Web UI as the reference and observed the following. These are **conditional reproductions**, not universal specifications.

| Observation (2026-10-05) | Details | Status |
| --- | --- | --- |
| Example differences from the Web UI (V5 Curated) | Automatically appends `, very aesthetic, masterpiece, no text` to the end of the body prompt. Negative prompt combines the Heavy preset + user input. Guidance 7.0. Per-character body text starts with `girl` (not `1girl`). `use_coords` is false when no position pins are used | 1 API generation compared against Web UI PNG |
| Internal parameters | Web UI PNGs have `deliberate_euler_ancestral_bug: false` and `prefer_brownian: true`. An API request omitting them produced the opposite (`true` / `false`). Because their individual effects were not isolated, specify both explicitly | Observation; individual effects unverified |
| `centers` affects the image even without position pins | Even with `use_coords: false`, the image changed unless `centers` matched the Web UI history (matching when the second character changed from 0.5 → 0.3) | 1 example |
| `tag_hint_qt` and `tag_hint_uc_preset` | Exact pixel match even when omitted | Verified on V5 |
| V5 Full vs. Curated | Only the model hash and UC preset differ (the Full Web UI prepends `nsfw, ` to the negative prompt). Quality tags, Guidance 7.0, and parameters are identical | 1 run each |
| V4.5 Curated | Web UI quality tags are `very aesthetic, masterpiece, no text, -0.8::feet::, rating:general`, and Heavy UC lacks `dithering` and `screentone`. Differs from the official documentation; matched by following the Web UI | 1 run |
| Web UI default Guidance | 7.0 on V5, 5.0 on V4.5 Curated (values displayed on the user's screen; cannot distinguish whether this is the Web UI default or user setting) | Observation |

- **Verified parity scope**: 1 run each of V5 Curated, V5 Full, and V4.5 Curated at 832 × 1216, 23 steps, 2 characters, no position pins, and no references. Compared by full-pixel difference after converting both PNGs to RGB. Other inputs or dimensions, active position pins, multi-run determinism under identical conditions, and 5×5 grid snapping for V4.5 position pins remain unverified.
- **Policy**: Do not rely solely on official documentation for quality tags and UC presets; cross-check against Web UI PNG metadata. To match the Web UI, copy the input text, per-character text, coordinates, seed, dimensions, steps, and sampler from the Web UI PNG metadata (`Comment`) into the arguments of `novelai_compose.py`. Per user instruction, the script does not prepend `nsfw, ` for Full (pass the full string to `--uc-preset-text` if you need an exact match). The `light` and `human` UC presets for V4.5 and V5 Full remain unverified due to the absence of Web UI PNGs.
- **Limitations**: The source check date is the project investigation date (2026-10-05); official documentation and Web UI screens were not re-fetched when importing into the kit. PNG metadata retains generation settings, not HTTP headers or transport framing (the Web UI uses `stream: msgpack`). Only output pixel parity was confirmed, not identical wire format. Because model and Web UI defaults can change, recheck the official documentation and Web UI immediately before sending. Actual Anlas consumption was not measured (`actualAnlasCost` is `null`), and this does not guarantee zero consumption.

### Saving the actual sent payload

On every submission, `rNNN.request-body.json` (the exact bytes sent) and `rNNN.request.json` (a formatted copy of the same content) are saved next to the candidate PNG, and their paths are recorded in `sentRequestFiles` within the execution record. Because `rNNN.request.json` has the same format as a request JSON file, you can copy it to `input/novelai/requests/`, edit it, and use it as the basis for regeneration or compare it against Web UI PNG metadata. It never contains the API key.

<a id="position-pins"></a>

## Position-pin requests

Use only when specifying the on-screen position of characters or objects in NovelAI. For UI usage, when to use pins, and differences by model, see [Position-pin production procedure](novelai-composed-production.md#position-pins).

In the official image API schema, we confirmed `use_coords` and `use_order` (booleans) in `parameters.v4_prompt`, and `char_caption` (string) and `centers` (an array of objects with numeric `x` and `y`) in `caption.char_captions`. V5 also uses these field names in existing implementations, and `novelai_api.py` preserves the specified structure. Do not replace it with an invented top-level `position` or pin numbers inside the prompt.

The following is an example of the `parameters.v4_prompt` structure, not a complete request that can be sent. Make the example's text match `input`, and align the style, exclusion text, model, generation dimensions, and so on with the project's adopted settings.

```json
{
  "caption": {
    "base_caption": "2girls, standing side by side, full body, outdoors",
    "char_captions": [
      {"char_caption": "girl, short black hair, blue jacket, on the left",
       "centers": [{"x": 0.3, "y": 0.5}]},
      {"char_caption": "girl, long brown hair, red jacket, on the right",
       "centers": [{"x": 0.7, "y": 0.5}]}
    ]
  },
  "use_coords": true,
  "use_order": true
}
```

The example is a verification candidate (for V5) that assumes normalized 0 to 1 coordinates with the origin at the top left of the generated asset, increasing rightward and downward. Do not confuse them with pixel coordinates in the page or with the typesetting `focus`. The official schema checked this time shows only the types of `x` and `y`; it does not state the coordinate range, the origin, or the numeric correspondence to the 5×5 grid of V4 and V4.5. Check their meaning and actual acceptance separately for the model in use, and do not assert an unconfirmed conversion as official specification.

For comparison, you can use a plan that keeps the body text, per-character text, seed, and so on identical and toggles `use_coords`. A request returning to automatic placement states `use_coords: false` explicitly. **Even with `use_coords: false`, `centers` values affected the generated image in observed testing** (see the Web UI parity observations above). When comparing with fixed coordinates, keep `centers` aligned as well. Keep per-character input and the exclusion of text and frames, and when you specify `v4_negative_prompt`, also check the corresponding characters and order. Position pins are a separate feature from dedicated image references; do not add a reference image because pins are used.

Source and checked date: 2026-10-04, [NovelAI公式画像APIスキーマ](https://image.novelai.net/docs/doc.json), `image.V4ConditionInput`, `image.V4ExternalCharacterCaption`, and `image.Coordinates`. What was confirmed is the format and a reading of the local implementation. API submission, generation effect, coordinate interpretation, and cost are unverified. Before generation, check the cost and allowance for all settings as usual.

## Generate after confirmation

With an active Opus subscription, add `--confirm-zero-anlas` **only after actually verifying that all settings of this request cost 0 Anlas**. It declares a verified human/tool finding; it does not force the server to avoid charges. Follow [Opus conditions](ai-production.md#novelai-opus), stopping if API applicability cannot be verified.

```powershell
python -X utf8 scripts/novelai_api.py generate --request input/novelai-request.json --output output/novelai/test-001.png --execute --confirm-zero-anlas --cost-note 'Record the verification method and date/time for all current settings'
```

V5 also requires `--confirm-v5-allowance` after confirming sufficient allowance for this request. Wait if insufficient. Do not add flags merely to make a request appear verified.

The no-consumption candidate range is at most 28 steps, 1,048,576 pixels, one image, and text-to-image. References, upscaling, and unknown parameters are rejected (except `controlnet_strength: 1.0`, which `novelai_compose.py` sends to match the Web UI and which is treated as ordinary generation). Being inside this range alone does not guarantee 0 Anlas. Do not send when cost is unknown.

Use `--allow-anlas` instead of `--confirm-zero-anlas` **only when the user explicitly authorizes Anlas consumption for these settings**; record verified cost and permission scope in `--cost-note`. Key setup, connection checking, or a generic generation request does not authorize paid use. Pass `--allow-anlas` and `--cost-note` on each run to record it. Automatic fee estimation, hard spending caps, and automatic reference encoding are not implemented. Reference features need correctly formatted official requests and separate cost verification.

Output must be PNG inside the project's `output/`. A neighboring `.novelai.json` records request, cost evidence/date, request SHA-256, six-character request ID, and actual output size, never the key. Requests/original PNGs are production material; remove metadata for publication as usual. Distinguish actual and requested dimensions and apply them to [placement/final PNG](page-layout.md). Actual Anlas consumption is not measured automatically, so `actualAnlasCost` remains `null`.

Subscription lookup (`/user/subscription`) is not called on every generation. It is called on the first generation (trial) and once every 10 generations thereafter counted from the previous check (user instruction, 2026-10-05; to reduce the risk of warnings from excessive API calls; the count is an operational guideline). Generations in between reuse the previous result and save the count in `output/novelai/subscription-check.json`. It queries regardless of count when the model, dimensions, steps, sample count, or additional features change, when the previous generation was not confirmed complete, or when remaining V5 allowance is low (`percent` is 3 or below, or insufficiency was indicated; 3 is a user-specified threshold). Delete this file to force a check. `status` always queries the API. This throttling applies only to the number of subscription lookup calls; paid-use authorization, cost-confirmation flags, and stopping conditions remain unchanged. See item 3 in the [Opus procedure](ai-production.md#novelai-opus) for details.

Create an execution record before sending; stop if the image/record name already exists. Never automatically resend after HTTP errors, timeouts, or save failures. First inspect the record and NovelAI-side result/cost. A different output name still constitutes a resend; do not repeat an unknown-outcome request. Extract PNGs from ZIP or JSON/base64 and verify chunk structure, CRC, and dimensions. Appearance requires separate visual review.

## Example request for a connection check

Use after preparing the key and reopening Codex in the project folder.

```text
Check this project's NovelAI connection.
Read AGENTS.md, docs/SETUP.md, and docs/knowledge/novelai-api.md.
I will put the key in the environment or .secrets/novelai.env.
Do not display secret-file contents or the actual key.
Run scripts/novelai_api.py key-status, then status.
Tell me the key source, whether subscription lookup succeeded, and any missing settings.
I do not authorize image generation or Anlas consumption for this check. Do not control a browser.
```

Additional request to check generation afterward:

```text
Prepare to generate one NovelAI test image.
Confirm style, model, and requested dimensions if still undecided.
Prepare input/novelai-request.json and page settings, then inspect the request without sending it.
Only if all settings are verified as 0 Anlas, and V5 allowance is sufficient when applicable,
generate once and present output/novelai/test-001.png.
If cost or allowance cannot be verified, do not send; report what remains unknown.
Paid use and automatic retries after failure are not authorized.
```

## Sources and checked scope

Checked: 2026-09-21. [NovelAI公式画像APIスキーマ](https://image.novelai.net/docs/doc.json) confirms Persistent API token authentication, `/user/subscription`, `/ai/generate-image`, parameters, JSON/base64 and ZIP responses, and request-ID format. Its `basePath` is `/` and host is unspecified, so this implementation fixes the endpoint to the schema provider, `https://image.novelai.net`. Authorization headers are not forwarded on redirects.

Defaults, storage rules, and cost-confirmation flags are kit implementation policy. Real subscription connections, each model's generation, API 0-Anlas applicability, V5 allowance, and image quality are unverified. Distinguish schema retrieval from real-API testing and record actual results in ordinary project progress.

### Remaining verification units

The 2026-09-26 feedback incorporation registered NAI-VERIFY-01 in the kit's private work plan. Separate current specifications/connection, cost/allowance, minimal real-API round trip, supported image inputs, per-panel comparison, and incorporation of findings into documentation. The work plan governs conditions/progress; this document is authoritative for connection/cost findings. Distributed files alone do not demonstrate verification.

For initial-image i2i, dedicated appearance/style references, and multiple-image inputs, separately verify the target model's actual schema, count, strength, preprocessing, and added fees. Do not infer API support from UI feature names or count t2i success as i2i validation. Do not reuse no-consumption t2i candidate conditions for image input.

Panel comparisons connect to the [shared external workflow](external-panel-i2i.md), but equivalent NovelAI effects are unverified. Completion evidence requires date, model, environment, supported inputs, request settings, permission/cost basis, actual results/art, failures/limits, and documentation destinations. Record unsupported cases with evidence; untested or unknown-cost features remain outstanding. Registering the task does not authorize API transmission or Anlas consumption.
