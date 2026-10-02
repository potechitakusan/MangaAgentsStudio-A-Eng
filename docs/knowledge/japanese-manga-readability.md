# Readability for US English Comics

Updated: 2026-09-20. External sources checked: 2026-09-12 unless individually noted. English localization: 2026-09-30. Scope: page comics read left to right and top to bottom, with horizontal English lettering. Adapt communication/display suggestions to the project's format. Reader testing has not been conducted. The filename `japanese-manga-readability.md` remains stable for compatibility.

## Distinguish kinds of guidance

Distinguish conventions confirmed in publisher tutorials, project-specific policy, and production suggestions. Repair confusing reading order. Evaluate intentional artistic departures by whether intended readers can follow them.

This English template uses **horizontal dialogue and internal monologue** and horizontal short labels within the art. This is a localization choice, not a universal prohibition on other lettering. Distinguish writing on depicted objects, such as signs/screens, from explanations addressed to readers. Record the scope/reason of format-specific changes.

<a id="dialogue-typesetting"></a>

## English alignment and punctuation (kit production policy)

The Japanese source's user-specified 2026-09-20 policy has been adapted for the English edition at the author's request. These are kit choices, not rules established by the cited Japanese sources. They apply to comic dialogue, internal monologue, and narration, not uniformly to production prose or quoted sources.

- **Center dialogue within balloons by default.** Use horizontal lines, balanced word wrapping, and enough interior padding. Do not imitate Japanese top-aligned vertical columns. Left-aligned narration may be used where its box and voice support it. Record adopted alternatives/artistic exceptions in `docs/production/DIALOGUE.md`.
- **Use natural US English sentence punctuation.** Periods are permitted; retain question marks, exclamation marks, contractions, and meaningful pauses. Do not remove a sentence boundary merely because Japanese manga lettering often omits a full stop.
- **Use commas according to meaning, grammar, rhythm, and character voice.** The Japanese 20-character threshold does not apply to English. Do not lengthen dialogue just to qualify for punctuation or use character counts as a substitute for editing.
- Treat connected balloons as a continuous utterance for meaning and pacing, while giving each balloon a clear place in reading order. Separate balloons by the same speaker are not automatically one text block. Treat unboxed monologue/narration as its own coherent block.
- Wrap at word boundaries and meaningful phrases. Do not split a word merely to fit a fixed character count. Keep punctuation with the words it belongs to; do not insert line breaks or balloon breaks that change emphasis, certainty, or reference.

Check punctuation in the panel script and approved text, then check alignment/padding in thumbnails and PNGs. For divided or connected utterances, verify sentence continuity, balloon order, and the reason for each break. Apply the same checks after editing, whether optional skills are enabled or not.

## What the sources establish

| ID | Short summary of confirmed content | Source and scope |
| --- | --- | --- |
| J01 | Japanese right-bound manga reads right to left and top to bottom; panel spacing helps indicate order. This is historical source context, not the English edition's reading direction. | [小学館: コマ割りについて（前編）](https://shincomi.shogakukan.co.jp/training/004.html). Introduction for page manga; does not impose this direction on English comics or vertical scrolling. Checked 2026-09-12 |
| J02 | Discusses balloon order, proximity to speakers, phrase-based line breaks, and splitting long speech. | [小学館: フキダシとセリフ](https://shincomi.shogakukan.co.jp/training/006.html). Introductory editorial guidance. Diagram images could not be retrieved in that review, so text alone does not establish exact numbered-shape details. Checked 2026-09-12 |
| J03 | The basic balloon is oval; changing shape can emphasize shouting and similar situations. | [小学館: まんが用語をおぼえよう！](https://shincomi.shogakukan.co.jp/training/001.html). Publisher's basic definitions; does not assign one unique meaning to every shape. Checked 2026-09-12 |
| J04 | CLIP STUDIO describes oval balloons and effect-line flashes, including radial bursts, as different creation mechanisms. | [ClipStudioOfficial: フキダシをつくろう！](https://tips.clip-studio.com/ja-jp/articles/863). Software creation/adjustment procedure, not a standardized emotional vocabulary. Checked 2026-09-12 |
| J05 | Japanese vertical text runs top to bottom with columns right to left; punctuation/closing brackets avoid line starts, and opening brackets avoid line ends. | [W3C: 日本語組版処理の要件](https://www.w3.org/TR/jlreq/), 2.3.1, 3.1.7, 3.1.8; 2020 Working Group Note. General Japanese typography, not a comic-specific mandate or English typesetting specification. Checked 2026-09-12 |
| J06 | Recommends padding between text and balloons and reserving lettering space in thumbnails. | [Effective Storytelling, Design Tips](https://www.clipstudio.net/en/comics-manga/design-tips/). International tutorial. English word-count guidance is not interchangeable with Japanese character counts. Checked 2026-09-12 |
| J07 | Bleeds, borderless panels, spreads, and irregular panels have different uses; text too close to the edge may be trimmed in print. | [小学館: コマ割りについて（後編）](https://shincomi.shogakukan.co.jp/training/005.html). Introduction including print. Set exact safe areas from the printer's specifications. Checked 2026-09-12 |

## Give art and dialogue different jobs (production suggestion)

Dialogue can show goals/self-image while art shows actions/results, allowing readers to compare. Check whether reaction dialogue merely explains a result already clear in the image. Shorten redundant explanation only if subject, object, causality, and motivation remain understandable.

Distinguish speech, inner thoughts, and narration, and clarify who receives each piece of information. Do not have characters respond as if they heard another person's thoughts. Identify the character and time/place of off-panel voices or voices crossing locations.

## Align reading order with understanding (production suggestion)

- Follow speakers and replies using the full intended text volume. Before shrinking lettering, look for duplicated meaning or unnecessary responses.
- Distinguish conditions, conclusions, and corrections. Mechanical fixed-length splitting can sever their relationship.
- Check whether a prominent word/image reveals the answer too early. Titles and previews also give readers advance information.
- When relying on multiple meanings, referents, or limits of a promise, verify that the original wording supports all intended interpretations.
- Distinguish imagination, character inference, and actual outcomes. Do not present a guess later overturned as objective fact.

## Review reading flow at three scales (production suggestion)

**Spread/page:** normally place entry at the upper left and exit at the lower right, and verify that panel order can be numbered. Check whether large faces, dense blacks, or strong sound-effect lettering attract attention before earlier panels are read. This does not mean a single straight diagonal eye movement.

Follow tier breaks, returns from long panels to adjacent columns, and entry points from a large view into detail. Diagonals and border breaks are not recommended for their own sake; when used, check that they do not obscure the next entry, text, or face. Distinguish multiple images meant as one simultaneous impression from successive moments.

**Panel:** place characters around the intended order of first line → next line → important reaction. Reconsider an existing composition if adding dialogue makes it hard to follow. When switching left/right positions during conversation, maintain spatial relationships through backgrounds and orientation.

**Inside a balloon:** read horizontal lines left to right, then downward. Balance centered lines and combine phrase boundaries with the speaker's breathing. At final dimensions/reduced display, verify that commas, apostrophes, ellipses, and small letters remain distinct.

| Symptom | Check | Smallest possible correction |
| --- | --- | --- |
| Reply is read first | Does the later balloon protrude above or to the left? | Move it; split the exchange into two panels if needed |
| Tails cross | Do speaker positions oppose speaking order? | Reposition characters or cut to a close-up of the other speaker |
| Reader skips to the next tier | Do gutters/vertical boundaries suggest another route? | Clarify tier divisions and adjust spacing |
| Reveal is visible too soon | Is the answer on the same visible page/spread? | Move it beyond the page turn for the actual display format |
| Text hides art | Was full dialogue volume present in the rough? | Reserve text space first and avoid essential artwork |

## Make action and positions traceable (production suggestion)

Follow who acts, toward what, in which direction, doing what, and with what result. Add any contact, outcome, or witness reaction whose omission would misidentify the cause. Not every action needs equal coverage.

If successive details lose spatial orientation, restore only the necessary overall view. Do not turn this into a fixed interval for wide shots. When sound/effects convey action, verify that source and result are understandable.

Check whether a foot, hand, or object insert prepares a later action or has another purpose. Ensure highlighted details do not read as unintended foreshadowing. When moving between objective views and a character's limited view, retain gaze/position cues and clarify the relationship between subjective perception and actual events.

## Keep balloon meanings consistent (production suggestion)

The table is an initial project vocabulary. J03 supports only basic oval/emphasis distinctions; finer emotional distinctions between jagged and radial bursts are project experiments. One shape can serve speech, thoughts, or shock in different works; shape alone does not establish speaker or whether words are spoken.

| Type | Initial use | Review point |
| --- | --- | --- |
| Oval | Ordinary conversation | Does size unintentionally imply volume? Is the speaker clear? |
| Jagged / explosive | Raised voice, shouting, strong surprise | Does quiet speech look shouted? Is intensity distinct from ordinary speech? |
| Radial burst / flash | Candidate for strong inner reaction, shock, urgent thought | Distinct from spoken dialogue? Do dense lines obscure small lettering? |
| Unboxed monologue | Candidate for unspoken words, horizontally lettered | Are viewpoint character, time, and narrator clear? |
| Silence / ellipsis | No answer, hesitation, or similar pause | Is there a change around the pause rather than reliance on "..." alone? |

Record visual distinctions too: jagged balloons have angular contours, while radial bursts use many lines converging around the text, although mixed forms exist. Do not equate tool names with narrative meaning.

## Lettering and final dimensions (production suggestion)

- Use horizontal English and centered balloon text by default, with phrase-based wrapping. Apply [alignment/punctuation policy](#dialogue-typesetting); avoid isolated punctuation at awkward line boundaries.
- Do not convert an English word limit into Japanese character counts or vice versa. Word length, font, emphasis, and balloon shape change the required space even at the same count.
- After splitting long speech, verify that readers still know it is the same speaker. Identify whether the break marks a topic change, breath, or intervening reaction.
- Do not accept AI lettering unchecked. Compare approved dialogue with the rendered text; when separate lettering is used, place that text on lettering layers. Check typos/omissions separately from reading order/readability.
- Do not judge only while zoomed in. Check intended paper dimensions, one-page ebook display, and smartphones when relevant.

Single pages, spreads, and scrolling reveal different amounts simultaneously. A crop alone cannot verify page turns or premature reveals. Read necessary text/details at publication size. Do not convert screen pixels into a supposed universal print-size standard.

<a id="typeset-script"></a>

## Typesetting script and automated checks

The project's `scripts/typeset_manga.py` creates transparent balloon, dialogue, in-art text, and panel-border layers and checks them without modifying the drawing. Follow [text finishing](page-layout.md#text-finishing): use separate typesetting after non-imagegen art, or with imagegen when lettering/balloons are added later. For whole-page generation including lettering, visually inspect and compare exact text. This kit-specific tool was added 2026-09-29; improved reader evaluation is unverified. English localization uses horizontal word-wrapped lettering by default.

- English text: horizontal lines, word-boundary wrapping, centered balloon alignment, and padding. Use `\n` for intentional phrase/breath breaks; inspect automatically wrapped text for balance and meaning. Legacy Japanese vertical features are not the English default.
- Balloons: `speech` (oval), `whisper` (dashed), `shout` (jagged), `flash` (radial burst), `narration` (rectangle), `monologue` (unboxed with white outline). Set `tail` to the speaker's mouth coordinates; the tail points toward it and stops before the face region.
- In-art text: `inserts` specifies paper/screen/sign bounds and text to create lettering depicted as part of an object.
- Fonts: search project `assets/fonts/` first, then suitable OS fonts. Fonts are not bundled. Record the chosen font in [lettering settings](../production/DIALOGUE.md); users check distribution/commercial-use terms.

Coordinates are page/placement pixels. With `layout` pointing to `prepare_page_layout.py`'s `layout.json`, page dimensions, panel shapes, text-safe area, and border thickness come from that file. `panel` is the panel's reading-order number; `order` is balloon order within it.

```json
{
  "schema_version": 1,
  "layout": "output/layout/page-001-v1/layout.json",
  "text": {"size": 28},
  "keep_out": [{"panel": 1, "box": [180, 280, 340, 440], "label": "Mio's face"}],
  "no_keep_out": {"2": "Sky with only a paper airplane"},
  "balloons": [
    {"id": "p1-a", "panel": 1, "order": 1, "speaker": "Mio", "kind": "speech",
     "text": "My future plans?\nThat's hard to say...", "center": [204, 180], "tail": [244, 300]}
  ],
  "inserts": [{"id": "form", "panel": 3, "box": [100, 780, 360, 950], "style": "paper",
               "title": "Future Plans Survey", "lines": ["Year 2: Mio Hinata"], "rotation": -4}]
}
```

```powershell
python scripts/typeset_manga.py --spec output/typeset/page-001.json --output output/typeset/page-001-v1 --background output/pages/page-001-art.png
```

Outputs: transparent `frames.png`, `inserts.png`, `balloons.png`, `text.png`; `preview.png`; `preview-display.png` reduced to intended publication width; review-only `check-overlay.png` showing exclusion areas, panel numbers, and balloon order; and `check.json`. Never publish the annotated overlay. Without `--background`, those three review images show lettering only, not source art. `novelai_batch.py build` separately creates `page-NN-display.png` and annotated `page-NN-check-overlay.png` from finished composites in the version folder. When PSD is requested, `check.json`'s `overlays_for_export_composed_psd` can populate `export_composed_psd.py`'s `overlays`. Use `--no-frames` if the art already contains borders.

Main checks include tail-less speech (warning; explain off-panel voices etc. in `no_tail_reason`), text over exclusion regions (error), balloon overlap, crossing tails, reversed reading order, content outside panel/text-safe bounds, overly long lines, small publication-size lettering, and unsupported glyphs (warnings/errors). English periods and grammatically needed commas are permitted; Japanese no-period/20-character-comma rules are not English validity conditions. Inspect the art and mark faces, hands, and essential props in `keep_out`; missing regions for a panel also warn. Use `group` for related connected balloons where needed.

Remaining errors produce exit code 1. Explain retained warnings under "Post-typesetting checks" in the [thumbnail review](../reviews/NAME-REVIEW.md). Passing automated checks does not establish readability. Actually open review images containing the art (`build`: `page-NN-display.png` and `page-NN-check-overlay.png`; standalone: `preview-display.png` with `--background`) and inspect speakers, order, face/hand overlap, and in-art text. Check easily confused letters, apostrophes, dashes, and ellipses at publication size.

## Border breaks, bleeds, and theatrical flair (production suggestion)

A **border break** extends a character/object beyond a panel border; a **bleed** extends art to the trimmed page edge. A single-panel page, borderless art, and a spread are distinct operations too; do not collapse them into "large panel."

At a character entrance, try extending a face/upper body outside the frame. Check that it does not appear to participate in the adjacent panel's event, block reading order, or interfere with text safety.

**Theatrical flair** here means exaggerated composition, pose, metaphor, effects, and border treatment that intensify an impression beyond literal realism. Before adopting it, write one sentence identifying what emotion/intensity is emphasized and where. Compare expressive gain with lost spatial information. Departure from realism is not inherently an error.

## Small white panels and withholding faces (production suggestion)

**Distinguish white panels from gutters.** A small framed white panel may read as its own beat; unframed whitespace may read as an ordinary separator. Sources reviewed here do not establish "three white panels = three seconds."

To suggest elapsed time, change time cues, light, object position, or action before/after, so the white panel does not bear the meaning alone. If it reads as a memory gap, glare, or scene change, ask readers whether elapsed time is clear. More white panels do not necessarily mean a longer perceived pause.

Without a visible face, look for legible change in body parts, a back, or nearby objects. Repeating images with nothing to infer does not distinguish missing explanation from resonance. See the panel-script example in [Immersion and Cinematic Direction](immersion-and-cinema.md).

## Original panel-script example: a beat before the answer

1. Upper-left panel. A stands left, B right. Place horizontal "Will you be here / tomorrow too?" near A. The slash is a planning note for a possible line break, not printed text.
2. Upper-right small panel. B grips a bag strap. No dialogue. The sleeve identifies whose hand it is.
3. Lower-left: one small framed white panel, tried as a waiting beat.
4. Lower-right: B in profile, with "Yeah." in a horizontal oval balloon.

If panel 4's expression is seen first, the waiting effect weakens. Compare moving it to the next page with withholding the face and showing only the reply. If the white panel looks like a scene change, replace panel 3 with a quiet background in the same place. This is an original production example; its effect has not been tested.

## Review procedure

Centralize actual lettering values and use-specific exceptions in `docs/production/DIALOGUE.md`. If unspecified, provisionally choose a dialogue baseline on the first page and inspect at publication size. Keep necessary information legible even in whispers. For long speech, compare splitting, rephrasing, and repositioning before shrinking. Carry equivalent use settings to subsequent pages while preserving justified emotional/viewpoint exceptions. Reference: [CLIP STUDIO公式・テキスト設定](https://tips.clip-studio.com/ja-jp/articles/851), retrieved 2026-09-19, covering size, line spacing, ruby, etc. No fixed use-specific values were adopted from it; the above remains a kit proposal.

1. In the panel script, check speaking order, speakers, chronology, and natural English punctuation. Check connected balloons together for sentence continuity.
2. Number panel and balloon order in thumbnails; identify unintended alternative routes.
3. At intended display dimensions, inspect letters, thin lines, padding, border breaks, centered balloon text, and word wrapping. Compare punctuation against approved text.
4. Classify issues as "misreading," "legibility," or "question about intended effect," and record page/panel IDs and a minimal fix.
5. Adjust suggestion depth to review priority 1–5. Even at low priority, fix missing text, mistaken speakers, and broken reading order.

Without finished images, distinguish what a script can establish from what it cannot. Prose alone cannot prove legible final lettering, safe print trimming, or completed visual flow.

<a id="optional-polish"></a>

## Optional Japanese source-text editing

Use only if "Japanese polishing skill" is enabled in OPTION. Default is disabled. Always continue normal typo, speaker, meaning, and source checks. At the first working session after enabling, install inside the project through [installation procedure](optional-skills.md), then apply only to the chosen Japanese source scope. A Gemini-dependent skill needs quota-use permission before installation even if the environment is available. Do not assume either third-party skill supports English prose.

1. Check source text and each character's self-reference, politeness, vocabulary, and approved voice samples. Distinguish dialogue, thoughts, narration, and project descriptions.
2. Generate candidates with the selected skill and place questionable originals alongside revisions, retaining an unchanged option. Add no new facts, experiences, feelings, hidden motives, or relationships. Prioritize user instructions and character voice over general style rules.
3. Separately compare meaning/certainty, voice, subtext, and text volume. Do not uniformly remove intentional stock phrases, repetition, or hesitation; do not overexplain thoughts. Sentence-length/ending variation is not a numerical target.
4. The main agent chooses according to project intent/instructions and records reasons in normal revision records. Respect fixed-source or candidates-only requests.
5. Update both `DIALOGUE.md` and placement for adopted text. For final English lettering, recheck [English punctuation policy](#dialogue-typesetting) and inspect alignment, emotion, reading order, and fit in PNGs. Japanese-source typography is a separate source-side concern. AI text review is not human reader testing.

This kit-specific comparison workflow dates to 2026-09-19 and prioritizes meaning, voice, subtext, and balloon fit. Third-party skill bodies are not bundled; retrieve only the selected skill within the project. See [installation procedure](optional-skills.md) for sources, pinned versions, and permission checks. Effects on actual reading experience remain unverified.

## Unverified matters and further research

- Standard emotional meanings of radial bursts: official sources support creation methods, not universal meaning.
- Relationship of white-panel count to perceived time, and reader fatigue from consecutive faces: currently user observations/production hypotheses.
- How identical thumbnails change order/surprise across print, single-page display, spreads, and vertical scrolling.
- 集英社「読みやすい画面作り」 was not used as evidence for specific drawing guidance because its text illustrations were not inspected. Its URL remains in the source register.
