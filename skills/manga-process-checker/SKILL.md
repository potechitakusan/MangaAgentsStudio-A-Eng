---
name: manga-process-checker
description: Use when a user asks to make future comic-production steps mandatory: discuss content, level, checkpoints, and carryover and register them in the project. Check evidence on stage reports, resumption, and handoff when requirements exist. Never add requirements automatically from ordinary creative instructions or dissatisfaction.
---

# Process checker

Compare the standard process and user requirements; return omissions and concrete actions to the main agent. Leave uninstructed staging, dialogue, composition, and acceptance of improvements to the main agent. This skill does not maintain a permanent separate agent.

## Entry

- Check project-root `project.json` and `config/process-requirements.json`. The full standard workflow is `docs/knowledge/manga/08-workflow-review.md`; use project OPTION and relevant knowledge for generation methods. Do not duplicate standard documents here.
- With zero active requirements, do not perform detailed checks/progress reports or install Hooks unless registration consultation is requested. Preserve existing AGENTS.md requirements. Missing/invalid JSON does not mean zero.
- Read only needed storage/command/input-output sections of `docs/knowledge/process-checker.md`. Paths are project-relative. Do not write new personal requirements back into shared kit templates or user-wide settings.

## Adding or changing requirements

1. Start from an explicit request such as "make this mandatory next time" or "remember this step as an instruction." Do not solicit registration after every production, or register complaints, one-off corrections, or standard recommendations on your own.
2. Discuss the following concretely without re-asking answered points:
   - Required action and conditions; whether to generalize wording so story-specific names/dialogue do not enter other works.
   - **Instruction** (`instruction`, checked at stage reports) or **strong instruction** (`strong-instruction`, reflected in AGENTS.md with Hooks if needed).
   - Starts with upcoming work/next revision or also applies to current deliverables; once per work or per page; deadline and evidence establishing completion.
   - Current project only or copy to later work on explicit carryover.
   - Whether AGENTS.md suffices for strong instructions or Hooks should supplement missed reports; overlap/conflicts and creative discretion.
3. Present concrete wording, level, conditions, checkpoint, carryover eligibility, and destination, then register after an explicit answer. A sufficiently specific initial registration instruction counts as that answer.
4. **If details are delegated, Codex chooses wording, level, timing, and implementation within that scope, briefly explains reasons, and registers.** Do not ask for another blanket approval. Delegation does not grant Hook execution trust, permission-boundary changes, external transmission, or paid use. Do not add many unspecified steps.
5. Prepare one discussed JSON item in `.work/process-checker/` and register with `scripts/process_checker.py add` or `replace`. Record original user wording and consultation details in that working folder; the canonical file contains reusable instructions and brief decision reasons. Use decision values `discussed` or `delegated`.
6. Immediately reflect strong instructions in AGENTS.md's managed section. If Hooks selected, show concrete `install-hooks` settings first, then save with `--apply` when covered by consent/delegation. Explain Codex review/trust to the user; never claim untrusted/unverified Hooks are active.

"Next time" does not order redoing past deliverables. Include the start in `condition`; discuss scope only for retroactive application. If AGENTS.md is edited in the same conversation, read the changed portion and obey its scope immediately rather than relying solely on automatic rereading.

## Stage reports

- At startup/resumption read canonical requirements and existing check records. At text storyboard, rough storyboard, page completion, before PNG presentation, before handoff, and other milestones, check what was due by then. Check strong instructions before their specified prerequisite stage as well.
- Decide target ID/version and applicability. Carry unresolved items forward; even reports skipping stages must check earlier deadlines. Give revised pages new versions. Before handoff enumerate actual pages and ensure reports cover every latest version.
- Do not mark complete by self-report alone. Read manuscript/images/review text/generation inputs/actual user answers and compare target, version, and content. Open actual images where needed. A reference file's existence does not prove it was attached to generation.
- Give `report` a status (`done`, `not-done`, `unverified`, `awaiting-user`, or `not-applicable`), reasons, and evidence files. Include both manuscript and review records to support rechecking after changes. The script manages IDs, deadlines, files, and hashes; it does not judge truth.
- For gaps return instruction ID, target, missing action/evidence, and next response to the main agent. Complete related work and recheck evidence. Deviation from a standard alone is not grounds to add requirements. Mandatory review does not mean adopting every suggestion.
- While awaiting answers, do not repeat questions; continue independent work. An unrelated consultation-only turn may end with a `noProgress` report. Never use `noProgress` to evade checks after actual production work.

## Carryover to the next work

Only when the user identifies the source, use the kit creation argument `-ProcessRequirementsFrom` or the new project's `import`. Do not automatically search other works/user areas. Copy only `carryForward: true` instructions, never completion records, assets, Hook configuration/trust, or external-use permissions.

If the destination already has requirements, discuss add/merge/replace differences. Do not migrate existing works automatically. Reflect strong instructions in the new AGENTS.md; configure/review Hooks separately in its environment.
