# Japanese 0.4.2 integration

Completed 2026-10-03 as **0.4.2-en-US.1**, source commit `b6a958a29ba9da5b8f9514f68c29c2e35401e6e5`. The supplied Japanese checkout was clean and left unchanged. Baseline: Japanese 0.4.1 recorded in the preceding manifest and English Git history. The previous source commit is absent from the supplied history; the available 0.4.1 revision `b873e2a` matches 18 modified baseline files with LF/CRLF normalization. `.gitattributes` differs from that baseline; retain the English rules and add the upstream `*.sh text eol=lf` requirement. Do not claim the missing commit was reconstructed.

## Reviewed scope

The byte-hash comparison reports **12 additions, 19 modifications, no deletions**. No image assets changed. Every changed source path is accounted for below.

| Source path | Change | Class | English disposition |
| --- | --- | --- | --- |
| `.gitattributes` | modified | distribution / line endings | Translated/adapted and integrated. |
| `.gitignore` | modified | distribution scope | Translated/adapted and integrated. |
| `AGENTS.md` | modified | translated prose / operating rules | Translated/adapted and integrated. |
| `README.md` | modified | translated prose / operating rules | Translated/adapted and integrated. |
| `distribution-version.txt` | modified | version | Translated/adapted and integrated. |
| `docs/architecture.md` | modified | translated prose / operating rules | Translated/adapted and integrated. |
| `docs/knowledge/codex-operation.md` | modified | translated prose / operating rules | Translated/adapted and integrated. |
| `docs/knowledge/image-generation/novelai-v5.md` | added | translated prose / operating rules | Translated/adapted and integrated. |
| `docs/knowledge/image-generation/production-evidence.md` | modified | translated prose / operating rules | Translated/adapted and integrated. |
| `docs/knowledge/manga/02-visual-direction.md` | modified | translated prose / operating rules | Translated/adapted and integrated. |
| `docs/knowledge/optional-skills.md` | modified | translated prose / operating rules | Translated/adapted and integrated. |
| `scripts/Initialize-OptionalSkills.sh` | added | code / regression tests | Translated/adapted and integrated. |
| `scripts/New-MangaProject.ps1` | modified | code / regression tests | Translated/adapted and integrated. |
| `scripts/New-MangaProject.sh` | added | code / regression tests | Translated/adapted and integrated. |
| `scripts/Resolve-ReviewProfile.sh` | added | code / regression tests | Translated/adapted and integrated. |
| `scripts/initialize_optional_skills.py` | added | code / regression tests | Translated/adapted and integrated. |
| `scripts/new_manga_project.py` | added | code / regression tests | Translated/adapted and integrated. |
| `scripts/public_release.py` | modified | code / regression tests | Already present in the English edition: root CLAUDE inclusion and template-owned knowledge resolution; retain alongside the new changes. |
| `scripts/resolve_review_profile.py` | added | code / regression tests | Translated/adapted and integrated. |
| `templates/manga-project/AGENTS.md` | modified | translated prose / operating rules | Translated/adapted and integrated. |
| `templates/manga-project/README.md` | modified | translated prose / operating rules | Translated/adapted and integrated. |
| `templates/manga-project/agent-modes/antigravity/AGENT-MODE.md` | added | translated prose / operating rules | Translated/adapted and integrated. |
| `templates/manga-project/agent-modes/antigravity/GEMINI.md` | added | translated prose / operating rules | Translated/adapted and integrated. |
| `templates/manga-project/docs/MANGA-KNOWHOW.md` | modified | translated prose / operating rules | Translated/adapted and integrated. |
| `templates/manga-project/docs/knowledge/novelai-composed-production.md` | modified | translated prose / operating rules | Translated/adapted and integrated. |
| `templates/manga-project/docs/reviews/NAME-REVIEW.md` | modified | translated prose / operating rules | Translated/adapted and integrated. |
| `tests/Test-Scaffold.ps1` | modified | code / regression tests | Translated/adapted and integrated. |
| `tests/test_optional_skills_portable.py` | added | code / regression tests | Translated/adapted and integrated. |
| `tests/test_public_release.py` | modified | code / regression tests | Translated/adapted and integrated. |
| `tests/test_review_profile_portable.py` | added | code / regression tests | Translated/adapted and integrated. |
| `tests/test_scaffold_portable.py` | added | code / regression tests | Translated/adapted and integrated. |

## Intentional English adaptations

- Retain US English prose, LTR panel/balloon order, horizontal lettering, ordinary punctuation, stable identifiers, original citations, URLs, licenses, and historical dates.
- Portable creation records `locale: en-US`, `readingDirection: ltr`, and `localizationVersion: 0.4.2-en-US.1`; it distributes editable English SFX SVGs as the PowerShell creator already does.
- Portable optional-skill selection recognizes the English `Japanese polishing skill` row and legacy Japanese rows/values. Polishing remains disabled by default and applies only to Japanese source text. Retain Japanese compatibility fixtures in tests and machine values.
- Antigravity remains an explicit optional mode; Codex is the default. Dedicated files preserve browser prohibitions, tool checks, NovelAI cost/consent rules, and the distinction between production mode and optional Gemini polishing consent.
- E4/E5 and N1–N5 retain one-project/model/input limitations, exact counts, evaluation caveats, and unperformed image-input verification. This localization repeats no external vendor/specification verification and consumes no generation quota.
- Existing example images and prompts are unchanged; their 0.4.1-en-US.2 records remain historical provenance.

## Review and verification

See [independent comparison](REVIEW-0.4.2.md) and [validation scope](VALIDATION.md). Content/diffs and baseline hashes were read; source and English state records were refreshed. Runtime, scaffold, shell, optional-skill, publication, and state-check commands were not executed. Earlier test results do not establish that 0.4.2 passes. Tests require the separate authorization described in [publication policy](../publication.md). No commit, push, or publication is included.
