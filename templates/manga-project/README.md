# Manga project

Codex must not launch, connect to, or control Chrome/Edge or use `chrome:control-chrome`. Inspect images with image-display tools; the user opens supplied HTML or other paths as needed.

Provide characters, synopsis, and page count to produce all Web comic pages through PNG without extra configuration. Defaults: single pages, white background, left-to-right reading, horizontal English lettering. For full-page generation, fit frames and PNG dimensions to the tool's actual output. OPTION can specify generation, frame-layout, and final dimensions separately. Image-generation/editing capability is required. Example: "The characters are Alex and Sam; the synopsis is [story]. Make an eight-page comic for online publication." Wait for the user's PNG revision answer.

Title/source kit are in `project.json`. At startup apply [OPTION.md](OPTION.md), state intent in `docs/story/BRIEF.md`, update `docs/PLAN.md` and `docs/PROGRESS.md`. Edit "Current setting" or state changes in conversation. Missing items use defaults; later edits require intent confirmation. Print-only [PRINT-OPTION.md](PRINT-OPTION.md) need not be completed for Web work.

Use panel templates as a rule, with reasoned custom layouts for staging needs. Supply imagegen an actual numbered layout image and panel contents in either case; default to whole-page generation and compare results to the plan. OPTION can set "required," "do not use," or generation units. See [Panel workflow](docs/knowledge/panel-layout-policy.md).

Margins/guides: [Basic-frame settings](docs/knowledge/page-layout.md). Lettering: [Dialogue source and placement](docs/production/DIALOGUE.md). PSD example: "After PNG confirmation, make a PSD with art, balloons, and text separated." Raster text may not be editable as strings; include source dialogue.

[Legacy Japanese polishing](docs/knowledge/optional-skills.md) is disabled for the English workflow and only applies to explicitly selected Japanese source text. It is not English polishing. When enabled for that work, installation begins at the first project session. `humanizer-jp` needs Git; ask before installing missing Git. `japanese-natural-writing` uses Gemini; confirm transmission/quota consent before installation even if the environment is ready. Silence/refusal defers installation while normal production continues.

After production, explicitly request future requirements, e.g. "Register character review after the text storyboard as an instruction." The [process checker](docs/knowledge/process-checker.md) discusses content, conditions, checkpoints, evidence, and carryover. "Instruction" is checked at stage reports; "strong instruction" also appears in AGENTS.md, with Hooks if necessary. If delegated, Codex chooses details. Save instructions in this project and read on resumption. The distributed list is empty, requiring no detailed checks. Next-project carryover requires naming the source project.

- Knowledge entry point: [Production workflow](docs/knowledge/review-workflow.md)
- Knowledge/skill map: [Shared know-how](docs/knowledge/review-workflow.md#common-knowledge)
- Humor, appeal, emotion, relationships, development: [Scene supervision](docs/knowledge/supervision/README.md), [records](docs/reviews/SUPERVISION.md)
- Requested feedback records: [Feedback workflow](docs/knowledge/feedback-workflow.md)
- Environment: [Setup](docs/SETUP.md)
- NovelAI key, connection, single-image generation: [API instructions/request prompts](docs/knowledge/novelai-api.md)
- Settings check: `.\scripts\Resolve-ReviewProfile.ps1 -Preset 'daily'`
- Toolkit terms: [MIT License](docs/toolkit-license.txt), not automatically applied to created comics or supplied assets.

Open this project's absolute folder path supplied at creation and begin in a new Codex conversation. Reopen from the kit into the work project. If you need help, describe your environment (Windows/Mac, app/VS Code). Only when asked for steps, Codex checks current official information for that environment and includes URLs/check date. If you know how, simply open the folder without replying. See [Reopen Codex in the project folder](docs/knowledge/codex-operation.md#reopen-codex-in-the-project-folder). No in-kit production exception file is needed here.

Choose from [Comic know-how](docs/MANGA-KNOWHOW.md): 77 techniques, fundamentals, staging/comparison workflows, and templates. Move from text storyboard to rough storyboard/artwork, then review/revise PNGs. Once no revisions remain, check PSD instructions; if absent, ask and wait, otherwise do not ask again. Create, validate, and hand off under [PSD requirements](docs/knowledge/psd-handoff.md). Normally humans finish in CLIP STUDIO PAINT and publish. CBZ requires explicit request. Film/television support only scenes that need them.
