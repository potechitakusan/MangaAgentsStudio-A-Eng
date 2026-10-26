# NovelAI batch-generation record

For NovelAI projects, record how humans can regenerate a page/all pages, choose images, and rebuild identical PNG/PSD placement. See [NovelAI workflow](../knowledge/novelai-composed-production.md#batch). Run commands at the project root.

## Generation conditions

- Model, steps, and cost verification method (example content for `--cost-note`):
- Cost flags, only when actually verified: `--confirm-zero-anlas`; for V5 also `--confirm-v5-allowance`.

## Subscription check frequency

The subscription, Anlas, and V5 allowance check API (`/user/subscription`) is called on the first generation (trial) and once every 10 generations thereafter counted from the previous check (user instruction, 2026-10-05; to avoid excessive API calls). The script counts automatically in `output/novelai/subscription-check.json` and records whether an API call or the previous result was used in `subscriptionCheck` within each generation's execution record (`.novelai.json`). It checks regardless of count when the model, dimensions, steps, or additional features change, when the previous generation did not complete, or when the remaining V5 allowance is low. Delete that file to force a check. Paid-use authorization, `--confirm-zero-anlas`, `--allow-anlas`, and `--cost-note` are still required on every run. Details: [Opus procedure](../knowledge/ai-production.md#novelai-opus).

## Per-page commands

| Page | Requests (`input/novelai/requests/`) | Generation (for dry run remove `--execute` and subsequent flags) | Rebuild |
| --- | --- | --- | --- |
| 1 | | `python -X utf8 scripts/novelai_batch.py generate --page 1 --execute --accept-warnings --confirm-zero-anlas --cost-note '…'` | `python -X utf8 scripts/novelai_batch.py build --page 1` |

All pages: `python -X utf8 scripts/novelai_batch.py generate --all --execute --accept-warnings …`, `python -X utf8 scripts/novelai_batch.py build --all` (add `--write-psd` when creating requested PSDs).

Inspect/select: `python -X utf8 scripts/novelai_batch.py list --page 1` → compare candidate images → `python -X utf8 scripts/novelai_batch.py adopt p01-02 --candidate 3`.

Adopt the highest-numbered PNG in each folder at once: `python -X utf8 scripts/novelai_batch.py adopt-latest --page 1` (use `--all` for all pages or `--ids p01-02,p01-04` for specific panels). Add `--dry-run` to display the targets only. For a panel whose new generation failed, an earlier highest-numbered PNG is selected, so check the generation results and the images before using them. Details: [editing and regeneration README](../novelai-prompts/README.md#adopt-the-highest-numbered-image-in-each-folder-at-once).

## Reasons for retaining prompt warnings

Normally fix warnings from the `generate` dry run. Only if retaining them, document reasons before sending with `--accept-warnings`.

The generation and regeneration examples include `--accept-warnings` by default. Remove it if you want to check warnings and stop sending when any remain. Warnings are still displayed when it is included, and cost confirmation and error validation are not skipped.

| Request ID | Warning | Reason retained | Date |
| --- | --- | --- | --- |
| | | | |

## Adoption records

| Request ID | Selected candidate | Reason / comparison points | Selected by (human/Codex), date |
| --- | --- | --- | --- |
| | | | |

## Pre-send content verification

When creating or revising prompts, use `manga-ai-production` and fill this in according to "Expanding scene relationships and continuing state into each request" and "Pre-send content verification" in `docs/knowledge/novelai-composed-production.md`. After variable expansion, verify the body text, per-character text, coordinates, and negative text. Do not simply transcribe the result of automatic warnings. Dialogue, lettering, balloons, and frames are typeset afterward.

| Request ID / version checked | Required relationship (actor, other party, contact point, etc.) | State continuing from the previous panel / changes this time | Assignment, contradiction, and text-separation check result / reason for revision |
| --- | --- | --- | --- |
| | | | |

## Character, style, and background variables (only when requested)

| Variable name | Character / purpose | Requests using it | Setup/check date |
| --- | --- | --- | --- |
| | | | |

Values live in project-root `.env.novelai` (API keys and URLs are in shared `.env`). Record only names here, not values. `NOVELAI_CHAR_*`, `NOVELAI_STYLE_*`, and `NOVELAI_BACKGROUND_*` may be used. Inspect with `python -X utf8 scripts/novelai_batch.py vars`. For editing, applying, and regenerating, see the [beginner README](../novelai-prompts/README.md).
