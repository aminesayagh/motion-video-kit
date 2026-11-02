"""The earlier scene mix (superseded by master.py setting C): SoundCraft high-pass + expander, constant pink room tone.

usage: expander_mix.py --take take.wav --out mix.wav [--session clean.scraft] [--limit-ceiling -9.5] [--tone-dbfs -66]

1. SoundCraft session (the take on one mono track), inserts:
   a) eq_7band: high-pass 60 Hz, 12 dB/oct (subsonic rumble only; no shelf: the noise is not HF hiss),
   b) expander_gate: threshold -45 dBFS (about 25 dB above the loudest steady pause noise and 17 dB under the
      speech RMS), ratio 4:1, range 15 dB, attack 1 ms, hold 0 ms, release 150 ms (chosen by a sweep),
   c) optional maximizer (no drive) at --limit-ceiling, for a take with one burst far over its other peaks.
   Centre pan at the session's -3 dB pan law. Bounced 32-bit float stereo.
2. numpy: one constant gain so the mix is -18 LUFS integrated, constant pink room tone (ffmpeg anoisesrc,
   100 Hz-5 kHz, --tone-dbfs RMS per channel). Exactly the take's frame count, 24-bit stereo.
Why it was replaced: the expander's release is exponential, so short pauses stayed near -71 dBFS, and the room
tone filled the pauses with a hiss the user heard switching on and off between words (docs/03-sound.md).
"""
import argparse, json, re, subprocess, sys, tempfile
from pathlib import Path

import numpy as np
import soundfile as sf
from scipy.signal import resample_poly

TONE = "anoisesrc=color=pink:seed={seed}:amplitude=0.5:r={sr}:d={d},highpass=f=100,lowpass=f=5000"
TARGET_LUFS, MAX_TRUE_PEAK = -18.0, -1.05
EQ = {"hpf_on": 1, "hpf_freq": 60, "hpf_slope": 1}
EXPANDER = {"threshold": -45, "ratio": 4, "range": 15, "attack": 1, "hold": 0, "release": 150}


def ffmpeg(*args):
    return subprocess.run(["ffmpeg", "-hide_banner", "-nostats", *args], capture_output=True, text=True, check=True).stderr


def lufs(data, sr, tmp):
    p = tmp / "probe.wav"
    sf.write(p, data, sr, subtype="FLOAT")
    err = ffmpeg("-i", str(p), "-af", "ebur128=peak=true", "-f", "null", "-")
    return float(re.findall(r"I:\s+(-?[\d.]+) LUFS", err)[-1]), float(re.findall(r"Peak:\s+(-?[\d.]+) dBFS", err)[-1])


def true_peak(mix):
    return 20 * np.log10(max(np.abs(resample_poly(mix[:, c], 4, 1)).max() for c in range(mix.shape[1])))


def rms_db(x):
    return 10 * np.log10(np.mean(np.square(x)) + 1e-30)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--take", required=True); ap.add_argument("--out", required=True)
    ap.add_argument("--session"); ap.add_argument("--limit-ceiling", type=float)
    ap.add_argument("--tone-dbfs", type=float, default=-66.0); ap.add_argument("--seed", type=int, default=1)
    a = ap.parse_args()
    dest = Path(a.out)
    for p in (dest, Path(a.session) if a.session else None):
        if p and p.exists(): sys.exit(f"exists, not overwriting: {p}")
    info = sf.info(a.take); assert info.channels == 1
    sr, frames = info.samplerate, info.frames
    with tempfile.TemporaryDirectory() as t:
        tmp = Path(t); bounce = tmp / "voice.wav"
        cmds = [("session.new", {"name": dest.stem, "sample_rate": sr, "bit_depth": 24}),
                ("file.import_audio", {"path": str(Path(a.take).resolve())}),
                ("mix.insert", {"track": 2, "slot": 0, "plugin": "eq_7band", "params": EQ}),
                ("mix.insert", {"track": 2, "slot": 1, "plugin": "expander_gate", "params": EXPANDER})]
        if a.limit_ceiling is not None:
            cmds.append(("mix.insert", {"track": 2, "slot": 2, "plugin": "maximizer",
                                        "params": {"threshold": 0, "ceiling": a.limit_ceiling, "release": 50}}))
        cmds.append(("file.bounce_mix", {"path": str(bounce), "format": "wav", "bit_depth": "32f", "dither": False}))
        args = ["soundcraft-cli", "run"]
        for cid, params in cmds:
            args += ["--cmd", f"{cid}={json.dumps(params)}"]
        if a.session: args += ["--save", a.session]      # note: saving copies the take into "Audio Files" next to it
        res = subprocess.run(args, capture_output=True, text=True, check=True).stdout
        assert 'track":2' in res, res
        voice, bsr = sf.read(bounce, always_2d=True)
        assert bsr == sr and voice.shape == (frames, 2), voice.shape
        tw = tmp / "tone.wav"
        ffmpeg("-y", "-f", "lavfi", "-i", TONE.format(seed=a.seed, sr=sr, d=frames / sr + 1), "-c:a", "pcm_f32le", str(tw))
        tone = sf.read(tw)[0][:frames]
        tone *= 10 ** ((a.tone_dbfs - rms_db(tone)) / 20)
        tone2 = np.stack([tone, tone], 1)
        gain_db, target = TARGET_LUFS - lufs(voice, sr, tmp)[0], TARGET_LUFS
        for _ in range(4):
            mix = voice * 10 ** (gain_db / 20) + tone2
            i, tp = lufs(mix, sr, tmp); tp4 = true_peak(mix)
            if tp4 > MAX_TRUE_PEAK: target = max(TARGET_LUFS - 0.3, i - (tp4 - MAX_TRUE_PEAK))
            if abs(i - target) < 0.05 and tp4 <= MAX_TRUE_PEAK: break
            gain_db += target - i
    sf.write(dest, mix, sr, subtype="PCM_24")
    print(json.dumps({"take": a.take, "mix": str(dest), "frames": frames, "voice_gain_db": round(gain_db, 3),
                      "mix_lufs": i, "mix_true_peak": tp, "true_peak_4x": round(tp4, 2), "target_lufs": round(target, 2)}))


if __name__ == "__main__":
    main()
