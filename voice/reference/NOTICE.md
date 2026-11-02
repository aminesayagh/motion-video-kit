# Voice reference

The voice cloning (`tools/voice/qwen_takes.py`) needs one short reference clip of the narrator and the exact words spoken in it:

| File | What to put here |
| --- | --- |
| `reference.wav` | 10–15 s of clean narration, 24 kHz mono, cut at a pause (never inside the next word: a clipped onset makes the model swallow first words) |
| `reference.txt` | the exact words spoken in `reference.wav` (an example is included) |

The audio is **not distributed** with this repository (it is git-ignored). Use a voice you own or are licensed to clone, and follow the terms of the service it comes from. See `docs/02-voice-tts.md` for how the original clip was chosen and cut.
