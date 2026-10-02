# Helper Scripts for Local Video Production

Updated: 2026-09-12. Use only when carrying out an optional video prototype. Do not start video processing during normal comic production or template creation.

These scripts use the Python 3.10+ standard library and ffmpeg/ffprobe for assembly. They connect to a separately prepared, running ComfyUI environment. They do not download models or obtain API keys. On Windows, set `$Python` to an available Python executable before using the examples. The Python bundled with ComfyUI is also suitable.

## Execution flow

Keep the source workflow, reference images, and prompts in the project. Check models and nodes before uploading an input image to local ComfyUI.

```powershell
& $Python .\scripts\video\comfy_video_job.py --url http://127.0.0.1:8188 upload --image .\assets\characters\cast.png --record .\docs\experiments\reference-upload.json
```

Use the name returned by upload as the next `--image` value. Input names are made unique to avoid overwriting existing ComfyUI images.

```powershell
& $Python .\scripts\video\build_minimax_prompt.py --workflow .\workflows\source-r2v.json --image UPLOADED_NAME.png --prompt-file .\workflows\cut-01.txt --seed 12345 --seconds 5 --width 896 --height 512 --steps 4 --output-prefix movie/cut-01-v1 --output .\workflows\cut-01-v1.json --server http://127.0.0.1:8188
& $Python .\scripts\video\comfy_video_job.py --url http://127.0.0.1:8188 submit --prompt .\workflows\cut-01-v1.json --record .\docs\experiments\cut-01-v1-job.json
```

The 4-step value above is a trial setting for a source graph containing the compatible older Larryvrh LoRA and its dedicated sampler. **Do not reuse it unchanged with LightX2V 8-step v1.0.** It is also not an instruction to reduce the regular model to 4 steps. API conversion follows only dependencies needed by the GUI's SaveVideo output and replaces the reference, prompt, seed, and duration. Nested I2V and R2V graphs are the initial validation targets; conversion of every arbitrary node is not guaranteed. Model names and similar settings are retained from the source workflow, while the reference image name is replaced for this run. The converter does not add a new LoRA automatically: prepare the correct source graph with its compatible nodes.

Under these H3 frame constraints, requesting 5 seconds produces 124 frames at 24 fps, approximately 5.167 seconds. A 10-second request is rejected because rounding would exceed 10 seconds. Check the actual generated duration with ffprobe or an equivalent tool. Preserve source workflows and existing API graphs; write a new version instead.

```powershell
& $Python .\scripts\video\comfy_video_job.py status --record .\docs\experiments\cut-01-v1-job.json
& $Python .\scripts\video\comfy_video_job.py collect --record .\docs\experiments\cut-01-v1-job.json --output .\output\cut-01-v1
```

status/collect use the recorded URL and prompt_id. If the submission response is uncertain, do not automatically resubmit: check client_id and the server's queue/history. submit refuses when another job is queued and does not interrupt it. Errors are recorded in the job JSON. When using another port, use the same URL for upload, conversion, and submit.

Local asset, workflow, and collection paths recorded by the helpers are relative to each record's location. Keep assets and records on the same drive. Raw server history and error details may contain environment information; keep them within the project, separately from sources and specifications intended for sharing.

## Model-specific examples

### ModelTC / LightX2V FL2V 8-step v1.0

Checked: 2026-09-12. Based on the [作者のComfyUI設定](https://github.com/ModelTC/Minimax-H3-Turbo/blob/main/COMFYUI_SETUP_AND_INFERENCE.md) and [モデル表](https://github.com/ModelTC/Minimax-H3-Turbo). `minimax_h3_fl2v_turbo_8step_v1.0_comfyui_bf16.safetensors` is a standard LoRA-format file for FL2VA. Connect FL2VA's UNETLoader → LoraLoaderModelOnly (1.0) → MiniMaxH3SigmaShift (video12/audio3) to BasicGuider and BasicScheduler. The setup uses Euler, simple, 8 steps, and CFG 1. Do not treat Ref2VA, 768p-specific variants, or older Larryvrh LoRAs as using the same settings.

These values are an example for that model. Do not apply them unconditionally to other models or resolutions. Check speed and quality in the actual environment.

### Continuing from the last frame

With a verified API graph, `continue_minimax_clip.py` can preserve model settings and change only the starting image, prompt, seed, and output name. Its input is API JSON, not a GUI workflow. It supports I2V with one LoadImage and rejects graphs with two images or multiple references. Extract and visually inspect the preceding clip's final frame, then pass its upload record.

```powershell
& $Python .\scripts\video\continue_minimax_clip.py --base .\workflows\cut-01-v1.json --upload-record .\docs\experiments\cut-02-reference.json --prompt-file .\workflows\cut-02.txt --seed 12346 --prefix movie/cut-02-v1 --output .\workflows\cut-02-v1.json
```

The source graph hash, reference, and changes are recorded in `.continuation.json`. Check them before submitting. If the last frame has a failure such as a disappearing character, fix it instead of propagating it into the next clip.

### Assembly with audio

```powershell
& $Python .\scripts\video\assemble_scene.py --clip .\output\cut-01.mp4 --clip .\output\cut-02.mp4 --clip .\output\cut-03.mp4 --clip .\output\cut-04.mp4 --output .\output\scene-v1.mp4
```

This concatenates same-resolution videos and their native audio into a 24 fps/H.264/AAC MP4. Actual input durations, hashes, ffprobe results, and the executed command are saved in a matching `.assembly.json`. If needed, `--trim-seconds 5` retains only the first 5 seconds of each clip; first check that this will not cut off dialogue or actions. Do not add silence without direction and call the audio finished.

For command examples, calling `assemble_clips()` from Python, input requirements, and supported scope, see [Using the Video Assembly Python Tools](video-assembly.md). Both video and record files are protected against overwriting.
