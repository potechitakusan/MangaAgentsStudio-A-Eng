# NovelAI batch-generation record

For NovelAI projects, record how humans can regenerate a page/all pages, choose images, and rebuild identical PNG/PSD placement. See [NovelAI workflow](../knowledge/novelai-composed-production.md#batch). Run commands at the project root.

## Generation conditions

- Model, steps, and cost verification method (example content for `--cost-note`):
- Cost flags, only when actually verified: `--confirm-zero-anlas`; for V5 also `--confirm-v5-allowance`.

## Per-page commands

| Page | Requests (`input/novelai/requests/`) | Generation (for dry run remove `--execute` and subsequent flags) | Rebuild |
| --- | --- | --- | --- |
| 1 | | `python -X utf8 scripts/novelai_batch.py generate --page 1 --execute --confirm-zero-anlas --cost-note '…'` | `python -X utf8 scripts/novelai_batch.py build --page 1` |

All pages: `python -X utf8 scripts/novelai_batch.py generate --all --execute …`, `python -X utf8 scripts/novelai_batch.py build --all` (add `--write-psd` when creating requested PSDs).

Inspect/select: `python -X utf8 scripts/novelai_batch.py list --page 1` → compare candidate images → `python -X utf8 scripts/novelai_batch.py adopt p01-02 --candidate 3`.

## Reasons for retaining prompt warnings

Normally fix warnings from the `generate` dry run. Only if retaining them, document reasons before sending with `--accept-warnings`.

| Request ID | Warning | Reason retained | Date |
| --- | --- | --- | --- |
| | | | |

## Adoption records

| Request ID | Selected candidate | Reason / comparison points | Selected by (human/Codex), date |
| --- | --- | --- | --- |
| | | | |

## Character-prompt variables (only when requested)

| Variable name | Character / purpose | Requests using it | Setup/check date |
| --- | --- | --- | --- |
| | | | |

Values live in project-root `.env`. Record only names here, not values. Inspect with `python -X utf8 scripts/novelai_batch.py vars`.
