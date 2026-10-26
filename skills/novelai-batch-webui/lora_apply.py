"""External LoRA application hook (plug-in entry point implemented per project).

This template does nothing by default. When the user asks to apply a LoRA (for example via ComfyUI),
an AI agent writes the implementation in this file and sets READY to True. The WebUI's "LoRA Mode"
can be turned ON only when READY is True, apply is callable, and check() returns (True, ...).

How it is called (invoked one panel at a time by lora_run.py)
  apply(job) -> dict | None
    job.root           Project root (Path)
    job.request_id     Request ID (e.g. p01-03)
    job.page           Page number (int, or None for non-page requests)
    job.source_image   Source image (Path: adopted image or latest candidate, or None if neither exists)
    job.request        Request JSON (dict with ${VARIABLE} placeholders from .env.novelai expanded: prompt, character captions, dimensions, seed, etc.)
    job.raw_request    Request JSON before variable expansion (retains ${VARIABLE})
    job.output         Destination PNG path (Path: output/lora/<request_id>/lNNN.png; must always be saved here)
    job.work_dir       Working directory (Path: output/lora/<request_id>/work/; intermediate files may be placed here)
    job.log            Logging callback (job.log("...") prints to the WebUI execution log)
  The returned dict is saved under "result" in the execution record (lNNN.lora.json) (model used, LoRA name, strength, seed, etc.).
  Raise an exception on failure. lora_run.py stops without running the remaining panels and does not retry automatically.

check(root) -> (bool, str)
  Called before turning LoRA Mode ON and before execution. Verify the endpoint (e.g., ComfyUI URL) and
  required model/LoRA files, returning (False, reason) if unavailable. Do not perform slow operations,
  image generation, or billable requests here.

Implementation rules
  - Never write credentials or API keys into this file, logs, or execution records. Read them from environment variables or .secrets/ if needed.
  - When using paid external services, run only within the scope explicitly permitted by the user and record how costs were verified.
  - Never overwrite source images (NovelAI candidates). Write output only to job.output.
  - Record the implementation details, endpoint, model, LoRA, default strengths, and verification results in the project's docs/production/ records.
"""
from __future__ import annotations

NAME = "unimplemented"   # Example: "ComfyUI img2img + character LoRA"
VERSION = "0"
READY = False            # Set to True after implementation and verification are complete


def check(root) -> tuple[bool, str]:
    if not READY:
        return False, "LoRA application is not implemented yet (READY is False in lora_apply.py)."
    return True, "Ready"


def apply(job) -> dict | None:
    raise NotImplementedError("LoRA application is not implemented yet. Implement apply(job) in lora_apply.py.")
