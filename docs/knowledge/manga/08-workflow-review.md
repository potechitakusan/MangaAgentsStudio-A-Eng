# 08 From Comic Thumbnails to PSD Handoff

Updated: 2026-09-20. Production operations from planning to human handoff. Film scripts and video generation are supporting options only when needed.

## Production workflow

The basic inputs are characters, synopsis, and page count. Once these three are supplied in a project folder, Codex provisionally decides unspecified details and produces the work using [Web defaults](../page-layout.md). Do not turn every planning field or option into an additional question. Respect the specified page count and prepare all page PNGs with a clear order. Proceed even if the publishing destination is undecided. Print settings, additional prose polishing, and PSD creation are not prerequisites for PNG production. Continue to wait for the user's response when confirming PNG revisions.

Check the working location before starting. If the distributed production kit is open, normally run `scripts/New-MangaProject.ps1` to create a project outside the kit and show its absolute path to the user. Follow [Instructions for reopening](../codex-operation.md#reopen-codex-in-the-project-folder), and proceed below after reopening Codex in the project folder. If already in a project, continue or resume there. Only when explicitly instructed that production must take place inside the distribution kit, begin after verifying that the user personally created `特別な理由でこのフォルダの中で漫画を作ります.txt` in the kit root. This compatibility filename means “I am making a comic inside this folder for a special reason.” Ordinary project folders do not require this file.

| Stage | Deliverable | Decision needed to proceed |
| --- | --- | --- |
| Concept and reader experience | Aim, format, page count, and intended feeling afterward | What is enjoyable, and whom do readers follow? |
| Scenes and characters | Before/after states, goals, obstacles, choices, and outcomes | Can the reasons in the premise be depicted as behavior? |
| Information and change | Actions and reactions, reader/character knowledge, recurring props | What is understood when, and what are readers waiting for? |
| Written comic script | Panel candidates, focal subjects, actions, dialogue, and purposes of silence | Can the prose become visible images and text? |
| Panel layout plan | Selected IDs per page, or custom placement, intended effect, and reason not to use a template; numbered layout images and each panel's content for imagegen | Normally use templates and follow the user's required/prohibited choices. Decide layout and reading order through the [Panel layout procedure](../panel-layout-policy.md) before generating page art |
| Thumbnails and comparisons | Page layouts containing full intended text in the selected lettering direction; horizontal English by default | Reading order, early reveals in the actual display format, temporal transitions, and visual density. Compare different allocations for uncertain scenes |
| Continuous read and integrated revision | Selected version, revision reasons, and lost effects | Do emotion, causality, and space remain coherent when individually good ideas are joined? |
| Artwork and lettering | Reference images, page or panel art, borders, balloons, effects, final dialogue, and text settings by use. imagegen normally generates the whole page including text and balloons; other methods use separate lettering after drawing ([Finishing policy](../page-layout.md#text-finishing)). Record comparisons and checks in [Thumbnail review](../../reviews/NAME-REVIEW.md) | Match panel count, placement, reading order, and content to the plan; check consistent characters, typos, accidental guide numbers, information size at publication size, continuity, and revision conditions from the preceding page. For separate lettering, finish post-art comparison first. For whole-page generation, compare the completed generated page |
| PNG preview and revisions | PNGs of the relevant pages and revision/re-presentation records | The user reviews the latest PNGs and confirms that no revisions remain. No reply means confirmation is pending |
| Confirmation of PSD creation | Confirmed PNG version, relevant pages, and creation instruction | If not instructed, ask whether to create PSDs and wait. Do not ask again when already instructed |
| PSD creation and verification | Per-page PSDs, verification images, handoff records, and original dialogue text | Reread all pages and inspect layers, dimensions, appearance, and unverified matters |
| Human finishing and publication | Manuscript finished in CLIP STUDIO PAINT and publication exports | A human decides finishing and publication. This is outside Codex's normal completion scope |

Even for “finish the comic,” ask about PSD creation after PNG review and revisions unless already instructed. PSD creation takes time; do not create it before both PNG revision confirmation and creation instructions are present. Deliver requested PSDs to the human under the [Handoff requirements](../psd-handoff.md). For PNG-only, thumbnails-only, or partial-revision requests, completion is limited to that requested scope. Resume from the necessary stage if a manuscript already exists.

When designing action, choose one main action at the panel-candidate stage. If contact occurs, record before, during, and after contact separately. More text does not compensate for missing visible information. Briefly fix the necessary people, hands, props, and backgrounds before transferring them to the page. When using generation or external transmission, record sending, retrying, regeneration, and acceptance with distinct times and reasons, and inspect existing outputs before resending.

For scenes needing an effect covered by the included supervision themes, consult `manga-supervision` about expressive options during script development. After PNG previews exist, actually view the target images and obtain improvement proposals for the same intent. Follow [Supervision routing](../supervision/routing.md); the main agent specifies the central effect and emotion to preserve, then integrates acceptance decisions. The 15 additional themes are experimental. Record checked scope and outstanding questions in [Supervision review](../../reviews/SUPERVISION.md).

## Revise according to the cause

Look for causes in this order: protagonist and goal → motivation and causality → information order → focal subject and composition → pauses → panel and balloon reading order → wording. Fix clear local errors, such as typos or wrong speakers, immediately. Break “poor pacing” into text quantity, repeated actions, missing purpose, and omitted important reactions.

For a continuous read, do not explain intent first. Record who wanted what, where circumstances changed, where rereading occurred, what was expected next, and how the final relationship was understood. Record agent inspection separately from a first-time human trial read; do not invent unperformed reader evaluation.

## Records and practice

Briefly record revisions useful on later pages in the existing `docs/reviews/NAME-REVIEW.md`, including reason for acceptance, applicability, exceptions, and page scope. Check applicability when starting the next page; do not turn a local mistake into a project-wide ban. Consolidate lettering settings in `docs/production/DIALOGUE.md`. Distinguish handoff within this project from kit feedback recorded only on request.

Put decisions, unresolved issues, and next revisions in progress records; acceptance decisions in reviews; and reusable observations in feedback only when asked to record them. Without a request, do not ask whether to record feedback. Append the reason for changes instead of rebuilding the settings collection after every conversation.

Small practice tasks include depicting one person's request to another without words, showing a conversation using only the listener, rendering the same scene in eight and five panels, changing characters or props in the same composition, and comparing the same conversation in an entryway and kitchen. Counts are exercise conditions, not fixed project rules.

Under constraints on pages, background quantity, or cast size, first decide which functions to cut and which emotions to preserve. Do not convert film budgets or running times into drawing effort or page counts. Do not normally create CBZ files; do so only when explicitly requested.
