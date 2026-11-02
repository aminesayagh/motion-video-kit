# Brief NNN: editor, scene <N> (<title>), version <vK>

You are the editor. Build ONE scene in EffectCraft as editable layers, timed on the narration's words
(docs/04-artcraft-linux.md, docs/06-style-rules.md). Do not touch any other scene or project.

## Inputs
- Storyboard: `<project>/storyboard/v<S>_scene<NN>/s<N>_MM.svg` (layout source of truth, 960×540, scale ×2) and
  their captions in `storyboard_v<S>.html`. Each SVG is the stage at the END of its moment: you animate the way in.
- Words: `<out>/voice/scene<NN>_<tag>.words.json`. Soundtrack: `<out>/sound/scene<NN>_master_C_<tag>.wav`.
- Kit: `tools/edit/kit.jsx`. Closest template: `tools/edit/templates/<template>.jsx`. Icons: `<project>/icons/`.
- Project: `<project>/<name>_s<NN>.ecproj` (this scene's own project).

## What to build
<screen by screen: what appears on which cue phrase, what leaves when>

## Rules
- Every beat is a variable computed from a cue phrase (`cue('...')`, never a literal time) and a comp marker.
- Animate only what changes; never cross-fade a whole screen to add one element. 250–400 ms ease-out, no bounce.
- Nothing appears before its words; each element leaves ≥ 1 s after its last spoken word.
- Nothing on screen that is a note for the editor. Don't import storyboard SVGs as footage.
- Import the soundtrack by its full path (never reuse a project item by name). End the script with `app.project.save();`.
- A fading group: the same opacity keys on every child layer.
- One render at a time, one effectcraft-cli process. Never overwrite a preview or still; new version names only.

## Command
`python tools/edit/build_scene.py --scene <scene.jsx> --words <words.json> --audio <master.wav> --icons <icons> --out build/s<NN>_<vK>.jsx --project <ecproj> --stills preview/s<NN>_<vK> --preview preview/s<NN>_<vK>.mp4`

## Gates
- G1 — CHECK: `ffprobe ... preview/s<NN>_<vK>.mp4` — EXPECT: h264 1280×720 30 fps with AAC audio; duration = soundtrack length (± 1 frame).
- G2 — CHECK: correlation of the preview's first 20 s with the soundtrack (docs/07) — EXPECT: r ≥ 0.99, lag 0.
- G3 — CHECK: one still per storyboard screen, each compared with its SVG — EXPECT: same elements, placement, text; list every difference.
- G4 — CHECK: `grep -nE "cue\('[^']*', *[0-9]" build/s<NN>_<vK>.jsx` — EXPECT: no literal search times.
- G5 — CHECK: <scene-specific: e.g. "frame at <cue+0.3 s> shows X; frame at <cue-0.1 s> doesn't">.

## Report (short)
Paths and durations; each gate in one line; every departure from the storyboard and why; anything not done.
