# Brief NNN: voice, scene <N> (<title>)

You are the voice specialist. Make the narration take of ONE scene with the approved method
(tools/voice/qwen_takes.py, docs/02-voice-tts.md). Do not start any other scene.

## Inputs
- Text: `<project>/narration/scene<NN>.txt` (approved; do not change a word).
- Config: `<project>/voice.json` (reference clip, spoken map, hint prompt). You may ADD entries to `spoken`,
  `watch` or `break_after`; list every addition in the report.
- Run: `tools/voice/run_scene.sh <project>/voice.json <N> <tag>` in the TTS venv.

## Rules
- Never overwrite or delete a file; the tag `<tag>` must be new. Earlier takes stay as they are.
- One heavy process at a time: nothing else rendering or loading a model while you run.
- Never time-stretch, denoise or splice inside a sentence. A bad read is fixed by another seed or the spoken map.
- A chunk that fails every try: keep the best take and flag it with its time in the scene; don't loop.

## Deliverables
- `<out>/scene<NN>_<tag>.wav` and `<out>/scene<NN>_<tag>.words.json`
- `<out>/scene<NN>_<tag>_checks.json`

## Gates
- G1 — CHECK: `ls -la <out>/scene<NN>_<tag>.wav <out>/scene<NN>_<tag>.words.json` — EXPECT: both exist.
- G2 — CHECK: `python tools/voice/final_check.py --config <project>/voice.json --scene <N> --tag <tag>` (already run by run_scene.sh; paste its line)
  — EXPECT: `len_equal` true, `dead_runs_left` 0, `stt_diffs` empty or each one explained, `chunks_not_ok` empty or flagged with times.
- G3 — CHECK: word count of words.json vs the text — EXPECT: equal; times ordered; last end < duration.
- G4 — CHECK: every watch phrase in `watch_heard` — EXPECT: all true.

## Report (short)
Paths and duration; each gate in one line; spoken-map additions; chunks retried (seeds) and why; times the
user should listen to; how long it took (model load, generation, checks).
