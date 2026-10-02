# Approved dialogue and lettering source

Dialogue/monologue defaults to horizontal English. Adopted user changes take precedence. Text in artwork follows its context. Do not assume PSD text is editable in CLIP STUDIO PAINT. Hand off provisional lettering separated from art and this source text.

Center dialogue lines in balloons with inner padding. Use natural US English punctuation, including periods, commas, and apostrophes as meaning requires. Wrap at word boundaries; Japanese character-count punctuation restrictions do not apply. For connected balloons, preserve sentence flow and explicit reading order. See [Lettering and punctuation](../knowledge/japanese-manga-readability.md#dialogue-typesetting).

## Project lettering settings

If unspecified, Codex provisionally selects a readable dialogue baseline on the first page, verifies it at publication size, and applies it afterward. Do not require the user to select fonts or fill every row. Record only uses that occur; do not estimate measurements from unseen images.

- Baseline page/panel, review PNG, and display dimensions:
- Font, fallback candidates, and licensing reference if fonts are used (`scripts/typeset_manga.py` writes the chosen filename to `check.json` as `font_file`):
- Shared direction, color, baseline size/unit, line spacing, padding:
- Dialogue alignment: centered (record affected text and reasons for changes/exceptions).

| Use | Change from baseline | Conditions | Exceptions / publication-size check |
| --- | --- | --- | --- |
| Dialogue | Baseline | Normal speech | |
| Whisper | Choose cues for quiet volume | Quiet speech | Do not make essential words unreadably small |
| Shout | Size, weight, balloon, etc. | Raised voice | Distinguish from inner thoughts |
| Inner thoughts | Distinguish from speech | Internal words | Preserve viewpoint character |
| Explanation | Narration, place, time, etc. | Necessary context | Do not obstruct dialogue order |
| Effects | Scene-appropriate drawn lettering, etc. | Sound/state | Preserve intentional exceptions |

For long text, compare dialogue, balloon, and panel-layout changes instead of shrinking alone. Font and emphasis preferences can change in conversation. Record concrete adopted values here once and check applicability to the same use on later pages. Font redistribution requires a separate license check.

## Approved source text

| Page/panel | Text ID | Speaker | Dialogue / thought / effect / explanation | Approved text | Pronunciation / line breaks / placement | PSD layer and editability |
| --- | --- | --- | --- | --- | --- | --- |
| | | | | | | |

Do not let production-note separators enter dialogue. For connected balloons, list linked text IDs in placement instructions and preserve intended sentence punctuation. When correcting, update source and provisional placement together; verify order, speaker, typos, punctuation, word wrapping, and centering.

Only when stylistic polishing is selected, retain original/candidate wording and acceptance reasons in revision records. Compare meaning, voice, implication, and text volume; apply only adopted wording. Legacy Japanese polishing remains for Japanese source text only. See [Readability](../knowledge/japanese-manga-readability.md#optional-polish).
