# Optional Japanese Source-Text Editing Skills

Updated and checked: 2026-09-19. Optional and disabled by default; unnecessary for producing Web PNGs from characters, a synopsis, and a page count. In the English edition, these third-party skills apply only to Japanese source text when explicitly selected. Do not assume they edit English. Normal English editing and source comparison remain part of the main workflow.

## Choices

Edit "Japanese polishing skill" in `OPTION.md`, or specify the choice in conversation.

| Setting | Installed material | Required checks |
| --- | --- | --- |
| Do not use | None | No external retrieval, Git check, or Gemini call |
| humanizer-jp | Pinned version of `tqkqt0/humanizer-jp` | Retrieved with Git; no separate generative AI service required. A simple "use" or "enable" instruction selects this provider |
| japanese-natural-writing | Gemini editing/Codex comparison skill published on note | Before installation, obtain permission to send this project's text to Gemini and consume its quota |

The default Japanese editing scope is dialogue and internal monologue. Explanatory text only, a project description only, or another scope may be selected. Ignore this field when disabled. Check typos, meaning, speakers, and source fidelity regardless of skill selection.

## At the project's first working session

1. Check `project.json` and the working folder, then resolve effective `OPTION.md` settings. Conversation instructions take precedence. For later file changes, follow [Applying Project Options](project-options.md).
2. Under the project's `AGENTS.md`, run the initialization script below when work first begins. It automatically retrieves/installs enabled skills; do not require manual installation commands from the user.
3. Use the same procedure on resumption. Matching installed versions/files finish without network access. If initially disabled, install at the first working session after enabling.
4. Confirm successful installation and recognition, then explicitly use the skill on the selected Japanese scope. Request reopening only if it is not recognized.

```powershell
.\scripts\Initialize-OptionalSkills.ps1
# Pass the setting adopted in conversation explicitly:
.\scripts\Initialize-OptionalSkills.ps1 -Provider humanizer-jp
```

"First launch" means Codex beginning work in the opened project, not a resident OS action triggered by displaying a folder. Do not retrieve/install skills or carry consent forward during project copying.

Use PowerShell 5.1+. Git is assumed installed and checked for `humanizer-jp` retrieval. The Gemini variant uses a direct public ZIP download and does not require Git for retrieval.

## When Git is missing

On `needs_git_consent`, ask, "Installing the Japanese editing skill requires Git. May I install Git?" **This confirmation is mandatory under the kit user's instructions.** Silence is not permission.

After permission, identify the OS, check the current [Git公式のインストール案内](https://git-scm.com/install/), and install. If Git exists but is absent from PATH, explain that before installing another copy. Confirm with `git --version`, then rerun initialization. If denied/deferred, defer the skill and continue comic production; do not repeat the same question. The script does not install Git itself.

## Always confirm Gemini use before installation

Selecting `japanese-natural-writing` does not authorize quota use. Finding `agy`, an authenticated account, or a compatible model does not either. **This confirmation is mandatory under the kit user's instructions.** Before installation, ask together:

> This skill sends the selected Japanese text to Gemini and consumes Gemini quota to edit it. May I use Gemini for the specified scope in this project and install the skill?

- No answer: `needs_gemini_consent`. Wait without retrieval/installation. Do not send test text or perform quota-consuming connection checks as environment verification.
- Denied/deferred: record `Denied` and the response. Continue normal production without Gemini; do not automatically switch to another service.
- Granted: record the actual response and text scope, then pass `Granted`. Existing explicit permission for this project, skill, and quota can be reused without asking again.

Use these calls only after an explicit answer. `ConsentNote` records the real answer and scope; an example is not evidence of permission.

```powershell
.\scripts\Initialize-OptionalSkills.ps1 -Provider japanese-natural-writing -GeminiConsent Granted -ConsentNote 'Record the actual user response and permitted scope here'
# After denial or deferral:
.\scripts\Initialize-OptionalSkills.ps1 -Provider japanese-natural-writing -GeminiConsent Denied -ConsentNote 'Record the actual denial or deferral here'
```

Reuse permission only for the same project, skill, pinned version, and approved scope. Address version changes, scope expansion, or withdrawal anew. Never copy consent to another project or automatically derive `Granted` from OPTION toggles or environment detection.

Installation only retrieves/places files; it does not call Gemini. Before use, read the execution contract and check Antigravity CLI, authentication, and support for the named model. If unavailable, defer that editing step rather than silently switching model, Gemini CLI, or direct API. Retrieval success does not demonstrate working Gemini editing.

## Storage, resumption, and disabling

- Install in the project's `.agents/skills/<skill-name>/`, never user-wide or in the kit template.
- Pinned versions and SHA-256 values are in `config/optional-skills.json`. Do not chase latest releases or silently accept changed packages. Do not overwrite existing same-name folders, different versions, or modified skills.
- Store installation results and Gemini consent in `.work/optional-skills/`. Briefly record enabled/disabled, installed/deferred, and permission scope in progress. Exclude keys, tokens, and account details.
- Retain failed downloads in `.work/optional-skills/`; do not report success. Defer only unavailable editing and continue basic production.
- After disabling in OPTION, stop using the skill even if files remain. Disable implicit invocation through installed `agents/openai.yaml` and explicitly apply only to the adopted scope. Record withdrawn Gemini permission as `Denied` and stop transmission.
- Follow the [comic comparison procedure](japanese-manga-readability.md#optional-polish) for meaning, voice, subtext, and text volume. User instructions and project settings override a third-party skill's general style rules.

## Sources, retrieval dates, and distribution scope

| Source | Findings and scope |
| --- | --- |
| [OpenAI・スキルの構築](https://developers.openai.com/ja-JP/docs/build-skills) | Checked 2026-09-19. Project `.agents/skills/` discovery, automatic change detection, disabling implicit invocation, and restarting when not recognized |
| [OpenAI・AGENTS.md](https://learn.chatgpt.com/docs/agent-configuration/agents-md) | Checked 2026-09-19. Reading instructions before work. Initializing from those instructions is a kit-specific procedure |
| [humanizer-jpの固定版](https://github.com/tqkqt0/humanizer-jp/tree/a8628b765b3de91cc7ea66ac78b5faab0777236f) | Retrieved 2026-09-19. SKILL.md, LICENSE, NOTICE, and SHA-256 checked. Preserve copyright/permission notices |
| [Geminiを使うスキルの配布記事](https://note.com/genkaijokyo/n/n8562c2500420) and [公開ZIP](https://note.com/api/v2/attachments/download/33c55af0abaece1236195095d1e31bb3) | Retrieved 2026-09-19. README, SKILL, execution contract, and all 12 files checked. Antigravity CLI and the named model are distributor requirements; check availability separately in the user's environment |

Do not bundle third-party skill bodies or ZIPs. Explicit redistribution permission was not found for the Gemini variant, so authorized projects retrieve it directly. Exclude installed third-party skills from project Git tracking. Kit settings distribute only retrieval locations, pinned versions, and hashes. Preserve original text at installation and record the invocation-policy addition. Writing quality, Gemini execution, quota amounts, and English editing support remain untested.

## Running on Linux

Use `bash scripts/Initialize-OptionalSkills.sh` from the project root. PowerShell is not required; Python 3.10 or later is required. `--provider`, `--gemini-consent`, `--consent-note`, and `--project-root` correspond to the PowerShell parameters of the same names. Results are JSON. Disabled defaults, consent before installation, pinned-version/file-hash checks, and project-specific receipts match the PowerShell procedure. Do not specify `--gemini-consent Granted` without an explicit user response.

## Applying optional skills in Antigravity mode

When `project.json` has `agentMode` set to `Antigravity`, follow the dedicated `AGENT-MODE.md`. Retain `.agents/skills/` as the storage location. Do not use skills while disabled, even if installed. When enabled, explicitly apply only the selected skill to selected Japanese source targets. Do not assume `agents/openai.yaml` settings work in Antigravity. Production in Antigravity does not authorize installation or additional calls to optional Gemini polishing skills. Apply the consent procedure above unchanged.

If a third-party skill requires Codex comparison or a specified CLI/model, do not silently substitute Gemini self-review, another CLI, or another API. Defer only that polishing if its required environment is missing. Execution in Antigravity mode is unverified. This kit operating policy was added 2026-10-03; the Codex installation procedure and defaults remain in effect.
