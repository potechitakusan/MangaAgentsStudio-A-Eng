---
name: manga-external-panel-i2i
description: Use when Qwen, NovelAI, or another external tool uses sketches, staged renders, or reference images to produce panel artwork for correction, cropping, and page assembly. Not for connection-only checks, text-only generation, or new imagegen panels/pages.
---

# Image-conditioned panel artwork with external tools

This skill is bundled with work projects. Paths are relative to the project root. `manga-ai-production` handles method selection; `docs/knowledge/external-panel-i2i.md` provides shared decision procedures.

## Scope and references

Once image-conditioned, per-panel production is selected, read the shared document and only references for the adopted model/version. Distinguish initial-image transformation, multiple-image references, control images, and dedicated appearance/style references. Verify available inputs and cost in the actual environment.

- Qwen-Image 2.1 records: `docs/knowledge/image-generation/qwen-image-2.1.md`. These do not guarantee behavior of other versions/nodes.
- NovelAI: `docs/knowledge/novelai-api.md` and `docs/knowledge/novelai-composed-production.md`. Follow service-specific connection, cost, and retry procedures. Successful t2i does not validate i2i.
- Other tools: verify supported inputs and current specifications. Do not transfer another model's image order, strength settings, or API fields.

Do not make Blender, particular lenses, LoRA, or imagegen usage restrictions defaults for every project. Carry forward adopted project restrictions and current authorization scope. Verify the relevant generation/editing skills and tools are available, then follow their procedures.

## Production

1. Receive focal subject, framing, visible headcount, face visibility, before/after action state, and preserved contact points from the text storyboard. Route staging gaps back to the references used by `manga-cinema-review` or `manga-immersion-review`.
2. Follow `docs/knowledge/panel-layout-policy.md` and `docs/knowledge/page-layout.md` for panel/page layout. Separate composition, appearance, and prop roles in inputs, and match actual connections/attachments to the actual submitted prompt.
3. Test input method and preservation requirements on a representative difficult case, then extend successful conditions. Depending on mismatch, reconsider references, instructions, model settings, local editing, or cropping. Retries stay within the authorized trial count and cost.
4. Actually open adopted images and verify actual dimensions/crop. Even when using finishing models or LoRA, compare left/right, costume, expression, tools, hidden faces, and continuity.
5. Assemble the page and return to checks in `docs/knowledge/japanese-manga-readability.md` and `docs/knowledge/manga/08-workflow-review.md`. After PNG revision confirmation, create only requested PSDs under `docs/knowledge/psd-handoff.md`.

Normal records retain actual inputs, settings, adopted originals, correction reasons, crops, postprocessing, failures, and unknowns. Use shared section C6 for fields and comparisons. Register feedback or personal mandatory steps only when each is requested by the user.
