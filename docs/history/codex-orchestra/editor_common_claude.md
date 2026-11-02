# Editor rules for the OrbitRows video (Claude subagents)

Folder: video_edit. Tool: `effectcraft-cli` (native Ubuntu; `effectcraft-cli --help`, `effectcraft-cli --project <file> script <jsx>`, `render`, `render-frame`). The previous editor's build scripts are in `build/` and are the reference for how to drive it: `build/kit.jsx` (function library: words, highlight, step panel, badges, tags, show/hide), and `build/s01_v2_full_v7.jsx` (scene 1, every element built as an editable layer, every beat a variable computed from a cue, plus a comp marker). Read the scene 1 script once to learn the pattern; reuse the kit.

Each scene has its OWN project file: `OrbitRows_v2_s0N.ecproj` (copies made for you). Never touch `OrbitRows_v2.ecproj`, `Untitled Project*.ecproj`, or any existing file in `preview/` and `build/`: new files only, with new version numbers. No git commits.

## What the user asked (apply everywhere)
- Animate only what changes. A new arrow, outline or tag appears by itself (250–400 ms ease-out, no bounce); the rest of the screen stays still. NEVER cross-fade a whole screen or a whole diagram to add one element (the user saw "the whole graph reload" in the last cut of scene 3).
- Few transitions; nothing on screen the viewer doesn't need; nothing that is a note for the editor.
- Check placement visually: centred things centred, chips of one line on one baseline, highlights exactly behind their word.
- Fonts Poppins and JetBrains Mono (installed). Colours: background #F9FEF6, teal #0A6E89, coral #FB938F, yellow #FED84D, lavender #C9BCEB, purple #6D5BA8, green #1FA35B, red #E63946.
- Right panel (x 632–940, y 20–520 at 960×540 scale; ×2 for 1920×1080): "THE PROMPT" on 3 lines, "Archive the draft Casa products" / "created in September," / "and show them." (the prompt now says AND, not "then"), then "WHERE WE ARE" with the 6 steps. From scene 2 on, the panel prompt is plain: no markers, no tags on it, no strikes. The active step is teal, a finished step gets a green tick.
- Layout source of truth: the storyboard SVGs `storyboard/v20_sceneNN/sN_MM.svg` (960×540, scale ×2) and their captions in `storyboard/storyboard_v20.pdf`. Each SVG is the stage at the END of its moment; you animate the way in. Build every element as an editable layer (text, shapes, imported icon paths from `icons/v3/` then `icons/v1/`; the gear is `icons/v1/code.svg`). Do not import the storyboard SVGs as footage.
- Soundtrack: the scene's mix in `audio/mixed/` as is. Scene length = last word end + 1.5 s.

## Deliverables per scene
720p H.264 preview with the audio, and one 1080p still per storyboard screen taken at the end of its moment (just before the next cue). Look at every still yourself and compare it with the storyboard SVG (render the SVG with `google-chrome --headless=new --no-sandbox --screenshot=… --window-size=960,540 file://…` if useful) before reporting.

## Report (short)
Paths, durations; each gate's result in one line; every departure from the storyboard and why; anything not done.

## Audio check (added after a wrong-narration render)
The kit's `newScene` reuses a project item by FILE NAME. Two soundtracks with the same name in different folders (e.g. `scene07_master_C_v1.wav`) then silently pick the OLD one. Import the soundtrack by its full path every time (never reuse by name), and before reporting, prove the preview carries the right audio: correlation of the preview's first 20 s with the given WAV must be ≥ 0.99.

## Group fades
In effectcraft, a parent layer's opacity does not pass to its children: a group that fades or moves needs the same keys on every child layer (the kit's `flyTag` does this), or text shows before its card.
