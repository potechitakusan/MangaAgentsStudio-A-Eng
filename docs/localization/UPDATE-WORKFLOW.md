# Updating the English edition

Maintain separate Japanese and English checkouts. The Japanese author remains the source author; the English edition adapts the production kit for US readers. Keep the English release in this checkout and publish from it using the repository's normal process.

## Baselines and versions

- `source-manifest.json`: Japanese source commit/version, capture date, and SHA-256 of every tracked source file. This records the version translated; it is not an assertion that today's Japanese checkout is unchanged.
- `translation-state.json`: source-to-English path mapping, current English hashes, and disposition of unchanged files and intentional adaptations.
- `example-localization.json`: source/English image hashes, dimensions, and disposition for all 35 bundled example images; exact editing prompts and reviewed scripts accompany the [example record](EXAMPLE-LOCALIZATION.md).
- `TRANSLATION-POLICY.md`: terminology and cultural decisions.
- `BACK-TRANSLATION-REVIEW.md`: independent semantic review and fixes.
- `VALIDATION.md`: checks actually performed, limitations, and exact scope.
- `HEARING-SHEET.ja.md`: outstanding owner preferences in Japanese. Working decisions remain usable while responses are pending.

The current source kit version is `0.5.0`; the English localization is `0.5.0-en-US.1`. The `0.4.1-en-US.3` release localized the kit, bundled comic pages, and source-fidelity corrections; version 0.4.2 incorporated the upstream update described in [the 0.4.2 record](UPDATE-0.4.2.md), and version 0.5.0 incorporates the one described in [the 0.5.0 record](UPDATE-0.5.0.md). When the upstream version file and the latest upstream commit message disagree, follow the version file and record the discrepancy. Record both in release notes and generated project metadata. The unchanged image and prompt records retain their revision-2 provenance. Do not silently reuse the same localization revision after substantive changes.

## Each Japanese update

1. Obtain the updated Japanese checkout and preserve the previous source revision. Never copy it over the English tree.
2. From the English kit root, compare it with the recorded baseline:

   ```powershell
   python scripts/localization_sync.py --source ../Japanese-upstream --output .work/localization/upstream-delta.json
   ```

   Paths in this example are relative placeholders. The tool reads the source and reports additions, modifications, and deletions; it does not translate, copy, delete, or merge files. In a Git checkout it compares tracked working files, including local edits and deletions. Commit/add intended upstream files before comparing so new files appear in that tracked inventory. For an exported source folder, local artifact folders are excluded.

3. Review each changed source file against the previous Japanese revision. Classify each change as prose, code, schema, layout, asset, attribution, or license. If a Japanese source is deleted, check English links and uses before deleting its counterpart. If a source file is renamed, record the mapping explicitly; the tool conservatively reports an addition and deletion.
4. Apply the source change to the English file while preserving the US decisions: LTR panels and balloons, horizontal English lettering, normal punctuation, and contextual sound effects. Do not overwrite English code with a Japanese implementation and thereby restore Japanese defaults.
5. When modifying panel geometry, regenerate SVG/JSON/HTML with `python scripts/build_panel_templates.py`, and regenerate PNGs with `python scripts/render_panel_templates.py --all`. These are maintenance operations, not browser automation. For changed SFX text, update the English catalog, run `python scripts/build_english_sfx.py`, and run `python scripts/refresh_asset_indexes.py` to update the offline galleries. Inspect the rendered assets. For changed example pages, inspect the new Japanese image against the prior source and reviewed script, update the English lettering and LTR panel/balloon plan, and preserve clue states and repeated lines. Use the saved prompts as editing specifications, not a guarantee of deterministic image generation. Review the actual output, remove image metadata, and update `example-localization.json` with the adopted file hashes and dimensions before recording the English state. Do not silently reuse stale image hashes or overwrite English pages with Japanese originals.
6. Have a different sub-agent read the new English text, reconstruct its Japanese meaning, and compare it with the changed source. Check negatives, numbers, optional versus required actions, permissions, evidence, warnings, and links. Record intentional localization changes separately from mistakes. Resolve findings before release.
7. Run the checks appropriate to the changes under the project's validation policy. Verify a newly scaffolded Codex project and, when relevant, Claude mode, configuration defaults, English lettering, and release links. Do not claim external API, browser, or editor behavior was tested unless it actually was.
8. Update the source manifest to the reviewed Japanese revision, increment the localization revision in project creation and `scripts/record_localization_state.py`, and record validation and remaining questions. Run `python scripts/record_localization_state.py` after finishing the English files, then `python scripts/record_localization_state.py --check` to verify the saved mapping. The script writes only the English state file and does not change the Japanese baseline. A changed hash alone is not proof of translation review. Hashes use exact file bytes: preserve the upstream checkout's line endings when comparing, and distinguish newline-only differences from substantive changes.
9. Review the intended Git diff and release notes. Commit or publish only when that operation is requested. Do not stage local snapshots, original-image backups, downloaded dependencies, secrets, or personal project records.

The local `.work/localization/source-ja/` snapshot supports this first review only; it is deliberately not part of the release. The committed Japanese revision and the public source hash manifest are the durable provenance. Original example images are additionally preserved in the ignored local original-image backup. They are traceable to the Japanese source manifest; the distributed English edits are mapped in the example manifest. Keep those originals or the source revision available for later comparison. Text-free retained images are identified explicitly. Linked external Japanese comics and PSD archives are not English deliverables.
