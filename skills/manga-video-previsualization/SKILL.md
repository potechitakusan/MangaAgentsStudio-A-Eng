---
name: manga-video-previsualization
description: Use only when explicitly asked to test cinematic staging or action in short videos: generate and connect shots from character references, then evaluate adoption in the comic. Not for ordinary comic production or framing review alone.
---

# manga-video-previsualization

An optional feature for checking comic staging ideas through video, limited to the user's requested trial scope. Paths are relative to the target project root. In the distribution kit, reference this skill by its explicit path.

Read `docs/PLAN.md` and `docs/PROGRESS.md`; record the effect to test, duration, dialogue, and completion criteria. Read needed sections of `docs/knowledge/video-previsualization.md` for workflow and `docs/knowledge/video-prompting.md` for model specifications/prompt evidence.

For actual submission, retrieval, and concatenation in local ComfyUI, helper scripts are available through `docs/knowledge/video-tools.md`. Use compatibility launchers for known versions only when the corresponding error requires them.

For Turbo verify author, version, target base, and node graph. Do not equate ModelTC/LightX2V FL2V 8-step v1.0 standard LoRA with the older Larryvrh dedicated TurboLoRA/TurboSampler. Standard new-LoRA configuration is in `video-tools.md`. If using ASR as an aid, do not prime it with expected dialogue; distinguish recognition output from direct listening.

1. Define fixed character traits and shot-to-shot spatial relationships. First make references with the available built-in image-generation tool, visually verify faces, clothing, build, and identifying features, then use them as inputs. Follow the available imagegen skill. If needed, use the same references for shot-start/intermediate images.
2. Start from the user-provided, verified MiniMax H3 workflow. Check nodes, actual model names/versions, reference-image inputs, duration/FPS/frame count, and output destination. Distinguish H3 model types and quantizations; do not reinterpret an abbreviation as another model. Modify a project-local working copy. If models are missing, identify exact files, distributors, and destinations and ask the user to download them.
3. Assign one readable main action to each shot of no more than 10 seconds, normally around 4–7 seconds. Define start state, main action, end state, framing/camera, and dialogue. Generate a baseline shot, verify reference input/output, then generate the rest. Record active job IDs and destinations; after a lost response inspect history before resending.
4. Check identity, action causality, anatomy errors, and movement direction in each shot. Record targeted corrections before regenerating; if failures repeat, split actions or change staging. Do not retry indefinitely; record unmet criteria and next methods.
5. Connect selected shots to the requested duration. Create dialogue in English; if the video model cannot produce suitable speech, use another available speech-generation method. Record added voice and synchronization methods. Inspect video, listen to English speech, and check transitions, duration, volume, and missing dialogue. Subtitles alone do not constitute completed English audio.
6. In `docs/experiments/`, record input references, full prompts, workflow and model/node versions, seed, duration, resolution, FPS, key settings, submitted/adopted counts, generation time, failures, and relative artifact paths. In `docs/reviews/`, record adoption and comic framing, omissions, and timing to use. Save feedback in `docs/feedback/` only when requested; otherwise do not ask. Update progress and next action at startup, decision changes, generation/validation, and interruption.

For speed improvements compare quality/time for the same use, separating official promotional claims from local measurements. If a faster alternative with little quality loss is not installed, present comparison evidence and download targets to the user. Never import project references, outputs, raw logs, machine-specific paths, or secrets into shared skills/templates. The main agent integrates final acceptance and explicitly marks items not generated, listened to, or evaluated.
