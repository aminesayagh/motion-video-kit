# 1. Workflow

The video is made scene by scene. Each stage has one owner who makes it and one person who approves it: the user. An agent's own review is useful input, but it is never the approval.

## The stages

| # | Stage | Made by | Output | Approved by |
| --- | --- | --- | --- | --- |
| 1 | Script | user + orchestrator | the story in plain words, one example that runs through the whole video | user |
| 2 | Storybook | orchestrator | per scene: the narration text (final wording) and what the screen shows | user |
| 3 | Storyboard | orchestrator | one SVG per screen (the stage at the END of its moment), HTML/PDF board | user |
| 4 | Voice | voice agent | `sceneNN_vK.wav` + `sceneNN_vK.words.json` | user (listens) |
| 5 | Sound | sound agent | scene master: cleaned, -18 LUFS, same length as the take | user (listens) |
| 6 | Edit | editor agent | the scene comp, a 720p preview with sound, one 1080p still per screen | user (watches) |
| 7 | Assemble | sound agent | 1080p renders, film mix, `film.mp4`, chapters | user |

Stages 4–6 repeat per scene. The next scene's voice starts only after the user says yes to the current scene.

## 1. Script

- Pick **one example** and keep it on screen through the whole video (in OrbitRows: "Archive the draft Casa products created in September, and show them."). Every scene explains one step of what happens to it.
- Name the steps once and number only the main ones on screen. Sub-steps are named in the narration, never numbered.
- Describe what the product does today. Anything still being built is fixed in the product before the video ships, or left out.

## 2. Storybook

A Markdown file: an intro (the example, the steps, the data on screen), then one `# Scene N · Title` section per scene with its narration and screen notes. `tools/storyboard/book.py` turns it into a PDF for review. Example: `examples/orbitrows/storybook.md`.

When the narration of a scene is approved, copy it to `narration/sceneNN.txt` (paragraphs separated by a blank line). That file is the voice step's only input.

Write the narration for the ear:

- Short sentences. One idea per sentence.
- Spell numbers the way they are said ("ten percent", "two hundred grams") unless the screen shows the digits.
- Avoid stacked "and … and …" (the TTS swallows the second "and").

## 3. Storyboard

`tools/storyboard/story.js` describes each scene as a list of frames; `build.py` draws them with the same code in the browser (HTML board, PDF) and in Node (one SVG per frame).

- An SVG shows only what the viewer sees at the end of that moment. Notes for the editor (motion paths, "kept on the right", sources) go in the caption under the frame, never inside it.
- The SVG is the layout source of truth for the editor, at 960×540 (the video is 1920×1080: everything ×2).
- Icons: plain `<path>`, `<rect>`, `<circle>`, no arc commands, no transforms (see docs/04).

## 4–6. One scene

1. **Voice.** The voice agent makes the take with `tools/voice/run_scene.sh` and reports what Whisper heard, which chunks were retried, and the spots to listen to. The user listens. Word fixes go into the config's `spoken` map, never into the narration text.
2. **Sound.** `tools/sound/master.py master --setting C` on the approved take. Same length, so the word times stay valid.
3. **Edit.** The editor writes the scene file (start from a template in `tools/edit/templates/`), every beat a `cue('phrase')`. `build_scene.py` builds it, renders one still per storyboard screen and a 720p preview. The editor compares each still with its SVG before reporting.
4. **User review.** The orchestrator shows the preview and the editor's list of departures from the storyboard. Directed small fixes (a label wording, a nudge the user described) are applied without another round of confirmation; anything else waits for the user.

Every output gets a new version name (`v1`, `v2`, …). A file the user is reviewing is never overwritten: an in-place re-render once broke the file being watched ("moov atom not found").

## 7. Assemble

1. Render every approved comp at 1080p, **one at a time**: `tools/edit/render_final.sh`.
2. `film_voice.py`: one 48 kHz voice track, each scene master placed at its scene's start (video frames × 1600 samples) and padded with noise matched to the masters' pauses (never digital silence). It writes `layout.json`.
3. `make_bed.py`: the music bed, exactly the film's length.
4. `film_mix.py`: clean and duck the bed, one gain to -16 LUFS, a gentle true-peak limiter.
5. `concat_film.sh`: join the renders (re-encoded with the concat filter) and mux the mix.
6. `chapters.py` and `film_gates.py`.

### Cutting a span after assembly

When the user drops a section from a finished scene (in OrbitRows: 10.8 s of scene 3):

- Choose frame-exact in/out points where both sides are quiet and no element is half-faded. Check the frames on both sides before choosing.
- Audio: `cut_span.py` removes the span from the voice track with a 30 ms equal-power crossfade and writes a new layout. Then rebuild the bed for the new length and remix.
- Picture: hold the last full frame before the cut for ~9 frames and crossfade 0.3 s into the frame after the out-point (a dissolve from a still hides a half-faded card).
- `film_gates.py` checks the join (no click, PSNR either side).

## Who approves what

- The user approves the script, the storybook, each storyboard, each scene's voice, each scene's picture and the film.
- The orchestrator relays the approval to the agents. It never approves "from its side" on the user's behalf. (Once it did, and a voice session rendered all 13 scenes ahead of review.)
- Agents act only on a brief. No brief, no work; a brief that says STOP or HOLD means do nothing.
