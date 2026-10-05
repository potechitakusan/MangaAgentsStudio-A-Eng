# Japanese 0.5.0 integration

Completed 2026-10-05 as **0.5.0-en-US.1**, source commit `b7a06f740da679a407b40cdc388d63a0b9a62126`. The supplied Japanese checkout was clean and left unchanged. Baseline: Japanese 0.4.2 at `b6a958a29ba9da5b8f9514f68c29c2e35401e6e5`, which is present in the supplied history, so the changes were reviewed as a real Git diff (`b6a958a..b7a06f7`) as well as by byte hashes.

Version note: the Japanese `distribution-version.txt` reads `0.5.0` at this commit. The final upstream commit message says "version 0.5.1", but that commit did not change the version file (its changes are within the NovelAI batch script, its tests, and three NovelAI documents). This edition follows the version file, so the source version is recorded as 0.5.0 and the English revision as 0.5.0-en-US.1. The later 0.4.2 commit `3dc5915` (NovelAI prompt verification) was not part of the earlier English 0.4.2 integration and is included here.

## Reviewed scope

The byte-hash comparison reports **1 addition, 13 modifications, no deletions**. No image assets, panel templates, or sound-effect assets changed, so no image or asset regeneration was needed. Every changed source path is accounted for below.

| Source path | Change | Class | English disposition |
| --- | --- | --- | --- |
| `README.md` | modified | translated prose | The version FAQ is replaced by the 0.5.0 summary, following the source. The English-only 0.4.2 FAQ is folded into it (its Linux and Antigravity content is item 4); the edition's reading/lettering note is retained. Header shows source 0.5.0 and revision 0.5.0-en-US.1. |
| `distribution-version.txt` | modified | version | `0.5.0`. |
| `docs/README.md` | modified | translated prose | New index row for the NovelAI editing README. |
| `docs/knowledge/novelai-api.md` | modified | translated prose / API example | New "Position-pin requests" section. JSON example and field names are unchanged; the checked date (2026-10-04) and the unverified-effect statements are retained. |
| `skills/manga-ai-production/SKILL.md` | modified | translated prose / operating rules | Variables extended to style and background; new "NovelAI prompt construction and pre-send verification" section and position-pin guidance. |
| `templates/manga-project/.env.example` | modified | configuration example | Style and background example variables; three-source variable reading and duplicate error. |
| `templates/manga-project/AGENTS.md` | modified | translated prose / operating rules | Pre-send verification rule and three-type variable rule. The heading it cites matches the English skill heading exactly. |
| `templates/manga-project/README.md` | modified | translated prose | Pointer to the editing README. |
| `templates/manga-project/docs/SETUP.md` | modified | translated prose | Pointer to the editing README. |
| `templates/manga-project/docs/knowledge/novelai-composed-production.md` | modified | translated prose / operating rules | Position pins, scene relationships and continuing state, pre-send verification, `adopt-latest`, `--accept-warnings` default, and style/background variables. |
| `templates/manga-project/docs/novelai-prompts/README.md` | added | translated prose / user procedure | New English README with the same eight steps, role table, command examples, and troubleshooting table. |
| `templates/manga-project/docs/production/NOVELAI-BATCH.md` | modified | translated record template | New commands, pre-send verification table, renamed variable section. |
| `templates/manga-project/scripts/novelai_batch.py` | modified | code | Three variable types, numeric candidate names of three or more digits, `adopt_latest`, and the `adopt-latest` command, with English messages and help. |
| `tests/test_novelai_batch.py` | modified | regression tests | Five upstream cases added with identical assertions. |

## Intentional English adaptations

- Retain US English prose, left-to-right panel and balloon order, horizontal lettering, ordinary punctuation, stable identifiers, original citations, URLs, licenses, and historical dates. Source labels that are Japanese in the baseline (for example the NovelAI official-documentation labels and the V5 announcement label) remain in Japanese, as the 2026-10-03 policy clarification requires; the surrounding explanation is English.
- Position pins, step 2: the source says not to copy the manga right-to-left reading order into the Character input order. The English text keeps the intent (input order follows the pin positions, top to bottom and left to right, not the reading order) and states that the Japanese mode reads right to left while this edition reads left to right.
- Scene-state step 1: the source tells the writer to make relationships concrete "in Japanese" before converting them to prompt terms. The English text says "in plain prose before converting to prompt terms", because the working language of this edition is English. The prompt fragments in the examples are English tags in both editions and are unchanged.
- The Japanese-value example in the editing README (one line of Japanese prompt text) is retained as a UTF-8 compatibility example, with its English meaning given in the sentence introducing it. The test fixture with a Japanese background value is likewise retained and labeled.
- The numeric-age pattern that includes a Japanese counter (`歳`) in the prompt check remains a Japanese-input compatibility rule, unchanged.
- Variable-name help text: the source's single sentence is rendered as "Variable names must start with NOVELAI_CHAR_, NOVELAI_STYLE_, or NOVELAI_BACKGROUND_ followed by uppercase ASCII letters, digits, or underscores." The three prefixes and the allowlist regular expression are identical to the source.
- Not changed: the position-pin guidance remains NovelAI-specific, unverified for placement accuracy, and subject to the existing cost checks. This localization performed no generation and consumed no Anlas.

## Review and verification

See [the 0.5.0 review](REVIEW-0.5.0.md) and [validation scope](VALIDATION.md). Content, diffs, and baseline hashes were read; the source manifest and English state record were refreshed. Python syntax of the changed script and tests was parsed, and the links and anchors in the changed documents were checked. The unit tests, scaffold tests, publication check, and state `--check` were not authorized, so they were not executed as test runs and nothing is reported as passing. No commit, push, or publication is included.
