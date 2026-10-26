# Shared Knowledge for AI Comic Production

## 1. How to judge consistency

**Production suggestion:** score "same character," "same style," and "same composition" separately. Similar faces do not preserve continuity if clothing changes; repeating one pose does not create acting.

| Axis | Keep stable | May vary with the scene |
| --- | --- | --- |
| Character identity | Face outline, eye shape, bangs, hair length, build, identifying accessories | Expression, gaze, angle, action |
| Costume continuity | Collar, sleeves, patterns, fasteners, asymmetric markings | Wrinkles, wind/motion deformation, story-specified dirt |
| Art style | Line weight, detail density, shading, solid blacks, tone grain | Emotional stylization and deliberately specified density |
| Spatial continuity | Height differences, holding hand, positions, light source, background landmarks | Camera position, framing, perspective |

Define 5–8 must-retain traits, costume version, left/right markers, and permitted stylization in the character register. Do not judge by general image atmosphere alone. When a face is hidden, mark relevant identity criteria N/A and judge hair/costume instead.

## 2. Methods and applications

| Method | Scope confirmed in official material | Production proposal / unverified aspects |
| --- | --- | --- |
| Fixed prompt and seed | NovelAI permits seed-based comparisons, but changing clothing instructions can change other elements even with the same seed [A04] | Standardize comparison conditions first; seed is not a character ID |
| Character reference image | NovelAI Precise Reference can reference character, style, or both; at the check date it was V4.5-only and incompatible with Vibe Transfer [A03] | Start with one character. Blending references is not the same as correctly distinguishing two characters |
| Qwen-Image-Edit-2511 | Developer reports improved identity and multi-character editing [A01] | Candidate for editing approved character sheets into new angles/poses; measure comic-art performance. Distinguish from Qwen-Image 2.1 records |
| LoRA | Adapts by training limited additional weights rather than the whole model [A05] | Consider character/style LoRA after observing recurring reference-editing failures. Do not prescribe universal image counts, training time, or VRAM |
| ControlNet | Guides structure with edges, depth, pose, and other conditioning images [A07] | Candidate for large gestures, positions, and limb structure; match model family and preprocessing |
| IP-Adapter | Developer supplies image conditioning and model-specific implementations such as SD1.5/SDXL [A08] | Candidate for referenced style/appearance. A file's existence does not establish compatibility with any model |
| Built-in image generation/editing | Operational choice under user policy | imagegen page art normally uses whole-page generation with a numbered layout image and every panel's content. Follow [panel layout procedure](panel-layout-policy.md) for artistic exceptions, per-panel alternatives, and output checks. Also useful for samples/local edits; consult the available imagegen skill/tool instructions when executing |

Source IDs link directly to references below. Evaluate both identity and acting before/after adopting any method.

### External per-panel image conditioning

Choose a generation approach through `manga-ai-production`. For image-conditioned panel art, use `manga-external-panel-i2i` and [shared C1–C6](external-panel-i2i.md#c1) to translate artistic intent into inputs, then corrections, cropping, and page review. Initial-image transformation, multiple-image references, control images, and dedicated appearance/style references are distinct features; do not equate their image order, strength, or cost.

Keep model-specific symptoms, operations, and input examples in [Qwen-Image 2.1](image-generation/qwen-image-2.1.md), and comparison conditions, attempt counts, and limitations in [Production Evidence](image-generation/production-evidence.md). The shared procedure is a production proposal, not a verified cross-model effect. Return to service-specific guidance such as [NovelAI API](novelai-api.md) for connections/costs. Do not force this method onto t2i or whole-page imagegen.

## 3. Character sheets

NovelAI's official guidance recommends a neutral full-body figure on a simple background, with face close-ups/multiple views as needed. Example tags include `multiple views`, `turnaround`, `reference sheet`, and `no text`. Excessive reference strength may also freeze angles/expressions. [Precise Reference](https://docs.novelai.net/en/image/precisereference/) (2026-09-12; NovelAI V4.5).

**Production suggestion:** keep the following in the project and have the main agent select one approved version.

1. Baseline front, three-quarter, side, and rear full-body views. Visually compare accessory placement on both sides.
2. Face close-ups comparing neutral, smiling, and surprised expressions. Do not distribute contradictory generated angles as references.
3. Costume/accessory details. Record reference colors for color art, or values/tones for black-and-white art.
4. Reference version/hash, adoption date, and change reason. Keep rejected images out of the approved-reference folder.

Details become small on a composite sheet, so compare face references for close-up panels and full-body references for full-body panels. Do not only edit each new output from the previous output; regularly return to approved baselines to detect cumulative drift.

## 4. Handling Qwen-Image-Edit-2511

Input `QwenImageEdit2511` means official **Qwen-Image-Edit-2511**. Do not silently reinterpret it as 2509 or another Qwen model. "Built-in LoRA" in the official model card means developer-selected functions have been integrated, not that project character LoRAs are automatically trained. [公式モデルカード](https://huggingface.co/Qwen/Qwen-Image-Edit-2511) (2026-09-12; model 2511).

ComfyUI's official 2511 example combines a diffusion model, Qwen text encoder, and Qwen VAE, optionally with a 2511-specific 4-step Lightning LoRA. Its diffusion weights are `qwen_image_edit_2511_bf16.safetensors`. Do not assume a local FP8-named file has the same weights/quality as the official BF16 example. [ComfyUI公式2511例](https://docs.comfy.org/tutorials/image/qwen/qwen-image-edit-2511) (2026-09-12; that workflow).

**Experiment proposal:** first verify one character, one reference, and one editing instruction. Then compare face/full-body references, and finally two-character differentiation. Compare Lightning enabled/disabled as separate conditions; do not blindly reuse normal-model steps/guidance. Check FP8 distributor, model hash, node support, and precision settings before measuring time, memory, and acceptance rate.

<a id="novelai-opus"></a>

## NovelAI Opus generation without Anlas consumption

**Confirmed facts (2026-09-20):** official subscription guidance describes Opus eligibility as up to 1024 × 1024 px, at most 28 steps, and one image per request. Image-generation guidance uses normal size or smaller; generating multiple images simultaneously consumes Anlas even with Opus. Image2Image using a source image is not included in this basic no-Anlas condition. [契約条件](https://docs.novelai.net/en/subscription/), [ステップ数](https://docs.novelai.net/en/image/stepsguidance/), [画像生成・枚数設定](https://docs.novelai.net/en/image/). This benefit belongs to a paid Opus subscription and differs from a free trial without a subscription.

Do not reinterpret 1024 × 1024 = 1,048,576 pixels as "each edge at most 1024 px," or infer custom-size eligibility solely from pixel arithmetic. Follow common [Page Settings](page-layout.md), adapt dimensions to the tool, and verify cost for the actual chosen size before execution.

**Kit default procedure:** apply the following only when NovelAI is selected and an active Opus subscription is confirmed. Do not repeat a question already answered in conversation or verified environment information. Do not assume an unknown plan is Opus or force these conditions on other environments.

| Item | Initial Opus setting |
| --- | --- |
| Steps | Official V5 default 23; kit default 28 for V4.5 and earlier; always at most 28 |
| Images per request | One; no simultaneous batch generation |
| Method/additional features | Text-to-image; no source image, Precise Reference, Vibe Transfer, etc. by default |
| Before execution | Cost display for selected model/all settings must show 0 Anlas; also check remaining V5 Opus usage allowance |

The [公式の利用上限説明](https://journal.novelai.net/opus-usage-limit-explained-jp/) confirms V5's default 23 steps and greater allowance consumption at 28. **V5 no-Anlas generation has a time-recovering allowance; after it is exhausted, generation uses Anlas.** This allowance does not apply to V4.5 and earlier. Never describe Opus as always unlimited and zero-consumption.

1. Preserve the user's environment/model choice. For Opus, fill unspecified steps/count/features from the table and dimensions from common page settings. Check chosen dimensions/steps against no-Anlas conditions and retain them if eligible. If not, propose a change instead of silently overwriting instructions or generating at a cost. While awaiting a change answer or cost confirmation, defer only generation and size-dependent placement. Explain that planning, character naming, story organization, and other independent work can continue, and proceed as needed.
2. Apply width/height to both `config/page-layout.json`'s `generationCanvas` and the actual generator. Record steps, count, reference features, and cost conditions among adopted OPTION values and production records, and set them in the generator. Dimension JSON alone does not control steps/fees. Determine [placement and final PNG](page-layout.md) from actual output dimensions.
3. Before every run, confirm 0 Anlas for all current settings. If V5 allowance is insufficient, defer generation and wait for recovery. If cost cannot be verified, do not run a paid-risk test to find out. Change models or continue with Anlas only within explicit user instructions. Do not ask again for an already authorized scope.
   - **Subscription and Anlas check API frequency (user instruction, 2026-10-05):** Do not call the query API (`/user/subscription`) that checks subscription, Anlas, and V5 allowance on every generation. To reduce the risk of warnings caused by excessive API calls, call it once on the first generation (trial), and thereafter **once every 10 generations counted from the previous check**. The count is an operational guideline and does not measure actual consumption. Generations in between reuse the previous check result and record whether an API call or the previous result was used in `subscriptionCheck` within the execution record.
   - Query regardless of count when: the model, dimensions, steps, sample count, or additional features differ from the previous check; the previous generation was not confirmed complete (failure or unknown outcome); or the remaining V5 allowance is low (`percent` in the query result is 3 or below, or insufficiency was indicated). The script records the count in the project's `output/novelai/subscription-check.json` (which contains no credentials). Delete this file to force a check. Because the API is queried on every run while remaining allowance is low, this does not risk overlooking an exhausted allowance. The threshold of 3 is a user specification (2026-10-05), not an official standard.
   - This frequency change applies **only to how often the subscription check API is called**; it does not change paid-use authorization, 0-Anlas verification, the requirement to specify `--confirm-zero-anlas`, `--allow-anlas`, and `--cost-note`, or the prohibition on automatic resending.
4. Check generated PNG dimensions and record size, steps, count, model, and method/date of 0-Anlas verification in ordinary project records. Do not label unobserved consumption as "measured zero." For APIs/external clients, research their specification and cost-check method; do not assume UI eligibility applies without verification.

**Confirmed additional fees:** [Precise Reference](https://docs.novelai.net/en/image/precisereference/) adds Anlas according to reference count. [Vibe Transfer](https://docs.novelai.net/en/image/vibetransfer/) has V4+ initial/re-encoding charges and charges beyond four references. Check each feature's cost for image references, panel-layout image inputs, Enhance, Upscale, Inpaint, and similar editing; dimensions/steps alone do not establish zero cost. Without reference features, use fixed character descriptions and visual output checks for consistency.

**Unverified:** the user's subscription, actual API consumption, generation quality, and lettering readability. This research did not log in, generate images, or perform Anlas-consuming tests. The table supplies starting settings aligned to official conditions, not quality guarantees. Recheck current official conditions if specifications change or displays disagree.

## 5. NovelAI API connection design

The official image API base is `https://image.novelai.net`. The public schema confirmed `POST /ai/generate-image`, image ZIP or JSON responses, and the `action`, `input`, `model`, `parameters` structure. Persistent API tokens are used in the Authorization header. The API also specifies human-initiated generation and prohibits excessive automated load. [公式画像APIスキーマ](https://image.novelai.net/docs/doc.json) (2026-09-12; public specification).

**Connection implementation (2026-09-21):** new projects include `scripts/novelai_api.py`, supporting automatic key loading, subscription queries without generation, and explicitly executed single-image generation/PNG saving. See [connection procedure and smoke-test prompt](novelai-api.md). Example generation requests leave model unset; recheck the current schema for the selected model/features. Do not equate reference UI explanations with API fields. Distinguish code implementation from real-API verification, and record actual results in the project.

- Manage keys per project. Exclude them from shared templates, workflow JSON, image metadata, and progress logs. Record only key presence and connection results.
- Record request IDs and generation numbers to track identity. Do not automatically duplicate a timed-out request with unknown outcome.
- For Opus, apply [no-Anlas conditions](#novelai-opus), verify cost, then validate the first response/save. Favor local ComfyUI for volume comparisons; record NovelAI run counts/costs in the project's experiment plan.

## 6. Matching style from NovelAI to ComfyUI

The following is a **production proposal, not a measured, quality-guaranteed workflow**.

1. **Fix direction first:** panel purpose, framing, expression, positions, and balloon space.
2. **Generate source art in NovelAI:** use selected model, fixed character text, and adopted reference conditions. Check face, costume, and composition first. Opus defaults to [no-Anlas conditions](#novelai-opus); evaluate reference surcharges separately. Save original PNG/settings.
3. **Choose ComfyUI processing:** compatible img2img for light style adjustment, compatible ControlNet for pose/outline retention, or Qwen-Image-Edit-2511 for reference editing. Treat branches as separate workflows.
4. **Compare a small strength range:** ordinary img2img may test denoise 0.2 / 0.35 / 0.5. These are experimental values, not recommended success settings. Do not transfer them directly to Qwen reference editing.
5. **Compare before/after:** check style along with face, hair, clothes, left/right, props, expression, gaze, and balloon space.
6. **Correct locally and review in page context:** fix only problem areas, compare neighboring panels at publication size, and undo mismatches such as an excessively detailed face.
7. **Freeze the adopted version:** save source → edit → correction relationships, workflow/weight versions, and selection reasons. Organize reproducible findings as feedback only if requested.

ComfyUI's official basic img2img example encodes the source into latents and adjusts change with denoise. The explanation that stronger values increase difference from the source applies to that process. [ComfyUI img2img](https://docs.comfy.org/tutorials/basic/image-to-image) (2026-09-12; basic example).

## 7. Seeds and reproducibility

A shared seed does not guarantee consistency. NovelAI also requires matching resolution, image count, reference images, etc., and describes sampler nondeterminism. A NovelAI seed does not produce the same image in ComfyUI. [NovelAI Seed](https://docs.novelai.net/en/image/seed/) (2026-09-12; NovelAI image generation).

Diffusers also states that a seed alone does not guarantee exact reproduction. A random Generator's state advances on use; distinguish recording the seed from managing random state. [Diffusers Reproducibility](https://huggingface.co/docs/diffusers/using-diffusers/reusing_seeds) (2026-09-12; Diffusers).

**Production practice:** check ComfyUI's per-run seed-changing settings and fix them for reproduction tests. Record model hashes, node versions, workflow JSON, prompts, references, sampler, scheduler, steps, guidance, denoise, resolution, batch, precision, and LoRA strength together. Report same-machine reproduction, approximate cross-environment reproduction, and usability as comic art separately.

## 8. Expression and pose experiment plan

The English prompts below are **untested candidates**, not officially guaranteed tags. Compare tag-style and natural-language instructions as separate conditions.

| Goal | Tag candidate | Editing-instruction candidate |
| --- | --- | --- |
| Small smile | `gentle smile, closed mouth` | `Give the character a subtle closed-mouth smile. Keep the hairstyle and outfit unchanged.` |
| Bright smile | `open-mouth smile, raised cheeks` | `Show a joyful smile with raised cheeks and an open mouth. Preserve the character's identity.` |
| Surprise | `surprised, wide eyes, raised eyebrows, open mouth` | `Make the character look startled, with wide eyes, raised eyebrows, and a slightly open mouth.` |
| Recoiling surprise | `startled, leaning back, hands raised` | `Show the character recoiling in surprise, leaning backward with both hands raised near the chest.` |

Separately define required cues: mouth corners/cheeks/eyes for smiles, or brows/eyes/mouth/torso for surprise. Retain failures where surprise becomes fear or joy.

### Stage 1: 24-image small comparison

Choose one working local route and one approved character. Compare 2 expressions (smile/surprise) × 2 instruction methods (tags/prose) × 3 seeds × 2 framings (face/upper body) = 24 images. Fix three seeds before the experiment and reuse them across conditions; do not reselect only preferred results. Hold model, references, and settings constant apart from instruction method within each comparison.

### Stage 2: identity and posture together

Fix the usable instruction method from stage 1. Compare 2 poses (natural standing/recoiling) × 2 reference methods (full body/reference with a sufficiently large face) × 3 seeds = 12 images. A model's difficulty with tags is a conditional result worth recording. Run the same experiment independently per model when comparing models.

### Records and evaluation

| Record | Content |
| --- | --- |
| Experiment identity | experiment_id, run_id, date/time, hypothesis, project/character/panel IDs, operator |
| Inputs/settings | Reference ID/hash, source ID, full prompt, model/LoRA/node versions, seed, resolution, batch, sampler, etc. |
| Volume/failures | Planned, submitted, successfully generated, errors, failed images, retry reasons |
| Expression success | Intended emotion/action: 0 unreadable, 1 ambiguous, 2 clear |
| Identity/style | Each 1–5: 1 different, 3 usable after correction, 5 matches baseline; record face/costume breakdown |
| Structure/direction | Limb failures, left/right reversal, props, gaze, space, panel readability |
| Cost | Seconds/image, initial load time, peak VRAM, RAM if needed, correction minutes/image, actual API costs |
| Decision | Accept/defer/reject, reason, evaluator, next variable to change |

**Provisional pass:** expression 2, identity at least 4, no major costume mismatch or limb failure. Report accepted/successful generations and accepted/all attempts. For small samples, state denominators such as 2/3 rather than implying general success rates. If feasible, have two evaluators judge blinded conditions and record disagreements. Automatic face similarity alone does not determine comic identity.

**Current experiment status:** not run. Success rates, best tags/strengths, generation speed, and required VRAM remain unknown.

## 9. Next steps if training a LoRA

**Production suggestion:** consider when a character appears in many panels and reference editing demonstrably requires substantial correction effort.

1. Fix target base model, trainer, and versions. SDXL training examples do not guarantee Qwen training support.
2. Collect only human-verified character images. Check angle/expression/costume bias, wrong left/right, and duplicates. Record allowed asset scope in the project.
3. Separate training/evaluation sets without similar-composition leakage. Caption costumes/backgrounds and evaluate unwanted character-background coupling.
4. Record rank, learning rate, steps, image count, and resolution; begin small. Test inference and training operation separately.
5. Evaluate unseen poses, expressions, and costumes against a reference-only baseline. Measure character/style LoRAs individually before combining them.

## References

A01–A10 were read on 2026-09-12. The additional Opus research is sourced and dated 2026-09-20 in its [dedicated section](#novelai-opus). Source specifications, comic-production proposals, and locally untested claims are distinguished above.

- A01: [Qwen公式モデルカード](https://huggingface.co/Qwen/Qwen-Image-Edit-2511) — 2511 name, functions, examples.
- A02: [ComfyUI公式2511ワークフロー](https://docs.comfy.org/tutorials/image/qwen/qwen-image-edit-2511) — model composition and filenames.
- A03: [NovelAI Precise Reference](https://docs.novelai.net/en/image/precisereference/) — references, constraints, sheets.
- A04: [NovelAI Seed](https://docs.novelai.net/en/image/seed/) — uses and reproduction limits.
- A05: [Diffusers LoRA](https://huggingface.co/docs/diffusers/training/lora) — training principles/examples; not Qwen training guarantees.
- A06: [ComfyUI img2img](https://docs.comfy.org/tutorials/basic/image-to-image) — basic change strength.
- A07: [ComfyUI ControlNet](https://docs.comfy.org/tutorials/controlnet/controlnet) — conditioning images, preprocessing, compatibility.
- A08: [IP-Adapter開発元](https://github.com/tencent-ailab/IP-Adapter) — image conditioning and published model families.
- A09: [NovelAI公式画像API](https://image.novelai.net/docs/index.html), [公開スキーマ](https://image.novelai.net/docs/doc.json) — endpoints, requests/responses, authentication.
- A10: [Diffusers Reproducibility](https://huggingface.co/docs/diffusers/using-diffusers/reusing_seeds) — random state, environment, reproducibility.

## Comic completion scope

For a request to finish a comic, follow [Thumbnails through PSD](manga/08-workflow-review.md) and [PSD handoff conditions](psd-handoff.md). First present PNGs from production assets, revise/re-present, and confirm no further revisions. Without a PSD instruction, ask and wait without creating one. With an existing instruction, proceed after PNG confirmation through creation, reopening, composite comparison, and handoff without asking again. Silence is neither "no revisions" nor a creation instruction. A person normally finishes in CLIP STUDIO PAINT and publishes. Create CBZ only when explicitly specified.
