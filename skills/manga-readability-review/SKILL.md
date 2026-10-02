---
name: manga-readability-review
description: Use to consult on or review panel and balloon order and lettering in US English comic storyboards or finished pages.
---

# Comic readability review

This skill is bundled with the manga project. Paths below are relative to the working project root. When testing the original in the distribution kit, use `templates/manga-project/config/review-profiles.json` for emphasis settings.

Confirm the target scene, intent, and input (synopsis / text storyboard / rough storyboard / manuscript / reference art), then read effective emphasis under `docs/knowledge/review-workflow.md`. The primary perspective is `readability`. For judgments, consult relevant sections of `docs/knowledge/japanese-manga-readability.md`.

Check how far speech reaches, the division between images and explanation, action causality, and reading order versus comprehension order. Separate stylistic preferences from obstacles to understanding and actually trace panel and within-panel text order. Confirm the English project policy: horizontal dialogue/monologue, centered balloon text, natural punctuation, word-boundary wrapping, and left-to-right/top-to-bottom reading. Record explicit exceptions. Distinguish oval, spiked, and radiating flash balloons according to voice, inner thoughts, and staging intent. Check whether border overflow or white panels obscure order and whether text competes with faces. If page layout is in scope, inspect repetition and pacing using `docs/knowledge/panel-layout-policy.md` and project settings as needed. Without images, label the review preliminary and text-based; do not judge unseen placement.

Include the location, observation, hypothesized reader effect, severity, proposed improvement, and effect that would be lost. For consultation, give proposals and reasons for choosing them. In reviews, honestly record "no issue" or "cannot judge" when appropriate. The main agent integrates final decisions and saves them in `docs/reviews/`. Record reusable feedback in `docs/feedback/` only when the user asks to retain it; otherwise do not ask whether to record it.

For pages separately typeset by `scripts/typeset_manga.py`, distinguish `check.json` findings (tails, face/hand overlap, reading order, punctuation, text size) from actual visual inspection of artwork-containing review images (`page-NN-display.png` and `page-NN-check-overlay.png` in the build version folder). For imagegen pages generated with text and balloons, compare the finished page with approved source dialogue; separate typesetting or creating `check.json` is not a review prerequisite. Passing automated checks does not establish readability.

For comic-page fundamentals use `docs/knowledge/manga/00-manga-basics.md`; record checks in `docs/reviews/NAME-REVIEW.md`. For PSD handoff, follow `docs/knowledge/psd-handoff.md` and verify approved source text and composite output. Mark unseen manuscript items unverified.
