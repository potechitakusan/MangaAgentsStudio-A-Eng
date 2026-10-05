# Semantic review of version 0.5.0

Reviewed 2026-10-05 by the integrating translator, comparing each changed English passage with the Japanese `b6a958a..b7a06f7` Git diff and the new Japanese README. **This was not the independent sub-agent review that [the update workflow](UPDATE-WORKFLOW.md) step 6 calls for.** No separate reviewer was engaged, so the independence requirement of that step remains open; see the open item below. The review used content and diffs only: it did not execute tests, scaffold a project, retrieve external documentation, call an API, or inspect artwork.

## Method

Each Japanese hunk was read, its English counterpart located, and the following were compared item by item: numbers and limits, negations, required versus optional actions, who performs each action (human, Codex, script), permission and cost boundaries, evidence status (confirmed, proposed, unverified), dates, and link targets. The new editing README was compared section by section (steps 1–8, the role table, every request example, and the troubleshooting table). The code and test hunks were applied one by one, then the English script was compared with the Japanese script again for the changed functions.

## Findings

No reversal of a requirement, optional action, permission boundary, or evidence qualification was found in the English changes.

- Counts and limits match the source: V5 up to 22 targets, V4 up to 6, V4/V4.5 5×5 grid; one to three distinguishing conditions per panel; 28-step and 0 Anlas conditions are untouched; the seed, interval, and per-run limit statements are unchanged.
- Cost and consent language is preserved. Asking Codex to prepare is not authorization for generation or paid use; neither the human nor Codex sends when 0 Anlas or the V5 allowance cannot be confirmed; `--accept-warnings` does not skip cost checks or errors; position pins do not imply 0 Anlas or placement agreement.
- Evidence status is preserved: the position-pin specification carries its 2026-10-04 date and source and its list of unverified items (placement accuracy, object placement, same-seed comparison, per-model API acceptance, contract/cost effects); the coordinate example remains a V5 candidate with no asserted V4/V4.5 conversion.
- Role assignment in the editing README matches the source: Codex prepares variables, references, feature lists, and content checks; the human edits text, runs or delegates commands, checks cost, and chooses images; PSD handoff still requires the PNG revision confirmation unless PSD creation was already instructed.
- `adopt-latest` semantics are identical: highest candidate number rather than modification time, all targets validated before any write, failure leaves the record unchanged, dry run writes nothing, other adoptions are preserved, and an earlier highest PNG is selected for a panel whose new generation failed.
- The three-prefix variable allowlist, the duplicate-source error across the environment and the three files, and the key-exclusion rule are unchanged in code and prose.

## Intentional English adaptations

Recorded in [the update record](UPDATE-0.5.0.md): the reading-order sentence in position pins, "in plain prose" for the relationship step, retained Japanese-value examples and fixtures, and original-language citation labels. These are cultural/linguistic adaptations, not meaning drift.

## Observations and open items

- The source's final commit is labeled 0.5.1 although the version file reads 0.5.0. The edition follows the version file and records the discrepancy. If the author intends 0.5.1, the version file, README header, and localization revision should change together.
- The English-only 0.4.2 FAQ paragraph (V5 production observations, prompt relationship checks, same-seed comparisons, V15) was folded into the source-style 0.5.0 summary and no longer appears as its own FAQ entry. The underlying documents are unchanged; only the README summary is shorter. Restore it if the owner wants the English README to keep that summary.
- Open: an independent sub-agent back-translation of the changed passages (workflow step 6) has not been performed.
- Automated checks were unperformed at this review's 2026-10-05 date. The owner-authorized 2026-10-06 follow-up ran the relevant unit/scaffold suites, publication check, and state `--check`; see [validation](VALIDATION.md) for exact results and remaining limits.

This qualitative review does not establish script behavior, Windows or Linux execution, API acceptance, generation quality, or editor behavior.
