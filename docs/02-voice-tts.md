# 2. Voice: local text-to-speech

The narration is generated on your machine from a short reference clip of the narrator. This doc covers the approved method (Qwen3-TTS voice cloning with strict per-take checks), the earlier engines and what they taught, and the repair tools.

## Terms

- **Voice cloning:** the model hears a reference clip and its exact transcript, then reads new text in that voice. The result is an approximation of the voice, not a copy of the original model.
- **Chunk:** a piece of the narration generated in one call (one to three sentences). Each chunk is an independent read, so more chunks means more joins and a less even voice.
- **Take:** one generation of a chunk with one random seed.
- **Word times:** `[{word, start, end}]` in seconds, from Whisper's aligner on the known text. The editor times every animation on them.

## Engines tried

| Engine | Result | Kept for |
| --- | --- | --- |
| Kokoro-82M (Apache 2.0) | Deterministic, exact word times from its own durations, fast on CPU. Voice blend 70 % `am_puck` + 30 % `am_fenrir`, speed 0.95. Chosen first from blind samples, then replaced by Chatterbox after a side-by-side listen. | Quick drafts; timing tests |
| Chatterbox (default voice) | Natural. Recipe: `exaggeration=0.4`, `cfg_weight=0.1`, seed per chunk, chunks ≤ 300 chars at sentence ends, no gap inside a paragraph, 0.6 s between paragraphs. Drops or changes words ("in" → "and", "asked" → "ask"), so every chunk needs a word check. | `tools/voice/chatterbox/` |
| **Qwen3-TTS 0.6B Base, cloning** | **Approved.** Clones the chosen narrator from a 14.3 s clip. ~2.5 GB of weights, fits an 8 GB GPU in bfloat16 without FlashAttention. | `tools/voice/qwen_takes.py` |

Things the user rejected for every engine: **time-stretching, denoising the speech, and stitching comma-sized clips**. All three sound robotic or uneven. Fix a bad read by regenerating its chunk with another seed, or by changing the spoken text.

## The reference clip

- 10–15 s, one speaker, no music, the delivery you want (calm explainer pace).
- An exact transcript in `reference.txt`, punctuation included.
- Cut it on a pause. Trim leading/trailing silence, but keep the room tone inside.
- You need the right to use the voice: use a voice you own or are licensed to clone. The clip is not shipped with this repository.

## The approved method: `qwen_takes.py`

Config: copy `examples/orbitrows/voice.json`. Run one scene end to end:

```bash
. .venv-tts/bin/activate
tools/voice/run_scene.sh my-video/voice.json 5 v1     # 8 rounds of gen+check, build, repairs, final check
```

What happens:

1. **Plan.** Each paragraph is cut at sentence ends into chunks of up to 260 characters. A step-name sentence ("Step four: matching.") is its own chunk followed by a ~0.5 s pause; sentences listed in `break_after` get the same pause after them.
2. **Gen (GPU, own process).** For every chunk without an accepted take, one new take with the next seed. `max_new_tokens = 2 × characters + 120` stops runaway generations (a stuck model otherwise babbles for a minute). The voice prompt is computed once and reused.
3. **Check (CPU, own process).** Whisper `medium.en`, int8, with a hint prompt naming the script's unusual words. A take is accepted when all hold:
   - token ratio ≥ 0.93 against the text (numbers compared as words: "682" = "six hundred and eighty-two");
   - **first word heard alone**: the first 1.2 s transcribed with no prompt and no context, so Whisper can't guess it from the sentence;
   - **last words**: the last two in context, and the last one heard alone in the last 1.5 s (catches a swallowed final "s");
   - **release**: after the last sound, the level must not fall 30 dB in under 40 ms (`release.py`; the model sometimes stops mid-word, "archive." became "archi"). Step names need ≥ 100 ms ("operati" had 70 ms);
   - **end level drop** < -25 dB against the take's loud frames;
   - **falling close**: a paragraph's last chunk must end with the pitch falling ≥ 3 semitones (median of the last fifth vs the first half of the last 1.2 s). A flat close sounds like the sentence continues. Measured: bad -1.0, good -12.7;
   - **watch phrases** (config `watch`) heard word for word; `watch_plain` ones also in a transcription without the hint (for short function words the hint could mask).
4. **Repeat** gen + check until each chunk passes or reaches `max_tries`. A chunk that never passes uses its best take and is listed in `chunks_not_ok` for a human listen.
5. **Build.** For each chunk, the exact segment that was checked (150 ms kept before the first sound, 180 ms after the last), joined with **pauses filled by noise matched to the voice's own hiss**, 25 ms equal-power crossfades. Pauses (last sound → next first sound): 0.84 s between paragraphs, 0.49 s between sentences, 0.5 s after a step name. Word times by Whisper alignment of the known text, per chunk, offset by sample position. A full-file Whisper pass lists any remaining differences.
6. **Repairs** (add-only, same length, same word times):
   - `patch_tails.py`: a breath or artifact after a chunk's last word (≥ 100 ms louder than -60 dB before the next onset) is replaced by matched hiss with 30 ms crossfades. Fricatives (> 30 % energy above 4 kHz) and voiced decays are kept as part of the word.
   - Dead-silence fill: any stretch under -80 dBFS for ≥ 100 ms gets -70 dBFS hiss added. Digital silence sounds like the sound switching off.
   - `soften.py`: a word tail that drops more than 15 dB within 20 ms into the hiss gets 40 ms of tail-shaped noise decaying to the hiss level: a natural release instead of a cut.
7. **Final check** (`final_check.py`): no length change, no dead runs left, full-file Whisper differences with their times, the patch report, falls per paragraph.

Deliver `sceneNN_<tag>.wav` (24 kHz mono, PCM 24) and `sceneNN_<tag>.words.json`.

### Why one model per process

The machine had 15 GB of RAM in WSL and other jobs running. Qwen on the GPU plus Whisper in RAM plus a render froze it. Each phase loads one model, saves its state to `state.json` after **every** take, and exits. A crash or a restart loses at most one take, and the next run resumes.

## Spoken-text tricks

The narration text stays as written (it is what the word check and the word times use). The config's `spoken` map changes only what is sent to the model:

| Written | Sent | Why |
| --- | --- | --- |
| `the ids of the rows` | `the I-Ds of the rows` | the model said "ideas" 8 times out of 8 |
| `checked SQL.` | `checked S-Q-L.` | letters, not "sequel" |
| `from the first of September up to` | `from the first, of September, up to` | without the commas it said "September first", 6 of 6 |
| `draft and Casa and September.` | `draft, and Casa, and September.` | the second "and" was reduced to "'n" |
| `OrbitRows` | `Orbit Rows` | two clear words |
| `touches the data, exactly.` | `touches the data, exactly...` | a longer, falling release on a closing line |
| `Jev` (a made-up name) | `Jehv` (Chatterbox only) | pronunciation; Whisper then writes it "Jeff", "Jhev": accept those spellings in the check |

Other lessons:

- "A I" vs "AI": Qwen and Chatterbox both say "AI" correctly; "A.I." was not needed.
- A name Whisper doesn't know fails the check even when it is spoken right. That is a speech-to-text limit, not the voice: check those chunks with the name in the hint prompt, and retake only for real word errors.
- Whisper writes "request one" as "request1", "10%" for "ten percent", "1st" for "first". Normalise before comparing (`num2words`; `stt_worker.py` shows the rules), or a correct read fails.
- Whisper's context can mishear a word in the full file ("them" → "then" after several "then"s) that it hears right in the chunk alone. Listen at that time before retaking.

## Regenerate one chunk in place

When the user approves a scene except one line:

- **The last chunk** (a new closing line, a better ending): edit the text, make takes for that chunk (`qwen_takes.py gen/check --scenes N`; only chunks without an accepted take are generated), choose a seed, then
  ```bash
  python tools/voice/replace_chunk.py --config voice.json --scene 9 --base v9 --new v10 --chunk scene09_p4_c1 --seed 3
  ```
  Everything before the chunk is asserted bit-identical to the approved take; the repairs run on the new part only, and the file end gets hiss under the release (the take's own tail is often dead at -93 dB).
- **A chunk in the middle**: rebuild the scene (`build` with a new tag). Accepted takes are reused, so only that chunk changes, but every later word moves by the length difference, so the editor rebuilds with the new `words.json`.

## The earlier engine: Chatterbox in phases

`tools/voice/chatterbox/drive.py` runs in the Whisper venv. Per seed round, it starts `gen.py` in the Chatterbox venv (generates every chunk still failing, then exits), then the Whisper worker checks them all. Lessons:

- Chatterbox (4.1 GB) and Whisper (1.6 GB) together made the shared machine page heavily: hence the phases.
- Cap torch threads (`CB_THREADS=6`). With the default 51 threads beside other jobs, sampling fell to 0.4 steps/s.
- On CPU, a seed gives the same audio every time, so a saved attempt can be reused instead of regenerated.
- Retake at most 4 seeds, then flag the chunk for a listen instead of looping.

## Quick first listen

`tools/voice/qwen_quick.py` reads a storybook (`## Narration` sections) and makes one WAV per scene with fixed digital-silence pauses and a light Whisper screen. Use it to judge a voice or the pace of a draft, not for the final takes.
