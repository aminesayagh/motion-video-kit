# 5. Orchestration

One main session (the **orchestrator**) talks to the user, writes briefs, reviews deliverables and relays approvals. **Specialist agents** do the tool work: voice, sound, editor (and an illustrator for icons). The orchestrator doesn't drive the tools itself and never approves on the user's behalf.

## Current approach: Claude Code subagents

Each piece of tool work is one subagent with one brief. Why this replaced the earlier Codex setup:

- Codex hit its usage limit in the middle of a scene and stopped.
- Codex's editor built two scenes by cross-fading full storyboard screens imported as footage, so a one-arrow change reloaded the whole graph. The Claude editor built every element as an editable layer.

How a brief travels:

1. The orchestrator copies a template from `templates/briefs/`, fills in paths, the text or cues, and the **gates**.
2. It starts a subagent with the brief. Heavy work runs in the background; the orchestrator waits for the notification instead of polling.
3. The subagent works, runs every gate itself, and returns a short report: deliverables with full paths, each gate's result in one line, every departure from the brief and why, anything not done.
4. The orchestrator **re-checks** the cheap gates itself (ffprobe, the correlation check, looking at the stills), then shows the scene to the user.
5. On the user's yes, the next scene's brief goes out. On a change request, a new brief with a new version number.

A follow-up on the same work (fix one thing) goes to the same agent (Claude Code: `SendMessage` to its id), so it keeps its context. A new task gets a new agent.

## Briefs with gates

A **gate** is a check with a command and an expected result, written into the brief. The agent may not report "done" without running them. Format:

```text
G3 — CHECK: ffmpeg -i out/scene05_master_C.wav -af ebur128=peak=true -f null - 2>&1 | tail -12
     EXPECT: I between -18.3 and -17.7 LUFS; Peak <= -1.0 dBFS
```

Good gates are cheap, objective and tied to a past failure: the audio correlation gate exists because a preview once carried the wrong narration; the release gate because a take ended mid-word. `docs/07-gates-catalog.md` lists the reusable ones.

Things to put in every brief:

- **Never overwrite or delete.** Every output gets a new version name. A previous version the user has seen stays exactly as it was.
- **The scope.** One scene. Don't touch other scenes, other projects, or files not named in the brief.
- **What not to decide.** If a line sounds wrong, the agent says so in the report; the orchestrator decides with the user. Don't change the narration text.
- **Resource rules** (below).

## Reviewing a scene

- **Stills.** One 1080p still per storyboard screen, taken just before that screen starts to clear. Look at each one next to its SVG: centred things centred, chips of one line on one baseline, highlights exactly behind their word, values in a column starting at the same x.
- **Audio identity.** Correlate the preview's first 20 s with the WAV the brief named: r ≥ 0.99 at lag 0.
- **Timing.** Spot-check a frame 0.2–0.3 s after a cue word: the element is there; a frame just before: it isn't.
- **Departures.** The editor lists every place it departed from the storyboard and why. Read them; they're the decisions the user should see.
- **Listening spots.** The voice report lists times to listen to (chunks that never passed, words Whisper misheard). Pass them to the user with the times.

## One scene at a time

No session works on the next scene, not even early stills, until the user confirms the current one. Directed small fixes (a wording, a nudge the user described) are applied directly and reported, without a new confirmation round.

## Resource limits

The machine: a laptop, WSL2 with 15 GB RAM, an 8 GB GPU.

- **One heavy process at a time.** Heavy = a TTS model, Whisper medium, an EffectCraft render, an ffmpeg encode of the film, the film gates. Two renders in parallel, or a render beside a TTS run, exhausted memory and killed WSL. Five parallel benchmark jobs took the whole machine; twelve crashed WSL.
- **One model per process.** The voice tools load Qwen (GPU) and Whisper (CPU) in separate processes that exit when done.
- **Save after every unit of work.** `state.json` is written after every take. A run killed by a restart loses one take, and the next run resumes.
- **Cap threads** when something else runs: `torch.set_num_threads(6)`, `ffmpeg -threads 1` for measurements.
- **No renders, no model loads in review.** The orchestrator reviews with ffprobe, short correlations and stills.
- Give WSL a fixed budget in `.wslconfig` (requirements/system.md) so a runaway job can't freeze Windows.

## Usage limits and resuming

- Agents can stop mid-task (usage limit, crash, restart). Design every tool to resume: skip outputs that exist, keep state in files, never depend on in-memory progress.
- When an agent stops, start a new one with the same brief plus one line: "Resume: outputs X and Y exist, continue from Z." Don't ask it to redo finished work.
- Keep the brief, the report and the logs on disk next to the outputs (an `orchestra/roles/<role>/inbox|outbox` layout works), not only in the chat.

## History: the Codex orchestra

Before the Claude subagents, four local Codex sessions (illustrator, editor, voice, sound) were driven from a folder with `run.sh brief <role> <brief.md>`: each role had a rules file, its own MCP tool only, a sandbox that could write only its own folder, and an inbox/outbox. It worked, but hit the issues above. The files are kept in `docs/history/codex-orchestra/` (README, common rules, per-role rules, `run.sh`, the editor rules written for the Claude editor).
