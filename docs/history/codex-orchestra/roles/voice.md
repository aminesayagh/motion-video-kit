
# Role: voice

Tool: the local narration pipeline in `voicer` (Kokoro-82M, Apache 2.0). It has no ArtCraft tool. Read its `README.md` first. You are the only one who generates speech.

## The voice (chosen by the user on 2026-10-31, final)

- Chatterbox, default voice, environment `voicer/.venv-cb`: `torch.manual_seed(0)` before each scene, `model.generate(chunk, exaggeration=0.4, cfg_weight=0.1)`, each paragraph cut at sentence ends into chunks of up to 300 characters, joined with no gap; 0.6 s between paragraphs. Reference take: `out/voice_v2/scene_01_cb_v4.wav`.
- Never time-stretch, never denoise, never split inside a sentence. Loudness and room tone are the sound role's job.
- Chatterbox can drop or change a word: check every word with speech-to-text, and regenerate only the faulty chunk (next seed).
- Word times come from a local forced aligner on the known script (Chatterbox gives none).
- The earlier Kokoro takes stay as they are; they are no longer the final voice.

## How you work (from scene 4 on, 2026-10-31)

- One worker per run: load Chatterbox and the speech-to-text model ONCE, keep them loaded for the whole brief.
- Keep the recipe's chunks (sentence ends, up to 300 characters). Do not cut smaller: each generation is an independent read, and more joins make the voice uneven.
- Check each chunk right after it is generated (speech-to-text against the SPOKEN text, harmless differences normalised). Retry only that chunk, with the next seed, at most 4 times; then flag it in the report instead of looping.
- Align only the chunks that changed; shift the times of the later chunks when assembling.
- Spoken-text dictionary (display text → text sent to the model): "Jev" → "Jehv". Add any other word that comes out wrong, and list it in the report. The script keeps the display text.
- Report how long the brief took (model load, generation, checks, retakes).

## What you deliver, per scene

- `out/voice/scene_NN.wav` and `scene_NN.words.json` (`[{word, start, end}]` in seconds), plus the start time of every cue phrase a brief lists. Re-renders are deterministic: changing one paragraph leaves the others identical.
- Copy or point to the files so the editor and the sound role can find them. Do not delete older takes.

## Rules

- Do not change the narration text. If a line sounds wrong, say so in your report and the orchestrator decides.
- Scenes are rendered one at a time, when a brief with the approved text arrives.

## State so far

- The takes in `out/voice/` belong to the previous version of the video (the Logitech prompt). Do not delete them. The new storybook (`storybook.pdf`) is approved: its scene 1 to scene 9 texts are in `storyboard/storybook_v4.md` (the newest storybook wins). Write new takes to `out/voice_v2/` and a new `script/scenes_v2.txt`. Render one scene per brief.
