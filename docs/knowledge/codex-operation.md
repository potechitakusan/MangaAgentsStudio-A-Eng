# Working with Codex

## Guidance for Antigravity mode

Only when the user explicitly chooses Gemini (Antigravity), select `-AgentMode Antigravity` during creation (`--agent-mode Antigravity` at the Linux Bash entry point). Verify the project's `project.json`, `GEMINI.md`, and `AGENT-MODE.md` exist, and provide an absolute-path link plus copyable text with “Reopen Antigravity in this folder.” The environment-specific guidance policy, reopening from kit to project, and relative saved paths below also apply. Consult current official Antigravity information only when the user requests operating steps. Use the project's dedicated `AGENT-MODE.md` for adaptations.

Added 2026-10-03. When Antigravity mode is not selected, retain the Codex behavior and guidance below.

Skills and instruction files checked: 2026-09-12. Official reopening information retrieved and checked: 2026-09-13.

The post-creation guidance policy changed at the user's request on 2026-09-19. Research and explain operating steps only when the user asks. Official information was not re-researched for that policy change.

Optional editing-skill installation was additionally checked on 2026-09-19. Based on the [AGENTS.mdの公式説明](https://learn.chatgpt.com/docs/agent-configuration/agents-md), project instructions initialize the feature when work first begins. Based on the [スキルの公式説明](https://developers.openai.com/ja-JP/docs/build-skills), install skills in the project's `.agents/skills/` with implicit invocation disabled. Changes are detected automatically; reopen only if they are not recognized. See [optional editing skills](optional-skills.md) for selection, confirmation when Git is missing, and permission to consume Gemini quota. This is not an OS startup action triggered merely by opening a folder. These Japanese-source editing skills are disabled by default in the English edition; English editing support is not established.

## Browser automation is prohibited

User-specified kit rule (2026-09-21): do not use `chrome:control-chrome`, or have Codex launch, connect to, or control Google Chrome or Microsoft Edge. This includes Playwright, Selenium, CDP, headless execution, and commands opening the default browser. Being installed or connectable is not permission. Do not evade the rule by switching control methods.

Inspect local PNGs and similar files with an image-viewing tool. Research through Web search/retrieval without browser control. If a person needs to view HTML or similar content, provide its path or URL for the user to open. For NovelAI style samples, continue to check existence and present the absolute path only.

Include this restriction in the kit and new-project AGENTS.md files. It applies regardless of the number of registered process requirements and is a shared kit restriction. It does not require uninstalling browsers/plugins or changing OS settings.

## Reopen Codex in the project folder

**Kit operating rule:** the source kit is for maintenance and distribution. Normal comic production takes place in an individual project created outside the kit with `scripts/New-MangaProject.ps1`. After confirming successful creation and the presence of `project.json` and `AGENTS.md`, give the user the following guidance. Do not treat `-WhatIf` or partial failure as completed creation.

1. Show the full absolute path as both a clickable Markdown link and the same directly copyable path text. Use the returned `AbsolutePath` or resolve the actual destination; do not guess names or paths.
2. Say, "Please reopen Codex in this folder. Comic production will begin in a new conversation opened in the project folder."
3. Add, "If you need help, tell me your environment (Windows or Mac, app or VS Code), and I can explain the steps." Do not research/explain steps on every creation or require everyone to answer whether they need instructions. Users who know how may open the project without replying. Silence confirms neither reopening nor a request for instructions.
4. Explain that the new session should read `AGENTS.md`, `project.json`, `docs/PLAN.md`, and `docs/PROGRESS.md`, then begin from `docs/story/BRIEF.md`. For an existing project, read progress and resume.

Display absolute paths in the reopening message. Use relative paths in distributed documents, settings, and saved records; do not embed machine-specific absolute paths in templates. Merely changing directory in the current conversation does not mean Codex's project or loaded instructions have switched.

### Research current official instructions only when requested

**Instructions for Codex:** if the user asks how to open the project or says they do not know how, explain steps appropriate to their environment. Ask their OS and app/VS Code choice only if unknown; do not repeat established questions. If instructions were requested, do not reconfirm whether to explain them.

Do not reuse the following examples as permanently current instructions. Search current official information and actually read the relevant page. Use the OpenAI Docs workflow if available. If a page moved, find it again on the official site. The target must be the created project folder whose existence was confirmed.

- For the ChatGPT Windows/Mac app, check installation, sign-in, selecting Codex, adding/selecting a local folder, and starting a new conversation for the user's OS.
- For VS Code, check installation of the official Codex extension, selecting the project folder, opening/signing into Codex, and starting a new conversation.
- Research multiple environments if requested; every OS/app need not be covered every time.
- Include official source links and the check date in the explanation. Distinguish verified operations from unverified on-screen labels. If searching is unavailable, state that the latest information is unverified and provide only dated reference information. Do not invent button names or support claims.

### Example: opening in the ChatGPT Windows or Mac app

**Confirmed from official information (2026-09-13):** on both OSes, users can sign into the ChatGPT desktop app and select Codex from the ChatGPT dropdown. Sources: [デスクトップアプリ](https://learn.chatgpt.com/docs/app) and [Quickstart](https://learn.chatgpt.com/docs/quickstart).

1. Open the ChatGPT app for the OS and sign in. If absent, install using official instructions.
2. Select Codex from the ChatGPT dropdown.
3. Open/add the created folder as a local project. To set a folder, use the project menu's `Edit project` → `Add folder` and select the supplied absolute path. With multiple folders, use `Make primary` for the comic project.
4. Select the project, open `New chat`, and request production.

Folder addition and primary-folder selection follow [Projects and chats](https://learn.chatgpt.com/docs/projects). The primary folder determines new conversations' working location and the base for automatic `AGENTS.md` and skill detection. Applying this to the comic project folder is a kit rule. Actual Windows/Mac UI operation is untested; check current official information when explaining it.

### Example: opening in VS Code

**Confirmed from official information (2026-09-13):** VS Code uses the Codex extension, and the open folder/workspace becomes the local project. See [Codex IDE extension](https://learn.chatgpt.com/docs/codex/ide) and [Projects and chats](https://learn.chatgpt.com/docs/projects).

1. Open the created project folder in VS Code and confirm it matches the supplied absolute path.
2. If needed, install the extension from OpenAI's official instructions and sign in.
3. Select the Codex icon. If absent, run `Codex: Open Codex Sidebar` from the command palette.
4. Start a new conversation for the project folder. In a multi-root workspace, select this project's root.

Installation and the opening command follow [Codex IDE extension](https://learn.chatgpt.com/docs/codex/ide); workspace selection follows [Projects and chats](https://learn.chatgpt.com/docs/projects). Actual VS Code UI operation is untested. Recheck labels, commands, and sign-in methods when giving instructions.

## Skills and instruction files

Official documentation describes selecting candidate skills by name and description and reading their bodies when needed. Repository-local skills can live in `.agents/skills/`: [Build skills](https://learn.chatgpt.com/docs/build-skills).

AGENTS.md holds project instructions with parent/child scopes and overrides. Start at the project root and verify recognition of intended instructions: [AGENTS.md公式文書](https://learn.chatgpt.com/docs/agent-configuration/agents-md).

[Rethinking skills and prompts for GPT-6 Astra](https://developers.openai.com/blog/rethinking-skills-and-prompts-for-gpt-6-astra) informed skill design: specific triggers, reading only necessary material, and avoiding bloated always-on instructions.

## Project design decisions

- Put stable rules in AGENTS.md, detailed knowledge in docs, situation-specific consultation/review procedures in skills, and the current production objective in the request.
- Skills are not independent running processes. The main agent follows a procedure or gives an available sub-agent the scope and procedure.
- Progress files do not preserve running processes. After a session ends, check recorded outputs and execution IDs before resuming; do not blindly resubmit generation requests.
- Record current objective, completed files, running processes, decisions, uncertainties, and immediate next actions. Do not record external-service secrets.
- Do not hard-code model names or tool availability in skills. Check the environment and do not guess capabilities or prices.

This document is distributed to projects. Individual verbatim instructions and development research logs are not. The Japanese exception-marker filename documented in the kit README remains a compatibility identifier; English project content uses English.
