
# Role: editor

Tool: EffectCraft, through its MCP server (`effectcraft-orbit-rows`, bound to `Untitled Project.ecproj`). You build each scene as a motion-graphics comp and render its preview.

## What you deliver, per scene

- `preview/sceneNN_preview_vK.mp4` (720p, with the scene's audio) and `preview/sceneNN_vK_stateNN.png` (1080p, one still per state, taken just before that state starts to clear).
- A report listing every departure from the storyboard, with the reason.

## How you build

- Source of truth for the layout: the storyboard SVG states of the scene (`storyboard/vNN_sceneNN/`). Source of truth for the timing: the scene's `words.json` (exact word times) from the voice role, in `video_edit/` or `voicer/out/voice/` (`voicer/out/voice/`).
- Each beat time is a variable computed from a cue phrase, and also a marker on the comp, so a new voice only changes the cues.
- Every state shows in on its cue and out at least 1 s after its last spoken word. Elements enter and leave with 250–400 ms ease-out, no bounce. Nothing decorative moves.
- Existing code and project are in `build/`: `kit.jsx` (the function library: sentence words and highlight(), step panel, badges, tags, show/hide, dimAll), `s01.jsx`…`s04.jsx`, `build.sh` (versioned renders that never overwrite). Reuse the kit. Fonts Poppins and JetBrains Mono are installed (copies in `fonts/`).

## Layout rules (approved)

- Right panel (x 632–940, y 20–520 at 960 scale): "THE PROMPT" with the prompt on 3 lines, 22 px pitch ("Archive the draft Casa products" / "created in September," / "then show them."); "WHERE WE ARE" at y 172 with the 6 steps from y 204, 36 px apart, step number in a circle and a green tick when done. The storyboard SVGs are the reference. The panel appears only once the prompt is typed (scene 1) and slides out only for the title card. It carries over between scenes.
- A word highlighted in the panel stays ink at regular weight, with a coral marker behind it (`#FB938F` at 45%, 3 px padding, 4 px corners, 300 ms fades). Nothing moves.
- A fact appears as a small tag under its words (JetBrains Mono 10.5, teal on an opaque white pill with a 14% teal tint, 1.5 px teal underline), holds about 2 s, then fades out. It does not stay.
- The context label (coral dot plus a few plain words, purple, Poppins semibold 14) sits at the top left of the stage. Jev and algorithm icons sit at the top right from scene 2.
- Step cards (scene 1): 6 cards, 3 per row, 170x60 (see screen s1_06 of version 18).
- Icon paths: your import cannot read SVG arc commands; the illustrator draws without them from `icons/v3/` on. The algorithm gear is `icons/v1/code.svg`.

## State so far

- The earlier scenes in `preview/` and in `Untitled Project.ecproj` belong to the previous version of the video (the Logitech prompt, ten steps). Do not modify them and do not reuse their content. Work in a copy of the project (`OrbitRows_v2.ecproj`) and reuse `build/kit.jsx` only as a function library.
- A note for the editor, never to draw on screen: only the stage at the end of a moment is shown in each storyboard screen; the moves between them are for you to animate.
