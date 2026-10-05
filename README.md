# Comic Production Kit — English Edition

Knowledge, ten skills, and a project template for planning a comic with Codex and developing its written script, thumbnails, artwork, and PNG review.

This kit was originally designed for creating manga for Japanese-speaking readers. This English edition was produced through automated AI translation of that Japanese kit, with subsequent localization and review. Some guidance and expressive conventions may still reflect Japanese manga practices.

This edition uses **US English, left-to-right and top-to-bottom panel and balloon order, and horizontal English lettering**. Dialogue is normally centered within balloons and uses standard English punctuation. Source filenames and machine identifiers are retained where needed for compatibility. Source citations retain their original Japanese wording. See [English maintenance records](docs/localization/README.md) for translation policy, validation, independent semantic review, and Japanese-upstream updates. Source kit version: **0.5.0**; localization revision: **0.5.0-en-US.1**.

**This folder maintains and distributes the kit. Normally, create a separate project outside it with `scripts/New-MangaProject.ps1` (or `scripts/New-MangaProject.sh` on Linux), reopen Codex there, and make your comic in that project.** `templates/manga-project/` is the master template; do not write a work directly into it.

The original author also reports that much of the kit can be used by giving ChatGPT Work this repository's URL along with comic characters and a story. This is a retained description of the author's usage, not a new verification of current product availability.

## What you can do

After opening a separate project, you can:

- Design the reader experience and story, developing a written script into thumbnails.
- Design pages around the intended staging using a library of 79 panel-layout templates as the starting point.
- Review story, immersion, cinematic staging, readability, terminology, and character consistency.
- Consult supervision guidance for humor, appeal, emotion, relationships, and developments, obtaining script options and improvements after previewing images.
- Draw using available image-generation/editing tools, then inspect and revise PNGs.
- Once PNG revisions are complete, create, verify, and hand off any requested PSDs.
- When asked to test staging in video, assist with generation/retrieval in local ComfyUI and video editing.

## Production workflow

```mermaid
flowchart TD
    P["Create a project outside the kit with New-MangaProject.ps1 or .sh"] --> Q["Provide the absolute path and reopening guidance; explain steps if needed"]
    Q --> R["User reopens Codex in the project folder"]
    R --> A
    A["Concept and reader experience"] --> B["Characters, scenes, and information order"]
    B --> C["Written comic script"]
    C --> C1["Panel layout plan"]
    C1 --> D["Thumbnails, comparisons, and continuous read"]
    D --> E["Integrated revision"]
    E --> F["Artwork and lettering"]
    F --> G["Present PNG previews"]
    G --> H{"Any revisions?"}
    H -->|Yes| I["Revise and present again"]
    I --> G
    H -->|Awaiting confirmation| O["Wait for the PNG review response"]
    O --> H
    H -->|No| J{"PSD creation already requested?"}
    J -->|No| K["Ask whether to create PSDs and wait"]
    K -->|Create| L["Create, verify, and hand off PSDs"]
    J -->|Yes| L
    K -->|No or deferred| M["Keep PNGs and production assets"]
    L --> N["Human finishes in CLIP STUDIO PAINT and publishes"]
```

Stage deliverables and checks are in the [Production workflow](docs/knowledge/manga/08-workflow-review.md); knowledge and templates are in the [Know-how index](templates/manga-project/docs/MANGA-KNOWHOW.md). Explanations of what this folder can do also begin with creating and reopening a separate project.

## Getting started

### Linux (Bash and Python 3.10 or later)

PowerShell and additional Python packages are not required. Run from the repository root:

```bash
bash scripts/New-MangaProject.sh --project-name 'My Comic' --what-if
bash scripts/New-MangaProject.sh --project-name 'My Comic'
# Another existing parent directory and Claude mode
bash scripts/New-MangaProject.sh 'My Comic' --destination-parent .. --agent-mode Claude
# Production with Gemini (Antigravity)
bash scripts/New-MangaProject.sh 'My Comic' --agent-mode Antigravity
# Carry forward requirements only from an explicitly named project
# bash scripts/New-MangaProject.sh 'Next Comic' --process-requirements-from '../Previous Comic'
```

`--what-if` (`--dry-run`) previews placement without creating files. Names may contain Japanese characters and spaces. Existing projects are not overwritten; copying through links is rejected. Legacy argument names `-ProjectName`, `-DestinationParent`, `-AgentMode`, `-ProcessRequirementsFrom`, and `-WhatIf` also work. You may invoke the entry point by path from any working directory. Relative destinations and inheritance sources are resolved from the current working directory. Set `PYTHON` to an interpreter executable path, or let the wrapper find `python3`, then `python`.

After creation, move to the displayed project folder. Review and optional-skill entry points are included in the project:

```bash
bash scripts/Resolve-ReviewProfile.sh
bash scripts/Initialize-OptionalSkills.sh
python3 scripts/process_checker.py status
```

Optional Japanese polishing skills are disabled by default and apply only to Japanese source text. Enabling them, external retrieval, and Gemini use follow the [existing consent procedure](docs/knowledge/optional-skills.md). Project creation on Linux does not retrieve optional skills, generate artwork, or call paid APIs. Use each `.sh` entry point's `--help` for arguments. On Linux, match the case of configured preset names, scene names, and choices. JSON results go to stdout; guidance and errors go to stderr. Calling through `bash` works even if ZIP extraction loses executable permissions.

### Windows PowerShell

Run from the repository root in Windows PowerShell 5.1 or later. Existing `.ps1` entry points, arguments, `-WhatIf`, and `-Confirm` remain available. Windows creation does not require installing the Linux Python implementation; requirements inheritance still requires Python as before.

```powershell
.\scripts\New-MangaProject.ps1 -ProjectName 'My Comic' -WhatIf
.\scripts\New-MangaProject.ps1 -ProjectName 'My Comic'
```

The kit primarily targets Codex with its available built-in image generation. Only when producing with Claude, such as Claude Code, add `-AgentMode Claude`. This adds `CLAUDE.md` and Claude adaptations in `AGENT-MODE.md`, including the default use of NovelAI for art when built-in image generation is unavailable. Without that option, creation uses the default Codex configuration.

```powershell
.\scripts\New-MangaProject.ps1 -ProjectName 'My Comic' -AgentMode Claude
```

For production with Gemini (Antigravity), specify `-AgentMode Antigravity`. This adds `GEMINI.md` and a dedicated `AGENT-MODE.md`. Reopen Antigravity in the displayed project folder. Codex remains the default; Antigravity files are distributed only when explicitly selected.

```powershell
.\scripts\New-MangaProject.ps1 -ProjectName 'My Comic' -AgentMode Antigravity
```

Antigravity mode checks available generation, editing, and image viewing tools before artwork. It defaults to NovelAI panel generation with separate composition, requiring an API key, style selection, and cost checks. Chrome, Edge, and built-in browser control are prohibited. Optional Japanese polishing stays disabled by default; installing or making additional calls to Gemini polishing skills requires the existing consent procedure. See [adaptations and verification scope](templates/manga-project/agent-modes/antigravity/AGENT-MODE.md). This mode does not cover other environments such as Gemini CLI. Operation in an actual Antigravity environment is unverified.

The default destination is `../My Comic/`. To use another parent, specify an existing relative path with `-DestinationParent` that places the project outside the kit. The repository folder may be renamed. Existing projects are not overwritten. `-WhatIf` only previews placement; it does not create a project.

On success, the script displays the **absolute destination path** and a message to reopen Codex there. When Codex creates it, Codex also verifies that it exists and replies with both a clickable Markdown link and the same absolute path as copyable text. This absolute path is for reopening; documents, settings, and saved records use relative paths.

### Reopen Codex in the created project

After creation, Codex says “Please reopen Codex in this folder,” and adds: **“If you need help, tell me your environment (Windows or Mac, app or VS Code), and I can explain the steps.”** If you know how, you can open the project without replying. Reopening instructions are researched only when requested, using current official information for your environment with source URLs and a check date. See [Reopening Codex](docs/knowledge/codex-operation.md#reopen-codex-in-the-project-folder).

Open the displayed project folder in the app or VS Code and start a new Codex conversation there. Running the creation script alone does not change this conversation's working folder. Read the project's `AGENTS.md`, `project.json`, `docs/PLAN.md`, and `docs/PROGRESS.md`, then record the aim in `docs/story/BRIEF.md` and begin. Common production knowledge and skills are copied into the project. NovelAI style samples still reference the kit's `resources/novelai-style-samples/index.html`, so retain the kit when using those samples. To resume an existing work, open that project instead of creating a new one.

<a id="exception-producing-a-comic-inside-the-kit"></a>

### Exception: producing a comic inside the kit

Normally use the separate project described above. Proceed with this exception only when the user explicitly insists on production inside the kit.

1. The user personally creates `特別な理由でこのフォルダの中で漫画を作ります.txt` in the kit root using a text editor or similar tool. The compatibility filename means “I am making a comic inside this folder for a special reason.” Check that it has no duplicate extension or alternate name.
2. Codex verifies that an ordinary file with that exact name exists. Do not begin without it. Codex must not create it for the user, copy it, or run a command that generates it.
3. Begin exceptional production only with both the explicit instruction and the file. Its presence alone is not a production request.

Do not distribute this file in templates or new projects; exclude it from Git commits. Store exceptional production assets and manuscripts in private areas such as `.work/`, separate from common knowledge, skills, and project templates. Editing the kit's own documents/scripts or conducting distribution tests does not require this marker.

## Scope and requirements

Image-generation tools, PSD creation/reloading tools, CLIP STUDIO PAINT, and model files are not bundled. The kit provides procedures for checking the necessary environment and proceeding. Video utilities require Python 3.10 or later; editing requires ffmpeg and ffprobe.

Without a PSD instruction, ask whether to create it after PNG revisions are confirmed and wait for the answer. Do not ask again if it has already been requested. Create CBZ only when explicitly requested. Record feedback only when asked to retain it; do not ask whether to record it.

## Frequently asked questions

### May I publish a comic made with this kit? Is credit required?

Yes. The repository's author claims no rights in your comic and imposes no additional restrictions on it merely because you used this kit. Credit for using the kit is optional.

For works with strongly political content or strong hostility toward others, the author asks that you refrain from credit or other wording associating the work with this kit. This is a request from the author, not a condition limiting use.

When using third-party works, characters, or assets, including fan works, check the relevant rights holders' guidelines and terms. The kit also assumes AI services may be used during production; users are responsible for checking the applicable service and model terms.

### Which ChatGPT model should I use?

The original author reports prototyping and operating on ChatGPT Pro with “Astra ExtraHigh.” The author also tried “Astra Ultra” but did not perceive a major difference beyond apparently greater allowance consumption. At the time of the original writing, reports on X described producing roughly 16–18 pages within a five-hour limit using the Work screen on ChatGPT Plus.

These are historical impressions from the author's environment and contemporaneous social-media reports, not current verified specifications. Model names, reasoning options, and limits may change. Complexity of the work and changes in Astra's capabilities or limits may affect results.

### Can I set parameters before production?

See the project's `OPTION.md`. Options include panel-template use, selection rates by panel count, limits on repeated three-wide-tier layouts, lettering direction, and PSD creation. Ask Codex about `OPTION.md` at the start if you want an explanation of how each option changes behavior. Unspecified choices use defaults; this English edition defaults to horizontal English and left-to-right reading.

### What changed in version 0.5.0 since the 0.4.0 release?

Version 0.5.0 includes the features added in 0.4.1 and 0.4.2 and the fixes made since. The main changes since the 0.4.0 release are summarized below.

New projects receive the updated documents and scripts. Existing works are not updated automatically. To bring the changes into a work in progress, ask Codex to compare it with the kit and make the necessary updates so that the work's own settings and revisions are kept. The US English reading and lettering defaults of this edition remain in effect.

1. **Steps for editing and regenerating NovelAI characters, style, and backgrounds**

   Each panel's request JSON is saved so that a human can generate, choose candidates, and rebuild PNGs; PSDs can also be created when needed. The procedure for gathering prompts into `.env` variables now covers style and backgrounds as well as characters. You can edit `.env` directly, or edit separate text and apply it with a command, and Japanese values are supported.

   Who does what, example requests for preparation, example prompt changes, and how to run the commands are collected in [Editing characters, style, and backgrounds](templates/manga-project/docs/novelai-prompts/README.md). You can start from a work whose prompts are already assembled or whose PNG previews are finished.

2. **NovelAI position pins, and per-panel requests and verification**

   We added a procedure for position pins, which specify where characters and other elements appear. It distinguishes V5 free placement from the 5×5 placement of V4/V4.5, reinforces positions in text, and checks the result after generation and after cropping. The API request example with coordinates is presented as a candidate to verify; actual generation results and placement accuracy are unverified. See the [position-pin production procedure](templates/manga-project/docs/knowledge/novelai-composed-production.md#position-pins) and the [API request example](docs/knowledge/novelai-api.md).

   We also made concrete the procedure for writing out, in each request, the contact between a character and an object, who does what, and the clothing, belongings, and positions that continue from the previous panel. It covers generation dimensions and cropping to fit the panel, warnings such as missing character features, and verification after generation. Even without automatic warnings, Codex checks the content of the requests and the images. See [NovelAI drawing and composition procedure](templates/manga-project/docs/knowledge/novelai-composed-production.md) for details.

3. **Typesetting of balloons and vertical text, and review after drawing**

   We added `scripts/typeset_manga.py` to projects for placing text after drawing. It handles balloon types, tails that point toward the speaker, vertical dialogue, output to transparent layers, and overflow checks. We also added to the production procedure a comparison of the drawn images with the plan, and checks after typesetting. The original Japanese release supports vertical dialogue; the English edition defaults to horizontal, centered English text.

   Codex normally handles this, so tell it the balloons or revisions you want. With imagegen, text and balloons are generated inside the image by default; with NovelAI and similar methods, they are added separately after drawing. See [Text, balloons, and finishing](docs/knowledge/page-layout.md).

4. **Linux support, and creation modes for Claude and Gemini (Antigravity)**

   On Linux, a project can be created with Bash and Python 3.10 or later, so PowerShell is not required. Modes for Claude and for Antigravity were also added. Only when the human specifies the environment is the instruction file for that environment copied into the work. See [Getting started](#getting-started). Operation in an actual Antigravity environment is unverified.

5. **Procedure for external drawing that uses roughs and reference images**

   The `manga-external-panel-i2i` skill draws panels with Qwen or similar tools from Blender renders, roughs, and reference images of characters and props. Based on production records with Qwen-Image 2.1, it also collects cautions such as confusing a character's left and right and filling in unwanted faces. See [Panel drawing with external generation](docs/knowledge/external-panel-i2i.md). Whether other models achieve the same effect is unverified.

### What changed in version 0.4.0, and how do I use it?

There are five main changes.

Use the request examples below after creating a project and opening Codex in it. Characters, synopsis, and page count are normally enough to begin a comic for web publication. You need not fill every configuration field; preferences can be given conversationally.

**If you choose Japanese prose polishing through Gemini (agy) or the NovelAI API, relevant text or generation instructions are sent to external services and may consume allowances or incur charges. Confirm the service, material sent, and cost conditions. Gemini allowance use must be approved before installation; NovelAI generation consuming Anlas requires explicit instructions covering that use. These options do not guarantee the intended expression or improved quality.** Japanese-polishing options are retained for Japanese-language work and are not English-polishing defaults.

1. **Scene-specific supervision**

   The kit includes knowledge for 16 themes, including comedy, straight-man responses, romance, fear, and reversals. Use it for script consultation and improvement proposals after viewing PNG previews.

   **Usage:** Name the scene and intended effect, for example, “Review this scene so the embarrassment and affection come through,” or “View this PNG and suggest ways to make the joke clearer.” You do not need to name a specialist skill.

   The 15 themes other than comedy are experimental. General reader effects remain unverified, so check each project's PNGs and trial reads. Use is not guaranteed, nor is improvement in quality.

2. **Panel layout and page-generation improvements**

   Templates remain the default, with custom layouts available where staging requires them. imagegen uses a numbered layout image as a reference and normally generates the whole page at once. Afterward, check panel placement, reading order, and dialogue.

   **Usage:** Usually no extra instructions are needed. You may ask for custom layout on showcase pages, mandatory templates on all pages, or free design without templates. The project's “Panel layout templates” option in `OPTION.md` also controls this. See [Panel template policy](docs/knowledge/panel-layout-policy.md).

   Templates were already included in version 0.3, but Codex often failed to use them; this update sought more reliable use.

3. **NovelAI asset generation and page assembly**

   Added a workflow in which NovelAI generates artwork and Codex places frames, balloons, and text. The kit includes ten style samples and 114 transparent sound-effect assets, supports recoloring, and can export PSDs preserving untouched original art. This English edition supplies English sound effects in three visual styles with stable asset IDs and editable SVG sources.

   **Usage:** After creating a project, obtain a persistent API token from account settings on the official NovelAI site and set `NOVELAI_API_KEY` in the project's `.env`. `.env.example` is only a field-name example; never put the actual key there. Then ask to generate art with NovelAI and add frames and text afterward.

   If no style is selected, Codex gives you the sample file's location. Open it yourself in a browser and provide the preferred style ID. Codex waits for selection before drawing. See [NovelAI production workflow](templates/manga-project/docs/knowledge/novelai-composed-production.md).

   If you also want a PSD, ask for one after PNG confirmation that preserves original art and separates artwork, balloons, and text. It is created after PNG revisions are confirmed. For rasterized lettering, the original dialogue text is included in the handoff.

   **A saved API-key file may be readable by Codex with execution access or by connection code. The kit instructs Codex never to print the key in answers, logs, or shared files. This is a behavioral rule, not a guarantee against unintended output or disclosure. Git ignore settings do not prevent Codex from reading the file.** If a leak is suspected, regenerate the token in NovelAI and update its usage settings. Issuing a new token invalidates the old one, according to the [公式のトークン取得・更新手順](https://docs.novelai.net/ja/text/usersettings/account/) checked on 2026-09-21. The source URL retains the original Japanese documentation provenance.

4. **Registering and carrying forward personal required steps**

   The process checker records tasks you always want performed. When reporting production progress, Codex compares those requirements with the manuscript and review records. On resume, it rereads both the requirements and prior implementation records, identifies unperformed or unverified work, and then continues. Explicitly selected requirements may also carry forward into the next project.

   **Usage:** For example, “Ask the process checker to register reviewing character goals and actions when the written script is complete as a required step from now on.” Codex discusses applicability and check timing with you and saves it within the project.

   Choose “Instruction,” checked during progress reports, or “Strong instruction,” also written into project working rules. To reuse requirements, ask to carry them forward during project creation in the kit and specify the previous project's folder.

   **This helps Codex detect and address missed registered tasks. It does not guarantee that no work will be missed or that quality will improve.** Register and revise requirements through repeated use as production reveals what is needed.

5. **Print settings, particularly experimental**

   `PRINT-OPTION.md` consolidates print-only trim dimensions, bleed, crop marks, binding margins, resolution, color, and submission format according to the printer's specifications. It is disabled by default and unnecessary for web-only PNGs.

   **Usage:** Specify the printer, product, and desired trim size, for example, “Prepare this as a left-bound US comic for this printer; check its official submission specifications and set up print output.” Provide any established specifications or official URL.

   To configure manually, set “Print output” to “Enabled” in the project's `PRINT-OPTION.md` and fill what you know. Resolve missing specifications with Codex. Preserve web masters and PNGs and prepare print data separately.

   The file organizes and cross-checks print conditions, including required pixel dimensions and clipped text. Request PSD creation or transmission to the printer separately if needed.

   **Print settings are experimental. Printer acceptance and actual printed results remain unverified; submission compliance and print quality are not guaranteed. Before submitting, compare against current printer specifications and inspect clipped text, bleed, binding margins, color, and detail at actual size. Consult the printer or obtain proofs as needed.**

   Image-generation allowance consumption can vary with generation size, quality, and regeneration count. Final PNG output size differs from generation size. Locally enlarging and exporting an existing image does not itself generate an image, but enlargement alone may not supply the detail needed for print. [OpenAI公式の画像生成・利用枠の説明](https://learn.chatgpt.com/docs/image-generation) was checked on 2026-09-21 for differences by size and quality; this citation records that historical check.

Other expanded areas include web dimensions, margins and line widths, optional Japanese prose polishing, dialogue alignment and punctuation, character/performance/readability guidance, carrying revisions forward to later pages, and distribution verification. The English edition replaces Japanese top-aligned dialogue and punctuation restrictions with centered horizontal English and standard English punctuation.

Express preferences conversationally or in `OPTION.md`, for example, “Export the final PNG at 2000 × 3000 pixels.” For a Japanese-language project, you may request humanizer-jp for dialogue and internal monologue.

Japanese-polishing skills are disabled by default. When enabled, Codex installs the selected skill in the project and uses it on the selected material. See [Optional polishing skill procedures](docs/knowledge/optional-skills.md) for selection, first installation, resumption checks, and disabling. Gemini authorization conditions are described at the start of this FAQ item.

You can ask Codex about usage.

### What changed in version 0.3?

Earlier behavior frequently produced monotonous pages with three vertically stacked panels. The workflow was improved to select from prepared panel-layout patterns, enabled by default. If you prefer free layout without those patterns, tell Codex before production or change `OPTION.md`.

## Related documentation

- [Documentation guide](docs/README.md)
- [Architecture and distribution](docs/architecture.md)
- [Sources and retrieval dates](docs/SOURCES.md) and [Scope of film and screenwriting references](docs/knowledge/manga-sources.md)
- [Verification before committing from this folder](docs/publication.md)
- [Usage terms and third-party material](docs/RIGHTS.md)

See `distribution-version.txt` for the current distribution version. [Examples](examples/README.md) contain public PNG/JPEG images and production conditions. They are for viewing and are not copied into new projects. The bundled comic pages use English lettering and left-to-right sequencing; text-free pages and character references are retained where compatible. See the [example localization record](docs/localization/EXAMPLE-LOCALIZATION.md) for scope and source provenance.
