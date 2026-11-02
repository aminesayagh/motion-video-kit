# 4. ArtCraft tools on Ubuntu

EffectCraft (motion graphics, After Effects–style scripting) and SoundCraft (audio sessions and plugins) run natively on Ubuntu as `effectcraft-cli` and `soundcraft-cli` in `/usr/bin`. VectorCraft (`vectorcraft-cli`) was used for icons. Nothing goes through Windows, even under WSL.

## effectcraft-cli

What it is: a headless EffectCraft. It opens a `.ecproj` project, runs JavaScript against an After Effects–style object model (`app.project`, comps, layers, properties), and renders.

```bash
effectcraft-cli --help
effectcraft-cli script build/s08_v1.jsx OrbitRows_s08.ecproj          # run a script on a project
effectcraft-cli --project P.ecproj render-frame --comp "S08 v1" --time 31.79 --out still.png
effectcraft-cli --project P.ecproj render --comp "S08 v1" --format h264 --resolution 0.6666667 --audio on --out preview.mp4
effectcraft-cli --project P.ecproj render --comp "S08 v1" --format h264 --resolution full --quality best --audio off --bitrate 14000 --out s08_1080.mp4
effectcraft-cli --project P.ecproj props "S08 v1" "layer name"        # a layer's property tree, to debug keys
```

How scenes are built here:

- `tools/edit/kit.jsx` is the function library: text, rounded rects, paths from SVG, fades and slides, markers, the right panel, chips, tags, ticks, and `cue('phrase')` / `cueEnd` / `narrationEnd` on the narration's word times.
- A scene file uses the kit and computes every beat from a cue, plus a comp marker per beat. A new voice take only needs a rebuild.
- `build_scene.py` prepends `WORDS`, `ICONS` and `AUDIO` to kit + scene, runs it, renders stills (`STILL <name> <seconds>` lines the script prints) and the preview.
- One project per scene (`<video>_s0N.ecproj`), so a rebuild of one scene can't damage another.
- Templates in `tools/edit/templates/`: `code_editor.jsx` (dark code-editor cards, typed code, a highlight band moving node by node), `table_tree_hidden_panel.jsx` (the panel slides out to give the full width; a table and an operation tree), `matching_strip.jsx` (slots filled on cues, shrinking into a strip that persists). Their timings are the OrbitRows cues: replace the `T = {…}` table and the content for your scene.

## soundcraft-cli

```bash
soundcraft-cli plugins                      # built-in plugins (eq_7band, expander_gate, maximizer, ...)
soundcraft-cli describe mix.insert          # one command's parameters as JSON
soundcraft-cli run --cmd 'session.new={"name":"s1","sample_rate":24000,"bit_depth":24}' \
  --cmd 'file.import_audio={"path":"/abs/take.wav"}' \
  --cmd 'mix.insert={"track":2,"slot":0,"plugin":"eq_7band","params":{"hpf_on":1,"hpf_freq":80,"hpf_slope":3}}' \
  --cmd 'file.bounce_mix={"path":"/abs/out.wav","format":"wav","bit_depth":"32f","dither":false}'
```

- The imported take lands on **track 2**; check `'track":2'` in the output.
- The session pans a mono track to the centre with a -3 dB pan law: account for it when you set a ceiling in dBFS.
- `--save session.scraft` copies every imported file into an `Audio Files` folder next to it. Don't save sessions you don't need.

## MCP servers (for agents)

An MCP server exposes a tool's commands to an AI agent. Each ArtCraft CLI has one (`mcp` subcommand, JSON-RPC over stdio).

**Claude Code** (project scope, one server per tool):

```bash
claude mcp add effectcraft -- effectcraft-cli mcp --project /abs/path/MyVideo_s01.ecproj
claude mcp add soundcraft -- soundcraft-cli mcp
claude mcp add vectorcraft -- vectorcraft-cli mcp --headless --automation-read-root /abs/video --automation-write-root /abs/video/icons
```

In practice the Claude subagents drove the CLIs through Bash (`effectcraft-cli script …`), which needs no MCP setup and keeps every command in the log. Use MCP when an agent must inspect a live project interactively.

**Codex** (the earlier setup, per run, without touching the global config):

```bash
codex exec --sandbox workspace-write --add-dir "$ROOT" \
  -c 'mcp_servers.effectcraft.command="effectcraft-cli"' \
  -c 'mcp_servers.effectcraft.args=["mcp","--project","/abs/MyVideo.ecproj"]' \
  -c 'mcp_servers.serena.enabled=false' "<prompt>"
```

or permanently in `~/.codex/config.toml`:

```toml
[mcp_servers.effectcraft]
command = "effectcraft-cli"
args = ["mcp", "--project", "/abs/MyVideo.ecproj"]
```

`--automation-read-root` / `--automation-write-root` confine what the agent's tool may read and write. Give each role only its own tool and only its own output folder (see `docs/history/codex-orchestra/run.sh`).

## Fonts

Install Poppins and JetBrains Mono for your user (requirements/system.md), run `fc-cache -f`, and check the PostScript names with `fc-list : postscriptname`. The kit sets `Poppins-Bold`, `Poppins-SemiBold`, `Poppins-Regular`, `JetBrainsMono-Regular`, `JetBrainsMono-Bold`. If a font is missing, EffectCraft silently falls back to another face: word layers positioned with the fallback's widths then overlap once the real font is installed. Install the fonts before the first build.

## Gotchas found (and the fix)

1. **A script does not save the project.** `effectcraft-cli script s.jsx P.ecproj` runs, prints, and exits; the comps vanish. End every scene script with `app.project.save();`. (`build_scene.py` warns if it is missing.)
2. **Reusing a footage item by file name picks the old file.** The first kit looked up the soundtrack with `findItem("scene07_master_C_v1.wav")`. Two files with that name in different folders: the preview silently used the OLD narration. Always `importFile` by full path (the kit's `newScene` now does), and gate it: the preview's first 20 s must correlate ≥ 0.99 with the given WAV (docs/07).
3. **A parent's opacity does not reach its children.** In EffectCraft, parenting carries position/scale/rotation, not opacity. A group that fades needs the same opacity keys on every child (the kit's `flyTag` does this), or the text shows before its card.
4. **`moveAfter(x)` puts the layer BELOW x** (layer stacking order, as in After Effects: after = lower). To put a highlight behind a word, `highlight.moveAfter(word)`; to bring something on top, `moveBefore`.
5. **JetBrains Mono turns `>=` into `≥`** (a ligature). For code on screen, put a zero-width non-joiner between the characters: `'>‌='`. It takes no column in a monospaced layout.
6. **720p preview = `--resolution 0.6666667`** of the 1920×1080 comp. `half` gives 960×540 and a blurry review.
7. **SVG arc commands (`A`/`a`) are not supported** by the kit's path importer (nor by EffectCraft's shape import). Draw icons with lines and cubic curves only; a hole uses an even-odd compound path. Tell the illustrator up front.
8. **One render at a time.** Two effectcraft-cli renders in parallel, or a render beside a TTS model, exhausted WSL's memory and killed the session. Render stills and videos sequentially in one process, and nothing heavy beside them.
9. **Cross-fading a whole screen to add one element** looks like the whole diagram reloading. Build each element as its own layer and animate only the one that changes (an earlier editor imported full storyboard frames as footage: a one-arrow change then reloaded the graph).
10. **Literal times rot.** `cue('show', 4)` uses 4 s as a search start; when the voice changes, it finds the wrong word. Search after another cue instead: `cue('show', cue('needs one kind of action'))`. A missing cue throws, so a stale script fails loudly instead of drifting.
11. **Concatenating renders with stream copy can drop frames** when renders carry different time bases. Use the concat filter and re-encode (`tools/assemble/concat_film.sh`).
12. **Storyboard SVGs are not footage.** Don't import them; rebuild every element as an editable layer from the SVG's coordinates (×2).
13. **No PDF renderer for agents?** If `pdftoppm` is missing, the editor reads the SVGs and the captions in the storyboard HTML instead; or screenshot an SVG with `google-chrome --headless=new --no-sandbox --screenshot=out.png --window-size=960,540 file:///abs/s1_01.svg`.
