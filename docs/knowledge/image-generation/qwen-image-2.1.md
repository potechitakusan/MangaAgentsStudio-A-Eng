# Observations from Qwen-Image 2.1 Panel Production

## Model and inputs covered

The records identify Qwen-Image 2.1 with ComfyUI's `TextEncodeQwenImage21`. E3's main model was `qwen_image_2.1_int8_convrot.safetensors`. This name alone does not establish distributor, identical weights, or compatibility. Check model identifiers, node versions, and input/output specifications when using it. Treat it separately from [Qwen-Image-Edit-2511](../ai-production.md#4-handling-qwen-image-edit-2511); 2511 official sources do not establish 2.1 behavior.

See [per-panel i2i](../external-panel-i2i.md) for shared production decisions. The following are symptoms, operations, and limits of the actual setup, not specifications reproduced across every Qwen version.

## Q1: Image numbers and roles

Separate image inputs were connected to `TextEncodeQwenImage21`'s `images.image_1`, `images.image_2`, etc., matching actual order to `<image1>` and related instructions. Composition came first, followed by needed character/object references. Three E1 runs retaining another character's description in a solo panel were excluded from comparisons.

Records using `resolution=0` based aspect ratio on the first image; node rounding required checking actual dimensions afterward. Do not transfer this setting unchanged to another Qwen node/API. If a character reference becomes first, check whether both role and size baseline change. Corresponds to [C2](../external-panel-i2i.md#c2) and [C6](../external-panel-i2i.md#c6).

### Example input instruction

The following is an untested English localization of a source-skill example, with project-specific information removed. Match image numbers, people, and appearance to actual inputs/panel. Equivalent effects between language versions have not been tested.

```text
Two people are visible. Character A on the left returns a prop to character B on the right. B looks at A in surprise.
Use <image1> for framing, character positions, action, room layout, and contact between the prop and hands.
Redraw simplified faces, hands, and clothing naturally, leaving room for cropping.
Use <image2> for the face, hair, and costume of A on the left; use <image3> for B on the right.
Do not copy the standing poses, expressions, or backgrounds of character references.
Use <image4> for the prop's shape, colors, and material; match its size, orientation, and contact to <image1>.
Draw a color comic image. Do not add text, balloons, borders, or reference sheets; these are handled separately.
```

This communicates roles, not a guarantee of complete control. Instructions separating borders/text apply only when that production method is adopted.

## Q2: Confusing multiple characters' left/right positions

E2 reversed character positions. Improvement followed ordering references screen-left to screen-right, explicitly naming positions, and rerendering without occluding objects. Consider checking all three when positions mix. Several conditions changed, so reference order alone is not a guaranteed fix. Corresponds to [C1](../external-panel-i2i.md#c1), [C2](../external-panel-i2i.md#c2), and [C4](../external-panel-i2i.md#c4).

## Q3: Completing unwanted faces/people

In E2 prop close-ups, a face fragment in the render could cause a completed face despite "zero people" text; render adjustments and final cropping removed it. E3 adopted a regenerated person-free overhead shot after removing common costume/body descriptions, but the seed also changed, so this does not isolate wording.

For object-only panels, separately check character descriptions, character references, and people remaining in composition images. Do not assume "zero people" alone suppresses them. Corresponds to [C1–C4](../external-panel-i2i.md#c1).

## Q4: Inheriting reference poses/expressions

E1 aligned appearance readily but retained standing posture, shallow water, and calm expressions. These persisted with upper-body references, so narrowing the reference crop is not an established solution.

Some edits improved after using only the finished image with aligned appearance, removing unnecessary character references, and giving short action/expression instructions. E2 corrected a book-presenting pose into reading. Conversely, E1 sometimes changed viewpoint/background or retained forward leaning. Distinguish whether appearance needs re-specification or only action needs correction, and check composition retention too. Corresponds to [C2](../external-panel-i2i.md#c2) and [C4](../external-panel-i2i.md#c4).

## Q5: Rear views, hidden faces, and detail close-ups

E3 adopted a rear-reference result preserving hairstyle, colors, and back orientation. Panels hiding a face behind an object used no frontal character reference; costume was specified in text. A result drifting toward white clothing was corrected using only the finished image, with eyes/nose/mouth verified hidden. This was not an isolated front-reference-on/off comparison.

A requested eye-only view reverted to a whole face; a crop retaining 40% of original width removed mouth/shoulders. Full-body action retained 96% of the original width, and an object-result panel retained 94% of the original width, protecting movement edges. These percentages describe those selected images. Choose references appropriate to visibility/focal detail and crop while retaining necessary pixels. Corresponds to [C1](../external-panel-i2i.md#c1), [C3](../external-panel-i2i.md#c3), and [C5](../external-panel-i2i.md#c5).

## Q6: Retaining crude Blender shapes/materials

E2 sometimes retained a 3D look when asked only to preserve contours/placement. Records report improved hand-drawn backgrounds after separating render-derived positions/action/room layout from redrawn face/hand/clothing/background surfaces. Distinguish spatial relationships to retain from shapes/surfaces to redraw; do not strongly demand both exact preservation of every contour and natural redrawing. Corresponds to [C2](../external-panel-i2i.md#c2) and [C4](../external-panel-i2i.md#c4).

## Q7: Specify correction scope precisely

E2's duplicated ribbon improved with a short instruction on the finished image to preserve the upper edge and remove only the lower one. E1 water-level attempts separated fixed and changed subjects, such as retaining the surface while submerging the character to the shoulders.

Untested local-edit example: "Remove only the duplicate area around the hands in `<image1>`. Preserve the upper edge, hand contact, framing, background, clothes, and other characters." Compare framing, background, object locations, and other people when adopting results; separate rendering improvement from continuity preservation. Corresponds to [C4](../external-panel-i2i.md#c4) and [C5](../external-panel-i2i.md#c5).

## Settings and next verification

E3 used 25 steps, CFG 1.0, euler / simple, denoise 1.0. These were not comparative tests of recommended settings. Do not equate source-image transformation i2i with reference conditioning in this setup. ANIMA_LORA's 12 steps, CFG 2.5, euler_ancestral / simple, and denoise 0.12 were a separate finishing stage, not properties of Qwen itself.

Next, compare the same panel/baseline changing only reference order, reference presence, or another single variable, and verify other models/versions. Current records do not establish general success rates or model rankings. Add model-specific documents for new models rather than duplicating shared workflow or authoritative connection/fee guidance.
