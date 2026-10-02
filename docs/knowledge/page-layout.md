# Web Page Dimensions and the Basic Frame

Updated: 2026-09-20. Production settings for page comics read online. Values are kit starting points, not mandatory platform specifications or guarantees of reader response.

<a id="text-finishing"></a>

## Finishing lettering and balloons

Production policy adopted 2026-09-29. Do not ask for a lettering-method decision when creating a project. Before drawing its pages/panels, choose from the actual drawing method and briefly explain it.

- **imagegen:** normally generate text and balloons within the image, then compare to the plan and approved exact text. Add text/balloons separately afterward when preferred or needed for corrections.
- **Other methods:** generate art without lettering/balloons, reserve room, then add them through separate typesetting. This applies to external environments including NovelAI and Qwen. Follow the [typesetting script procedure](japanese-manga-readability.md#typeset-script).

Using imagegen only for character references or local art corrections does not change the separate-lettering workflow for externally generated art. Follow each method's existing border-placement and generation-unit procedures.

## Generation, placement, and export

Given characters, synopsis, and page count, produce single-page comics read left to right and top to bottom. Use a white background, PNG, and screen-oriented RGB/sRGB; monochrome art may use this export too. Determine dimensions in three stages. Do not require answers to every field; Codex may provisionally choose supported dimensions for the tool.

| Stage | Dimensions described | Default |
| --- | --- | --- |
| Generation size | Requested width × height and actual generated width × height | Choose supported dimensions, aiming for portrait 2:3. Record requested and actual values separately |
| Frame placement size | Working page for art, borders, and lettering | For whole-page generation, match actual generated dimensions |
| Final PNG size | Page image delivered to readers | Match placement size; use another export size only when specified |

For example, a 1024 × 1536 px result normally means 1024 × 1536 px placement and final PNG. This is illustrative, not a fixed built-in generator output size. "Final PNG at 2000 × 3000 px" specifies export, not guaranteed generation dimensions. State width × height and the relevant stage, not just "3000 px."

For whole-page generation:

1. Check supported tool dimensions. For imagegen, follow [panel layout procedure](panel-layout-policy.md): choose a template or artistic custom layout and actually supply the numbered reference and each panel's content. Place provisionally at planned dimensions; do not pass unsupported arbitrary sizes.
2. Read the saved output's actual dimensions. Reposition borders accordingly rather than blindly overlaying the planned-size frame. Visually check that generated panel divisions match.
3. Record the first adopted placement size as the project's common `canvas`. For later images of different dimensions, distinguish proportional scaling from placement/cropping changes. Preserve originals.
4. Finish art, balloons, approved lettering, and necessary borders. Check elements generated together by imagegen; separately composite any missing/revised elements. Normally export at the same size.

For per-panel generation, each panel's image dimensions differ from the assembled page's. Choose the page size from publication needs and pixels available within panels, then set `canvas`. Do not treat one panel image's dimensions as the whole page's actual dimensions.

If a publication destination is named, check its official size, file-size, and format conditions and apply them to a publication copy. Record actual color settings and export methods. Increasing pixel count alone does not create original-art detail. A person decides external posting.

## Scale margins and line widths with page size

Bundled border PNGs are 2000 × 3000 px. Preserve this as the source-asset and conversion baseline, not the default generation/final-PNG size.

| Setting | At 2000 × 3000 px | Conversion to placement size |
| --- | --- | --- |
| Basic frame margins | 120 px on all sides | Scale left/right by width and top/bottom by height |
| Text-safe margins | 160 px on all sides | Scale left/right by width and top/bottom by height |
| Border stroke | 10 px | Use the smaller width/height scale |
| Review guides | 3 px stroke, 16 px dash, 10 px gap | Same scale as borders |

At 1024 × 1536 px, the scale is 0.512: basic margins 61.44 px, text-safe margins 81.92 px, and stroke 5.12 px. Keep fractional coordinates in calculations/SVG and render at rasterization. With another aspect ratio, use separate horizontal/vertical scales but one stroke scale. Reposition art and text rather than stretching them unevenly.

Configure in `config/page-layout.json` (version 2); Codex applies adopted `OPTION.md` values.

- `generationCanvas`: requested generation dimensions. `null` means fit the tool. Setting it does not run image generation through the layout process.
- `canvas`: placement width/height. `null` means use actual generated dimensions. Before generation, use requested dimensions or `--canvas` provisionally.
- `exportCanvas`: final PNG dimensions. `null` means match placement. Setting it alone neither resizes images nor saves PNGs.
- `referenceCanvas`: margin/stroke baseline, default 2000 × 3000. `basicFrame`, `textSafeArea`, and `frameStroke` use this baseline. Recalculate from it on every resize; never write converted values back as baseline values.
- `fixedPixels`: only fields to hold at fixed placement pixels, e.g. `{"basicFrame":{"left":80},"frameStroke":6}`. Other margins scale automatically. If the whole page is resized at final export, fixed values scale with the composite too.
- `showGuide`: review-only guide visibility. Exclude guides from published PNGs.

Version 1 remains readable. Its existing `canvas` and pixel margins/strokes are retained; changing dimensions with `--canvas` uses the old `canvas` as the baseline. When migrating an existing project to version 2, retain previous dimensions in both `referenceCanvas` and `canvas`, with original margins/strokes. Do not change `canvas` to `null` without an instruction to adopt automatic dimensions.

## Frame placement and guides

The basic frame is a placement reference, not a clipping mask. Art may extend beyond it when intent and reading order support that choice. Distinguish it from panel dividers, page edges, and lettering guides.

Run from the project root. Only Python 3.10+ standard library is required.

```powershell
# Match a whole-page PNG's actual dimensions without changing its contents:
python scripts/prepare_page_layout.py --template P5-212-equal-normal-straight --page-image output/page-001-art.png --output output/layout/page-001-v1 --guide
# Provisional pre-generation layout or an assembled page for per-panel art:
python scripts/prepare_page_layout.py --template P5-212-equal-normal-straight --canvas 1024 1536 --output output/layout/page-001-v2
```

Placement-size precedence is `--canvas` → configured `canvas` → `--page-image` actual size → `generationCanvas`. If all are absent, prompt for a size decision rather than silently using 3000 px. Record actual generation size as unverified when no image was supplied.

- `frames.svg`: transparent panel borders at placement dimensions, suitable for final compositing.
- `guide.svg`: transparent guides produced only with `showGuide: true` or `--guide`. Blue indicates the basic frame, purple the text-safe area, and brown the border-breaking character region. Overlay separately in the editor and toggle visibility. `--no-guide` suppresses generation regardless of settings.
- `layout.json`: converted coordinates, margins, strokes, requested generation size, actual size (`null` if unverified), placement size, final PNG size, and scale factors. The 79 original templates and configuration are unchanged.

`prepare_page_layout.py` places existing template IDs; it does not design custom layouts or output numbered reference PNGs. Its `guide.svg` contains basic-frame and similar guides, distinct from the catalog's numbered `guides/ID.svg`. For imagegen references using revised or custom layouts, add reading-order numbers to the coordinates and separately render a reference PNG with an available tool. Custom layouts retain project page dimensions, margins, and stroke settings.

When rasterizing SVG for reference/compositing, export at its declared width × height. Do not overlay a bundled 2000 × 3000 px border PNG unconverted on differently sized art. This tool handles placement only; SVG rasterization, art scaling, image generation, and final compositing belong to their production stages.

This process rejects differing aspect ratios from generated image to placement or from placement to final PNG. Decide on padding, cropping, or repositioning, perform that adjustment separately, then use the adjusted image/layout dimensions.

Aspect-ratio conversion affects borders and effect regions only. Reposition art/text rather than distort them. Erase borders for a character breaking out of a panel along the actual character silhouette. The tool does not automatically judge lettering readability or the artistic effectiveness of border breaks. Use a new output directory each time to avoid reusing old guides.

The tool preserves template reading order. English templates use left-to-right, top-to-bottom order. If another reading direction or vertical scroll is chosen, redesign placement/order and do not require unsuitable existing templates. Do not repeatedly ask approval for identical dimensions merely to verify actual size or apply instructed settings.

## Export checks

For a different export size with the same aspect ratio, scale art, borders, and text together or redraw/reposition all elements at the same scale. This is also where a 2000 × 3000 px final PNG is produced. Record method, original/target dimensions, and scale in `docs/production/PSD-HANDOFF.md`.

Final PNGs include art, balloons, approved text, and necessary borders. Do not add unrequested titles, page numbers, logos, or signatures; filenames/records show order. Do not duplicate already generated borders/text without inspection. `guide.svg` and numbered catalog previews are references, not final compositing layers. Remove leftover numbering, color coding, or guides from generated art too. Visually confirm that toggling guides does not move art/border coordinates, lettering is not clipped at page edges, and the page reads at publication-equivalent reduced size. If PSD includes guides, put them on a separate hidden layer such as "Guides" and verify they remain absent from the reopened composite.

Use the project's [PRINT-OPTION.md](../../PRINT-OPTION.md) only if print is selected.

## Evidence and limitations

- Confirmed fact: [CLIP STUDIO公式・基本的なコマ枠の作り方](https://tips.clip-studio.com/ja-jp/articles/610) describes basic-frame sizes, margins, and border placement. Retrieved 2026-09-19; scope is that application's basic-frame settings.
- Production suggestion: separate generation/placement/export dimensions and convert borders to actual size. Baseline dimensions and 120 px basic margins preserve existing-asset compatibility. The 160 px text-safe margin and stroke handling under unequal scaling are kit-specific starting points.
- Unverified: improved reader responses from these margins/pixel counts, compatibility with every generator/platform, or suitability for print. Dimension settings alone do not prove generated art follows border coordinates.
