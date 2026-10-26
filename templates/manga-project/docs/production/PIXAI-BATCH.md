# PixAI Batch Generation Log

A log for projects using PixAI so humans can re-run generation per page or across all pages, choose adopted images, and rebuild PNG and PSD files with identical placement. For the procedure, see [PixAI Production Procedure](../knowledge/pixai-composed-production.md#batch). Run commands from the project root.

## Generation conditions and cost authorization

- Model, `mode`, aspect ratio & resolution, images per task, LoRAs, and style preset:
- Scope of credit consumption authorized by the user (number of tasks, image count, timestamp):
- Example `--cost-note` text (balance, membership plan, approved scope):
- User agreement to use undocumented parameters (i2i, inpainting, ControlNet, `latentCouple`, IP-Adapter, v1 seed / negative prompt): yes / no (pass `--allow-unverified` only when yes)

The official documentation provides no API for querying credit balance or consumption. Actual credit usage is checked by the user in the PixAI web UI and recorded here when needed.

| Date | Model, `mode`, & resolution | Tasks & images per task | Credits consumed (verified by user in web UI) | Notes |
| --- | --- | --- | --- | --- |
| 2026-10-25 (example) | Tsubaki.3, `pro`, `1k` | 1 task × 1 image / 1 task × 4 images | 4,000 / 7,000 | Example verified by user in PixAI usage history |
|  |  |  |  |  |

## Per-page commands

| Page | Requests (`input/pixai/requests/`) | Generate (remove `--execute` and later flags for a dry-run check) | Rebuild |
| --- | --- | --- | --- |
| 1 |  | `python -X utf8 scripts/pixai_batch.py generate --page 1 --execute --accept-warnings --confirm-credits --cost-note '…'` | `python -X utf8 scripts/pixai_batch.py build --page 1` |

Re-fetching records whose completion polling was interrupted: `python -X utf8 scripts/pixai_batch.py fetch --page 1` (does not re-send generation). Adopting candidates: `list --page 1` → compare images → `adopt p01-02 --candidate 3`, or `adopt-latest --page 1`.

## Reasons for keeping prompt warnings

| Request ID | Warning | Reason for keeping | Date |
| --- | --- | --- | --- |
|  |  |  |  |

## Adoption log

| Request ID | Adopted candidate | Reason for adoption & comparison notes | Adopted by (human / Codex) & date |
| --- | --- | --- | --- |
|  |  |  |  |

## Pre-send content verification

Fill out following "Expanding scene relationships and continuity into each request" and "Pre-send content verification" in `docs/knowledge/pixai-composed-production.md`. Verify the prompt, negative prompt, LoRAs, and reference images after variable expansion.

| Request ID & verified version | Required relationships (actor, counterpart, contact points, etc.) | Continuing state from previous panel / changes in this panel | Subject, LoRA, reference-image, and text-separation check / revision reason |
| --- | --- | --- | --- |
|  |  |  |  |

## Results of using undocumented features

| Request ID | Feature (i2i, ControlNet, IP-Adapter, etc.) | Accepted? / observed effect / notes | Date |
| --- | --- | --- | --- |
|  |  |  |  |

## Character, style, background, and LoRA variables (only when requested)

| Variable name | Character / purpose | Requests using it | Date configured & verified |
| --- | --- | --- | --- |
|  |  |  |  |

Values live in `.env.pixai` at the project root (API keys and URLs live in the shared `.env` file). Record only variable names here—do not copy secret values. Check registered variables with `python -X utf8 scripts/pixai_batch.py vars`. For editing, applying changes, and regenerating, see the [user-facing README](../pixai-prompts/README.md).
