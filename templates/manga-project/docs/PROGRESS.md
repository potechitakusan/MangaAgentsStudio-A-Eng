# Progress and resumption notes

Current: created from the initial template; comic production has not started.
Creation date, title, distribution version: see `../project.json`.

## Completed

- Shared knowledge, review skills, emphasis settings, and recording templates installed.

## In progress

- None. No external generation process started.

## Decisions and open items

- Page count, story, and characters unset. Actual generated dimensions unverified. Default: fit frames and final PNG to actual full-page generation. See OPTION and `config/page-layout.json`. Printing disabled by default. English reading is left to right with horizontal lettering.
- Review/revise PNG first; proceed to PSD after no revisions remain. Without PSD instructions ask and wait; do not re-ask existing instructions. Requested PSDs include creation, validation, and handoff. Normally a human finishes in CLIP STUDIO PAINT and publishes. CBZ only on explicit request.
- PNG: not presented (after presentation record path/version/pages/user answer). PSD instruction: none.
- Record "awaiting PNG confirmation" or "awaiting PSD answer" when applicable. Silence is not no revisions or an instruction.
- Knowledge: `docs/MANGA-KNOWHOW.md`; handoff/validation: `docs/production/PSD-HANDOFF.md`.

## Next actions

- Read `config/process-requirements.json` and, if requirements exist, `.work/process-checker/state.json`. Carry unresolved instructions, pages, versions, and next actions forward. Past completion does not verify changed manuscripts.
- Resolve OPTION, record current purpose/constraints in `docs/story/BRIEF.md`, and make `docs/PLAN.md` concrete.

## Production options

- Status: not started. At production startup record effective values/sources for every adopted item.
- Checked OPTION: unverified (record presence, SHA-256, date at startup).
- PRINT-OPTION: unverified; printing disabled by default, details only if enabled.
- Page settings: unverified (record adopted values and `config/page-layout.json` presence/SHA-256).
- Panel/generation method: not adopted. Default templates with recorded custom-staging exceptions; imagegen whole-page generation with numbered layout references. Record per-page choices, references, and post-generation comparisons in `docs/production/PANEL-LAYOUT-POLICY.md`.
- Japanese polishing: disabled, legacy Japanese source text only. Initialize on first work and record selection, installation, and answer about missing Git. For Gemini refer to explicit pre-install consent/scope and `.work/optional-skills/` records; environment availability is not permission.
- Pending changes: none. After startup record old/new values and user answers; do not overwrite adopted values before confirmation.
- Procedure: [Production options](knowledge/project-options.md).

## History

- Initial creation. Feedback only on recording request.
