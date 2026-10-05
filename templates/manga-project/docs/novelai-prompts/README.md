# Editing and regenerating NovelAI characters, style, and backgrounds

This README gives the steps for a human to change the look of a work **whose NovelAI prompts are already assembled, or whose comic PNG previews are finished**. Work in the existing project folder. You can edit characters, style, and backgrounds in the project folder's `.env` settings file. Do not use this for image generation other than NovelAI.

In these steps, **Codex (or another AI agent such as Claude Code, Grok Build, or Antigravity) prepares the editing environment, and the human edits the text, runs the commands, and chooses the images.** If you want to hand command execution to Codex, ask for that work at each stage. Asking for preparation does not authorize image generation or paid use.

| Task | Usually handled by |
| --- | --- |
| Turning existing prompts into variables, setting up references in request JSON, creating editable text | Codex |
| Deciding the look, style, and background to change, and editing the text | Human |
| Updating the feature list, verifying the content of expanded requests and warnings | Human asks Codex |
| Running the apply, dry-run check, generate, adopt, and build commands | Human (each stage can also be requested of Codex) |
| Checking cost and allowance, deciding whether to run generation, choosing images, reviewing PNG revisions | Human; Codex assists with checks and judgment |

The order is **Codex prepares → human edits and applies the text → Codex checks the content → dry-run check → generate → adopt images → rebuild pages.** Editing settings alone does not change images that were already made.

After PNGs are finished, regenerate and rebuild using the existing requests, adopted images, and page manifests. If images have not been generated yet, do the first generation and adopt every panel after editing. If the page manifests, text placement, or typesetting environment are not ready, Codex prepares them before build.

Variable names and file names below are examples. After preparation, use the file names and commands for your own work that Codex gives you.

## 1. Ask Codex for the initial preparation

Open Codex in the existing project folder and make a request like the following. If preparation is already done, check with Codex where the editable files and commands are, then go to step 3.

> This work has NovelAI prompt assembly done (or PNG previews done). Using the existing prompts, set it up so that I can edit characters, style, and backgrounds myself from .env. Show me the variable names, current text, and affected panels, and after I confirm, set up the references in the request JSON and create editable UTF-8 text files. Keep the existing images, adoption records, and page manifests. Record the files I should edit and the commands I should run in docs/production/NOVELAI-BATCH.md, and walk me through them. Do not generate images this time; only prepare.

Codex prepares only the requested work, matching the existing style and character settings. Codex shows you the variable names and text, and after you confirm, sets up `.env`, the editable text, and the request JSON references. You do not need to adopt the examples below as your work's settings.

Existing works do not receive updates automatically. If an old script does not support style and background variables, ask Codex to update it while keeping the work's own changes.

## 2. What you can change

A "prompt" is the text that describes the picture to be generated. A "variable" is a name attached to that text. Variable names use uppercase ASCII letters, digits, and underscores.

| Purpose | Example variable name | What you change |
| --- | --- | --- |
| Character | `NOVELAI_CHAR_MIO` | Mio's hairstyle, clothing, and the appearance needed to identify her |
| Style | `NOVELAI_STYLE_MAIN` | Line, color, shading, and other art style |
| Background | `NOVELAI_BACKGROUND_CLASSROOM` | The classroom's desks, windows, light, and so on |

**Setting up the request JSON is Codex's job.** Codex puts style and background into the scene-wide text (Base) and characters into the corresponding per-character text (Character). For requests that do not use per-character input, Codex merges them into the body. Codex keeps pose, expression, and action in each panel's request so that only the appearance is easy to change.

Codex separates background variables by location. If you change the classroom variable, only requests that use the classroom variable change. Requests that do not reference the variable are unchanged.

For example, **Codex** prepares references like the following in the request JSON. This is an excerpt that illustrates the mechanism; you do not need to copy it into JSON. When `v4_prompt` is used, Codex sets the same Base in both `input` and `caption.base_caption`.

```text
Base: 1girl, standing, ${NOVELAI_BACKGROUND_CLASSROOM}, ${NOVELAI_STYLE_MAIN}
Character: ${NOVELAI_CHAR_MIO}, smiling, on the left
```

## 3. Confirm where to run commands

Run commands in a **terminal whose working location is the project folder**. On Windows, one way is to open the project folder in File Explorer, type `powershell` in the address bar, and press Enter. If you hand each command to Codex, you do not need this terminal step.

Copy the following one line at a time and press Enter. Do not copy the code block's surrounding marks. In later command examples, the `1` is "page 1"; change it to the target page of your own work.

```powershell
Get-Location
Test-Path project.json
Test-Path scripts/novelai_batch.py
```

Confirm that the first output is your project folder and that the other two both show `True`. If one shows `False`, reopen the terminal in the project folder. If Python cannot be found, tell Codex the error that was displayed.

Run the apply command in Method B in this terminal as well.

## 4. Choose one editing method and change the text

### Method A: edit .env directly

Open the project folder's `.env`, which Codex set up, in a text editor. If the file cannot be found, ask Codex about its creation status. `.env.example` is only a sample; editing it does not change any settings.

Example before:

```dotenv
NOVELAI_CHAR_MIO="girl, short black hair, blue jacket"
NOVELAI_STYLE_MAIN="clean lineart, soft colors, anime style"
NOVELAI_BACKGROUND_CLASSROOM="classroom, desks, windows, daylight"
```

Example after:

```dotenv
NOVELAI_CHAR_MIO="girl, black twintails, blue jacket"
NOVELAI_STYLE_MAIN="bold lineart, vivid colors, cel shading"
NOVELAI_BACKGROUND_CLASSROOM="classroom, desks, windows, warm sunset light"
```

In this example, the hairstyle changes to twintails, the style to bold lines and vivid colors, and the classroom light to sunset. Do not change the name to the left of `=`; edit only the text inside the quotation marks on the right, and save as UTF-8. Write each setting on one line, and do not change other settings such as the API key. This method needs no apply command.

### Method B: edit text files and apply them to .env

If you do not want to touch `.env` directly, edit the **text files Codex created** in step 1. For example, in `input/novelai/prompts/mio.txt`, write only the following text. The variable name, `=`, and outer quotation marks are not needed.

```text
girl, black twintails, blue jacket
```

Edit any other files you want to change in the same way.

| Example text file | Example text |
| --- | --- |
| `input/novelai/prompts/style-main.txt` | `bold lineart, vivid colors, cel shading` |
| `input/novelai/prompts/background-classroom.txt` | `classroom, desks, windows, warm sunset light` |

Keep the text on one line and save as UTF-8. If this is your first time using commands, open a terminal as in step 3. Then run the following commands one line at a time, and the script applies them to `.env`. You can run only the commands for the files you changed.

```powershell
python -X utf8 scripts/novelai_batch.py env-set NOVELAI_CHAR_MIO --value-file input/novelai/prompts/mio.txt
python -X utf8 scripts/novelai_batch.py env-set NOVELAI_STYLE_MAIN --value-file input/novelai/prompts/style-main.txt
python -X utf8 scripts/novelai_batch.py env-set NOVELAI_BACKGROUND_CLASSROOM --value-file input/novelai/prompts/background-classroom.txt
```

Confirm that "updated" or "added" is displayed. The script updates the relevant setting and does not generate images. It keeps other setting values, but it normalizes line endings and character encoding in `.env` when saving.

**Text files are not synchronized automatically.** Run the apply command every time you edit a text file. If you run Method B after Method A, the script replaces the `.env` value with the contents of the text file.

An example request when you hand the apply step to Codex:

> I saved the editing text files. Check the changed files and apply them to .env with env-set. Do not generate images.

### Writing in Japanese

You can also write Japanese in the value on the right or in the editable text files. For example, this single line (it means "a girl, black twintails, a blue jacket"):

```text
女の子、黒髪のツインテール、青いジャケット
```

The script does not translate the text; it puts it into the request as is. You and Codex check in the generated image whether the intended look was achieved. If you change from English to Japanese, also ask Codex to update the feature list in step 5.

## 5. Ask Codex to check the content, then run a dry-run check

First tell Codex which items you changed and ask it to check the expanded requests. **Adjusting the feature list and the request JSON is Codex's job.**

> I changed Mio's hairstyle from short hair to black twintails. I also changed the style and the classroom light. Update the feature list in characters.json and the visible-feature specification for each panel to match .env, and check the expanded requests. Also check the assignment to per-character input and the continuity of the scene. Do not generate images this time.

After Codex's check, run the following command to see the registered variable names. The script normally does not display the text.

```powershell
python -X utf8 scripts/novelai_batch.py vars
```

If you also want to read the prompt text, run the following command. The script does not include the API key in what it displays.

```powershell
python -X utf8 scripts/novelai_batch.py vars --show-values
```

Next, check page 1's requests without sending them.

```powershell
python -X utf8 scripts/novelai_batch.py generate --page 1
```

The script displays dimensions, seeds, the variables used, and warnings, and finally shows "Not sent." If a warning or error appears, tell Codex its content and ask for a fix. This display confirms that the settings are ready; it does not generate an image or guarantee that the content is correct.

An example request when you also hand the command execution to Codex:

> Run vars and the dry-run check with generate --page 1, and check the settings and warnings. Make any necessary fixes, and do not generate images.

### When you change a character's features

For example, if you change from short hair to twintails, Codex changes the hair feature in Mio's `features` in `input/novelai/characters.json` to the same wording as the new prompt. For close-ups where hair is not visible, such as hands, Codex adjusts the targets in `cast`. You do not need to edit the JSON by hand.

The script checks whether the registered feature strings appear in the request text. It does not judge paraphrased meaning, which character a feature attaches to, or whether twintails were actually drawn in the generated image. You and Codex check the image separately after generation. Without a feature list, the script does not run the feature check. There is no equivalent feature-list check for style and background.

Codex reviews each warning and, as a rule, fixes the prompt. If you and Codex decide to keep a warning deliberately, Codex records the reason in `docs/production/NOVELAI-BATCH.md`. The generation and regeneration examples below include `--accept-warnings` by default, which allows sending even when warnings remain. If you want to check warnings and stop sending when any remain, remove this argument. Warnings are still displayed when it is included. It is not an argument that skips cost checks or errors. Use the dry-run check examples without this argument.

## 6. Check cost and allowance, then run generation

Check the cost of this run's style, model, and all settings. Even when Codex helps with the check, confirm the result and any unconfirmed items before deciding to run. Even with Opus, having a subscription does not mean that 0 Anlas has been confirmed for this run. Also check the V5 allowance. For details, see [connection and cost procedure](../knowledge/novelai-api.md#generate-after-confirmation). If it cannot be confirmed, neither you nor Codex should send.

**Only when all of this run's settings are confirmed to be 0 Anlas and the V5 allowance is also confirmed**, run the following V5 command. Rewrite the `--cost-note` text to the actual verification method and time. For V4 and V4.5, remove `--confirm-v5-allowance`.

```powershell
python -X utf8 scripts/novelai_batch.py generate --page 1 --execute --accept-warnings --confirm-zero-anlas --confirm-v5-allowance --cost-note 'Enter how and when you confirmed the cost and allowance for all settings this run'
```

`--execute` is the flag that actually sends generation. The script generates each panel on the page one image at a time and adds candidates without overwriting earlier images. For a work whose images have not been generated, this is the first generation; for a work with finished previews, it is regeneration. If a run fails, the script does not resend automatically. Check the result and consumption, and ask Codex to summarize the situation if needed.

An example request when you hand generation to Codex:

> Generate page 1 with NovelAI after the changes. Run it only if 0 Anlas is confirmed for all of this run's settings and, for V5, the allowance is sufficient. If it cannot be confirmed, do not send and tell me. I do not authorize paid use or automatic resending after a failure.

Ordinary regeneration may change the seed (the number that determines generation variation). If you want to compare only the prompt change, ask Codex before generating to compare at the same seed. Codex sets `parameters.seed` to the same value in the before and after requests and prepares a command with `--seed request`. Even with the same seed, character and composition matches are not guaranteed.

## 7. Check the images and adopt the new candidates

Check candidates and the adoption status with the following command.

```powershell
python -X utf8 scripts/novelai_batch.py list --page 1
```

Candidates are in places like `output/novelai/candidates/p01-02/r003.png`. Open the images, check the look, background, action, and character positions, and choose the candidate to use. `p01-02` is panel 2 of page 1, and `r003.png` is candidate number 3. Run the adopt command for the candidate you chose.

```powershell
python -X utf8 scripts/novelai_batch.py adopt p01-02 --candidate 3
```

Replace the request ID and candidate number with real ones, and adopt each changed panel. For a first generation, adopt every panel on the page. Regeneration alone does not switch the adopted image, so if you skip this, the page may be rebuilt with old images.

### Adopt the highest-numbered image in each folder at once

To use the highest-numbered PNG of each regenerated panel, you can adopt them together with the following command without rewriting numbers by hand. First check the targets with `--dry-run`, review the images, and then adopt.

```powershell
# Only display the targets (the adoption record is not changed)
python -X utf8 scripts/novelai_batch.py adopt-latest --page 1 --dry-run
# Adopt the highest-numbered PNG in each folder on page 1
python -X utf8 scripts/novelai_batch.py adopt-latest --page 1
# Adopt for all pages
python -X utf8 scripts/novelai_batch.py adopt-latest --all
# If you regenerated only some panels, specify just those request IDs
python -X utf8 scripts/novelai_batch.py adopt-latest --ids p01-02,p01-04
```

For example, if one panel's highest number is `r003.png` and another's is `r005.png`, each is chosen. "Latest" is decided by candidate number, not by modification time. Targets are panels that have request JSON, and `--all` covers all pages in the `p01-...` format. Choose the same `--page`, `--all`, or `--ids` that you used for generation and regeneration.

This command replaces the existing adoption for the target panels in `input/novelai/adopted.json` and keeps adoptions for other panels. For a panel with no new PNG, such as after a failed generation, the earlier highest-numbered PNG is selected. If any target has no candidate PNG at all, the command stops with an error and does not change the adoption record. Check the generation results and the images before using it. It makes no API connection; after adopting, rebuild the page PNGs with `build` in step 8.

An example request when you hand the adoption record to Codex:

> I reviewed the images. I will use candidate 3 for p01-02. Record the adoption with adopt.

> I reviewed the images. I will adopt the latest (highest-numbered) image in each folder. Record the adoption with adopt-latest.

Codex reflects the candidates you specified in the adoption record. If you also ask for an image review, Codex actually opens the images, checks them, and explains its recommendation.

## 8. Rebuild the page PNGs and review the finished page

For a work with finished previews, run the following build command using the existing page manifests. If you started before image generation and the page manifests, text placement, or typesetting environment are not ready, first ask Codex to prepare them. Codex performs the post-artwork comparison and sets up the necessary structure. After preparation, run the following.

```powershell
python -X utf8 scripts/novelai_batch.py build --page 1
```

The script saves the result in a per-version folder such as `output/build/page-01/v001/`. Open the page PNG at the location shown in the output, and check how it looks after cropping, the lettering, and the reading order. Build does not send any generation to NovelAI.

An example request when you hand the build and review to Codex:

> Rebuild page 1's PNG with the adopted images, then review the finished page and show it to me. If the page manifest or text placement is not ready, prepare it first. Do not create a PSD this time.

If there are revisions, tell Codex where. Codex presents the revised PNG again, and you check the latest PNG.

### If you also want a PSD

If you create an adjustment PSD yourself, run the following command.

```powershell
python -X utf8 scripts/novelai_batch.py build --page 1 --write-psd
```

A PSD you create with this command is a manuscript for adjusting in painting software. If you ask Codex to create and hand over a PSD, finish the revision review of the latest PNG first and then say, "This PNG needs no revisions. Please also create and verify a PSD and hand it over." If you have already instructed PSD creation, Codex proceeds to creation and verification after the PNG revision review.

## Where to look when you are stuck

| Display or situation | What you check or ask |
| --- | --- |
| Invalid variable name | Tell Codex what was displayed. Codex checks the three permitted variable name types and the script version |
| Variable not found | Check whether you applied the text edit. If the reference setup is the problem, ask Codex |
| The same variable is in several places | Ask Codex to sort out the duplicate. Codex consolidates it into one of the environment, `.env`, `.secrets/novelai.env`, or `.secrets/.env` |
| The value must be one line | Remove line breaks within the text you edited and save it on one line |
| Text file not found | Check the file name and apply command Codex gave you |
| Changed the setting but nothing changed | Check whether you generated and adopted new candidates. Codex checks the request's variable references |
| Build fails | Tell Codex the error. Codex checks adoption, page manifests, text placement, and the typesetting environment |

`templatize`, which replaces the initial requests with variables, changes every place that has the same text. **Codex uses it during the initial preparation**, after checking the targets with `--dry-run`. For ordinary editing you only change the text of the variables Codex set up; you do not need to run `templatize` each time.

The authoritative procedure is the [NovelAI production procedure](../knowledge/novelai-composed-production.md#character-variables), and the per-work commands and adoption records are in [NovelAI batch records](../production/NOVELAI-BATCH.md). Upstream explanation updated 2026-10-05. This guidance is based on the local script implementation; check the effect of actual generation for each work.
