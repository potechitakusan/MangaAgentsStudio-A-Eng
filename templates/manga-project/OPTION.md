# Comic production options

Provide characters, synopsis, and page count to produce an online comic through PNG without additional configuration. Edit "Current setting" or describe changes in conversation. These are distribution defaults; answering every item is unnecessary.

| Item | Current setting | Alternatives and notes |
| --- | --- | --- |
| Publication format | Single Web pages, left to right | Portrait, roughly 2:3, adapted to the tool. Spreads, horizontal reading, vertical scrolling, and named platforms are possible. White background, RGB/sRGB |
| Generation dimensions | Match the tool; verify actual dimensions afterward | Desired width × height may be specified. Separate from final dimensions |
| NovelAI Opus generation | No Anlas consumption; one image, at most 28 steps (V5 initially 23; V4.5 and earlier 28); no extras such as references | Only for NovelAI Opus. Confirm 0 Anlas and sufficient V5 allowance before execution; wait for recovery if insufficient. Paid use needs explicit scope authorization |
| Frame-layout dimensions | Same as the full-page generated image | Working page for art, frames, and text. Use provisional dimensions before generation, then compare actual output. For panel generation choose destination-page dimensions |
| Final PNG dimensions | Same as frame layout, no enlargement | Example: "Only final PNG: 2000 px wide × 3000 px high." Does not guarantee native generation pixels. Adjust placement if ratios differ |
| Basic-frame margins | Scale with page dimensions: 120 px each side at reference 2000 × 3000 px | Distance from edges. Left/right scale by width; top/bottom by height. Fixed values such as "left 80 px" allowed. Overflow is not universally forbidden |
| Text-safe margins | Scale with page dimensions: 160 px each side at the same reference | Keep essential text away from edges. Scale on resize; fixed px allowed |
| Frame stroke | Scale with page dimensions: 10 px at the same reference | Use smaller width/height scale factor. Fixed values such as 6 px allowed |
| Basic-frame guide | Hidden | Enable a separate rough-storyboard/editing guide. Never include in publication PNG |
| Japanese polishing skill | none | Disabled by default; Japanese source text only. For explicitly requested Japanese work: `humanizer-jp` (no Gemini) or `japanese-natural-writing` (Gemini). Unqualified "enable" for that work selects humanizer-jp. Install at first project session when enabled. Gemini needs quota consent before installation. Neither is claimed to polish English |
| Legacy Japanese polishing targets | Japanese source dialogue and inner thoughts only | Only if legacy skill enabled. Explicit Japanese descriptions/synopses also possible. Ordinary typo, speaker, and meaning checks always apply |
| Panel templates | Use as a rule; custom layouts allowed for staging with recorded reasons | "Use" means the same; "required" forbids Codex-selected exceptions; "do not use" allows free design and disables proportions/repetition/diagonal guidance below. Always decide layout/order before artwork generation |
| imagegen generation unit | Entire page with numbered layout reference | Individual panels if needed. Custom layouts also require numbered images and panel content. Not universal for NovelAI/other tools |
| Text and balloons | imagegen: within the image; other tools: add after drawing | No startup answer needed. Separate imagegen lettering allowed by request/correction need. Reference-only/local-fix imagegen use does not change method |
| Panel-count proportions | Five 60%; four 15%; three 15%; six 10% | Example: five 40%, four 30%, three 20%, six 10%. Aim for 100%; adjust for large/two-panel pages and staging |
| Three horizontal tiers: repetition | Four intervening pages minimum; at most three in any 20 consecutive pages, tilted variants included | Change gap/window/limit; unlimited allowed |
| Diagonal five-panel frequency | Aim for at most once in any 20 consecutive pages | Change count; unlimited allowed |
| Dialogue and monologue direction | Horizontal English, left-to-right/top-to-bottom reading | Explicit scene-specific exceptions allowed |
| Dialogue alignment | Centered in balloons | Center each line, preserve word boundaries and inner padding. Record exceptions/reasons in lettering settings |
| Dialogue/narration punctuation | Natural US English punctuation | Periods, commas, apostrophes, and expressive punctuation follow meaning. No Japanese 20-character restriction. See [Lettering and punctuation](docs/knowledge/japanese-manga-readability.md#dialogue-typesetting) |
| PSD creation | If not instructed, ask and wait | Create / do not create / defer. Do not re-ask existing instructions. Create after PNG revision confirmation |
| CBZ creation | Explicit requests only | Create / do not create |
| Video trials | Explicit requests only | Try / do not try |
| Feedback records | Only when requested | Milestone recording / do not record. Ordinary progress, corrections, and validation recorded separately |

## Applying settings

- Actual generation at 1024 px wide × 1536 px high gives default frame layout and PNG at 1024 × 1536 px. This illustrates dimensional relationships. Reference 2000 × 3000 px scales margins/strokes; it is not a generation/export specification.
- See [Generation without Anlas](docs/knowledge/ai-production.md#novelai-opus) for Opus conditions/official sources. V5 has a replenishing allowance; references/editing have separate cost conditions. Dimensions and steps alone do not establish free use.
- Print-only [PRINT-OPTION.md](PRINT-OPTION.md) is disabled by default; Web work need not read/complete it.
- Frame settings: [Page dimensions/basic frame](docs/knowledge/page-layout.md). Polishing installation/consent: [Legacy Japanese skills](docs/knowledge/optional-skills.md). Ask before installing missing Git; available Gemini access does not waive quota consent.
- PSD request example: "After PNG confirmation, create a PSD with art, balloons, and text separated." Separately produced elements are movable; raster text is not directly editable as strings. Include dialogue source text.
- Missing file, deleted item, or blank setting uses the item's default, also stored in [Applying options](docs/knowledge/project-options.md). Explicit conversational instructions prevail.
- Explain main adopted settings at startup; proceed if no changes are requested.
- Inspect later edits at startup, resumption, or the next stage and clarify intent. File/item deletion restoring defaults is treated the same.
- Defer applying changes to affected work until answered. Do not re-ask edits reflecting instructions already given in conversation.
- PNG revision confirmation and external publication/transmission instructions are separate. These settings alone do not confirm unreviewed PNGs or authorize publication.
