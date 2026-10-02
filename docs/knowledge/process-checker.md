# Process Checker: Registration, Review, and Carry-Forward

Updated and official sources checked: 2026-09-21. This is a kit-specific workflow. It does not guarantee that omissions disappear; effectiveness in actual conversations, resumptions, and revisions requires separate evaluation.

## Use and scope

When a user with comic-production experience says a step should be mandatory in future, discuss registration through `manga-process-checker`. Without a registration request, do not create candidates or ask about registration on every production/revision. This is explicitly requested project configuration, distinct from ordinary feedback records.

| Level | Use | Where reflected |
| --- | --- | --- |
| `instruction` | Check execution when reporting milestones such as script/page completion; address omissions | Requirements file and review records |
| `strong-instruction` | In addition to report-time checks, put execution at the specified checkpoint in AGENTS.md; optionally use Hooks to catch forgotten reports | Requirements file, managed AGENTS.md section, and Hooks selected through discussion |

Both levels are mandatory user requirements. `instruction` does not mean optional. Mark inapplicable items with reasons, but never waive, downgrade, or remove them based on Codex's preference. Change/remove requirements only on explicit user instruction.

Discuss the action, conditions, effective start, level, scope unit, deadline, evidence, carry-forward permission, and destination. "From now on" applies to future work/revisions; discuss scope before applying to past deliverables. If delegated, Codex decides within that scope and explains/records why. Delegation does not automatically approve Hooks trust operations.

## File roles

| Location relative to project root | Role |
| --- | --- |
| `docs/knowledge/manga/08-workflow-review.md` | Authoritative standard process; reference when checking only required steps |
| `config/process-requirements.json` | Authoritative user requirements; empty array in new distributions |
| `.work/process-checker/` | Original discussion, before/after registration, report input, execution records, and pre-Hooks backup; project-private |
| `process-checker:strong` managed region in `AGENTS.md` | Execution instructions generated from strong requirements; preserve everything outside the region |
| `.codex/hooks.json` | Optional requested Hooks; preserve other Hooks when adding |
| `scripts/process_checker.py` | Registration, relative paths, statuses, evidence hashes, explicit carry-forward, and Hooks setup/responses |

Do not copy personal requirements into the kit/shared template or a user-wide folder. Project `.gitignore` excludes the requirements file, `.work/`, and Hooks. Before publishing a project's AGENTS.md containing strong requirements, review its personal-settings region too. Maintain only the empty authoritative file in the distribution kit.

## Commands and registration format

Python 3.10+ standard library only. Examples run from the project root. Codex reflects the discussion and runs commands; do not require users to handwrite JSON or commands.

```powershell
python -X utf8 scripts/process_checker.py status
python -X utf8 scripts/process_checker.py checkpoints
python -X utf8 scripts/process_checker.py add --input .work/process-checker/request.json
python -X utf8 scripts/process_checker.py replace --input .work/process-checker/replacement.json
python -X utf8 scripts/process_checker.py remove --id proc-example --decision-note 'Summary of the user instruction to remove this requirement'
```

Registration example; do not add it as a default requirement:

```json
{
  "id": "proc-script-review",
  "level": "instruction",
  "instruction": "After completing the panel script, review consistency between character goals and actions",
  "checkpoint": "script-complete",
  "scope": "project",
  "condition": "When this project's panel script is created or substantively revised after registration",
  "completionCriteria": "A review identifies the version and records how findings will be addressed",
  "carryForward": true,
  "enforcement": "report",
  "decision": "discussed",
  "decisionNote": "The user specified content, level, checkpoint, and carry-forward to the next project"
}
```

- `id`: stable identifier for changes/reports/removal; `add` assigns one if omitted.
- `level`: `instruction` or `strong-instruction`. Discuss if unspecified; Codex chooses only when delegated.
- `scope`: `project` or `page`. If chapters or other units are needed, explain current support and discuss scope handling.
- `condition` / `completionCriteria`: applicability and completion criteria. The main agent reads matters requiring judgment, such as expressive effectiveness; a script alone cannot certify quality.
- `carryForward`: whether to copy on explicit carry-forward. Use `false` for this project only.
- `enforcement`: `report` for `instruction`; `agents` or `agents+hooks` for `strong-instruction`. Registering the latter does not install Hooks.
- `decision` / `decisionNote`: actual discussion (`discussed`) or delegation (`delegated`), and the decided scope. Input values alone are not proof of consent; Codex must verify the actual user's statement. Keep verbatim discussion and project-specific details in `.work/`; retain necessary generality in text intended for carry-forward.

Adding/changing requirements updates the managed AGENTS.md section too. For direct edits to the authoritative file, confirm intent through the existing change procedure and, once authorized, use `sync-agents`. Never silently undo user edits.

## Checkpoints

| Identifier | Milestone |
| --- | --- |
| `brief-complete` | Brief complete |
| `script-complete` | Panel script complete |
| `layout-complete` | Panel layout plan complete |
| `name-complete` | Thumbnails complete |
| `before-generation` | Before page generation |
| `after-generation` | After page generation |
| `page-complete` | Page complete |
| `before-preview` | Before PNG presentation |
| `after-preview` | After PNG review |
| `before-psd` | Before PSD creation |
| `after-psd` | After PSD creation |
| `before-handoff` | Before handoff |

This order indexes overdue requirements; it does not command every stage. If a generation method/request scope skips a stage, compare applicability and mark it `not-applicable`. Discuss a suitable milestone for custom checkpoints; do not silently substitute another with changed meaning.

## Reports and evidence

```powershell
python -X utf8 scripts/process_checker.py report --input .work/process-checker/report.json
```

```json
{
  "checkpoint": "page-complete",
  "scope": "page",
  "subject": "page-001",
  "revision": "v1",
  "results": [
    {
      "id": "proc-script-review",
      "status": "done",
      "note": "Read the target script and review, and confirmed that responses to the findings are recorded",
      "evidence": ["docs/story/TEXT-STORYBOARD.md", "docs/reviews/STORY-REVIEW.md"]
    }
  ]
}
```

If the example review document does not exist, reference actual records. An empty template or one-line "done" statement is insufficient. The tool cannot certify input JSON as true. Canonical statuses are `done`, `not-done`, `unverified`, `awaiting-user`, and `not-applicable`.

- Check project-wide requirements due at or before the report checkpoint and requirements for the reported page. Unreported items are `unverified`; retain prior unresolved matters.
- Page completion requires `scope: page`, page ID, and revision. A passing first page does not cover the second. After a revision, update its version, retain old records, and check the new version.
- Include target manuscripts in evidence so project-wide requirements can also be rechecked after manuscript changes. `done` needs an existing file; SHA-256 is captured when saving. Changed evidence or instructions later become `unverified`.
- `not-applicable` and `awaiting-user` need specific reasons too. Do not invent responses or interpret conditions arbitrarily to pass. Unrelated work may continue while waiting.
- Before handoff, compare actual page inventory with records. The tool does not infer page existence from filenames: the main agent lists all targets and reports each latest revision.
- An empty unresolved list from `status` does not verify unreported stages/pages. The main agent following the skill judges the meaning of reports and deliverables.

A consultation-only turn with no production progress may report `{"noProgress": true, "note": "Explained settings only; no production stage advanced"}`. Existing omissions remain unresolved. Do not use this to skip checks after actual work.

## Strong requirements and Hooks

First state conditions/deadlines in AGENTS.md. Check irreversible prerequisites, such as supplying references or obtaining an answer before generation, before execution.

Before adding Hooks, check the environment's Python invocation and existing Hooks. `install-hooks` defaults to displaying a proposal without changes. Confirm approval of that proposal or that it falls within current delegated scope before `--apply`.

```powershell
python -X utf8 scripts/process_checker.py install-hooks
python -X utf8 scripts/process_checker.py install-hooks --apply
```

Provided Hooks are `UserPromptSubmit` (prompts consulting strong requirements and reporting this turn) and `Stop` (requests continuation once if a report/evidence is missing). They do not use a separate AI to judge report content. Check semantic pre-generation conditions through AGENTS.md and the skill. If a dedicated `PreToolUse` is needed, separately discuss/implement the exact tool, checkable conditions, and recovery from a stop. Do not execute arbitrary command strings from requirements files.

After saving configuration, review/trust Hooks in the actual Codex environment. The official CLI entry point is `/hooks`. If unsupported, disabled, Python unavailable, or untrusted, distinguish AGENTS.md operation from inactive Hooks. Do not fabricate trust records, enable features without permission, or use trust-bypass arguments. Verify in a session that loaded the new settings.

Hooks request continuation at most once per turn. They do not seek automatic fixes for `awaiting-user`, or continuation after a no-progress consultation report. Explain and hand over unresolved issues without treating them as checked. Errors/lock conflicts generate warnings; allowing continuation is not validation success.

## Carrying requirements to a new project

The user explicitly identifies the source. At the kit root:

```powershell
.\scripts\New-MangaProject.ps1 -ProjectName 'New Comic' -ProcessRequirementsFrom '../Previous Comic'
```

Without a source, begin with an empty list. With a source, Python 3.10+ is required. Validate its format first, copy only carry-forward requirements, and reflect strong ones in the new AGENTS.md. After moving to the new project, review registered content/conditions before production.

From an already-created project with no requirements:

```powershell
python -X utf8 scripts/process_checker.py import --from-project '../Previous Comic'
```

Do not transfer execution records, assets, Hooks configuration, trust information, paid-use permissions, or external-transmission permissions. Preserve `agents+hooks` intent as a requirement, but install/trust actual Hooks separately in the new environment. If the destination already has requirements, stop and discuss differences. Copied projects do not automatically synchronize.

## Sources and verification scope

- [公式Skillsガイド](https://learn.chatgpt.com/docs/build-skills): skills bundle procedures, references, and optional scripts; selected by explicit invocation or description match. No guaranteed continuous monitoring.
- [公式AGENTS.mdガイド](https://learn.chatgpt.com/docs/agent-configuration/agents-md): loading project instructions at work start; reference for storing strong project-specific instructions.
- [公式のSkills運用例](https://developers.openai.com/blog/skills-agents-sdk): design reference for conditional mandatory skills in AGENTS.md, procedures in skills, and repeatable processing in scripts.
- [公式Hooksガイド](https://learn.chatgpt.com/docs/hooks): checked `UserPromptSubmit`, `Stop`, input/output, `stop_hook_active`, review/trust of unmanaged Hooks, and Windows `commandWindows`. Some paths are outside Hooks coverage; they do not guarantee complete execution.

Sources retrieved/checked 2026-09-21. Registration format, two levels, explicit cross-project copying, and state management are kit-specific proposals. Distinguish official-specification review from implementation testing and conversation-effectiveness evaluation. For the kit's automated checks and tests, follow the execution checks in the source kit's `docs/publication.md`, which is not distributed to projects.
