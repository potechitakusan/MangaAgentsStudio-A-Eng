# Observations from NovelAI V5 panel asset generation

## Model and inputs covered

The model was `nai-diffusion-5-full`, with 23 steps, `k_euler_ancestral`, scale 5, and one image per request using ordinary t2i. No reference or initial images were used. These color slice-of-life comics kept `year 2025` and the quality terms `masterpiece, best quality, highly detailed, anime style, very aesthetic` fixed. Evidence: [E4](production-evidence.md#e4) and [E5](production-evidence.md#e5). Organized on 2026-09-30.

Use [NovelAI production](../novelai-composed-production.md) as the authoritative guide for request writing, batch generation, and comparison, and [NovelAI API](../novelai-api.md) for connections and costs. The symptoms, operations, and limits below concern V5 Full under these conditions. Do not transfer them to V4.5 or earlier, Curated, or image inputs as verified facts.

<a id="n1"></a>

## N1: Removing relationships can change the action even when names remain

Even with character and object names retained, removing hand/object contact, the operating hand, the inside of a bag, the separate roles of the left and right hands, mutual gaze, a rear viewpoint, or distance from the ground weakened the target depiction across all three seeds in E4. A water bottle was placed on a seat instead of held; even with crouching wording retained, a ball moved away from the ground.

In some cases with unchanged scores after relationship wording was removed, character coordinates, viewpoint, or negative prompts supported the same meaning. When shortening, read the main prompt, character prompts, coordinates, and negative prompts together; do not remove the last remaining expression of the relationship. This corresponds to item 10 in [Request prompt construction](../novelai-composed-production.md#prompt-writing).

<a id="n2"></a>

## N2: Closer framing makes instrument and hand defects more visible

Closer framing of hands at a keyboard magnified defects such as black keys arranged almost every other key and inconsistent sizes or skin colors between one person's hands. Changing a four-hand piano duet to an oblique view produced five, six, and five arms/hands. Pressing a single key with one finger and relaxed fingers were not achieved across three seeds with one-hand, overhead, or more side-on versions.

When instrument or hand detail is not the subject, retaining the wider original to show both people's positions and their shared tool may lose less information. If fingering or playing technique is central to the request, treat it as unresolved for this model and these conditions, and consider another method.

<a id="n3"></a>

## N3: Adding shape descriptions does not always produce the intended object

In some examples, adding more wording to describe an upright piano's shape produced a narrow box or a flat, board-like instrument. The project changed the instrument to a grand piano because its type was not a requested condition. This was a production-setting change; it does not mean an upright piano was successfully generated. If the object's type is central to the request, do not count changing the setting as success.

After changing a setting, check whether negative wording excluding the new setting, such as terms avoiding a grand piano, remains in the request. Four panel requests in E5 retained old negative wording.

<a id="n4"></a>

## N4: Container and tool structures can change into different objects

Lunchbox dividers, lids, and hinges, and the height and color of a ball basket's grid were prone to structural changes when their presentation changed. Even if eating progress or cleanup reads clearly, compare the object with neighboring panels. If it no longer reads as the same object, reduce the number of panels showing its state or retain the original.

<a id="n5"></a>

## N5: Effects of quality and style terms were not isolated

E4 and E5 kept quality terms and `year 2025` fixed; they do not establish individual terms' effects or relative merits. Earlier exploration in the same project (record NAI-R03, one image per condition) included a comparison changing only the presence of `high complexity`. Hair and clothing shading increased, but face tilt, hand position, and button count also changed. Treat this as a candidate to compare before using it in panels requiring consistency, rather than a general rule. Distinguish officially documented special tags from words added as natural language, such as `highly detailed` and `anime style`.

## Further verification

Additional seeds for a few important cases, transfer to other characters/scenes/angles, removing two expressions simultaneously, comparisons changing only quality terms, independent human evaluation, and comprehension evaluation when reading neighboring panels have not been performed. Verification of methods using image inputs remains in NAI-VERIFY-01.
