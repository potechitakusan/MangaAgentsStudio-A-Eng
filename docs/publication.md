# Verification Before Committing from This Folder

The release version is managed in `distribution-version.txt`. Neither repository name nor working-folder name is fixed.

Use this folder directly as the Git working tree; the user commits the required changes here. Do not create a publication ZIP or separate release folder. `scripts/public_release.py` only inspects files and does not modify them.

## When to run tests and automated checks

**Do not run or rerun prepublication tests or automated checks after every edit. Run them when the user requests pre-commit checks, after confirming the intended work.** This applies to kit publication inspection, frame checks, distribution tests, optional-skill installation tests, and Python tests.

1. Read the changes and earlier verification results, then identify necessary targets, scope, and reasons for rerunning. Do not run tests first as preparation for asking.
2. Present commands, targets, and scope and ask permission to execute. A request for “pre-commit checks” alone is not permission to run tests. Do not ask again if this turn's targets and scope already have explicit authorization.
3. Run only the authorized scope. If no answer, deferral, or refusal, do not run; record tests as not performed.
4. After fixes based on results, do not automatically repeat tests. If a rerun exceeds the confirmed scope, explain the necessary targets and reasons and seek confirmation. Do not default to repeating everything.
5. Record targets, results, unperformed items, and out-of-scope items in `docs/PROGRESS.md`. Earlier success does not verify a subsequently edited version.

Ordinary reading of edits and diffs may happen at any time. PNG review, PSD verification during production, and checking a newly created project's destination follow their existing procedures. Permission for tests under this rule does not authorize staging, committing, or external publication.

## Publication scope

General knowledge is integrated into `docs/knowledge/manga/` and existing documents directly under knowledge, then published and distributed as ordinary knowledge. Under `docs/knowledge/supervision/`, include only the supervision documents, source register, and manifest listed in `docs/knowledge/supervision/distribution.json`. Research illustrations, draft history, and verification exercises remain in `.work/` and are not bundled.

Publish the README, working rules, common knowledge, skills, project templates, distribution and video scripts, tests, public examples and descriptions in `examples/`, and English-edition maintenance guidance in `docs/localization/`. The kit-only `resources/novelai-style-samples/` and `resources/pixai-model-samples/` directories are included as anonymized viewing libraries. Exclude source input other than designated examples, deliberation history, old versions, assets, other comic/video samples, local environment information, and verification outputs.

In `examples/`, PNG and JPEG (`.jpg`, `.jpeg`) are allowed in addition to ordinary document and code formats. Examples are not copied to new projects. Bundled comic pages are adapted for English reading; their Japanese originals are preserved in the private localization backup. External Japanese example artwork and PSD links remain labeled as originals. Frame assets additionally allow only `index.html`, SVGs directly in `svg/` and `guides/`, and PNGs directly in `png/` and `previews/` under `templates/manga-project/templates/panel-templates/`; these are distributed into projects. `resources/novelai-style-samples/` additionally allows only `catalog.json`, `index.html`, and WebP directly in `previews/`; `resources/pixai-model-samples/` additionally allows only `catalog.json`, `index.html`, and JPEG (`.jpg`) directly in `previews/`; neither is distributed into projects. Portable Bash entry points are allowed only as `.sh` files directly under kit `scripts/`; the project creator copies the designated review and optional-skill entry points into projects. Do not blanket-allow images, HTML, or shell scripts elsewhere.

Remove ancillary metadata from public PNGs, including Exif, text, generation provenance, color profiles, and resolution. Publication inspection allows only image chunks `IHDR`, `PLTE`, `IDAT`, `IEND`, and transparency `tRNS`; other chunks or trailing data are errors. Preserve image data without recompression and confirm matching dimensions and pixels. Check that SVG, HTML, and JSON are generic assets without project titles, dialogue, personal data, or local paths.

Likewise remove Exif, comments, generation provenance, color profiles, and resolution metadata from public JPEGs. Inspection rejects APP segments and comments, except for a fixed JFIF 1.01 header with no resolution unit, 1:1 aspect ratio, and no thumbnail. Metadata between scans and extra data after the image end are also checked. Preserve image data without recompression and confirm matching dimensions and pixels.

Exclude `backup/` and `.work/` from Git commits. Local working `docs/PLAN.md` and `docs/PROGRESS.md` are private; templates with those names distributed to projects are public. The user-created exception marker `特別な理由でこのフォルダの中で漫画を作ります.txt` is neither tracked nor distributed to new projects. Exceptional in-kit production assets and manuscripts belong in private areas such as `.work/` too.

`.gitignore` limits public locations and document, code, example PNG, and JPEG formats, and excludes backups, asset/output folders, caches, and secret settings within public directories. Only `manga-project/` is in scope under `templates/`. It cannot detect private prose inside an allowed document format, so inspect diffs before publication as well.

`.gitignore` does not apply to tracked files or earlier commits and does not prevent `git add -f`. Keep backups and work outputs in root-level `backup/` or `.work/`, outside public directories.

## Commands to run after confirmation

These are candidate checks. Confirm the current targets and scope using the procedure above, then run approved commands. Neither this list's existence nor a document edit triggers automatic execution.

```powershell
python .\scripts\public_release.py check
python .\scripts\check_panel_templates.py
.\tests\Test-Scaffold.ps1
.\tests\Test-OptionalSkills.ps1
python -X utf8 -m unittest discover -s tests -p 'test_*.py'
```

Publication inspection reads only public targets and checks working absolute paths, fixed folder names, local links, disallowed formats, and possible secrets. External URLs are not working paths. Run video-editing tests when ffmpeg and ffprobe are available.

Use `-X utf8` for the full Python test run so verification records, including any Japanese text, remain readable on Windows.

Regenerate frame assets only when they change: run `python scripts/build_panel_templates.py`, then `python scripts/render_panel_templates.py --all` in the kit. The English-edition renderer uses Python and Pillow directly on catalog geometry, without launching a browser. The retained `node scripts/render_panel_templates.cjs --all` command is a compatibility wrapper for that Python renderer and additionally requires Node.js. Generation does not overwrite project settings JSON. Ordinary project production uses bundled assets. The prohibition on browser automation remains in force.

## Inspect Git diffs and commit

At this folder's root, inspect candidate additions and changes.

```powershell
git status --short
git diff --check
git diff
git ls-files --cached --others --exclude-standard
git ls-files --cached --ignored --exclude-standard
```

The final command checks for tracked files that should be ignored; its output should be empty. Publication inspection reads the working tree, so candidate additions and staged content need separate review.

After the user stages the desired changes, review using these commands or the Git interface and commit directly from this folder. Examples include `examples/README.md` and metadata-stripped PNG/JPEG images.

```powershell
git diff --cached --name-status
git diff --cached --check
git diff --cached
```

Codex commits, creates GitHub repositories, configures remotes, pushes, or registers releases only when each operation is requested. Original portions are published under MIT. Also review [Third-party material](RIGHTS.md).
