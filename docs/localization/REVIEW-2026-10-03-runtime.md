# Independent back-translation review: general knowledge documents

Reviewed: 2026-10-03. Reviewer: independent semantic-review sub-agent.

## Method and actual scope

Read the frozen Japanese source and US English text of all 21 Markdown files directly under `docs/knowledge/`, plus both Markdown files under `docs/knowledge/image-generation/`. Compared requirements, conditions, examples, uncertainty, permission boundaries, and evidence claims by paraphrasing English meaning back into Japanese. Read the current localization policy, earlier runtime review, and local PLAN/PROGRESS before proceeding. The manga and supervision subdirectories, runtime code, generated images, external source contents, and live services are outside this review. Skills/templates/scripts were assigned to another reviewer; two skill files were read for context only and are not claimed as exhaustive coverage here.

## Corrections applied

| ID | File | Japanese meaning | Drift and correction | Back-translation assessment |
| --- | --- | --- | --- | --- |
| GN-01 | `docs/knowledge/video-tools.md` | The example's four steps are trial settings for an older Larryvrh graph | "was tested with" implied completed testing. Changed to "is a trial setting for" | The setting is for trials with the old graph. It does not newly claim execution or success. |
| GN-02 | `docs/knowledge/process-checker.md` | Follow the execution checks in publication guidance | "permission procedures" changed execution verification into a permission process. Changed to "execution checks" | Follow the source kit's execution verification; do not invent an additional approval requirement. |
| GN-03 | `docs/knowledge/immersion-and-cinema.md` | Consider whether hiding the face reduces the burden of devising an expression, delays an answer, or invites inference about feelings | "expression-processing demand" could mean the reader's processing burden. Changed to "the effort of devising an expression" and explicitly named readers as the recipients of inferred feelings | Distinguish the effort of designing an expression from inviting readers to infer inner feelings. The context clarifies whose effort the source leaves implicit. |
| GN-04 | `docs/knowledge/japanese-manga-readability.md` | The original illustrative line hesitates in response to being asked about future plans | "My plans for the future..." retained the topic but lost hesitation. Changed the JSON example to "My future plans?\nThat's hard to say..." | The speaker hesitates when asked about future plans. No definite ambition, refusal, or new character background is added. |

GN-03 and GN-04 were discussed with the main reviewer before adoption. The dialogue is a documentation example, not a change to Japanese source or an embedded comic image. Technical keys, coordinates, reading-order IDs, and paths were preserved in these edits.

## Preserved meaning and intentional adaptation

The review found no additional concrete semantic error in the remaining read documents. Existing explicit-authorization boundaries for Anlas, Gemini transmission/quota, Git installation, PSD creation, CBZ, video work, feedback recording, Hooks trust, and publication remain intact. Lost/unknown generation responses are not automatically resent. Planning can continue independently of unresolved generation parameters. Trial findings and historical Japanese speech tests remain distinct from universal claims and English validation.

Horizontal lettering, centered English balloons, natural English punctuation, left-to-right reading, and English audio for new English productions intentionally adapt the original Japanese defaults under the owner's localization instructions. Historical Japanese source descriptions/tests retain their original scope. These are intentional adaptations, not accidental back-translation defects.

The main agent restores source identities and original Japanese attribution labels; those labels were not edited by this reviewer. All external Markdown link URL sequences in the 23 reviewed documents match the frozen Japanese source in order. No current source information was fetched, and this review does not revalidate historical product specifications.

## Source preservation and verification

All 23 reviewed Japanese source files match their SHA-256 values in `source-manifest.json` after the edits. The Japanese snapshot was read only. Local verification confirms the four corrected strings and unchanged external URL sequences; no broad test suite or live API calls were needed for prose-only changes.

## Files read in full

- `docs/knowledge/ai-production.md`
- `docs/knowledge/codex-operation.md`
- `docs/knowledge/external-panel-i2i.md`
- `docs/knowledge/feedback-workflow.md`
- `docs/knowledge/glossary.md`
- `docs/knowledge/image-generation/production-evidence.md`
- `docs/knowledge/image-generation/qwen-image-2.1.md`
- `docs/knowledge/immersion-and-cinema.md`
- `docs/knowledge/japanese-manga-readability.md`
- `docs/knowledge/manga-sources.md`
- `docs/knowledge/novelai-api.md`
- `docs/knowledge/optional-skills.md`
- `docs/knowledge/page-layout.md`
- `docs/knowledge/panel-layout-policy.md`
- `docs/knowledge/process-checker.md`
- `docs/knowledge/project-options.md`
- `docs/knowledge/psd-handoff.md`
- `docs/knowledge/review-workflow.md`
- `docs/knowledge/story-structure.md`
- `docs/knowledge/video-assembly.md`
- `docs/knowledge/video-previsualization.md`
- `docs/knowledge/video-prompting.md`
- `docs/knowledge/video-tools.md`
