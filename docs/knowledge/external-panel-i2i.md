# Shared Workflow for External Per-Panel Image Generation

Organized: 2026-09-26. Decision workflow adopted from Qwen production records, not a procedure proven effective across multiple models. See [Production Evidence](image-generation/production-evidence.md) for evidence/attempt counts and [Qwen-Image 2.1](image-generation/qwen-image-2.1.md) for specific symptoms/operations.

## Scope and entry point

Use when sketches, renders, or reference images condition panel art that will be assembled into pages. Begin with `manga-ai-production`; after choosing this method, use `manga-external-panel-i2i`. Excludes text-only t2i, connection-check-only requests, and new panel/page drawing with imagegen. imagegen page art follows [panel layout policy](panel-layout-policy.md).

Here, i2i broadly means image-conditioned drawing. Do not equate these features:

| Input method | Check before execution |
| --- | --- |
| Transform an initial image | Meaning of source, mask, and strength; relationship to output dimensions |
| Reference several images | Supported count, connections, and mapping of image numbers/input order to instructions |
| Specify structure with control images | Compatible model/control feature, preprocessing, strength |
| Dedicated appearance/style reference | Referenced attributes, feature combinations, count, additional fees |

Check model name/version separately from execution environment; do not invent unsupported features. Follow service documentation for input method, count, and fees. For NovelAI, see [API procedure](novelai-api.md) and [Opus conditions](ai-production.md#novelai-opus). Registering an experiment or selecting this workflow does not authorize paid use.

Whether imagegen supplies initial references/final edits, or Blender/LoRA is used, depends on project policy. Do not generalize one project's "imagegen only for initial references and pre-completion editing" restriction to all projects. Where adopted, do not evade it by relabeling new scene drawing as a reference or final edit.

<a id="c1"></a>

## C1: Panel intent supplied to drawing

Organize focal subject, visible person count, character/prop positions, before/after action, framing, face visibility, and contact points to preserve. Use [Framing and Viewpoint](manga/02-visual-direction.md) for angle/distance and [Beats, Pacing, and Information Order](manga/03-beat-pacing-timing.md) for silent pauses/information density. The generation stage translates decided intent into images/text. More angle types or hidden-face panels are not goals in themselves.

Compare the same panel under the same baseline conditions and enumerate changes. Do not infer one parameter's effect or a general success rate from another scenario's improvement or simultaneous changes to multiple conditions.

<a id="c2"></a>

## C2: Separate what each input conveys

| Material | Primary information | Information decided elsewhere |
| --- | --- | --- |
| Sketch / Blender render, etc. | Framing, positions, action, depth relationships, contacts | Final rendering of faces, hands, clothes, background |
| Character reference | Face, hairstyle, costume, colors, identifying traits | This panel's pose, gaze, emotion |
| Prop reference | Shape, pattern, colors, material | On-screen size, orientation, placement, contact |

This assigns production responsibilities; it does not guarantee the generator separates them automatically. Translate roles into image numbers/order/strength/masks per model. Do not demand multiple inputs from a feature that only accepts one.

Select necessary references and record images actually attached/connected. A filepath in a prompt is not an image input. For local corrections, decide whether finished art already supplies enough information and compare removing unnecessary references. Verify effects per model.

<a id="c3"></a>

## C3: Composition references and cropping room

In Blender, place necessary people/objects and check gaze, hands, contacts, and occlusion before rendering. Distinguish people present in the scene from people visible in the render. Specify how far simplified faces/contours should be redrawn. Treat effects of unwanted people/face fragments as model-specific observations.

For later cropping, preserve limb/tool extremities and balloon space. Wider views reduce subject pixels, so balance margins against necessary detail. Do not make 50 mm, 85 mm, or 75% cropping universal constants. Apply the same checks to non-Blender sketches.

<a id="c4"></a>

## C4: Prototype, correct, and select

Inspect actual images at representative difficult points: composition, person count, appearance, hand/prop contact, and instructions withholding faces. Verify supported input methods in that environment before scaling to all panels.

Decide whether a mismatch belongs in the composition reference, unnecessary references, prose, model settings, local output editing, or cropping. Correcting only a face cannot approve a wrong framing/action. Do not assume repeating identical instructions improves results. Retry counts/costs/failure handling follow service rules and current permission scope; reconsider conditions if improvement stops or a limit is reached. Never automatically resend a request with unknown result/consumption.

<a id="c5"></a>

## C5: Cropping and page review

Under [Page Settings](page-layout.md), distinguish requested panel dimensions, actual dimensions, adopted crop, and assembled-page dimensions as width × height. A panel's actual size is not the whole page size. Do not automatically crop to a fixed percentage; inspect faces, hands, action edges, space, and required publication pixels. For non-imagegen art, add lettering/balloons afterward. Check for unintended text/balloons, and stray borders when borders are meant to be separate.

After using a finishing model or LoRA, recheck left/right, clothes, expressions, tools, and concealed faces. Beautiful isolated panels still need correction if handoffs, gaze, or action do not connect across the page. Judge compositional improvement separately from rendering quality.

Return to [Readability](japanese-manga-readability.md) for lettering, [Production Workflow](manga/08-workflow-review.md) for read-through/revision, and [Handoff](psd-handoff.md) for PNG revision confirmation and instructed PSDs. Positive impressions alone establish neither "no revisions" nor a PSD instruction.

<a id="c6"></a>

## C6: Reusable records

Record the following as needed in ordinary production/experiment records. Do not make a new mandatory form a prerequisite to starting.

- Service, model/version, execution environment such as nodes, available identifiers/settings.
- Panel intent, actual input images/order, actual submitted text, requested/actual dimensions.
- Adopted art, changes, rejected/failed results, each retry's conditions, crop region, postprocessing.
- Status (untested, observed, conditionally reproduced, candidate for shared guidance, rejected), evidence date, applicable conditions, counterexamples, uncertainties.

Distinguish a planned reference's existence from actual input and exclude secrets. If organizing records without newly viewing images, cite past visual reviews instead of claiming current revalidation. Keep project-specific assets/personal settings out of shared templates.

Consider generalizing methods verified on other models with input method, targets, and limits specified. Different nodes for the same base model are not independent cross-model validation. Additional feedback records/kit incorporation follow the [on-request procedure](feedback-workflow.md).
