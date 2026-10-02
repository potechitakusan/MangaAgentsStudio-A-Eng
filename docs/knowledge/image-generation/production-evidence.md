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

## Adopted decisions and remaining limits

What was generalized is the [input-role, correction, cropping, and recording workflow](../external-panel-i2i.md). Operations in the [model document](qwen-image-2.1.md) are candidates based on observations in this setup. Equivalent improvements in other models, Qwen versions, or quiet scenes remain unverified. Consider counterexamples where hiding faces removes necessary emotion.

For NovelAI, distinguish the existence of connection code/API documentation from real-service verification; register NAI-VERIFY-01 as an unperformed verification task. [NovelAI API](../novelai-api.md) is authoritative for connection/cost handling. Incorporating these records does not authorize subscription queries, generation, or Anlas use.

Do not incorporate character/project names, costume settings, original art, Blender scenes, personal process requirements, credentials, or unorganized logs. The 50 mm lens, crop percentages, generation settings, and finishing settings are observed conditions, not universal recommendations.
