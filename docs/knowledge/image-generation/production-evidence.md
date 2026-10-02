# Production Evidence for Per-Panel Image Generation

## Sources and applicable scope

The existing Qwen skill's `references/qwen-prompts.md` and `references/evidence.md` were also compared, consolidating input examples and verification scope into this document set. Give precedence to actual inputs corrected in later record organization. Mapping to the provider is retained in the kit's private working records.

<a id="e1"></a>

## E1: Underwater action comparison

- Conditions: one imagegen scene sample and 18 Qwen runs: 9 valid condition comparisons, 3 excluded runs before correction of character descriptions, and 6 additional edits.
- Recorded observations: character references aligned appearance but also retained standing poses, shallow water, and weak expressions. Editing the finished image without unnecessary references improved some areas, but some examples changed viewpoint/background or retained a forward lean.
- Limits: the sample differed in dimensions, composition, and subject size. This was not a controlled model ranking or success-rate comparison. Distinguish scene-sample generation from the imagegen-use restriction adopted later for that project.

<a id="e2"></a>

## E2: Per-panel production of a quiet conversation

- Conditions: 4 color pages, 16 panels. Blender renders with characters at 50 mm → Qwen → individual crops → specified Anima LoRA → lettering. 21 Qwen jobs, 4 Anima jobs. imagegen: 2 initial character/prop-reference jobs and 1 pre-completion edit.
- Recorded observations: corrected left/right character reversal, completion of face fragments, standing poses/calm expressions inherited from references, a pose presenting a book to the camera, and duplicate ribbons. Adopted individual crops retaining 62–94%.
- Limits: left/right correction changed reference order, position wording, and render occlusion together. It does not isolate reference order's effect. Real production counts include failures, re-renders, and edits; do not convert them into a general success rate.

<a id="e3"></a>

## E3: Evaluation of four pages with action

- Conditions: the same characters as E2 in 4 color pages/16 panels; final 1024 × 1536 px. Character-containing 50 mm renders → Qwen → cropping/lettering → ANIMA_LORA. 16 initial Qwen jobs plus 3 corrections = 19; 4 ANIMA_LORA jobs. imagegen: 1 initial-reference job and 1 pre-completion edit; zero new scene/panel/page drawing jobs.
- Changes: scenario, location, costumes, activity level, some layouts, framing, and action presentation. Connected feet, fingertips, eyes, full-body movement, object trajectories, and results; chose hands-only contact, a response with a face hidden by an object, and rear views, while retaining faces where emotion required them.
- User evaluation: after criticism of repetitive framing/action in the preceding work, one positive response recognized overall improvement and requested a record. This was neither an angle-only controlled experiment nor evaluation of individual settings. Distinguish it from an explicit "no revisions" response or PSD instruction.
- Recorded observations: corrected unwanted people, eye-detail requests reverting to full faces, clothing color with hidden faces, and orientation mismatches. A rear-reference example was adopted. The throwing panel's face/hands were edited with imagegen before completion, so they are not evidence of Qwen alone.
- Actual-input correction: hidden-face panels had a planned front-reference candidate, but saved inputs show one render for the first draft and one finished image for the revision. No frontal character reference was supplied. In a person-free overhead panel, the render input SHA-256 was unchanged, but character-description removal and seed change happened together; the result does not isolate prose effects.

<a id="e4"></a>

## E4: Removing request expressions in NovelAI V5

- Records: NAI-R06 and NAI-R07 (project-local material without public URLs). Organized/read on 2026-09-30. Kit integration compared the supplied summaries with counts in aggregate JSON. Original artwork was not reinspected.
- Conditions: `nai-diffusion-5-full`, 23 steps, `k_euler_ancestral`, scale 5, one image per request, ordinary t2i. No references or i2i. From a 40-page, 182-panel color slice-of-life comic, 50 panels with complex contact, operations, or spatial relationships were selected. Each panel had independent removals A and B and an unchanged control C, generated with the same three seeds (450 images total). Seeds, dimensions, quality terms, character descriptions/coordinates, and negative prompts were fixed; failed seeds were not replaced. Simultaneous removal of A and B was not tested.
- Scoring: two predefined aspects per panel, scored 0 (absent/different state), 1 (partial/ambiguous), or 2 (clear), with condition names anonymized. Of 100 removal patterns: 29 declined across all three seeds; 11 across two; 8 across one; 29 showed no detected difference; 4 improved (all in only one seed); 19 had insufficient controls (15 panels where the unchanged control clearly succeeded in fewer than two seeds).
- Recorded observations: even with person/object names retained, removing rubbing eyes, cupped/pressed palms, tying/adjusting/fastening operations, placing something inside a bag, separate roles for the hands, mutual gaze, rear viewpoints, proximity to the ground, or holding relationships weakened the target depiction across all three seeds. In some equal-score conditions, coordinates, viewpoint, or negatives retained the meaning. Outside the main scoring, an action aligning empty shoes changed to wearing shoes across all three seeds.
- Limits: deliberately selected complex panels, not a random sample. Three seeds per condition; a removal pattern could change multiple clauses, so effects cannot be isolated to individual words. The 100 conditions share 50 panels. One AI visually scored them; designer and evaluator were the same. No agreement among multiple human raters, statistical significance, or reader evaluation was established. Some temporal items, such as immediately after playing music, could not be judged from a single image.

<a id="e5"></a>

## E5: Alternative presentations of difficult actions in NovelAI V5

- Records: NAI-R09 and NAI-R10 (project-local material as above). Organized/read on 2026-09-30. Counts were compared with aggregate JSON. Original artwork and the comparison edition were not reinspected.
- Conditions: the same project and generation settings as E4. Records for all 182 panels were compared; 54 panels were selected based on repeated failures, recovery through composition/state changes, compromises, and insufficient E4 controls. Alternative A covered 54 panels; additional B covered 14, each with three seeds. Including original request C, 366 images were visually inspected (303 new, 63 C images reused from E4). The same three seeds were paired; failed seeds were not replaced.
- Scoring: “specified visible state,” “original intent,” and “connection to neighboring panels,” each 0/1/2. Of 68 alternative conditions, 19 had all three axes scored 2 in three seeds; 7 in two seeds; 10 in one seed; 32 in none. AI agents divided non-blind visual scoring. C and A/B had different presentation targets, so score differences were not treated as effect sizes.
- Recorded observations: successful examples included moving closer to expressions (a mug cupped in both hands and a face with eyes closed), showing completion (handle on a hook, closed bag, both hands returned to the lap), retaining one contact point (right hand and pencil tip), shifting time (just after a ball separates from the arms), and distributing information across neighboring panels. Pressing one key with one finger, signaling a beat, relaxed fingers, and four-hand piano duets had 0/3 seeds scoring 2 on all axes in both A and B. Lunchboxes/baskets changed structure even when the intent remained readable. Replacing one panel sometimes contradicted the next panel's hands; the comparison edition also adjusted neighboring panel crops.
- Adoption: 36 representative panels were incorporated into 21 pages of a 40-page comparison edition; the remaining 19 pages retained the originals. The 36 include alternatives successful in only one seed and conditional adoptions involving crops or neighboring adjustments (six images whose uncropped artwork scored below 2 on at least one axis). Eighteen panels retained the original adoption. In some cases, original spatial information or flow was preferred over a new alternative successful in three seeds.
- Limits: a practical comparison changing angle, timing, and multiple expressions together, not a causal experiment on words. No reader test established that comic quality did not decline. Four panels retained negative wording for an old instrument setting; only A was corrected before sending, so these were not angle-only comparisons.

## Adopted decisions and remaining limits

What was generalized is the [input-role, correction, cropping, and recording workflow](../external-panel-i2i.md). Operations in the [model document](qwen-image-2.1.md) are candidates based on observations in this setup. Equivalent improvements in other models, Qwen versions, or quiet scenes remain unverified. Consider counterexamples where hiding faces removes necessary emotion.

E4/E5 inform production proposals for relationship checks and shortening in [Request prompt construction](../novelai-composed-production.md#prompt-writing), [comparisons using paired seeds](../novelai-composed-production.md#batch), checking whether artwork depicts a different action, and [alternative presentations of difficult actions](../manga/02-visual-direction.md#v15). Model-version-specific symptoms belong in [NovelAI V5](novelai-v5.md). These are observations from one project, one model version, and ordinary t2i; do not transfer them to V4.5 or earlier, Curated, other models, i2i, or reference inputs as verified facts.

For NovelAI, E4/E5 provide production records for V5 Full ordinary t2i. Real-service verification involving image inputs (initial images/references) remains unperformed under NAI-VERIFY-01. [NovelAI API](../novelai-api.md) is authoritative for connection/cost handling. Incorporating these records does not authorize subscription queries, generation, or Anlas use.

Do not incorporate character/project names, costume settings, original art, Blender scenes, personal process requirements, credentials, or unorganized logs. The 50 mm lens, crop percentages, generation settings, and finishing settings are observed conditions, not universal recommendations.

The complete E4/E5 requests, images, API responses, account status, and style-candidate research lists are also excluded.
