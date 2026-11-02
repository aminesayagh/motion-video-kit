# OrbitRows video: the orchestra

Four local Codex sessions, one per role, each driving one tool. The orchestrator (the Claude session `orbitrows_script`) plans, writes briefs, reviews, and brings each scene to the user. The previous Claude specialist sessions (graphist, speak, illustrator) are retired.

| Role | Tool it manages | Delivers to |
| --- | --- | --- |
| illustrator | VectorCraft (MCP `vectorcraft`) | `icons/vN/` |
| editor | EffectCraft (MCP `effectcraft-orbit-rows`, project `Untitled Project.ecproj`) | `preview/` |
| voice | the local Kokoro pipeline in `voicer` (no ArtCraft tool) | `voicer/out/voice/` |
| sound | SoundCraft (MCP `soundcraft`) | `audio/mixed/` |

FilmCraft, PhotoCraft and LightCraft are installed but not assigned. FilmCraft would suit a final assembly of the scenes, if we ever want one.

## How a brief travels

1. The orchestrator writes a brief as a file in `roles/<role>/inbox/` (for example `001_scene05_icons.md`).
2. It runs `./run.sh brief <role> <that file>`. Codex works headless, with only that role's tool, and writes its report to `roles/<role>/outbox/<brief>_report.md` (a full log sits next to it).
3. The orchestrator reads the report, checks the deliverables, and shows them to the user. Nothing moves to the next scene until the user says yes.

Every brief resumes the same Codex session of that role (one folder, one session), so a role remembers earlier briefs. Roles cannot message the orchestrator: it reads the outbox.

## Commands

Run them from `video_edit/orchestra/`. Every ArtCraft tool runs natively on Ubuntu (`/usr/bin/*craft-cli`); nothing goes through Windows.

- `./run.sh status` : briefs and reports per role.
- `./run.sh brief <role> <brief.md>` : send a brief (headless).
- `./run.sh open <role>` : open the role's Codex interactively, to watch or talk to it. The first time, Codex asks you to trust the folder. Use one terminal per role.

## Rules and files

- `common.md` holds the rules every role follows, and `roles/<role>/role.md` holds that role's own. `run.sh` joins them into `roles/<role>/AGENTS.md` before every use, which is the file Codex reads. Edit `common.md` or `role.md`, never `AGENTS.md`.
- `board.md` is the scene board, kept by the orchestrator.
- Each role's sandbox can write only its own folders (see `run.sh`). Other MCP servers of your Codex config (serena, excalidraw, code-review-graph, and EffectCraft for the roles other than the editor) are switched off for these runs; your global config is not changed.

## Checked

- 2026-10-31, on Ubuntu: the VectorCraft, EffectCraft, SoundCraft and FilmCraft MCP servers start and list their tools (33, 27, 17, 17). The editor role built and rendered scene 1 headless, without any approval prompt. Poppins and JetBrains Mono are installed for the user (`~/.local/share/fonts/orbitrows/`).

- The VectorCraft, SoundCraft and FilmCraft MCP servers start and list their tools (33, 17 and 17).
- A headless brief creates a session, the next brief resumes the same session and remembers the first, and only the role's own tool is visible. This was tested on a scratch folder with the sound role; no real role has received a brief yet.
- Not tested yet: a real VectorCraft or EffectCraft task, and the voice role running the Kokoro pipeline.

## Things to know

- A headless brief can take several minutes. Run it in the background if you want your terminal back.
- A role that finds the brief unclear writes that in its report instead of guessing.
- The storyboard (the HTML page with the drawn states) is made by the orchestrator, not by one of the four roles.
