# Independent back-translation review

Completed 2026-09-30 for localization 0.4.1-en-US.1. Three translation sub-agents each reviewed another translator's completed work against the frozen Japanese source. Reviewers reconstructed the English meaning in Japanese, then compared agency, conditions, negation, numbers, optional versus required actions, permission boundaries, and evidence qualifications.

| Independent reviewer | Scope and detailed record |
| --- | --- |
| Story/supervision translator reviewing project/runtime text | [Project templates and runtime skills](REVIEW-project-runtime.md): 19 documents covering project rules/options, production, reviews, Claude mode, and nine skills |
| Core-knowledge translator reviewing story/publication text | [Story, supervision, and publication](REVIEW-story-publication.md): all 37 scoped Markdown documents structurally compared; 15 documents read in full against the source, plus targeted source/register and README checks |
| Project/runtime translator reviewing core knowledge | [Core knowledge](REVIEW-core-knowledge.md): 23 knowledge documents, kit AGENTS rules, SFX README, and all 38 sound-effect expression families |

Eleven semantic wording issues were corrected. Examples include restoring “default” to the 30-request limit; translating a prop's holding hand without implying two people holding hands; preserving interest without inventing affection; clarifying that 96%/94% crop figures concern width; and accurately stating which model-specific aspects the local client does not validate. The project review also records two resolved integration issues: English SFX documentation had to match the rebuilt catalog, and the disabled optional-skill value had to remain the machine-readable `none`.

Reviewers found no unresolved material reversals of requirements, permissions, or evidence qualifications within their stated scopes after correction. This is a qualitative audit with explicitly recorded coverage, not a claim of independent sentence-by-sentence review of every file, a legal opinion, a reader study, or external product verification. Runtime and visual checks are recorded in [Validation](VALIDATION.md).

The following are intentional, authorized adaptations: left-to-right panels and balloons; horizontal, word-wrapped English lettering; normal English punctuation; contextual English sound effects; and Japanese polishing tools described only as optional Japanese-source support. Source dates, attributions, API identifiers, compatibility paths, and licensing boundaries remain traceable.

The revision-1 audit did not cover embedded example lettering. Revision 2 closes that bundled-image gap: a separate [dialogue review](REVIEW-example-dialogue.md) checked all proposed narrative text against all 29 source pages and applied five further precision corrections. Actual edited-image checks are scoped in the [image review](REVIEW-example-images.md). Provisional name readings and source speaker ambiguities remain in [the Japanese hearing sheet](HEARING-SHEET.ja.md). External Japanese comics and PSDs remain outside the localized deliverables. Future upstream revisions require a new review of affected text and images; earlier audits do not automatically cover later edits.

## Follow-up review, 2026-10-03

Revision 0.4.1-en-US.3 adds a further independent comparison requested by the owner and restores original Japanese source identities. Three sub-agents reviewed general knowledge, story/supervision and saved example dialogue, and scaffold/skills/operating text. Resolved corrections and actual coverage are recorded in the [follow-up review](REVIEW-2026-10-03.md). This is a new prose and saved-dialogue review; the earlier image inspections are not represented as having been repeated.

## Japanese 0.4.2 update

The separate reviewer compared changed English prose and new portable code against the supplied Japanese 0.4.2 source. See [0.4.2 review](REVIEW-0.4.2.md) for exact scope and findings. The review covered numbers, negation, permissions, optional/mandatory distinctions, and evidence limits. It does not carry earlier runtime/image checks forward to this version.

## Japanese 0.5.0 update

The integrating translator compared the changed English prose, the batch-script port, and the new editing README against the Japanese `b6a958a..b7a06f7` diff. This was **not** an independent sub-agent review; that workflow step remains open. See [0.5.0 review](REVIEW-0.5.0.md) for method, findings, intentional adaptations, and open items.
