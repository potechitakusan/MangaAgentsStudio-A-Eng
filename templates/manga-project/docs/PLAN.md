# Production plan

Status: newly created; story content not yet configured.

At startup/resumption check `config/process-requirements.json`. If requirements exist, use the [process checker](knowledge/process-checker.md) to compare evidence at milestones and before handoff; also check strong instructions before their specified stage. Carry unresolved items into next actions. Zero requirements need no detailed checks.

On first work resolve OPTION and initialize [optional polishing](knowledge/optional-skills.md). Legacy Japanese polishing is disabled for English work and only for explicitly selected Japanese source text. Install only if enabled; do not fetch if disabled. Ask before installing missing Git; Gemini requires text-transmission/quota consent before installation regardless of environment readiness. Continue normal production while installation is deferred.

1. Receive characters, synopsis, and page count; start Web PNG work with OPTION defaults. Record adopted values in progress and request/provisional details in `docs/story/BRIEF.md`. Do not demand every option/print answer.
2. Decide characters, desires, obstacles, and ending; design scene changes.
3. Make rough storyboards with final-volume lettering from the text storyboard. Use templates as a rule and record per-page IDs in `docs/production/PANEL-LAYOUT-POLICY.md`. For necessary custom layouts record target, intent, and reason; prioritize user-required/disabled templates. Compare alternatives where needed, read through, review, and integrate revisions. Map to film shots only when useful.
4. Establish character standards with references and a few generation tests, then produce pages. For imagegen follow [Panel workflow](knowledge/panel-layout-policy.md): actually supply numbered template/custom layout images and panel contents, default to whole-page generation, and record reasons for separate-panel generation. Follow environment-specific NovelAI/other procedures. Distinguish requested and actual generation dimensions; use [Page settings](knowledge/page-layout.md) for layout/final PNG dimensions and margin/stroke scaling. Compare generated panel count, placement, reading order, and content with the plan.
5. Apply adopted direction (default horizontal English) and use-specific DIALOGUE.md settings. Compare generated lettering against source and fix it; place later lettering as needed. Check left-to-right reading, time transitions, density, and movement continuity. Check adopted correction conditions on later pages.
6. Make all requested PNG pages with ordered filenames; inspect no guides and readability at publication size, then present. Apply/re-present revisions and confirm the latest PNG needs none.
7. If PSD creation was not requested, ask and wait without creating it. Do not re-ask an existing instruction. Record reviewed PNG version/pages/answer and PSD instruction in `docs/production/PSD-HANDOFF.md`.
8. With both PNG confirmation and PSD instruction, create target PSDs; validate reopening, layers, recomposition against confirmed PNGs, and full read-through.
9. Record source dialogue, PSD specifications/results, and human finishing in `docs/production/`; hand off. Requested PSDs reach Codex completion here.
10. A human finishes in CLIP STUDIO PAINT and decides publication. Save feedback only when requested; do not ask whether to record it.

Specify target, deliverables, and completion criteria for each request. Awaiting PNG/PSD answers is legitimate; silence is neither no revisions nor a creation instruction. For PNG-only work or no/deferred PSD answers, record scope/status.

Before each stage inspect OPTION changes and apply adopted options to this plan. Defer unconfirmed changes to affected work.

References: [Applying options](knowledge/project-options.md), [Know-how](MANGA-KNOWHOW.md), [PSD handoff](knowledge/psd-handoff.md). CBZ requires explicit request.
