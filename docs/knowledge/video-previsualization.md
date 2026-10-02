# Testing Comic Direction with Short Videos

Updated: 2026-09-12. Optional stage only when the user asks to test cinematic direction in video. Normal comic production does not require video generation.

This is a **proposed production workflow**, not a model-performance guarantee. See [Video Models and Prompt Research](video-prompting.md) for official model names, supported inputs, duration/audio specifications, external prompt evidence, and dates. Record actual success/failure/speed in the project's `docs/experiments/`; reading documentation is distinct from testing generation.

## Purpose

Observe whether framing, spatial continuity, action/reaction, and pauses between tension/release communicate. Even successful video motion requires redesign for comic omissions, simultaneously visible panels, page turns, and reader-controlled speed. Do not mechanically map one shot to one panel. Use [Immersion and Cinematic Direction](immersion-and-cinema.md) for comic adaptation.

## Initial preparation

| Item | Decide | Project location |
| --- | --- | --- |
| Prototype objective | Effect to check, approximate duration, what must communicate to whom for acceptance | docs/experiments/ |
| Character references | Built-in-generator baseline images, fixed traits, costume, left/right markers, version/hash | assets/characters/ |
| Space and shots | Positions, screen movement direction, start/end states, main action, camera | docs/experiments/ |
| English dialogue | Speaker, exact text, speech start, time slot, delivery | docs/experiments/ |
| Environment | ComfyUI, GPU, actual model/node versions, destination | docs/experiments/ |
| Workflow | Working copy based on a checked, known-working original | workflows/ |
| Outputs | Clips, audio, assembly, comparison stills | output/ |

Multiple characters on one sheet may make reference identity ambiguous. Check face, hair, clothes, and build in individual baselines; specify each person/position in multi-character shots. This is a prototype proposal; verify model-specific reference ability. Derive needed starting/intermediate images from approved baselines too, detecting appearance drift from successive generations.

## Verify the workflow

Start from a known-working MiniMax H3 workflow and read its JSON nodes/actual models. See [model research](video-prompting.md) for H3 variants, quantization, and acceleration LoRAs. Abbreviations/filenames alone do not establish compatibility. Record the provider's prior verification separately from this run with current inputs.

Before execution, check reference connections, duration/frame constraints, FPS, resolution, output saving, and audio. Distinguish GUI JSON from API JSON and validate with available conversion/submission methods. Start with one planned shot and verify input-output correspondence before submitting all shots.

Preserve the known-working original; change a project copy and record edits. Exclude credentials/other projects' absolute paths from shared files. If models are missing, identify exact names, source URLs, locations, and purposes and ask the user to download them.

## Assemble shots

**Production guideline:** for about 20 seconds, prepare several 4–7-second clips. Bundled helpers keep each asset at most 10 seconds and follow the model's duration/FPS/frame constraints. Split into readable causal units before packing many sequential actions into one prompt.

| Shot-plan field | Record |
| --- | --- |
| ID and time | Target duration, assembled start time, references |
| Starting state | Positions, poses, expressions, gaze |
| Main action | Who does what and how others/surroundings respond |
| Ending state | Pose, position, emotion, movement direction passed forward |
| Camera | Framing, view direction, necessary movement; prototype complex moves that compete with acting |
| Dialogue/sound | Speaker, English text, time slot, required ambience |

Example: negotiation fails → attack begins → evade/subdue first attacker → subdue second and show composure. Even with multiple people, choose framing that makes whose action to follow clear. These are initial staging candidates; evaluate actual output afterward.

Compare adjacent shots for clothing, face, count, positions, screen left/right, and fallen characters' states. Inspect format, resolution, FPS, and audio before assembly and align as needed. Measure finished duration and inspect frame-rounding fractions/audio cuts.

## English audio and review

Check English dialogue support in the actual model/version. If video lacks audio, use an available separate voice-generation method, recording speaker, voice, speed, and placement before compositing. For added dialogue, consider close-up lip synchronization or off-screen delivery. If text exceeds its time slot, adjust wording/duration while preserving intelligible speech speed.

Inspect beginning, middle, end, and key action moments; watch at normal speed when possible. Actually listen for English pronunciation, speaker matching, volume differences, silence, and cutoffs. Metadata analysis/transcription assists but does not prove listening occurred. If playback is unavailable, record audio review as not performed. Subtitles are supplementary, not a substitute for requested English audio.

## Records for objective comparison

Define criteria before generation. These provisional examples may change with project intent.

| Axis | Observe | Provisional score |
| --- | --- | --- |
| Action readability | Requested causality, such as evasion → opponent reaction | 0 unclear, 1 ambiguous, 2 clear |
| Character identity | Face, hair, costume, build, count changes | 0 different/mixed, 1 needs correction, 2 retained |
| Space/connection | Left/right, direction, positions, before/after states | 0 contradictory, 1 underexplained, 2 continuous |
| Bodies/contact | Limb count/shape, contacts, objects passing through bodies | 0 major failure, 1 minor, 2 does not obstruct intent |
| Acting | Intended composure, anger, tension, etc. | 0 opposite/blank, 1 ambiguous, 2 clear |
| Audio | English text, speaker, intelligibility, synchronization | 0 missing/failed, 1 needs correction, 2 works; unplayed audio remains unverified |

Record decisions per clip/assembly, evaluator, attempts, accepted count, and failure reasons. Self-assigned provisional scores are not measured reader evaluation. One success establishes no general success rate; distinguish reproduced from unverified conditions.

Record reference IDs/versions/hashes, full prompts/negative prompts, workflow version/hash, model/node versions, seed, sampler/key settings, precision, resolution, FPS, frames, and actual duration. Where possible separate initial loading, inference, saving/postprocessing, and assembly/audio time; record seconds/clip and processing seconds per output second. Track job ID, submission/completion, and outputs, plus total time including failures.

For acceleration comparisons, match references, action, duration, resolution, and criteria as closely as possible. Distinguish official speed claims from this machine's measurements. Faster output with broken identity/action is not an equivalent-quality replacement. When proposing another model, give comparison evidence, unknowns, and exact downloads required.

## Returning to comics

In `docs/reviews/`, record which moments, framings, spatial relationships, and pauses helped the purpose. Decide omitted actions, retained key poses, reaction panels, and transitions readers can infer. Evaluate video quality separately from usefulness to the comic.

Only when feedback recording is requested, organize it in `docs/feedback/` under [Feedback Workflow](feedback-workflow.md). Do not ask whether to record. Do not distribute character art, project-specific dialogue/settings, generated assets, unorganized logs, or machine-specific paths in shared templates. Distribute this procedure/skill and only generalizable findings with their conditions.
