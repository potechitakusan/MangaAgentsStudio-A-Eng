# Review Priorities and Responsibilities

Updated: 2026-09-26. Project workflow design, not a scale with demonstrated evaluation effects.

## Meaning of 1–5

Priority describes attention and revision priority, not quality: 1 light check, 2 where needed, 3 standard, 4 detailed, 5 central concern with multiple alternatives. Even 1 does not permit broken reading order or continuity contradictions.

| Key | Focus | Initial priority |
| --- | --- | --- |
| immersion | World immersion, emotion, pauses, information density | 5 |
| cinema | Framing, viewpoint, space, shot connections | 4 |
| story | Desire, obstacles, causality, change, ending | 4 |
| readability | English, balloons, panel order, reading flow | 5 |
| characterConsistency | Face, hair, costume, props, build | 4 |
| terminology | Worldbuilding terms and production terminology | 3 |

Configuration: `config/review-profiles.json`. Resolution order: defaults → scene preset (or command Preset if none) → scene weights. An unknown scene ID is treated as a typo/error. Omitting Preset is equivalent to base. Presets are starting candidates, not assumptions about comic genres.

```powershell
.\scripts\Resolve-ReviewProfile.ps1 -ConfigPath '.\config\review-profiles.json' -Preset 'confession'
.\scripts\Resolve-ReviewProfile.ps1 -ConfigPath '.\config\review-profiles.json' -SceneId 'scene-001'
```

Example entry inside scenes:

```json
"scene-001": {
  "preset": "confession",
  "weights": { "cinema": 5, "terminology": 2 },
  "reason": "Convey unspoken feelings through hands and distance"
}
```

<a id="common-knowledge"></a>

## Shared knowledge references

Keep cross-genre knowledge in existing documents by purpose/review focus. Integrate additions into the matching topic. Each skill reads only the relevant portions.

| Purpose | Guidance | Main skills |
| --- | --- | --- |
| Desire, change, causality, payoff, ending | [Story, Character, Theme](manga/05-story-character.md) | `manga-story-review` |
| Acting, dialogue, scene change | [Scenes, Dialogue, Props](manga/04-scene-dialogue-props.md) | `manga-story-review`, `manga-immersion-review`, `manga-cinema-review` |
| Information gaps, setup, pacing, silence | [Beats, Pacing, Information Order](manga/03-beat-pacing-timing.md) | `manga-immersion-review` |
| Focal subject, reactions, bodies, space | [Framing and Viewpoint](manga/02-visual-direction.md) | `manga-cinema-review` |
| Communication through art/text, order, display | [US English Comic Readability](japanese-manga-readability.md) | `manga-readability-review` |
| Generation methods, identity, experiments | [AI Image Production](ai-production.md) | `manga-ai-production` |
| Image-conditioned panels, corrections, cropping | [Shared workflow](external-panel-i2i.md) and selected-model guidance, e.g. [Qwen-Image 2.1](image-generation/qwen-image-2.1.md) | `manga-external-panel-i2i` |
| Findings, comparisons, actual images/readers | [Review records](#review-records) and following sections here | Review skills and `manga-supervision` |
| Register/check user-required steps | [Process Checker](process-checker.md) | `manga-process-checker` |

`manga/` indexes comic workflows/techniques; documents directly under knowledge provide focused details and operations. Consult PSD handoff, production settings, Codex operation, or optional video guidance as needed. Choose effect-specific expressive ideas/supervision through [supervision/](supervision/README.md); use shared guidance above for character, causality, and order.

## Production and consultation flow

The main agent understands intent and each scene's before → after change, then creates panel scripts/thumbnails. Consult relevant skills, compare alternatives, and integrate findings. Invoking a skill does not itself launch another agent. In a delegation-capable environment, give a sub-agent objective, pages, effective priorities, and skill path when delegation is authorized.

| Skill | Main focus | Typical use |
| --- | --- | --- |
| manga-immersion-review | Emotion, pauses, overexplanation | Overall reading experience of scripts/thumbnails |
| manga-cinema-review | Distance, direction, shot connections | Scene shot design consultation/review |
| manga-story-review | Roles, desire, causality, change | Synopsis/episode/scene structure |
| manga-supervision | Existing comedy guidance plus 15 trial scene themes (see supervision) | Expressive ideas during scripting; improvements after preview |
| manga-readability-review | Horizontal English lettering, order, placement | Thumbnail/lettering consultation and review |
| manga-ai-production | Character consistency, model choice, experiments | Producing panels from references |
| manga-external-panel-i2i | Actual composition/reference inputs, art corrections, post-crop consistency | After choosing external image-conditioned panel production |
| manga-terminology-review | Inconsistent term/worldbuilding spellings | Review only; do not require the glossary during initial drafting |
| manga-process-checker | Explicitly registered requirements and evidence | Registration, resumption/milestones/handoff for projects with requirements |

Specify target and effect, e.g. "scene-003, pages 4–5: preserve tension before the confession; consider silent panels and framing. Text follows..." Not every skill is needed every time.

For per-panel generation, supply cinema's focal subject/framing/contact points and immersion's pauses/emotion/face visibility. Generation translates intent into inputs and checks retention after generation, cropping, and finishing. Return causality to story and borders/text/order to readability. Do not make angle variety or hidden-face frequency universal generation rules. [Evidence E3](image-generation/production-evidence.md#e3) supports adopting this coordination, not demonstrated reader effects of individual techniques.

If `config/process-requirements.json` contains requirements, report target/version/evidence to the checker at script completion, each page completion, and other specified milestones. Check strong requirements before entering their specified stages too. Empty lists need no detailed review; standard recommendations alone do not justify registering requirements.

### Two stages of scene supervision

When a scene needs a particular effect, pass intent, elements, and effect to retain from the main agent to `manga-supervision` while scripting. After PNG creation, actually open the images and check whether the same intent comes through, then propose improvements. Follow [supervision routing](supervision/routing.md), select necessary guidance from comedy and 15 added themes, and compare alternatives while preserving the main effect. Those 15 themes are trial guidance with unverified general reader effects; check project images/readers. A separate agent is not mandatory.

Distinguish facts, production suggestions, and uncertainties. Use [shared knowledge](review-workflow.md#common-knowledge) for general judgments. Record in [Supervision Consultation and Review](../reviews/SUPERVISION.md); the main agent integrates decisions. Do not add genre-specific weights/quality scores; route findings to existing axes. Without image review, judgments remain preliminary text-based checks.

## Review records

Record in `docs/reviews/`:

| Target | Focus/priority | Observed fact | Hypothesized reader impact | Severity 1–3 | Improvement | Effect lost / exception retained |
| --- | --- | --- | --- | --- | --- | --- |

Severity: 1 minor, 2 obstructs understanding/emotion, 3 breaks order/story coherence. Priority × severity can help order revisions, but unreadability/continuity failures come first. Do not mechanically pass/fail by numbers. For an axis with no findings, record checked status or inapplicability rather than inventing a problem.

Connect version/location, observed fact, reader-impact hypothesis, proposal, and retained/lost effects. Replace vague "bad pacing" with specific duplicated explanation, missing goals, inferential leaps, missing evidence, or redundant reactions.

Image reviews require actually opening the PNG/image. A panel script cannot verify finished expressions/order. If images are unavailable, continue preliminary text review and mark visual judgments unverified. After revision, recheck changes and only necessary surrounding context.

The main agent records acceptance/rejection and reasons for each finding, then checks affected pages and continuity.

Keep normal production decisions/revisions/validation as needed. Records intended to feed project feedback back into the kit require a user request. Supervision does not authorize moving assets/dialogue into shared knowledge. Do not ask whether to record feedback without a request.

## Creating comparisons

Keep required information/scene purpose constant and vary the difference being investigated: explanation, silent reaction, listener, evidence presentation, etc. A reader who already knows the ending cannot supply a second first-read surprise response.

Stopping midway to ask predictions differs from normal uninterrupted reading. Record presentation order, prior knowledge, display method, and author explanations. Small samples do not establish genre-wide standards.

## Check these separately

- Understanding: what happened, who wanted what, and why the outcome followed.
- Prediction: where/what readers expected and what changed their interpretation.
- Emotion/preference: enjoyment, fear, empathy, and impressions of characters.
- Readability: where readers backtracked and whether subject, object, words, or causality were unclear.

Ask open responses first. Do not label agent inference as real reader response or fabricate an unperformed reading test. Understanding and the intended emotion are separate outcomes.

## Check revisions combining genres

Check whether added humor erases a serious wish, a reversal removes an established constraint, or an unrelated ability resolves a relationship. Connect the principal effect to the specific changed part and review the adopted version.

Correct knowledge distribution/references do not establish a better comic. Record format validation, script consultation, image review, and actual reader reactions separately.

## Production and handoff

Select guidance through `docs/MANGA-KNOWHOW.md`. Follow [Thumbnails through PSD](manga/08-workflow-review.md), centering planning, panel scripts, and thumbnails, with alternatives where needed, read-through, and integrated revision. Film/TV and screenwriting skills are supplementary references for relevant portions.

Review/revise PNGs first and confirm no further revisions. Without a PSD instruction, ask and wait; with one, do not ask again. Requested PSDs require [creation, validation, and handoff](psd-handoff.md). Awaiting PNG review/PSD decisions are valid waiting stages. A person normally finishes in CLIP STUDIO PAINT before external publication. CBZ requires explicit request. Image-production skills include this confirmation workflow; review skills validate their requested focus.
