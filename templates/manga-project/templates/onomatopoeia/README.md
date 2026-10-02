# Reusable English sound-effect assets

Transparent monochrome lettering for comics and illustrations, with any production tool. The US English edition contains 38 expressions/variants × 3 styles = 114 images. Open `index.html` to search offline by meaning, wording, use, intensity, style, and repetition count.

The English lettering is rendered from original geometric vector strokes using `scripts/build_english_sfx.py` in the kit. Editable SVGs are included under `svg/`. No third-party font file or text cut from another comic is included. Styles retain the upstream IDs: `block` (bold geometric), `burst` (slanted impact), and `drybrush` (textured slant). These English styles are adaptations, not reproductions of the Japanese NovelAI-generated glyphs. The Japanese source used baan-v2, doon-v1, and gogogo-v1 as style references and assembled approved single glyphs for repeated effects; that is historical provenance, not how these English images were made.

IDs remain stable for update tracking. For example, `block-doon` now displays `BOOM!`, and `block-puru` displays `TREMBLE`. `source_text_ja` records the original Japanese wording for comparison. Use the current `text` and `meaning_en`, not the romanized ID, to select an effect. Fields ending `_ja` are deprecated compatibility aliases containing English descriptions in this edition.

The catalog's relative paths point to lossless WebP images with real alpha and grayscale visible pixels, at most 256 pixels high. Original high-resolution Japanese artwork is not distributed as an English asset. Use the SVG for larger sizes, or generate suitable new lettering and inspect the result if more detail is needed.

## Select wording for the scene

Japanese mimetic words are not literal one-to-one English sound effects. The catalog gives a working English expression plus context and alternatives. A quiet action can use an action label or no lettering at all. Preserve the scene's meaning and intensity.

| Intended action or state | Stable suffix | English default and use |
| --- | --- | --- |
| Small continuing tremor | `puru` | `TREMBLE`; one label can express ongoing motion |
| Continuing crowd murmur | `zawa` | `MURMUR`; repeat only when the pacing calls for it |
| Lively conversation | `wai` | `CHATTER` |
| A strong heartbeat | `doki` | `THUMP`; repeat for successive beats |
| Repeated light contact or fluttering | `pata` | `PAT`; choose `FLAP` for wings if appropriate |

When repeating an effect, keep its parts close enough to read as one continuing sound or action from left to right. Placing unrelated copies on opposite sides of a character does not automatically express repetition. Reserve space before placement; keep faces, dialogue, and contact points clear. Check the actual text and spacing in the PNG. Honor an intentional interrupted rhythm when requested.

Do not mechanically duplicate every effect. The source edition normally paired Japanese `puru` to express an ongoing tremor; English `TREMBLE` does not need that duplication. Repeated assets already contain four to seven whole English expressions. `text`, `grapheme_count`, and `repeat` describe what is in the image, not how many copies to place. The repeat unit may therefore be a whole English word. Read `placement_hint_en` together with the scene.

The Japanese placement policy was recorded on 2026-09-21 from the author's production request, without an external source. The English adaptation was made on 2026-09-30. The source selection included frequent terms from a conditional corpus study; it never established universal top-20 status, and no English frequency ranking is claimed.

## Repeated effects

Repeated variants use four through seven whole English words, such as `RUMBLE RUMBLE RUMBLE RUMBLE`. Choose the count and placement to convey duration, rhythm, and intensity in the scene. The stable legacy IDs identify source families; their Japanese syllable counts do not prescribe English syllable counts. Shorten a long effect when it competes with dialogue or obscures the artwork.

## Recoloring and PNG conversion

Use the supplied image directly for monochrome output. Create colored versions in the individual project, not in the shared template. Python and Pillow are required.

```powershell
python scripts/recolor_onomatopoeia.py --input templates/onomatopoeia/images/block-baan.webp --output output/onomatopoeia-colored/block-baan.png --ink-color '#C02030' --white-color '#FFF2D6'
```

Black and white endpoints can be changed independently; grays interpolate between them. Alpha stays unchanged: this does not turn white into transparency. Use image editing for complex shape changes. For applications that do not accept WebP, run `python scripts/export_onomatopoeia_png.py block-baan` to convert to PNG.

[CC0 1.0 terms](LICENSE.md) apply to the designated images and original metadata: commercial use, modification, and redistribution are permitted without credit. This does not cover third-party rights, tools, or corpora.
