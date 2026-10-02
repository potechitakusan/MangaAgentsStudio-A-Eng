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

`.env.example` demonstrates field names and is not loaded. `.secrets/` and `.env` are Git-excluded. An old environment key overrides a newly edited file key; inspect the source using `key-status`. No full/partial key or key length is shown.

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
2. Copy `config/novelai-request.example.json` to `input/novelai-request.json`; set `input` to the prompt and `model` to the verified model ID. Review sampler/scale for that model. Example model/prompt are blank and cannot be sent unchanged.
3. If both `width` and `height` are in the request, use them: each at least 64 and a multiple of 64. Per-panel assets may be wider than their final crop and differ from whole-page requested dimensions. If absent, fill from `generationCanvas` in `config/page-layout.json` under [Page Settings](page-layout.md). Bundled 2000 × 3000 px frames are not default generation dimensions. This replaced rejection of a `generationCanvas` mismatch under a 2026-09-29 user instruction.
4. Default missing steps to 23 for V5, otherwise 28. Limit n_samples to one and fix the seed. If V4/V5 `v4_prompt` and `v4_negative_prompt` are absent, derive a structure without per-character prompts from the main text. Preserve supplied per-character structures. The local client does not validate model-specific additional requirements or sampler compatibility.

```powershell
python -X utf8 scripts/novelai_api.py generate --request input/novelai-request.json
```

This stage neither reads the key nor communicates. It displays dimensions, steps, count, model, and SHA-256 of the full prospective request. Do not send a test before verifying cost.

For panel assets, save one request JSON per panel in `input/novelai/requests/` and use `scripts/novelai_batch.py` to generate page/all-page assets sequentially, one image at a time. Validation, cost confirmation, records, and no-resend handling are the same. See [NovelAI production procedure](novelai-composed-production.md#batch). Official API guidance requires human-initiated generation and prohibits excessive automated load: start batches on human instruction and preserve default intervals/count limits. Compliance of this workflow with service terms is unverified; users must check current terms.

## Generate after confirmation

With an active Opus subscription, add `--confirm-zero-anlas` **only after actually verifying that all settings of this request cost 0 Anlas**. It declares a verified human/tool finding; it does not force the server to avoid charges. Follow [Opus conditions](ai-production.md#novelai-opus), stopping if API applicability cannot be verified.

```powershell
python -X utf8 scripts/novelai_api.py generate --request input/novelai-request.json --output output/novelai/test-001.png --execute --confirm-zero-anlas --cost-note 'Record the verification method and date/time for all current settings'
```

V5 also requires `--confirm-v5-allowance` after confirming sufficient allowance for this request. Wait if insufficient. Do not add flags merely to make a request appear verified.

The no-consumption candidate range is at most 28 steps, 1,048,576 pixels, one image, and text-to-image. References, upscaling, and unknown parameters are rejected. Being inside this range alone does not guarantee 0 Anlas. Do not send when cost is unknown.

Use `--allow-anlas` instead of `--confirm-zero-anlas` **only when the user explicitly authorizes Anlas consumption for these settings**; record verified cost and permission scope in `--cost-note`. Key setup, connection checking, or a generic generation request does not authorize paid use. Automatic fee estimation, hard spending caps, and automatic reference encoding are not implemented. Reference features need correctly formatted official requests and separate cost verification.

Output must be PNG inside the project's `output/`. A neighboring `.novelai.json` records request, cost evidence/date, request SHA-256, six-character request ID, and actual output size, never the key. Requests/original PNGs are production material; remove metadata for publication as usual. Distinguish actual and requested dimensions and apply them to [placement/final PNG](page-layout.md). Actual Anlas consumption is not measured automatically, so `actualAnlasCost` remains `null`.

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
