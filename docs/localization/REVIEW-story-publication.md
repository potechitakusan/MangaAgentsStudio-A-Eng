# Independent Back-translation Review: Story, Supervision, and Publication

Reviewed: 2026-09-30. Reviewer: a separate sub-agent from the translator of these documents. Source baseline: `.work/localization/source-ja/`. This is a source-comparison and back-translation review, not a fresh investigation of third-party sources, a reader study, a legal review, or a test run.

The reviewed passages preserve the source's substantive narrative distinctions, production safeguards, and limits on evidence. Six local ambiguities were corrected below. US reading direction and English lettering are intentional adaptations. Historical example artwork remains Japanese and is explicitly labeled; this review does not certify it as localized artwork.

## Scope and method

The structural comparison covered all 37 Markdown documents in this scope: the ten files in `docs/knowledge/manga/`, the 22 files in `docs/knowledge/supervision/`, `README.md`, `docs/RIGHTS.md`, `docs/SOURCES.md`, `docs/publication.md`, and `examples/README.md`. For every file, source and English heading counts and table-row counts matched, and no original external URL was missing. The supervision `distribution.json` was also compared: its schema version and 22 document paths are unchanged. These checks detect structural omissions; they do not establish sentence-by-sentence equivalence.

Paired semantic reading covered these full documents:

- `docs/RIGHTS.md`, `docs/publication.md`, and `examples/README.md`.
- Manga basics, pacing and timing, story and character, series and comedy, workflow and review, and the worked comparison example: manga files 00, 03, 05, 06, 08, and 09.
- Supervision routing, straight-man responses, non-explicit allure, romance, reconciliation, and all 23 comedy mechanisms.

Additional targeted reading covered the top-level README's license and credit claims, historical model observations, production defaults, questions, and completion boundaries; the source register's retrieval-date explanation; and supervision sources S01–S12 plus the register's introductory evidence limits. Other scoped documents received structural comparison rather than a complete semantic audit. Creator-name romanizations, official English titles, live service specifications, and external links were not independently researched.

For the high-risk concepts below, the reviewer read the English as an independent instruction, paraphrased it back into Japanese, and compared that meaning with the Japanese baseline. The Japanese phrases here are review paraphrases, not replacement project instructions.

## Corrections made during review

| Location | Japanese source meaning | Initial English risk | Resolved English and Japanese back-paraphrase |
| --- | --- | --- | --- |
| [Comic basics](../knowledge/manga/00-manga-basics.md), continuity item 8 | 持ち手: maintain which hand holds a prop | “holding hands” could imply two characters joining hands | “which hand holds each prop” → 「小道具をどちらの手で持つかを照合する」 |
| [Story and character](../knowledge/manga/05-story-character.md), S04 | 関心 can be inferred; the kind of feeling is not established | “evidence of care” could imply affection or concern beyond the source | “evidence of interest in that person” → 「その人物への関心の証拠にはなるが、感情の種類は断定できない」 |
| [Allure](../knowledge/supervision/allure/README.md), A05 | Close details can obscure 空間や主体 | “space or agency” could turn visual attribution into a claim about freedom of choice | “spatial orientation or whose action or viewpoint is being shown” → 「空間関係や、誰の動作・視点かが見えにくくなる」 |
| [Straight-man responses](../knowledge/supervision/tsukkomi/README.md), T03 | 慣れた受け流し means letting familiar behavior pass | “Familiar acceptance” could imply endorsement | “Letting familiar behavior pass” → 「見慣れた行動を受け流す」 |
| [Comedy mechanisms](../knowledge/supervision/gag/mechanisms.md), G21 | 体面 means social face or reputation | “Appearance” could mean physical looks | “Saving face” → 「重大事より先に体面を気にする」 |
| [Comedy mechanisms](../knowledge/supervision/gag/mechanisms.md), G23 | 俗っぽさ can reveal a mundane or worldly side | “ordinary self-interest” narrowed the meaning to selfish motives | “a mundane or worldly side” → 「立派な評判や外見の下に俗っぽい面がのぞく」 |

These corrections change wording only. They do not add new narrative requirements, remove exceptions, or strengthen claims about reader effects.

## Meaning checks retained without correction

| Topic and source meaning | English meaning checked | Japanese back-paraphrase and result |
| --- | --- | --- |
| MIT applies to original kit material; using the kit does not automatically license the user's outputs | Copyright-notice retention remains required for relevant kit redistribution; credits in comics are not newly required | 「キットの独自部分はMIT。利用者の漫画や素材へ自動適用せず、第三者素材の包括的許諾にもならない」 — preserved |
| Third-party study material and optional Japanese skills have separate rights | Personal-study wording is not treated as a standard open-source grant; unconfirmed Gemini redistribution permission remains unconfirmed | 「個人学習用という記載を再配布許可と決めつけない。確認できない許諾を補わない」 — preserved |
| Source dates distinguish recorded checks from backfilled dates | 2026-09-12 remains a backfilled record date when retrieval is unknown; listing a URL does not imply complete reading, current specifications, or redistribution permission | 「補完日と実際の閲覧確認日は別。掲載だけでは全文読了や現行仕様を保証しない」 — preserved |
| Supervision guidance consists of production proposals informed by creator statements | Source claims, visual observations, adaptation hypotheses, and measured reader responses remain separate | 「作者の制作観からの提案であり、読者効果を実験で立証した法則ではない」 — preserved |
| Japanese source material describes Japanese manga conventions | The source's right-to-left claim remains attributed as such, while the English kit explicitly adopts left-to-right and horizontal English | 「原典の右から左という説明はそのまま帰属させ、英語版の制作判断として左から右へ変更する」 — intentional adaptation, not a changed source claim |
| Ability, confidence, belief, facts, and interpretations are different | Story and pacing guidance does not make a character's explanation automatically true or equate victory with moral correctness | 「人物の仮説や自信を事実・能力・正しさと同一視しない」 — preserved |
| Comedy has setup, development, and payoff, but need not erase serious emotions | Repetition can change meaning; straight-man responses need not always shout, correct, explain, or shorten dialogue | 「笑いのために深刻な感情を消さず、ツッコミを一律の大声や訂正へ限定しない」 — preserved |
| Non-explicit allure concerns attention and characterization, without mandatory nudity or sexual acts | Unknown age does not become assumed adulthood; an observer's attention is not proof of invitation, reciprocity, or romance | 「注目した側の反応だけで、相手の誘い・相互の好意・恋愛成立を補完しない」 — preserved |
| Romantic approach must preserve the recipient's wishes and reply | Deferral or refusal is not filled in as hidden acceptance; blushing alone is not proof of romance | 「保留や拒否を内心の承諾と決めつけず、赤面だけで恋愛と断定しない」 — preserved |
| Reconciliation distinguishes apology, forgiveness, resumed contact, and continuing life | Understanding motives does not erase harm; restitution does not buy forgiveness; one-sided harm is not mechanically shared | 「事情の理解と行為の責任は別。謝罪・赦し・関係再開は別で、全関係を仲直りにしない」 — preserved |
| Production previews, PSD instructions, tests, and publication have distinct consent boundaries | No reply is not PNG confirmation; an existing PSD instruction is not requested again; tests and external publication retain their separate procedures | 「返答なしは確認待ち。既存の指示は有効だが、テスト許可で公開やコミットまで認めたことにはしない」 — preserved |
| Agent inspection is different from a first-time human reader's reaction | Text-only review is not reported as image review; hypothetical effects and unperformed reader studies remain unverified | 「エージェントの見立てを実読者の反応や未実施の検証結果として記録しない」 — preserved |
| Example descriptions record the actual Japanese production history | The English text translates briefs and revision records while retaining original Japanese settings, artwork, and documented vertical lettering | 「作例の説明は英訳したが、当時の日本語原画や制作履歴を英語版の実績へ書き換えてはいない」 — deliberate historical retention |

## Limits and follow-up

No tests, external API calls, browser sessions, publication actions, or original-art edits were performed for this review. The comparison validates the recorded source meaning, not current provider terms, third-party licensing conclusions, official romanizations, or empirical effectiveness.

The historical examples remain an explicit release-scope limitation if a release requires every visible comic page to be English. Their artwork and linked external comics need a separate localization decision and production task; English descriptions alone do not complete that work. See the [Japanese hearing sheet](HEARING-SHEET.ja.md). Future Japanese-source updates should use the recorded baseline and [Update workflow](UPDATE-WORKFLOW.md), then repeat independent semantic review for affected passages rather than assuming this result covers later edits.

## Later image-localization follow-up

On 2026-09-30, revision 0.4.1-en-US.2 completed the bundled comic images described as pending in this earlier audit. See the [example localization record](EXAMPLE-LOCALIZATION.md), [separate dialogue audit](REVIEW-example-dialogue.md), and [image review](REVIEW-example-images.md). This follow-up does not enlarge the historical review scope above. Linked external Japanese comics and PSD files remain untranslated.
