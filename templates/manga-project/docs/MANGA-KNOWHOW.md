# Comic production know-how index

Use this template around comic planning, text storyboards, rough storyboards, artwork, PNG review, and PSD handoff. Review/revise PNG previews first; once no revisions remain, create, validate, and hand off requested PSDs. If PSD creation has not been instructed, ask and wait; do not re-ask existing instructions. Normally humans finish in CLIP STUDIO PAINT before publication. CBZ only on explicit request.

Explanations use English. Preserve filenames, product names, source URLs, and machine identifiers. Film/screenwriting knowledge supports only scenes that need it.

This index is distributed with projects. Inside the source kit, knowledge text lives in `docs/knowledge/`. New-project creation also bundles that text so links below work.

## Choose by task

Version 0.3.2 [Shared know-how](knowledge/review-workflow.md#common-knowledge) covers character, causality, information, reading order, and endings through the documents below. [Scene supervision](knowledge/supervision/README.md) covers existing comedy plus 15 added themes for storyboard consultation and PNG improvements; `manga-supervision` selects needed text. The 15 additions are experimental, with general reader effects unverified; check through project images and test reading.

| Problem/stage | Knowledge | Form/check destination |
| --- | --- | --- |
| Learn comic process/page basics | [Storyboard, page, artwork basics](knowledge/manga/00-manga-basics.md) | [Brief](story/BRIEF.md) |
| Define story/characters | [Story, character, theme](knowledge/manga/05-story-character.md) | [Scene design](story/SCENE-TEMPLATE.md) |
| Divide moments into panels | [Text to rough storyboard](knowledge/manga/01-conversion.md) | [Text storyboard](story/TEXT-STORYBOARD.md) |
| Choose layouts and avoid monotony | [Panel workflow](knowledge/panel-layout-policy.md) | [Panel policy](production/PANEL-LAYOUT-POLICY.md) |
| Web dimensions, margins, guides | [Page dimensions/basic frame](knowledge/page-layout.md) | [Options](../OPTION.md), `config/page-layout.json` |
| Lettering and optional polishing | [Readability](knowledge/japanese-manga-readability.md#optional-polish) | [Dialogue/settings](production/DIALOGUE.md) |
| Install optional legacy Japanese-source polishing | [Installation, Git, Gemini consent](knowledge/optional-skills.md) | [Options](../OPTION.md); disabled for English work |
| Prepare print output | [Print options](../PRINT-OPTION.md) | Specifications/validation in that file |
| Check personally required steps in future work | [Process checker](knowledge/process-checker.md) | `config/process-requirements.json`, `.work/process-checker/` |
| Choose framing, reactions, props | [Subject, framing, viewpoint](knowledge/manga/02-visual-direction.md) | [Scene design](story/SCENE-TEMPLATE.md) |
| Adjust silence, tempo, page turns | [Beats, pacing, presentation](knowledge/manga/03-beat-pacing-timing.md) | [Information/recurrence](story/INFORMATION-SHEET.md) |
| Show conversation visually | [Scene, dialogue, props](knowledge/manga/04-scene-dialogue-props.md) | [Text storyboard](story/TEXT-STORYBOARD.md) |
| Serial, ensemble, comedy work | [Series/comedy](knowledge/manga/06-series-comedy.md) | [Information/recurrence](story/INFORMATION-SHEET.md) |
| Compare staging options | [Effect patterns](knowledge/manga/07-case-patterns.md), [Panel-allocation comparison](knowledge/manga/09-worked-example.md) | [Storyboard checks](reviews/NAME-REVIEW.md) |
| Read through and revise | [Storyboard to PSD](knowledge/manga/08-workflow-review.md), [Review workflow](knowledge/review-workflow.md) | [Storyboard checks](reviews/NAME-REVIEW.md) |
| Fix horizontal lettering, balloons, reading order | [English comic readability](knowledge/japanese-manga-readability.md), [Typesetting/checks](knowledge/japanese-manga-readability.md#typeset-script) | [Approved dialogue](production/DIALOGUE.md); "Post-artwork comparison" and "Post-typesetting checks" in [Checklist](reviews/NAME-REVIEW.md) |
| Generate art and preserve identity | [Image production/experiments](knowledge/ai-production.md) | [Experiment](experiments/TEMPLATE.md) |
| Supply sketch/reference images to external per-panel tools | [Shared workflow](knowledge/external-panel-i2i.md), [Qwen-Image 2.1](knowledge/image-generation/qwen-image-2.1.md), [Production evidence](knowledge/image-generation/production-evidence.md) | `manga-external-panel-i2i`, [Experiment](experiments/TEMPLATE.md) |
| NovelAI assets/composition | [Connection/cost](knowledge/novelai-api.md), [Production](knowledge/novelai-composed-production.md), [Batch/adopt/rebuild](knowledge/novelai-composed-production.md#batch) | Adopted settings/normal records; distinguish t2i/image inputs. [Batch records](production/NOVELAI-BATCH.md) |
| PSD for human finishing | [Handoff requirements](knowledge/psd-handoff.md) | [Specifications/validation](production/PSD-HANDOFF.md) |
| Check terminology, sources, acceptance | [Glossary](knowledge/glossary.md), [Imported sources](knowledge/manga-sources.md), [Feedback workflow](knowledge/feedback-workflow.md) | [Story terms](story/TERMS.md), [Requested feedback](feedback/TEMPLATE.md) |

## Technique index (77 items)

Six areas collect techniques for comic production/review, consolidating knowledge with the same purpose. Distinguish verified facts, production proposals, original examples, and unverified effects. Numbers are search IDs, not a required reading order or count of mandatory items.

### 01 From comic text storyboard to panels and rough storyboard

| ID | Technique |
| --- | --- |
| C01 | [Write the storyboard in the order readers experience it](knowledge/manga/01-conversion.md#c01) |
| C02 | [Create comic panel candidates; map existing shots only if needed](knowledge/manga/01-conversion.md#c02) |
| C03 | [Count shots, beats, and panels separately](knowledge/manga/01-conversion.md#c03) |
| C04 | [Split long shots where meaning changes](knowledge/manga/01-conversion.md#c04) |
| C05 | [Combine only when simultaneous viewing preserves meaning](knowledge/manga/01-conversion.md#c05) |
| C06 | [Give staging instructions as purpose plus visible content](knowledge/manga/01-conversion.md#c06) |
| C07 | [Turn silence into a visually specified panel](knowledge/manga/01-conversion.md#c07) |
| C08 | [Translate sound, movement, and inner states into comic information](knowledge/manga/01-conversion.md#c08) |
| C09 | [Distinguish the scopes of advice to avoid camera directions](knowledge/manga/01-conversion.md#c09) |
| C10 | [Check problems revealed only on the page](knowledge/manga/01-conversion.md#c10) |

### 02 Focal subject, framing, angle, viewpoint

| ID | Technique |
| --- | --- |
| V01 | [State the main subject in a phrase](knowledge/manga/02-visual-direction.md#v01) |
| V02 | [Use wide shots for context and close-ups for evidence](knowledge/manga/02-visual-direction.md#v02) |
| V03 | [Choose angles from needed information](knowledge/manga/02-visual-direction.md#v03) |
| V04 | [Show recognition through viewer, object, reaction](knowledge/manga/02-visual-direction.md#v04) |
| V05 | [Show the listener rather than the speaker](knowledge/manga/02-visual-direction.md#v05) |
| V06 | [Choose reverse shots for relationship changes rather than speaking turns](knowledge/manga/02-visual-direction.md#v06) |
| V07 | [Reveal character through backs, gait, and hand contact](knowledge/manga/02-visual-direction.md#v07) |
| V08 | [Use obstructions to limit information](knowledge/manga/02-visual-direction.md#v08) |
| V09 | [Switch objective and subjective views to shape experience](knowledge/manga/02-visual-direction.md#v09) |
| V10 | [Give empty-space shots independent meaning](knowledge/manga/02-visual-direction.md#v10) |
| V11 | [Repeat composition so readers notice differences](knowledge/manga/02-visual-direction.md#v11) |
| V12 | [Create meaning by juxtaposing adjacent images](knowledge/manga/02-visual-direction.md#v12) |
| V13 | [Preserve spatial continuity in the text storyboard](knowledge/manga/02-visual-direction.md#v13) |
| V14 | [Reduce the image to check whether important elements look important](knowledge/manga/02-visual-direction.md#v14) |

### 03 Beats, pacing, presentation timing, pauses

| ID | Technique |
| --- | --- |
| R01 | [Distinguish beats, structural milestones, and brief pauses](knowledge/manga/03-beat-pacing-timing.md#r01) |
| R02 | [Design pacing separately from presentation timing](knowledge/manga/03-beat-pacing-timing.md#r02) |
| R03 | [Separate event time, depicted time, and reading time](knowledge/manga/03-beat-pacing-timing.md#r03) |
| R04 | [Write changes as verbs to expose repetition](knowledge/manga/03-beat-pacing-timing.md#r04) |
| R05 | [Make stimulus, recognition, choice, and response visible](knowledge/manga/03-beat-pacing-timing.md#r05) |
| R06 | [Pause for anticipation before turns and absorption afterward](knowledge/manga/03-beat-pacing-timing.md#r06) |
| R07 | [Change expectation or danger as buildup lengthens](knowledge/manga/03-beat-pacing-timing.md#r07) |
| R08 | [Use reaction order to determine the scene emphasis](knowledge/manga/03-beat-pacing-timing.md#r08) |
| R09 | [Combine scene length and density](knowledge/manga/03-beat-pacing-timing.md#r09) |
| R10 | [Enter late and leave after the necessary aftertaste](knowledge/manga/03-beat-pacing-timing.md#r10) |
| R11 | [Arrange reader knowledge in three ways](knowledge/manga/03-beat-pacing-timing.md#r11) |
| R12 | [Place key words/images where the reaction begins](knowledge/manga/03-beat-pacing-timing.md#r12) |
| R13 | [Use page turns as information boundaries](knowledge/manga/03-beat-pacing-timing.md#r13) |
| R14 | [Record the reader state when evaluating pauses](knowledge/manga/03-beat-pacing-timing.md#r14) |
| R15 | [Check types and functions of silence](knowledge/manga/03-beat-pacing-timing.md#r15) |

### 04 Scenes, dialogue, props

| ID | Technique |
| --- | --- |
| D01 | [State the difference between scene start and end](knowledge/manga/04-scene-dialogue-props.md#d01) |
| D02 | [Separate what each character wants from how they pursue it](knowledge/manga/04-scene-dialogue-props.md#d02) |
| D03 | [Assign dialogue a verb describing its effect on the other person](knowledge/manga/04-scene-dialogue-props.md#d03) |
| D04 | [Separate spoken words, hidden feelings, and inexpressible desires](knowledge/manga/04-scene-dialogue-props.md#d04) |
| D05 | [Turn exposition into information characters use](knowledge/manga/04-scene-dialogue-props.md#d05) |
| D06 | [Break long speech with reactions](knowledge/manga/04-scene-dialogue-props.md#d06) |
| D07 | [Let a third subject carry the real dispute](knowledge/manga/04-scene-dialogue-props.md#d07) |
| D08 | [Make words and actions point in opposing directions](knowledge/manga/04-scene-dialogue-props.md#d08) |
| D09 | [Give brief replies and hesitations a function](knowledge/manga/04-scene-dialogue-props.md#d09) |
| D10 | [Define each character's language and gestures](knowledge/manga/04-scene-dialogue-props.md#d10) |
| D11 | [Connect everyday actions with emotion](knowledge/manga/04-scene-dialogue-props.md#d11) |
| D12 | [Give props multiple functions](knowledge/manga/04-scene-dialogue-props.md#d12) |
| D13 | [Let locations generate action](knowledge/manga/04-scene-dialogue-props.md#d13) |
| D14 | [Redirect scenes with entrances, exits, sounds, interruptions](knowledge/manga/04-scene-dialogue-props.md#d14) |

### 05 Story, character, theme

| ID | Technique |
| --- | --- |
| S01 | [State protagonist, goal, resistance, and cost in one sentence](knowledge/manga/05-story-character.md#s01) |
| S02 | [Show theme through choices and consequences](knowledge/manga/05-story-character.md#s02) |
| S03 | [Define desire and the belief obstructing it](knowledge/manga/05-story-character.md#s03) |
| S04 | [Turn character research into behavioral differences](knowledge/manga/05-story-character.md#s04) |
| S05 | [Reveal character through choices under pressure](knowledge/manga/05-story-character.md#s05) |
| S06 | [Give the opposing side a coherent purpose](knowledge/manga/05-story-character.md#s06) |
| S07 | [Do not skip the middle of change](knowledge/manga/05-story-character.md#s07) |
| S08 | [Let previous actions create the next problem](knowledge/manga/05-story-character.md#s08) |
| S09 | [Open with a changing situation and a reason to watch](knowledge/manga/05-story-character.md#s09) |
| S10 | [Give setups a natural function on first appearance](knowledge/manga/05-story-character.md#s10) |
| S11 | [Concentrate the climax into one action or image](knowledge/manga/05-story-character.md#s11) |
| S12 | [Fit structural methods to the reading experience](knowledge/manga/05-story-character.md#s12) |

### 06 Serialization, ensembles, comedy

| ID | Technique |
| --- | --- |
| L01 | [Use verbs to state what the comic does each episode](knowledge/manga/06-series-comedy.md#l01) |
| L02 | [Separate episode resolution from ongoing conflict](knowledge/manga/06-series-comedy.md#l02) |
| L03 | [Build a character network where strengths also cause problems](knowledge/manga/06-series-comedy.md#l03) |
| L04 | [Establish main and secondary lines before interweaving them](knowledge/manga/06-series-comedy.md#l04) |
| L05 | [Use transitions for time omission and contrast](knowledge/manga/06-series-comedy.md#l05) |
| L06 | [Vary types of episode hooks](knowledge/manga/06-series-comedy.md#l06) |
| L07 | [Differentiate ensemble reactions and interests](knowledge/manga/06-series-comedy.md#l07) |
| L08 | [Derive comedy from setting and character](knowledge/manga/06-series-comedy.md#l08) |
| L09 | [Guide reading through setup, development, punchline](knowledge/manga/06-series-comedy.md#l09) |
| L10 | [Return to the setup when humor is weak](knowledge/manga/06-series-comedy.md#l10) |
| L11 | [Update meaning in recurring jokes](knowledge/manga/06-series-comedy.md#l11) |
| L12 | [Fit humor and serious-scene placement to the characters](knowledge/manga/06-series-comedy.md#l12) |

## Supporting knowledge only when needed

- [Cinematic staging/immersion](knowledge/immersion-and-cinema.md): when camera framing or continuous action references help.
- [Story-structure research](knowledge/story-structure.md): for detailed theory/source verification.
- [Video workflow](knowledge/video-previsualization.md), [Video prompting](knowledge/video-prompting.md), [Video tools](knowledge/video-tools.md), [Video assembly/editing](knowledge/video-assembly.md): only on explicit video-trial requests.
- [Codex operation](knowledge/codex-operation.md): for skills and continuity records.

Knowledge text lives in shared knowledge; forms and this index live in the project template. The creation script bundles all needed documents.
