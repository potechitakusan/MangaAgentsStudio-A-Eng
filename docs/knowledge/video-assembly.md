# Python Tools for Video Assembly

Use `scripts/video/assemble_scene.py` for simple concatenation and `scripts/video/edit_scene.py` for frame-based shot editing. Both provide command-line and Python-function interfaces. The same source files and this document are distributed with new project templates.

## Requirements

Python 3.10+, ffmpeg, and ffprobe. No additional Python packages, GPU, or running ComfyUI instance are required. Replace `python` below with the path to an available Python executable if needed. If ffmpeg/ffprobe are not on PATH, specify them with `--ffmpeg` and `--ffprobe`.

## Command-line use

Run from the project root. Clips are assembled in the order of the `--clip` arguments; originals are preserved. Input filenames are unrestricted, and you can use two, four, or more clips.

```powershell
python .\scripts\video\assemble_scene.py --clip .\output\cut-01.mp4 --clip .\output\cut-02.mp4 --output .\output\scene-v1.mp4
```

To use up to the first 3 seconds of each video:

```powershell
python .\scripts\video\assemble_scene.py --clip .\output\cut-01.mp4 --clip .\output\cut-02.mp4 --trim-seconds 3 --output .\output\scene-v2.mp4
```

`--trim-seconds` applies the same maximum duration to every input. It does not trim from the beginning or specify different start/end times for individual clips. Check separately that dialogue is not cut off.

## Calling from another Python program

Include the project root on Python's module search path. Arguments accept either strings or Path objects.

```python
from scripts.video.assemble_scene import assemble_clips

report = assemble_clips(
    ["output/cut-01.mp4", "output/cut-02.mp4"],
    "output/scene-v3.mp4",
    # trim_seconds=3,  # Optional
    # ffmpeg="tools/ffmpeg.exe",
    # ffprobe="tools/ffprobe.exe",
)
print(report["probe"]["format"]["duration"])
```

The function returns the same dictionary saved as the assembly record. It raises FileExistsError for existing outputs, ValueError for invalid inputs, and subprocess/OSError-family exceptions for external-tool failures. The command-line version displays the reason and exits with an error.

## Output and supported scope

- Input: short videos of identical dimensions with both video and audio. Each asset is expected to be 1–10 seconds; metadata rounding up to 10.05 seconds is allowed. At least 1 second must remain after trimming.
- Output: MP4 at 24 fps with H.264 video and AAC, 48 kHz stereo audio. Input audio is concatenated and re-encoded. This is neither lossless copying nor automatic loudness normalization.
- Record: `scene-v1.assembly.json` stores input order, actual/used duration and SHA256 for each input, ffprobe results, the ffmpeg command, and finished-video information.
- Asset, output, and command working paths in the record are relative to the record's location. `path_base` is `.`. Keep assets and records on the same drive. Distinguish internal runtime path resolution from paths saved in records.
- Protection: if either the output video or matching record already exists, processing is refused. Use a new version name. A failed encode may leave intermediate files for investigation.
- Not supported by simple concatenation: adding silence to silent sources, automatic resizing, crossfades, subtitles, per-clip edit points, and inserts shorter than 1 second. Use the frame-based editor below for the last two.

Check technical assembly separately from continuity of meaning, action, and audio. Determine each film shot's duration in the edit design; do not automatically make every shot last the model's generated 4–7 seconds.

## Specifying each shot's start and end frames

For 24 fps material, specify a frame range with an inclusive start and exclusive end. For example, 12–30 is 18 frames, or 0.75 seconds. Assets must contain audio, share the same dimensions, and contain no more than 241 frames each. A selection can be as short as one frame. Asset paths are resolved relative to the edit JSON's location.

```json
{
  "version": 1,
  "shots": [
    {"id": "F01", "file": "wide.mp4", "start_frame": 0, "end_frame": 24,
     "manga_panel": "P1-1", "reason": "Establish the characters' left/right positions first"},
    {"id": "F04", "file": "hand.mp4", "start_frame": 12, "end_frame": 30,
     "manga_panel": "P1-4", "reason": "Signal anger before the command"}
  ]
}
```

```powershell
python .\scripts\video\edit_scene.py --edit-list .\output\timeline.json --output .\output\scene-edited.mp4
```

```python
from scripts.video.edit_scene import assemble_timeline
report = assemble_timeline("output/timeline.json", "output/scene-edited.mp4")
```

Optional `crop: [x, y, width, height]` values must all be even, preserve the original aspect ratio, and fit within the frame. The cropped image is scaled back to the original output dimensions. `audio_gain` ranges from 0 to 4 (default 1). Audio is cut at the same times as video, converted to 48 kHz stereo, and given 5 ms fades at its edges. Avoid cutting mid-line and check edit points including the trailing sound.

The finished MP4 and `.assembly.json` are saved. The record includes the edit JSON's SHA256, source SHA256 values, original frame ranges, starting frames on the finished timeline, all shot information including panel IDs and selection reasons, ffmpeg commands, and output inspection results. Existing videos and records are never overwritten. The editor does not automatically normalize audio, add subtitles, or create crossfades. Independently generated voices, ambience, and action require a content review of the completed sequence for continuity.
