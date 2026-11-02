# 3. Sound

Two jobs: a **scene master** for each approved voice take (used in the scene's preview and then in the film), and the **film mix** (voice track, music bed, ducking, mastering).

## Terms

- **LUFS:** perceived loudness, integrated over the whole file (EBU R128). -18 LUFS is a comfortable level for a voice; streaming platforms play around -14 to -16.
- **True peak (dBTP):** the highest level the waveform reaches between samples, measured with 4× oversampling. Keep it under -1 dBTP so encoding to AAC doesn't clip.
- **Pause:** a stretch where the take is under -60 dBFS for more than 0.3 s. **Gap between words:** 0.1–0.3 s.
- **Ducking:** lowering the music while the voice speaks.

## What the user rejected

- **Denoising the speech** in a way that changes the voice, and **time-stretching**: both sound processed.
- **Pink room tone** under the voice (an earlier mix used -66 dBFS): it filled the pauses with a hiss that seemed to switch on and off against the gaps between words.
- A music bed at -22 dB under the voice: too present. -32 dB was approved.

## Scene master: settings A, B, C

`tools/sound/master.py master --setting C --take take.wav --out master.wav`

All three settings share one chain:

1. **SoundCraft session** (`soundcraft-cli run`): the take on one mono track, centre pan (-3 dB pan law), bounced to 32-bit float stereo. Inserts:
   - `eq_7band` (per setting, below);
   - `maximizer`, threshold 0 (no drive), release 50 ms, ceiling set so peaks stop at -1.5 dBFS in the final mix. It only touches the loudest few peaks.
2. **Pause gate (numpy)**: each pause gets its own attenuation, so its noise lands at **-75 dBFS** after the final gain (a pause already quieter is raised by at most 6 dB). Raised-cosine curve in dB: down over 200 ms from the pause start, up over 40 ms ending exactly at the pause end, so a word's tail and the next onset are never touched.
3. **One constant gain to -18 LUFS**, iterated until true peak ≤ -1.05 dBTP (4× oversampled). Same frame count as the take, so the word times stay valid. No room tone.

| Setting | EQ | Extra | Result |
| --- | --- | --- | --- |
| A "quiet pauses" | high-pass 60 Hz, 12 dB/oct (rumble only) | – | pauses at -74 dBFS; hiss between words ~11 dB louder than the pauses |
| B "A + gentle EQ" | high-pass 80 Hz 24 dB/oct; bell 1700 Hz -4 dB Q 4 | – | the noise had one bump at 1.35–1.85 kHz (40 % of its A-weighted power); the voice loses ~1.6 dB in its 2 kHz octave |
| **C "B + light spectral reduction"** | as B | ffmpeg `afftdn` nr 8 dB before SoundCraft | **approved** |

Why C:

- `afftdn` leaves the voice exactly as B: 0.00 dB difference in every octave band on voiced frames, same words in the Whisper check.
- It lowers the hiss **between words** by 3–4 dB. The on/off contrast between gaps and pauses drops from ~11 dB to ~7 dB, which was the effect the user disliked.

`afftdn` details that matter:

- Its noise profile is learned (`asendcmd … afftdn sn start/stop`) from a prefix made of the take's own steady pauses, then the prefix is cut off.
- `nf` = the take's measured pause level, rounded (about -70 dBFS).
- It delays its output (600 samples here). The delay is measured by cross-correlation and removed, or the master drifts from the word times.

Why not SoundCraft's `expander_gate` for the pauses: its release is exponential, so 0.3–0.8 s pauses stayed near -71 dBFS (4 of 11 pauses on target), and its range is one number while the takes' pauses held either -70 or -80 dBFS noise. `tools/sound/expander_mix.py` keeps that earlier mix for reference.

Listening comparison for the user (same excerpt of each file, a soft beep between them):

```bash
python tools/sound/master.py compare --out ab.wav --start 24 --end 49 old_mix.wav A.wav B.wav C.wav
```

Gates: `master_gates.py --take take.wav current=old.wav A=a.wav B=b.wav C=c.wav` (frames, LUFS/TP, pauses within 3 dB of -75, gaps, octave bands).

## Loudness targets

| What | Integrated | True peak |
| --- | --- | --- |
| Scene master | -18.0 LUFS (±0.3 allowed when a peak forces it lower) | ≤ -1.05 dBTP (4×) |
| Film mix | -16.0 LUFS (gate ±0.5) | limiter ceiling -1.8 dBTP; gate ≤ -1.5 dBTP |
| Music under voice | median -32 dB on voiced frames (gate ±4 dB per scene) | – |

## Film voice track

`film_voice.py --scenes film_scenes.json --out voice.wav --layout layout.json`

- Each scene lasts exactly its 1080p render's frame count × 1600 samples (48 kHz / 30 fps), so picture and sound are locked by construction.
- Each master is placed untouched (resampled 24 → 48 kHz) at its scene start and padded with a constant noise floor shaped like, and as loud as, the masters' own pauses. Never digital silence.
- `layout.json` records every scene's start, length and voice length: the bed, the mix, the cut tool and the gates read it.

## Music bed

`make_bed.py --layout layout.json --out bed.wav` synthesises original music in numpy, so there is nothing to license:

- D major, I–vi–IV–V (D, Bm, G, A), 4 bars per chord; chord length = film length / 41 (~14 s, ~68 BPM), so the 41st chord is the tonic and rings to the end.
- Pad: 3 detuned band-limited saws per note (-7/0/+7 cents, panned L/C/R), harmonics rolled off above ~1.4 kHz, 2.5 s attack, 4.5 s release.
- Air: soft triangle an octave up on the 3rd and 5th. Bass: sine on the root.
- Bell: a quiet 3-note figure every 8 bars (`--no-bell` removes it if it distracts from the speech).
- Slow drift ±0.8 dB at 0.05 Hz; synthetic stereo reverb (RT60 3 s, darkened), 30 % wet; 2 s fade-in, 3 s fade-out ending on the last sample; -20 dBFS RMS.

The detuned saws beat against each other (dips up to 3 dB within 50 ms): it reads as shimmer, but tell the user to listen for it.

## Ducking and master

`film_mix.py`:

1. Clean the bed: high-pass 60 Hz, -3 dB around 2 kHz (Q 0.7) to leave room for the voice.
2. Voice activity on 10 ms frames (> -55 dBFS). In pauses over 1.5 s, and in scene holds (unvoiced over 1.0 s across a cut), the music rises toward +6 dB: up over 1.2 s starting 0.05 s into the pause, back down over 0.6 s finishing exactly when the voice returns. Dense narration means few rises; mostly the scene holds.
3. Base level: the bed's gain is set so the median (music - voice) on voiced 100 ms frames is `--music-under` (-32).
4. Mix = voice (untouched) + music; one gain to -16 LUFS; a true-peak limiter (ceiling -1.8 dBTP, 25 ms ramps) only where peaks exceed it. In the OrbitRows film it reduced at most 2.9 dB over ~10 s of 566 s. If it sounds squashed, -17 LUFS removes most of it.

`--out-bed` keeps the processed bed at its mix level so the gates can measure music vs voice per scene.

## Gates

See docs/07-gates-catalog.md. In short: same frame count as the take, LUFS and true peak, pauses on target, voice spectrum unchanged on voiced frames (< 1 dB per octave band), the same words before and after (Whisper), and for the film: voice correlation ≥ 0.99 at lag 0 per scene, music-vs-voice per scene, no click at any join, PSNR per cut.
