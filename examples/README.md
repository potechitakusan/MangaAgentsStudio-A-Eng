# About the Examples

These comics were produced from simple prompts after following Codex's guidance to create production projects separate from the kit.

The English-lettered comic pages were first generated as part of the Japanese edition. Codex then edited the existing images to replace Japanese dialogue and other lettering with English; these pages were not originally generated in English.

**The 29 bundled comic pages are presented as a US English edition.** Twenty-six pages were edited with built-in imagegen for horizontal English lettering and left-to-right sequencing. Three wordless pages already support that reading direction and retain their original artwork; the six text-free reference images are also unchanged. Read panels left to right, then top to bottom. Whole panels were repositioned where needed; artwork was not intentionally mirrored.

The briefs and revision notes below describe the original Japanese production history. The later English image edits are recorded separately in the [example localization record](../docs/localization/EXAMPLE-LOCALIZATION.md), including exact editing prompts and independent meaning review. Generated edits approximate the original art and may change fine linework or framing. External comic and PSD links explicitly labeled Japanese still lead to the original editions.

## 01

Prompt used for the original Japanese production:

- A Japanese high school.
- A scene where two close female friends become aware of a faint romantic feeling.
- Dialogue should be casual conversation only; communicate the scene's meaning visually.
- One has short black hair; the other has brown hair in a half-up style.
- The girl with the half-up hairstyle is the one who recognizes her romantic feelings.

A human reviewed the generated comic and requested these changes:

- Specified where to add exclamation marks, question marks, and ellipses in the dialogue.
- Visually identified unnatural parts of the artwork and requested corrections.

![Example 01, page 1 — English edition](01/page-001.png)

![Example 01, page 2 — English edition](01/page-002.png)

## 02

Prompt used for the original Japanese production:

- Draw the final round of a magic battle tournament in a fantasy comic.
- Both characters are girls and childhood friends. Each specializes in a different elemental magic. Use a bright, pop-inspired style; both are powerful.
- Keep dialogue as sparse as possible and explain visually. End with a panel of intense light that leaves the winner unclear.

A human reviewed the generated comic and requested these changes:

- Add aerial combat.
- Make some panel divisions diagonal to avoid monotony.

![Example 02, page 1 — English edition](02/page-001.png)

![Example 02, page 2 — English edition](02/page-002.png)

![Example 02, page 3 — English edition](02/page-003.png)

## 03

Character reference images (`03/character1.png`, `03/character2.png`) were created in advance through discussion with ChatGPT and saved in the project's `input` folder.

Prompt used for the original Japanese production:

- Use the two characters in the input images to create a fantasy comic titled “A Promise on a Rainy Day.”
- Convey speech-balloon content through images and symbols instead of written words.

During the original Japanese production, no human edits or further revision requests were made after automatic generation. The English edition later received the localization edits described above.

![Example 03, A Promise on a Rainy Day, page 1 — English edition](03/page-001.png)

![Example 03, A Promise on a Rainy Day, page 2 — English edition](03/page-002.png)

![Example 03, A Promise on a Rainy Day, page 3 — English edition](03/page-003.png)

![Example 03, A Promise on a Rainy Day, page 4 — English edition](03/page-004.png)

## 04

Character reference images (`04/character1.png`, `04/character2.png`, `04/robot1.png`) were created in advance through discussion with ChatGPT and saved in the project's `input` folder.

Prompt used for the original Japanese production:

- Original Japanese title: 『少しだけ寂しいボクらの世界で』.
- Use the PNG images in the input folder for the main characters. Add other characters in the same visual style as needed. Everyone except the baby is a robot.
- Balloons should generally contain only images and symbols. Written narration in rectangular captions is fine, but use it only to explain the world and setting.
- character1 is the protagonist.
- Three hundred years after humanity died out from an infectious disease, robots live peacefully. They choose where to live, from forests to modern cities.
- The protagonist enjoys a peaceful, carefree life in the forest. One day, they discover a mysterious facility containing a crying human baby, even though humans are thought extinct. The baby is about ten days old.
- The facility has some food for humans, but at most about a year's supply.
- Although shy around strangers, the protagonist remembers a scientist robot who once helped them and sets out to seek advice.
- Continue developing the story and add world details as needed.
- The baby gradually grows into an adult. The full story should run about 15–20 episodes and end with [ending omitted here to avoid spoilers; a rough ending was supplied in the actual brief].
- Use about ten pages per episode. First develop the overall plot, then produce individual episodes.

The entire work could not be completed in one session, so the user made several requests such as “Please continue.” After automatic generation, a human visually inspected the pages and requested corrections to some malformed hands. A few issues remain.

This example includes only its three text-free reference images in the repository. The linked full comic is the original Japanese edition and is outside this English localization: [少しだけ寂しいボクらの世界で](https://manga.potechi-takusan.workers.dev/sukoshi-samishii/).

## 05

In this original Japanese-edition example, NovelAI generated art assets without lettering or panel borders. Codex handled panel layouts, asset placement, balloons, and vertical Japanese lettering. This records the historical workflow. The pages below were subsequently adapted for English with horizontal lettering and left-to-right reading.

Prompt used during production, organized as bullets for readability:

- I want to make a 6–12-page comic titled “An Incident in the Old Forest” using NovelAI.
- Use the hatching of style-01 for a weighty visual style.
- The party includes a burly warrior, a beautiful elf, a woman who helps the party, and other supporting characters.
- During a journey to another country, they enter a forest with a different atmosphere. Begin at camp while they watch for nearby monsters.
- After expressing a little unease and reassuring each other, they have a mysterious experience connected to the forest early the next morning.
- End with renewed awe of the forest. Leave a lingering sense of the inexplicable and irrational.

![Example 05, An Incident in the Old Forest, page 1 — English edition](05/page-001.jpg)

![Example 05, An Incident in the Old Forest, page 2 — English edition](05/page-002.jpg)

![Example 05, An Incident in the Old Forest, page 3 — English edition](05/page-003.jpg)

![Example 05, An Incident in the Old Forest, page 4 — English edition](05/page-004.jpg)

![Example 05, An Incident in the Old Forest, page 5 — English edition](05/page-005.jpg)

![Example 05, An Incident in the Old Forest, page 6 — English edition](05/page-006.jpg)

![Example 05, An Incident in the Old Forest, page 7 — English edition](05/page-007.jpg)

![Example 05, An Incident in the Old Forest, page 8 — English edition](05/page-008.jpg)

No human artwork revision requests were made during the original Japanese production. Codex inspected generated images and used regeneration or placement adjustments to address inconsistent character counts or clothing, extra weapons, and prop sizes.

The [original Japanese PSD library](https://examples-psd.potechi-takusan.workers.dev/) contains the original layered files. These external downloads have not been translated and do not match the English lettering shown here.

With NovelAI, PSD dialogue is on separate layers by default. With Codex's built-in image generation, request separation of dialogue from the image at the outset.

## 06

**The Sumeragi Detectives: “The Little Bookmark Case”**

User specifications for the original Japanese production:

- Make an approximately 12-page monochrome comic titled “The Sumeragi Detectives” using NovelAI.
- Use `style-10`.
- A relaxed comedy about three or four girls in the detective club at Sumeragi High School.
- Start with brief character introductions and finish with a pleasant feeling.
- Continue production through the preview stage.

![Example 06, The Sumeragi Detectives, page 1 — English edition](06/page-001.jpg)

![Example 06, The Sumeragi Detectives, page 2 — English edition](06/page-002.jpg)

![Example 06, The Sumeragi Detectives, page 3 — English edition](06/page-003.jpg)

![Example 06, The Sumeragi Detectives, page 4 — English edition](06/page-004.jpg)

![Example 06, The Sumeragi Detectives, page 5 — English edition](06/page-005.jpg)

![Example 06, The Sumeragi Detectives, page 6 — English edition](06/page-006.jpg)

![Example 06, The Sumeragi Detectives, page 7 — English edition](06/page-007.jpg)

![Example 06, The Sumeragi Detectives, page 8 — English edition](06/page-008.jpg)

![Example 06, The Sumeragi Detectives, page 9 — English edition](06/page-009.jpg)

![Example 06, The Sumeragi Detectives, page 10 — English edition](06/page-010.jpg)

![Example 06, The Sumeragi Detectives, page 11 — English edition](06/page-011.jpg)

![Example 06, The Sumeragi Detectives, page 12 — English edition](06/page-012.jpg)

During the original Japanese production, Codex used its built-in imagegen tool to edit details difficult to control through NovelAI prompts, such as the number of cookies on a page. The English adaptation also checked the cookie counts and bookmark clues.

The [original Japanese PSD library](https://examples-psd.potechi-takusan.workers.dev/) contains the original layered files. These external downloads have not been translated and do not match the English lettering shown here.

With NovelAI, PSD dialogue is on separate layers by default. With Codex's built-in image generation, request separation of dialogue from the image at the outset.
