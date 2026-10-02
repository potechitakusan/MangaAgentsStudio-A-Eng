# Independent Back-Translation Review: Project Templates and Runtime Skills

Review date: 2026-09-30. Reviewer: the story/supervision localization subagent, independently reviewing the project/runtime subagent's English text.

This was a semantic comparison, not a test run. I read the English documents, paraphrased their operative meaning back into Japanese, and compared that meaning with the corresponding frozen Japanese files in `.work/localization/source-ja/`. Intentional US localization was evaluated separately from changes to permissions, requirements, scope, or evidence. No browser, external service, generation request, test suite, or image review was used.

## Scope actually read

- `templates/manga-project/AGENTS.md`, `README.md`, `OPTION.md`, and `PRINT-OPTION.md`.
- Project `docs/production/NOVELAI-BATCH.md`, `DIALOGUE.md`, and `PSD-HANDOFF.md`.
- Project `docs/knowledge/novelai-composed-production.md` and `docs/reviews/NAME-REVIEW.md`.
- `templates/manga-project/agent-modes/claude/AGENT-MODE.md`.
- Nine `skills/*/SKILL.md` files: `manga-external-panel-i2i`, `manga-ai-production`, `manga-process-checker`, `manga-readability-review`, `manga-story-review`, `manga-supervision`, `manga-cinema-review`, `manga-immersion-review`, and `manga-terminology-review`.

The reviewer did not independently audit every runtime script or generated image. In particular, this record does not claim execution-level correctness, font rendering quality, paid-service behavior, or actual PSD import compatibility. The video skill and project documents outside the list above are outside this review's scope.

## Findings corrected

| ID | Source meaning | Initial English and potential drift | Corrected English / Japanese back-paraphrase | Resolution |
| --- | --- | --- | --- | --- |
| RT-01 | NovelAI startup step 5: 採用した画風文・除外文・人物外見文・主要生成設定を共通化する | “Share adopted style/negative/appearance wording…” could mean present or disclose it to someone, rather than reuse common settings across panels | “Use the same adopted style, negative-prompt and appearance wording, and major generation settings across panels…” → 採用した画風・除外・外見の文と主要設定をコマ間で共通に使う | Corrected in the NovelAI workflow |
| RT-02 | Batch generation: １回の上限は既定30件 | “maximum 30 per run” omitted that 30 is the default, potentially converting a configurable default into an absolute rule | “a default limit of 30 requests per run” → １回当たりの要求数上限は既定で30件 | Corrected in the NovelAI workflow |
| RT-03 | Supervision proposal step 2: 好意や関係の成立を勝手に補わない | “invent mutual attraction” narrowed the restriction to reciprocal attraction; the Japanese also excludes invented unilateral affection | “invent affection or an established relationship” → 好意や成立した関係を勝手に追加しない | Corrected in the supervision skill |
| RT-04 | Original sound-effect guidance describes Japanese source assets and repetition as duration/rhythm cues | Initial English wording said a Japanese catalog remained, while the English asset rebuild had replaced its visible lettering | The runtime author synchronized the paragraph to the English catalog, stable legacy IDs/field names, English whole-word repetition, and context-dependent PAT versus FLAP | Coordinated fix by the runtime author; asset image quality was not reviewed here |
| RT-05 | The optional Japanese polishing skill is disabled by default; the configuration field must retain a value accepted by the parser | The human-readable value “Disabled; Japanese source text only” described the intended behavior but was rejected during the main agent's scaffold integration check | The value is now `none`; “Disabled by default; Japanese source text only” and the opt-in rules remain in the Notes column → 既定は無効で、明示的に依頼された日本語原稿だけが対象。機械用の値は `none` を維持する | Corrected by the main agent; the reviewer reread the final OPTION row. Integration result is reported by the main agent, not independently executed here |

The three semantic edits were coordinated with the runtime author and reread after application. RT-04 is an asset/document synchronization finding. RT-05 records a human-readable translation that needed to preserve a machine-readable token. Neither finding alleges a defect in the Japanese source.

## Material requirements preserved

| Check | Japanese source meaning | English meaning checked | Back-paraphrase / assessment |
| --- | --- | --- | --- |
| Opus paid-use boundary | 有料利用の明示指示なしにAnlasを消費しない。寸法・ステップだけで無料としない | Explicit paid authorization remains required; actual model, subscription, allowances, extras, and request cost must be checked | 有料利用は明示された範囲だけ。寸法とステップだけで0 Anlasを認定しない。Preserved |
| Unknown generation result | タイムアウト・失敗時は記録を確認し、結果不明のまま自動再送しない | Inspect records; no automatic resend with an unknown result | 結果不明の要求を確認前に再送しない。Preserved |
| NovelAI style selection | 未指定なら選択を待ち、0 Anlasでも試作しない。独立したあらすじ作業は進めてよい | Wait for style ID before style-dependent art, including free trials; independent requested planning may continue | 画風選択前の作画は止め、独立作業は続行できる。Preserved |
| Style sample handling | 実在と絶対パスのみ案内。HTML本文・画像を読んで候補説明しない | File-existence-only guidance and no reading/listing/summarizing/attaching samples remain explicit | 見本の実在だけ確認し、その場所を案内する。Preserved; not loosened into browser use |
| Character prompt variables | 人間の依頼時のみ。変数名と値を確認。APIキーを表示・変更しない | Human request and confirmation remain; only intended character variables are handled | 依頼と確認がある場合に外見の変数化を行い、他の秘密設定に触れない。Preserved |
| Gemini optional skill | OPTIONの選択だけで送信・利用枠消費許可としない。未回答なら導入せず通常制作を続行 | Transmission/quota consent before installation; silence/refusal does not authorize fetching or test calls | 有効化は外部送信の承諾ではない。回答待ちでも通常制作は続けられる。Preserved |
| Actual image evidence | 画像を実際に開く。計画の写しや未確認の一致記録は不可 | Post-artwork comparison requires inspecting actual images and distinguishing plan from observation | 実画像を見て確認し、見ていない画像を一致済みにしない。Preserved |
| imagegen versus separate lettering | imagegenは文字込みのページ生成が基本。それ以外は作画後に組版。別組版回答は開始条件でない | Both branches and their respective comparison timing remain distinct | 使用手段に応じて仕上げを選び、不要な事前回答を制作の条件にしない。Preserved |
| Layout reference actually attached | 番号付き画像と内容を実際に渡す。IDやパス文字列だけは添付ではない | Real image input remains necessary; custom layouts also need references | ファイル名だけ渡して参照画像を添付した扱いにしない。Preserved |
| PNG and PSD gates | PNGの修正なし確認とPSD作成指示が必要。既に作成指示済みなら再質問しない | Both requirements remain; neither silence nor PNG acceptance alone requests PSD creation | PNG確認とPSD指示を別々に確認し、既存指示は再確認しない。Preserved |
| Editable PSD claims | ラスタ文字を編集可能な文字列と呼ばない。未分離の絵を独立レイヤー扱いしない | Rasterization, separated scope, preserved originals, and unverified actual CSP import remain explicit | 再編集できる範囲だけを説明し、実読込未確認を引き継ぐ。Preserved |
| Mandatory process registration | ユーザーの登録依頼だけで開始。おまかせは範囲内で判断するが権限・外部送信・有料利用の承諾ではない | Explicit request, scoped delegation, and separate hook trust/permission boundaries remain | 登録の依頼なしに工程を増やさず、おまかせでも利用許可を代行しない。Preserved |
| Missing process data | 欠落・不正なJSONは０件扱いにしない | Missing/invalid data is not an empty requirement list | 不正や欠落を「必須事項なし」に読み替えない。Preserved |
| Carryover | 元作品を明示した場合のみ、carryForward指示だけ。実施記録・秘密・Hooksの信頼等はコピーしない | Named-source carryover and exclusions remain explicit | 指示だけを引き継ぎ、旧環境の許可や実施済み状態は引き継がない。Preserved |
| Print scope | 既定無効。Web制作の前提にせず、印刷選択だけでPSDや印刷所送信を指示したことにしない | Opt-in print settings, separate output, and separate PSD/transmission instructions remain | 印刷設定の選択はPSD作成や外部送信の依頼ではない。Preserved |
| Review versus measured response | エージェントの見立てと実読者の反応を分ける。画像未確認は予備点検 | Review skills keep observations, hypotheses, unknowns, and trial reads distinct | 見立てを読者実験の結果や画像確認済みへ格上げしない。Preserved |
| Feedback and main-agent authority | フィードバックは記録依頼時のみ。改善案は全採用必須ではない | No unsolicited feedback registration; main agent retains acceptance decisions | 記録は依頼時のみ、レビュー実施と提案採用は別。Preserved |
| External i2i scope | 画像条件付きコマ制作のみ。t2i成功でi2iを検証済みにしない。Blender等を全作品へ強制しない | Inputs, model/version limits, authorization scope, and excluded branches remain | モデル固有の成功例や制約を別方式に無条件で流用しない。Preserved |
| Claude fallback | 作画手段がなければ作画を停止。独立した企画等は継続。未使用imagegenを使用済みとしない | Same branch and no fabricated completion or changed network permissions | 利用できない生成手段を使ったことにせず、可能な独立工程を続ける。Preserved |

## Intentional localization differences

These are authorized changes rather than translation defects:

- Japanese right-to-left page/balloon order becomes left-to-right, top-to-bottom English reading. Back-paraphrase: 英語版のコマと吹き出しは左から右、上から下へ読む。
- Vertical, top-aligned Japanese dialogue becomes horizontal English, centered in balloons with word-boundary wrapping and padding. Back-paraphrase: 単語を不自然に分断せず横組みし、吹き出し内で中央に揃える。
- The Japanese ban on full stops and 20-character comma condition becomes standard US English punctuation governed by meaning and voice. Back-paraphrase: 英語の文意に必要なピリオド・コンマ等を使い、日本語の文字数制限は適用しない。
- Print guidance identifies left-side binding as the US English baseline while still requiring the selected printer's actual specifications.
- Japanese polishing integrations remain disabled by default and are explicitly limited to requested Japanese source work; no unsupported English-polishing capability is invented.
- Character display names and layer names are English; compatibility IDs and fields such as `name_ja` remain stable. Cultural reading changes do not authorize mirroring hands, props, or in-world writing.

Within the reviewed text, the corrected issues above leave no identified material drift in authorization, hard requirements, optional steps, or evidence claims. This conclusion is limited to the listed documents and semantic reading; it is not a substitute for the separate technical and visual verification records.
