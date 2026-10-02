# Video Prototypes and MiniMax H3 Prompts

Checked: 2026-09-12 (JST). English adaptation: 2026-09-30.
Scope: optional short cinematic videos in local ComfyUI to investigate comic framing, action, pauses, and continuity. Do not make video generation mandatory in normal comic production.
Evidence labels: **Confirmed fact** means the linked source states it; **Production suggestion** means project judgment; **Unverified** requires local execution/viewing evaluation.

## Choose the model and reference method first

**Confirmed fact:** the official name is **MiniMax H3**. H3-Base-FL2VA supports text/start/end images; H3-Base-Ref2VA supports multiple image/video/audio references. Official specifications state 4–15 seconds, 24 fps, and 32 kHz stereo. Japanese is among the 11 languages described as stable in the original source review. H3-Context-IR is hosted preprocessing; local public weights alone do not reproduce the full official service. [MiniMax公式README](https://github.com/MiniMax-AI/MiniMax-H3). English production must still verify the selected version's actual language/audio behavior; historical Japanese tests below do not establish English performance.

**Production suggestion:** distinguish character references for identity, scene images for composition/location, and starting images for the literal first frame. To avoid displaying a character sheet at the start, use it as a Ref2VA identity reference or first create a scene image and supply that to I2VA.

**Confirmed fact:** ComfyUI FL2VA and Ref2VA weights differ. Ref2VA reference tags follow connection order. `match` reduces references to generation resolution; `max` uses larger references for identity with higher computational cost. [ComfyUIネイティブワークフロー](https://docs.comfy.org/tutorials/video/minimax/minimax-h3-native).

## Build a reference prompt

**Confirmed fact:** H3's full-reference mode uses six sections. The main description is English; dialogue, lyrics, and on-screen writing retain their intended exact text. `<Subject N>` identifies reusable content such as a person; `<Picture N>` identifies a concrete frame/composition reference. [MiniMax全参照ガイド](https://raw.githubusercontent.com/MiniMax-AI/MiniMax-H3/main/skills/h3-prompt-writing/references/ref-en.txt).

| Section | Content |
| --- | --- |
| `subject_definitions` | Reference connection numbers and each role: person, place, composition, etc. |
| `summary` | Short generated scene and how references are used |
| `retention_analysis` | Faces, clothes, backgrounds, etc. to retain or intentionally change |
| `detailed_description` | Starting frame through action, reaction, and sound in playback order |
| `overall_soundscape` | Ambience, footsteps, clothing rustle, etc. |
| `non_diegetic_music` | Score; `N/A` if unnecessary |

This **original, untested English example** illustrates format, assuming image 1 contains a person and image 2 a room. Inspect actual inputs and replace accordingly.

```text
subject_definitions:
<Subject 1> is the adult negotiator in <Picture 1>, preserving his face, dark suit, white shirt, and narrow tie.
<Subject 2> is the room in <Picture 2>, preserving the table, doorway, and warm side lighting.

summary:
[reference generation] <Subject 1> calmly delivers one short line inside <Subject 2>.

retention_analysis:
<Subject 1> (appears in [Shot 1]): fully_preserved - identity and clothing.
<Subject 2> (appears in [Shot 1]): fully_preserved - layout and lighting.

detailed_description:
The video has a restrained live-action style.
[Shot 1] An eye-level medium shot places <Subject 1> beside the table in <Subject 2>. The camera remains still. He lifts his eyes toward the listener. His low, even voice (S1) says: <d>[English] Please hear me out.</d> He pauses with relaxed shoulders.

overall_soundscape:
Quiet room ambience and a slight rustle of suit fabric.

non_diegetic_music:
N/A
```

**Confirmed fact:** start/end-frame modes differ from this six-section format: begin with image/time correspondence, then `integrated_multimodal_description`, `overall_soundscape`, and `non_diegetic_music`. Describe camera movement type, needed distance, and speed in prose. Keep speaker IDs such as `(S1)` consistent, place spoken text in `<d>` tags with a language label, and put voice/acting instructions outside. For multiple shots, use increasing cut times from shot 2 onward. The original reviewed Japanese example used `<d>[Japanese] ...</d>`; the localized example above uses English. [MiniMax始終フレーム系ガイド](https://raw.githubusercontent.com/MiniMax-AI/MiniMax-H3/main/skills/h3-prompt-writing/references/base-en.txt).

**Production suggestion:** one-shot generation needs only `[Shot 1]`. Verify individual shots before attempting many timed cuts in one generation. Replace vague "powerful" or "cool" with observable relaxed shoulders, gaze, evasion direction, or final opponent position. Do not combine incompatible directions such as a locked camera and tracking movement.

## Divide about 20 seconds into 4–7-second clips

**Confirmed fact:** ComfyUI rounds H3 lengths to `17k+5` frames at 24 fps. Dimensions are multiples of 32; a standard landscape canvas is 1344 × 768. [ComfyUIプロンプトガイド](https://docs.comfy.org/tutorials/video/minimax/minimax-h3-prompt-guide).

**Production suggestion:** four 124-frame clips at 24 fps total approximately 20.67 seconds. If needed, trim toward 20 seconds without cutting dialogue/reactions. Record both calculated and inspected actual durations.

| Candidate frames | Calculated duration at 24 fps | Suggested use |
| --- | --- | --- |
| 107 | About 4.46 s | Short reaction or command |
| 124 | About 5.17 s | Negotiation, evasion and resolution |
| 141 | About 5.88 s | Action with a reaction pause |
| 158 | About 6.58 s | Clearly establish an action's start and result |

**Production suggestion:** divide an all-at-once crowd attack into who moves first, protagonist action, and opponent end state per shot. Distinguish two attackers by hairstyle, shirt color, and position as well as build. Choose angles that show approach → evasion → fall. Increase crowd size only after this chain reads clearly.

**Production suggestion:** start English audio with one speaker and one short sentence per shot. Limit combat dialogue and place lines in negotiation/command shots to make meaning and lip motion easier to assess. Independently generated voices/ambience may shift between clips: actually listen for level, timbre, and clipped starts/ends. Separate TTS does not automatically guarantee lip sync.

## Preserve character and spatial continuity

**Production suggestion:** fix face, hair, clothes, left/right positions, and lighting direction through references/text. Map references per shot; never assign different people to the same tag. Store character references separately from generation scene images and record filenames/hashes. Use the same references when recreating a next-shot image; a good final frame from the previous clip may also anchor continuity.

**Production suggestion:** flawed frames propagate flaws when reused. Check eyes, contours, sleeves, limbs, and clothes first. Revise shot by shot without simultaneously changing prompt, resolution, model, and steps. Do not generalize one seed's success; compare a few other seeds when needed.

## Compare speed and quality

**Confirmed fact:** Comfy-Org repackages pruned/quantized H3 weights and prioritizes `int8_convrot` when PyTorch cu130 is available. The `nvfp4_awq` text encoder does not have a Blackwell-only requirement. [Comfy-Orgモデルカード](https://huggingface.co/Comfy-Org/MiniMax-H3).

**Confirmed fact:** Larryvrh describes Turbo LoRA's effective range as 4–8 steps and notes possible ghosting in fast/large motion with v4 at 4 steps. Increasing to 6–8 or using older v1 selectively are the author's suggestions. These describe a developing derivative, not a MiniMax base-model quality guarantee. [Turbo作者モデルカード](https://huggingface.co/larryvrh/MiniMax-H3-Turbo-Lora).

**Confirmed fact:** ModelTC/LightX2V Turbo is a separate family. Ref2VA 4-step v0.1 targets 544p; FL2VA has 768p 4/8-step variants, with differing training resolutions and audio/video shifts. Similar names do not justify mixing LoRAs/samplers. [ModelTC作者README](https://github.com/ModelTC/Minimax-H3-Turbo).

**Confirmed fact:** FL2VA's `minimax_h3_fl2v_turbo_8step_v1.0_comfyui_bf16.safetensors` is a 544p-family 8-step v1.0 using a standard LoRA loader, Euler, video shift 12/audio shift 3. Distinguish the 768p-specific video shift 6. [作者のモデル表](https://github.com/ModelTC/Minimax-H3-Turbo/blob/main/README.md), [設定手順](https://github.com/ModelTC/Minimax-H3-Turbo/blob/main/COMFYUI_SETUP_AND_INFERENCE.md).

**Historical local observation:** the 8-step variant generated audio/video at 896 × 512/124 frames through standard LoraLoaderModelOnly + SigmaShift + Euler. The new standard-format LoRA was not run through the older dedicated TurboLoRA node. Match target base, key format, and author workflow instead of relying on "Turbo" naming. Two Japanese lines matched unguided ASR, but ASR alone did not establish voice-quality/lip-sync success. This remains Japanese-language evidence, not an English test.

**Production suggestion:** create one baseline with a known-working setup and measure whether the bottleneck is text processing, weight loading, sampling, decoding, or upscaling. Fewer steps do not reduce loading time. First remove unnecessary upscaling, then compare 4/8 steps with identical material for readable motion, faces, ghosting, and English speech. Record quantization, pruning, Turbo use, author/version, and actual settings; do not assume equivalence to official-service demos.

**Confirmed fact:** ComfyUI describes Sage Attention acceleration, but unsupported dtypes may fall back to standard attention. [ComfyUI速度改善資料](https://docs.comfy.org/tutorials/video/minimax/minimax-h3).

**Production suggestion:** if compatible Sage settings already exist, check actual use in logs. Decide on new backends/large model downloads only after measuring and comparing the existing setup.

## Alternative candidates

Candidates as of the check date. **None has been compared with H3 on the same GPU, references, and scene**; do not conclude "same quality, faster."

| Candidate | Scope confirmed from developer/author material | Remaining checks |
| --- | --- | --- |
| H3 + existing Turbo | Reuses references and permits step comparisons | Measure first; initial candidate when no download is needed |
| H3 + newer Larryvrh Turbo | Author describes 4–8 steps and detail/fast-motion tradeoffs | Compare installed version, audio, multi-person action, VRAM; not necessarily faster |
| H3 + ModelTC/LightX2V Turbo | Dedicated Ref2VA 4-step variant exists | Compatible sampler, shift, resolution, reference identity |
| LTX-2.5 distilled | Developer offers a few-step fast route; ComfyUI guidance covers synchronized audiovisual generation | Requires separate 22B weights, encoder, VAE, upscaler; quality/actual speed versus H3 untested |
| Wan2.2 TI2V-5B | Developer states 720p/24 fps; official command guidance names GPUs with at least 24 GB | Verify 16 GB operation, separate requested-language audio workflow, and multi-person identity |

LTX-2.5 capabilities/components: [Lightricks公式リポジトリ](https://github.com/Lightricks/LTX-2) and [公式ComfyUIガイド](https://docs.ltx.io/open-source-model/usage-guides/text-to-video). Official requirements list at least 32 GB VRAM; do not assume a 16 GB replacement works. [LTX必要環境](https://docs.ltx.io/open-source-model/getting-started/system-requirements). Wan conditions: [Wan2.2開発元README](https://github.com/Wan-Video/Wan2.2).

**Production suggestion:** a download proposal must identify model ID, exact files, distributor, destination, required storage, reusable installed components, expected improvement, and unknowns. Without evidence that quality loss is small, do not make downloads mandatory.

## Evaluation records

**Production suggestion:** distinguish "MP4 produced" from "intended scene communicated." Record per shot:

- Technical: actual duration, fps, dimensions, audio track, generation time, actual steps, model/references, seed, errors.
- Direction: who did what, start/result, protagonist composure, opponent response, information conveyed by framing.
- Continuity: face/clothes, count, left/right, gaze/movement, fallen characters, room layout.
- Audio: English intelligibility, actually spoken words, speaker, voice, lip matching, cuts at joins. Preserve the language label of any historical test.
- Comic adaptation: candidate panels, necessary intermediate poses, information needing supplementation in still art despite working in video.

Record technical inspection, visual viewing, and audio listening separately. Mark unseen/unheard items unverified; a contact sheet alone cannot establish temporal continuity.
