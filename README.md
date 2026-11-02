# motion-video-kit

A local toolchain for making a narrated motion-graphics explainer video on Ubuntu (or WSL2): voice, sound, animation and assembly, driven by AI agents with checkable gates.

It is the method behind a 9.5-minute product explainer (the OrbitRows video, kept here as the worked example). Everything runs on your machine: no cloud TTS, no paid API, no upload of the script.

## What is in it

| Part | What it does | Tools |
| --- | --- | --- |
| Storyboard | Draws every screen as an SVG "end state", plus an HTML/PDF board and a storybook PDF | Node, headless Chrome |
| Voice | Clones a narrator from a 15 s reference clip and reads the script, chunk by chunk, with a strict word check on every take | Qwen3-TTS, faster-whisper |
| Sound | Cleans and levels each scene, synthesises a music bed, ducks it under the voice, masters the film | SoundCraft (`soundcraft-cli`), ffmpeg, numpy |
| Edit | Builds each scene as editable layers from a script, timed on the narration's word times | EffectCraft (`effectcraft-cli`) |
| Assemble | Joins the scene renders, muxes the film mix, writes chapters, runs the final gates | ffmpeg |
| Orchestration | One agent per tool, briefs with pass/fail gates, the user approves each scene | Claude Code subagents (earlier: Codex) |

## The pipeline

```text
 script ──► storybook ──► storyboard (SVG end states)
   │            (text, approved)        │
   ▼                                    │
 narration per scene ──► voice take + words.json ──► scene master (-18 LUFS)
                              │                            │
                              ▼                            │
                   scene build (EffectCraft, cues = words) │
                              │                            │
                              ▼                            ▼
                    720p preview + stills ──► USER APPROVES THE SCENE ──► next scene
                                                           │
                         all scenes approved ──► 1080p renders, one at a time
                                                           │
             voice-only film track ──► music bed ──► duck + master (-16 LUFS)
                                                           │
                                     concat + mux ──► film.mp4 + chapters ──► final gates
```

Two rules hold the whole thing together:

- **Words drive time.** The voice step outputs `words.json` (`[{word, start, end}]`). Every animation beat is computed from a cue phrase in it, so a new take only needs a rebuild.
- **Nothing moves forward without a yes.** The user approves each scene (voice, then picture) before the next one starts. Agent reviews are input to the user, not approval.

## Quick start

These steps take a new project from a script to a film. Each links to the doc with the details.

1. **Install the system tools** (once): see [requirements/system.md](requirements/system.md). You need ffmpeg, Node, Google Chrome, the fonts, and the ArtCraft CLIs for the edit and sound steps.
2. **Create the Python environments** (once):
   ```bash
   uv venv --python 3.12 .venv-tts && uv pip install --python .venv-tts/bin/python -r requirements/tts-qwen.txt
   uv venv --python 3.12 .venv-sound && uv pip install --python .venv-sound/bin/python -r requirements/sound.txt
   ```
3. **Write the script and storybook.** One text file per scene, paragraphs separated by a blank line (see `examples/orbitrows/narration/`). The storybook is the approved text plus what each screen shows ([docs/01-workflow.md](docs/01-workflow.md)).
4. **Draw the storyboard** from your own `story.js`:
   ```bash
   python3 tools/storyboard/build.py --version 1 --out storyboard/ --icons icons/ --fonts fonts/
   ```
5. **Pick the narrator.** Put a clean 10–15 s clip and its exact transcript in a folder like `voice/reference/` (you need the rights to that voice). Copy `examples/orbitrows/voice.json` and point it at your texts and clip.
6. **Make one scene's voice**, listen, fix words in the `spoken` map, repeat:
   ```bash
   . .venv-tts/bin/activate
   tools/voice/run_scene.sh my-video/voice.json 1 v1
   ```
   Deliver `sceneNN_v1.wav` + `sceneNN_v1.words.json` ([docs/02-voice-tts.md](docs/02-voice-tts.md)).
7. **Master the scene's sound** (setting C was the approved one):
   ```bash
   .venv-sound/bin/python tools/sound/master.py master --setting C --take out/voice/scene01_v1.wav --out out/sound/scene01_master_C.wav
   ```
8. **Build the scene** from a template, then render stills and a 720p preview ([docs/04-artcraft-linux.md](docs/04-artcraft-linux.md)):
   ```bash
   python3 tools/edit/build_scene.py --scene my-video/s01.jsx --words out/voice/scene01_v1.words.json \
     --audio out/sound/scene01_master_C.wav --icons icons/ --out build/s01_v1.jsx \
     --project my_s01.ecproj --stills preview/s01_v1 --preview preview/s01_v1.mp4
   ```
9. **Get the user's yes**, then repeat 6–8 for the next scene.
10. **Finish the film** ([docs/03-sound.md](docs/03-sound.md), [docs/01-workflow.md](docs/01-workflow.md)):
    ```bash
    tools/edit/render_final.sh render_list.txt out/1080                        # one render at a time
    python tools/sound/film_voice.py --scenes film_scenes.json --out out/film/voice.wav --layout out/film/layout.json
    python tools/sound/make_bed.py --layout out/film/layout.json --out out/film/bed.wav
    python tools/sound/film_mix.py --voice out/film/voice.wav --bed out/film/bed.wav --layout out/film/layout.json \
      --out-mix out/film/mix.wav --out-bed out/film/bed_ducked.wav --stats out/film/mix_stats.json
    tools/assemble/concat_film.sh out/film/mix.wav out/film/film.mp4 out/1080/scene0*_1080.mp4
    python tools/assemble/chapters.py out/film/layout.json > out/film/chapters.txt
    python tools/sound/film_gates.py --film out/film/film.mp4 ... --out out/film/gates.json   # see docs/07
    ```

If agents do the work, give each one a brief from [templates/briefs/](templates/briefs/) and follow [docs/05-orchestration.md](docs/05-orchestration.md).

## Requirements

- Ubuntu 22.04+ or WSL2 Ubuntu. Measured on a laptop with an RTX 4060 (8 GB VRAM) and 15 GB RAM in WSL.
- An NVIDIA GPU with CUDA for Qwen3-TTS (CPU works for Whisper and for the earlier Chatterbox engine, slowly).
- Python 3.12 for the TTS venv, Node 18+, ffmpeg 6+, Google Chrome (headless, for PDFs and SVG previews).
- EffectCraft and SoundCraft CLIs (ArtCraft suite, native Linux builds) for the edit and sound steps. The voice, music bed, mix and assembly steps need only Python and ffmpeg.

Pip requirements per environment are in [requirements/](requirements/).

## Docs

1. [Workflow](docs/01-workflow.md): the stages, who makes and who approves what.
2. [Voice (local TTS)](docs/02-voice-tts.md): Qwen3-TTS cloning, the checks, spoken-text tricks, regenerating one chunk.
3. [Sound](docs/03-sound.md): cleanup settings, loudness targets, music bed, ducking.
4. [ArtCraft on Linux](docs/04-artcraft-linux.md): `effectcraft-cli` / `soundcraft-cli`, MCP setup, every gotcha found.
5. [Orchestration](docs/05-orchestration.md): briefs with gates, review, resource limits, agents.
6. [Style rules](docs/06-style-rules.md): the visual and editing rules the user set.
7. [Gates catalog](docs/07-gates-catalog.md): reusable check commands.

## Layout

```text
tools/voice/       qwen_takes.py (approved method), run_scene.sh, patch_tails.py, soften.py, release.py,
                   final_check.py, replace_chunk.py, qwen_quick.py, chatterbox/ (earlier engine)
tools/sound/       master.py (+ master_gates.py), expander_mix.py (earlier), make_bed.py, film_voice.py,
                   cut_span.py, film_mix.py, film_gates.py, common.py
tools/edit/        kit.jsx (function library), build_scene.py, render_final.sh, templates/*.jsx
tools/storyboard/  build.py, book.py, helpers.js, story.js (example), page.css, intro.html
tools/assemble/    concat_film.sh, chapters.py
templates/briefs/  voice, sound and editor briefs with gate lines
examples/orbitrows the nine narration texts, the storybook, the voice config, chapters
voice/reference/   the narrator reference clip (NOT under the MIT licence, see its NOTICE.md)
docs/history/      the earlier Codex-based orchestra, kept for reference
```

## Licence

The code and docs are MIT ([LICENSE](LICENSE)). No voice audio is shipped: put your own reference clip in `voice/reference/` ([voice/reference/NOTICE.md](voice/reference/NOTICE.md)). Model weights (Qwen3-TTS, Whisper, Chatterbox, Kokoro) keep their own licences and are downloaded on first use, not shipped here.
