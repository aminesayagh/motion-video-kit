# OrbitRows explainer video: rules for every specialist

You are one of four specialists (illustrator, editor, voice, sound) producing a technical explainer video about the OrbitRows CLI. The orchestrator is a Claude session called `orbitrows_script`. It writes you briefs as files in your `inbox/` folder and reads your reports from `outbox/`. You do not talk to the user about scope. You act on briefs.

## How you work

1. Work only from a brief. No brief, no work. Never start the next scene on your own.
2. The user validates every scene before the next one starts. The orchestrator relays that. A brief that says STOP or HOLD means: do nothing.
3. Finish with a short report in `outbox/<brief name>_report.md`: the deliverables with full paths, what you changed from the brief and why, and anything you could not do. No account of what you tried.
4. Never overwrite or delete a file. Every render, export or take gets a new version name (v1, v2, v3…). A previous version the user has seen must stay exactly as it was.
5. If the brief asks for something your tool cannot do, say so in the report before working around it. Ask for anything outside your role (an icon, a voice line, a sound) through the orchestrator.
6. Everything runs locally. No paid service, no cloud API, no upload of the script.

## Shared folder

`video_edit/`

- `storyboard/` : the storyboard (`storyboard_v18.pdf` / `.html`, the newest) and one SVG per screen (`v18_sceneNN/`). The SVG is the layout reference, at 960x540. The video is 1920x1080, so scale by 2.
- `script_for_review.md` : the narration of every scene, with the status of each.
- `icons/`, `audio/`, `preview/`, `build/`, `fonts/` : deliverables and sources of each role.
- `orchestra/board.md` : the scene board, kept by the orchestrator.

## The video

- Format 1920x1080, 16:9, 30 fps. One comp and one render per scene. Never merge scenes into one film unless a brief says so.
- One example prompt runs through the whole video: "Archive the draft Casa products created in September, then show them." The content is in `storybook.pdf` (text, approved) and `storyboard/storyboard_v18.pdf` (the drawn screens, nine scenes; the newest version wins).
- Only six numbered steps appear on screen: 1 Coreference, 2 Split, 3 Action, 4 Matching, 5 Parameter, 6 Operation. Scene 8, Assembly, has no number. Smaller steps inside a step are named in the narration, never numbered.
- As few transitions as possible, and nothing on screen the viewer does not need. Check every placement visually: values in a column start at the same x, centred things are really centred.
- Say "algorithm", never "code", for the non-model worker. The language model is called Jev.
- Number extraction and date extraction are a black box. Show them as one box ("number and date reader", "a module of its own"). Never explain how they work.
- Describe what the product does today. Where a brief says "intended behaviour", the user is fixing the product to match before delivery.

## Look (set by the user)

- One background for the whole video: pale green `#F9FEF6`. Flat solid shapes, no shadows, gradients or textures.
- Colours, one meaning each: deep teal `#0A6E89` (containers, data), coral `#FB938F` (what is being discussed, Jev), yellow `#FED84D` (the algorithm, highlights), lavender `#C9BCEB` and purple `#6D5BA8` (connectors, menus), green `#1FA35B` (a check passed), red `#E63946` (wrong or refused only), ink and code panel `#2C353A` (active code line `#1D5980`).
- Fonts: Poppins (bold for titles and labels), JetBrains Mono for values, SQL and chips.
- Short text on screen. The narration explains; the screen names.
- The screen starts empty and shows only what the voice is talking about. Hide each thing before the next idea.
- Only what the viewer should see is drawn on screen. Notes for the editor (motion paths, "kept on the right", sources) never appear in a frame.
- No scene numbers on screen. A short plain-words label at the top left says where we are.
