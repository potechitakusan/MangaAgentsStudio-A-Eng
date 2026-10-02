# Rough-storyboard checklist and revision record

Without images, label this a preliminary text review. Distinguish human test reading from agent checking. Check only inspected items; leave unseen items blank and label them unverified. Untouched template entries do not count as completed work.

Work / version:　　　 Reviewer:　　　 Date:

## Post-artwork comparison

**Complete before separate typesetting; for imagegen with text/balloons, complete after generation. Finish this comparison before starting separate typesetting.** Actually open the image and record its appearance after cropping, rotation, and placement. "Plan" comes from the text storyboard; "Observed image" describes what is actually drawn, not a copy of the plan. Mark match / partial match accepted with reason / mismatch. Resolve mismatches through regeneration, placement changes, or plan revision, then update the corrected version. Unseen panels are unverified, never matched.

| Page/panel | Plan (subject, action, framing, characters/props) | Observed image | Match | Acceptance/action |
| --- | --- | --- | --- | --- |
| | | | | |

Key checks: main action stages in order (e.g. fold → release → land → pick up → unfold); appearance (hair, glasses, clothing layers, prop side); posture (sitting/standing); face/hands cut off by edges; visible space in wide shots; prop state (folded/open).

## Post-typesetting checks

Inspect completed pages including text/balloons and fill per page. For `scripts/typeset_manga.py`, record `check.json` counts and reasons for retained warnings. For imagegen text/balloons, visually inspect and compare source text after generation; mark `check.json` not applicable (whole-page generation). Automatic checks identify potential corrections, not a substitute for visual review.

| Page | check.json errors/warnings | Retained warnings/reasons | Visual result at publication size with artwork (build: version-folder page-NN-display.png): speaker, order, face/hand overlap, in-world text | No unrequested title/page number/other text |
| --- | --- | --- | --- | --- |
| | | | | |

## Story and scene

- [ ] Who wants what and what prevents it comes across.
- [ ] Information/motivation needed for a choice is supplied beforehand.
- [ ] Relationship, information, or expectation changes across the scene; aftermath scenes have intent.
- [ ] Dialogue/panels do not merely rephrase the same tactic repeatedly.
- [ ] Omitting an important decision's middle has not made a character change abruptly.

## Visuals and reading order

- [ ] Per-page template IDs or custom-layout intent/reasons are recorded and follow user-required/disabled-template choices.
- [ ] For imagegen page artwork, a numbered layout image and panel contents were actually supplied and generated count/placement/order/content compared with the plan. If not generated, mark unverified.
- [ ] Each panel has a clear first focal subject.
- [ ] The reader can follow whose viewpoint sees what.
- [ ] Face, hand, back, prop, and empty-space shots have reasons.
- [ ] Character left/right, orientation, gaze, possessions, and entrances/exits connect.
- [ ] Place/time transitions are recognizable.
- [ ] For flashback, omission, or parallel action, presentation order versus chronology, narration versus depicted time, and return point are followable. Deliberately withheld information has a point where it becomes understandable.
- [ ] Repeated framing/faces have intent; missing space/time/state information was checked and alternatives with backgrounds compared.
- [ ] Boarding, alighting, entrances, and exits visually connect start → action → destination.
- [ ] The panel's main action is readable; simultaneous actions have a justified relationship.
- [ ] Contact actions preserve before/during/after stage and whose hand touches what across panels.
- [ ] Balloon speakers and sequence are unambiguous in left-to-right/top-to-bottom reading.
- [ ] Essential text and prop details are readable at publication size.
- [ ] Dialogue is normally horizontal and centered with inner padding and word-boundary wrapping; exceptions/reasons are recorded in lettering settings.
- [ ] The page follows project frame/lettering settings and publication PNGs contain no guides or panel numbers.

## Pauses and pacing

- [ ] Necessary recognition, reaction, and choice follow stimuli.
- [ ] Silent panels identify whose action/emotion the pause awaits.
- [ ] Anticipation, danger, or understanding changes during buildup.
- [ ] Key dialogue/art is not visible earlier than intended.
- [ ] Strong scenes have needed contrast/breathing room around them.
- [ ] Page-turn effects were checked in actual spread presentation and the adopted left-to-right format.
- [ ] Reading duration was not inferred solely from panel count.

## Language, repetition, and ending

- [ ] Source and placed dialogue/narration preserve natural US English punctuation, meaning, contractions, and voice.
- [ ] Commas/periods follow sentence meaning, with no Japanese character-count restrictions. Connected balloons preserve sentence flow; follow [Lettering policy](../knowledge/japanese-manga-readability.md#dialogue-typesetting).
- [ ] Dialogue does not unnecessarily explain what art already shows.
- [ ] Agreement/disagreement between words and body language fits character intent.
- [ ] Returning words/props/compositions acquire updated meaning.
- [ ] Setup supports payoff; explanation does not overstay after the punchline/payoff.
- [ ] The ending has necessary reaction and aftertaste.
- [ ] Serialized work makes this episode's reward and next question clear.

## Scene supervision (needed themes only)

- [ ] Relevant themes/items were selected from [Routing](../knowledge/supervision/routing.md).
- [ ] Storyboard proposals were compared with effects conveyed by the actual preview.
- [ ] Main/additional effects coexist without canceling preserved emotions/characterization.
- [ ] Verified facts, production proposals, actually inspected image scope, and unknowns are distinguished.

Keep proposals/main-agent decisions in [Supervision](SUPERVISION.md). Mark not applicable when no relevant element exists. See [Shared review](../knowledge/review-workflow.md) for general checks.

## Reading record

| Panel/page | Author intent | Reader interpretation | Reread / confusion / early understanding | Evidence for reader account |
| --- | --- | --- | --- | --- |
| | | | | |

## Revision record

| Date/version | Location | Symptom | Root-cause hypothesis | Change/acceptance reason | Recheck result |
| --- | --- | --- | --- | --- | --- |
| | | | | | |

Review structure → motivation → information order → visuals → pacing → lettering. Fix clear local errors immediately. Do not treat every item as an equally strong rule; judge against the work's intent.

### Project conditions reused on later pages (only if needed)

| Adopted condition/reason | Applicable scenes | Exceptions/effects to preserve | Page scope | Next-page recheck |
| --- | --- | --- | --- | --- |
| | | | | |

Local artwork mistakes belong only in the revision table above. Use this table only for reusable conditions; do not apply them where the next page does not qualify. Keep actual lettering values in [DIALOGUE.md](../production/DIALOGUE.md). Project-to-kit feedback only on recording request.

References: [Workflow/revision](../knowledge/manga/08-workflow-review.md), [Pacing](../knowledge/manga/03-beat-pacing-timing.md), [Source map](../knowledge/manga-sources.md).
