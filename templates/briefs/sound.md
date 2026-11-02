# Brief NNN: sound, scene <N> master

You are the sound specialist. Master ONE approved voice take with setting C (tools/sound/master.py, docs/03-sound.md).

## Inputs
- Take: `<out>/voice/scene<NN>_<tag>.wav` (approved by the user on <date>).

## Rules
- Never overwrite or delete; the output name must be new.
- Do not change the words, the pauses or the length: the animation is timed to the take's words.json.
- No time-stretch, no room tone, no extra denoising beyond setting C.
- One heavy process at a time.

## Command
`python tools/sound/master.py master --setting C --take <take> --out <out>/sound/scene<NN>_master_C_<tag>.wav`

## Gates
- G1 — CHECK: `ffprobe -v error -show_entries stream=duration_ts,sample_rate,channels -of csv=p=0 <take> <master>` — EXPECT: same duration_ts; 24000; master 2 channels.
- G2 — CHECK: `ffmpeg -hide_banner -nostats -i <master> -af ebur128=peak=true -f null - 2>&1 | grep -A12 Summary` — EXPECT: I -18.0 ± 0.3 LUFS; Peak ≤ -1.0 dBFS.
- G3 — CHECK: `python tools/sound/master_gates.py --take <take> C=<master>` — EXPECT: pause median -75 ± 1.5 dBFS; ≥ 90 % of pauses within 3 dB of -75.
- G4 — CHECK: Whisper word list of take vs master (docs/07, "Same words before and after") — EXPECT: identical.

## Report (short)
Path; each gate in one line; anything unusual (a pause off target, the limiter touching a peak).
