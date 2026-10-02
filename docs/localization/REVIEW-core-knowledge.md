# Independent Back-Translation Review: Core Knowledge

Review date: 2026-09-30. Reviewer: the project/runtime localization subagent, independently reviewing the core-knowledge subagent's translation and the coordinating agent's kit rules and sound-effect wording.

I compared the English text with the corresponding frozen Japanese files in `.work/localization/source-ja/`, reconstructing the English instructions in Japanese to check agency, conditions, quantities, certainty, and implied permission. Intended US English adaptations were assessed separately from unintended meaning changes. This was a document and catalog review: no external sources were refreshed, no generation requests or tests were run, and no images or audio were inspected during this review.

## Scope actually reviewed

The review covered the kit `AGENTS.md` and all 23 core knowledge documents:

- `docs/knowledge/ai-production.md`, `novelai-api.md`, `optional-skills.md`, `external-panel-i2i.md`, `project-options.md`, `process-checker.md`, and `psd-handoff.md`.
- `docs/knowledge/codex-operation.md`, `feedback-workflow.md`, `glossary.md`, `immersion-and-cinema.md`, `japanese-manga-readability.md`, `manga-sources.md`, `page-layout.md`, `panel-layout-policy.md`, `review-workflow.md`, and `story-structure.md`.
- `docs/knowledge/video-assembly.md`, `video-previsualization.md`, `video-prompting.md`, and `video-tools.md`.
- `docs/knowledge/image-generation/production-evidence.md` and `qwen-image-2.1.md`.

I also read `templates/manga-project/templates/onomatopoeia/README.md` and compared the source/English text and meanings for all 38 expression/variant families in `catalog.json`, using the `block` entries. The three visual style variants share those meanings. This does not claim that all 114 images were visually reviewed or that their metadata was independently verified.

## Corrections made

| File | Wording before review | Back-translation concern | Correction |
| --- | --- | --- | --- |
| `docs/knowledge/novelai-api.md` | Model-specific requirements and sampler compatibility were described as “not fully locally validated.” | This can imply partial validation of those specific aspects. The Japanese source says the local client does not validate them. | Changed to “The local client does not validate model-specific additional requirements or sampler compatibility.” Existing checks of other payload fields remain described separately. |
| `docs/knowledge/image-generation/qwen-image-2.1.md` | The 96% and 94% retained crop figures omitted their measurement dimension. | A reverse translation could read them as retained area rather than retained width. | Explicitly stated “of the original width” for both figures, matching the source's quantitative meaning. |

Both are documentation precision corrections. They change no runtime behavior, permissions, model settings, or source evidence.

## High-risk meaning checks

The Japanese phrases below are reviewer paraphrases of the English meaning, not additional user instructions or newly verified external facts.

| Subject | Meaning reconstructed in Japanese | Result |
| --- | --- | --- |
| Opus defaults and paid use | 有効なOpus契約では1回1枚・28ステップ以下を基本とし、V5の初期値は23。寸法だけで無料と断定せず、全設定と追加料金を実行前に確認する。有料利用の明示指示なしにAnlasを消費しない。 | Preserved. The 1,048,576-pixel candidate is not misrepresented as independent limits on each edge, and the rule is not generalized to other generators. |
| NovelAI confirmation flag | `--confirm-zero-anlas` はユーザー側の確認表明であり、料金上限や消費ゼロの技術的保証ではない。結果や消費が不明な要求を別名で再送しない。 | Preserved. The experiment registration is not transmission permission; local checks are not server-side cost verification. |
| Optional skill consent | 日本語推敲の選択だけではGeminiへの文章送信・利用枠消費を許可したことにならない。Gitがなければ導入許可が必要。 | Preserved. English support is not invented; the optional feature remains disabled and limited to Japanese source text. |
| PNG and PSD stages | PNGを提示し、修正を反映して再提示し、修正なしを確認する。PSDが既に依頼済みなら再質問しない。未依頼なら回答を待つ。沈黙を承認にしない。 | Preserved. Raster text layers are not advertised as editable native text, and untested CLIP STUDIO import is not claimed as verified. |
| Process requirements | ユーザーが登録を依頼した項目だけを作品内に保存する。登録値だけを承諾の証拠にせず、強い指示でもHooksの導入・信頼は別途確認する。 | Preserved. Named-source carry-forward excludes execution records, trust, paid-use permission, and external-transmission permission. English wire values are an intentional compatible localization. |
| Options after production begins | 会話で既に指定された変更は聞き直さない。未確認の実質的変更は採用値に上書きせず、関連作業を保留し、無関係の作業は続ける。 | Preserved. Missing fields use defaults at initial application; existing finished dimensions are not silently migrated to automatic dimensions. |
| Evidence and causal claims | 試行数・除外条件・同時変更を記録し、単一モデルの観察や一度の成功を一般的効果や他モデルの実証にしない。 | Preserved across Qwen, production evidence, video, and review guidance. Historical counts, model versions, and dates remain historical. |
| Image and audio review | 文章確認を実画像レビューと呼ばず、ASRやメタ情報を試聴の証明にしない。未確認は未確認と記録する。 | Preserved. Japanese audio observations remain Japanese evidence and are not relabeled as successful English tests. |
| Attribution and licensing | 参照元の個人学習向け利用表記を残し、キットのMITを第三者資料へ適用しない。書誌だけの確認を本文の確認済みとしない。 | Preserved. Source URLs and dated verification scopes remain distinguishable from localization choices. |
| Feedback and publishing | 記録依頼のないフィードバック収集・還元を行わず、通常の進捗記録とは区別する。記録作成と外部送信・公開は別の指示範囲で扱う。 | Preserved. Comic production still centers project creation/reopening, and the personally created Japanese exception-marker filename remains a compatibility identifier. |

## Intentional adaptations accepted

The upper-right to lower-left Japanese reading path becomes upper-left to lower-right, including panel examples, speaker placement, balloon order, and reveal timing. This changes layout planning rather than mirroring existing artwork. Horizontal English lines, centered speech-balloon text, word-boundary wrapping, and normal punctuation replace Japanese top-aligned vertical lettering and the no-period/20-character-comma rule. These are labeled English-edition choices; the Japanese publisher and W3C sources are still described as Japanese sources, not evidence for a supposed universal English standard.

Film and video remain optional. New example dialogue and requested audio use English, while historical Japanese tests and their limitations remain identified. Names, Japanese-setting details, technical identifiers, and source attribution are not automatically Americanized. Terms such as “panel script,” “thumbnails,” “reading flow,” and “theatrical flair” retain the glossary's project-specific meaning and distinctions.

Sound effects use context-dependent English equivalents rather than one-to-one transliteration: for example, `doki` becomes `THUMP`, `puru` becomes `TREMBLE`, and `bata` defaults to `FLAP` while its description identifies a different choice for a fall. Source IDs and original Japanese text provide provenance. Repeated variants contain whole English expressions; Japanese syllable counts and obligatory duplication are not imposed on English. The README distinguishes the new original vector production method from the historical NovelAI glyph workflow and makes no English frequency-ranking claim.

## Result and limits

No unresolved reversal of a permission, requirement, negation, or evidence qualification was found within this scope after the two corrections. This is a qualitative translation audit, not proof of model capability, billing behavior, runtime correctness, typography quality, reader response, or actual PSD compatibility. Those checks must be recorded separately. Future Japanese updates should repeat this comparison for changed paragraphs, especially costs, prerequisites, numerical claims, and historical observations.
