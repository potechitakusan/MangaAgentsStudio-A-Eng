# Panel layout library v1 — US English edition

**[Open the picker](index.html)**. All 79 layouts are included. The initial view shows the 18 standard five-panel layouts with straight dividers.

- Each ID has an editable SVG, transparent frame PNG, numbered preview, and individual JSON.
- The [catalog](catalog.json) contains shapes, suggested uses, reading order, panel coordinates, and asset paths.
- [Production policy and usage](../../docs/production/PANEL-LAYOUT-POLICY.md) explains the variants, proportions, character breakouts, time-passage panels, and JSON format.
- Initial proportions: five panels 60%, four 15%, three 15%, six 10%. Explain these when production starts and adjust for the story and user preferences.
- By default, leave at least four intervening pages between three-tier wide layouts, with at most three uses in any rolling 20-page window. Count slanted variants together. Project settings take precedence.
- Two-panel choices include a square above or below a wide panel, equal vertical halves, and unequal sizes for an afterbeat.
- A [20-page example plan](plan-example-20.json) is included.

Panels are numbered **left to right, then top to bottom**. Time-passage panels grow or shrink in that direction. Artwork is not mirrored. Geometric IDs such as `rl`, `lean-right`, and `breakout-right` keep their physical meanings.

SVG coordinates use a 1000×1500 canvas; PNG assets are 2000×3000 pixels. Transparent frame PNGs have no numbers or colored fills. These are not native CLIP STUDIO PAINT frame-border folders, and import into that application has not been verified.

The picker and example show distribution defaults; project JSON changes do not update them automatically. Read the individual JSON for the required ID when using coordinates.
