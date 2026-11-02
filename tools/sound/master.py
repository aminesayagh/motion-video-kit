"""Scene master: cleanup + level of one voice take, three settings to choose from by ear (C was approved).

usage: master.py master --setting C --take scene01_v1.wav --out scene01_master_C.wav
       master.py compare --out ab.wav --start 24 --end 49 current.wav A.wav B.wav C.wav
         (one listening file: the same excerpt of each file in turn, 1 s gap with a soft beep between them)

Needs soundcraft-cli (SoundCraft, native Ubuntu) and ffmpeg. The output is stereo, 24-bit,
exactly the take's frame count, -18 LUFS integrated, true peak <= -1 dBTP. No pink room tone (an earlier mix
had one at -66 dBFS, which was most of what the pauses held). Never overwrites: an existing output stops it.

Every setting:
  SoundCraft session, take on one mono track, centre pan (-3 dB pan law), bounced 32-bit float, inserts:
    eq_7band   per setting, below
    maximizer  threshold 0 (no drive), release 50 ms, ceiling = -1.5 dBFS in the mix (ceiling in dBFS at the
               take = -1.5 + 3 - the scene's gain, about -8.6 to -9.5): touches only the loudest peaks
               (a first bounce with the EQ alone gives the gain)
  numpy pause gate (the SoundCraft expander_gate could not do it, see below): every pause (take under
    -60 dBFS for more than 0.3 s) gets its own attenuation, so its noise sits at -75 dBFS after the gain
    (at most 6 dB of lift for a pause already quieter); raised-cosine ramps in dB, 200 ms release from the
    pause start, 40 ms attack ending at the pause end (the next onset and the tail before are untouched).
    Then one constant gain to -18 LUFS. No room tone.
  Why not expander_gate: its release is exponential, so a 250 ms release keeps 0.3-0.8 s pauses near
    -71 instead of -75 (4/11 and 4/26 pauses within 3 dB of -75 on scenes 1 and 5), its range is one
    number while the takes' pauses hold -70 or -80 dBFS noise, and with the -66 room tone gone a range of
    11 dB (not 25-30) already gives -75 on the -70 pauses.
Settings:
  A "quiet pauses"   eq_7band high-pass 60 Hz 12 dB/oct (as in v5: subsonic rumble only)
  B "A + gentle EQ"  eq_7band cut on the noise bands measured on the takes' pauses:
      high-pass 80 Hz 24 dB/oct   (noise is flat at -99 dB/Hz under 140 Hz; the voice starts at ~85 Hz,
                                   so this costs it < 1 dB at 90 Hz and nothing above 110 Hz)
      MF bell 1700 Hz, -4 dB, Q 4 (the noise's one bump, 1.35-1.85 kHz, 8 dB over its neighbours and 40%
                                   of its A-weighted power; costs the voice's 2 kHz octave about 1.8 dB)
  C "B + light spectral reduction": B, with ffmpeg afftdn on the take before SoundCraft:
      afftdn nr=8 dB, nf = the take's measured pause level (dBFS, rounded), noise profile sampled
      (sample_noise start/stop) on a prefix made of the take's own steady pauses; the prefix and afftdn's
      delay (600 samples, measured by cross-correlation) are cut off.
"""

import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
import soundfile as sf
from scipy.signal import correlate, resample_poly

TARGET_LUFS, MAX_TRUE_PEAK = -18.0, -1.05          # true peak 4x oversampled
PAUSE_TARGET = -75.0                               # dBFS RMS per channel, pause noise after the gain
EQ = {
    "A": {"hpf_on": 1, "hpf_freq": 60, "hpf_slope": 1},
    "B": {"hpf_on": 1, "hpf_freq": 80, "hpf_slope": 3, "mid_freq": 1700, "mid_gain": -4, "mid_q": 4},
}
EQ["C"] = EQ["B"]
RELEASE_S, ATTACK_S = 0.2, 0.04                    # pause gate ramps (raised cosine in dB)
MAX_PAUSE_BOOST = 6.0                              # a pause quieter than the target is raised, at most this
PEAK_CEILING = -1.5        # dBFS in the mix: SoundCraft maximizer ceiling (no drive), only the loudest peaks
PAN_LAW = -3.0             # SoundCraft's centre pan, after the inserts
AFFTDN_NR = 8


def ffmpeg(*args):
    return subprocess.run(["ffmpeg", "-hide_banner", "-nostats", *args], capture_output=True,
                          text=True, check=True).stderr


def db(x):
    return 10 * np.log10(np.mean(np.square(x)) + 1e-30)


def pauses(x, sr):
    """Runs of 25 ms frames under -60 dBFS (speech is about -26 RMS) longer than 0.3 s, in samples."""
    F = int(0.025 * sr)
    n = len(x) // F
    quiet = 10 * np.log10(np.mean(x[:n * F].reshape(n, F) ** 2, 1) + 1e-30) < -60
    runs, k = [], 0
    while k < n:
        j = k
        while j < n and quiet[j] == quiet[k]:
            j += 1
        if quiet[k] and (j - k) * F > 0.3 * sr:
            runs.append((k * F, j * F))
        k = j
    return runs


def steady_pause_level(x, sr, runs):
    """Median RMS of the pauses' interiors (50 ms off each end): the steady noise the take's pauses hold."""
    e = int(0.05 * sr)
    return float(np.median([db(x[a + e:b - e]) for a, b in runs]))


def loudness(path):
    err = ffmpeg("-i", str(path), "-af", "ebur128=peak=true", "-f", "null", "-")
    return (float(re.findall(r"I:\s+(-?[\d.]+) LUFS", err)[-1]),
            float(re.findall(r"Peak:\s+(-?[\d.]+) dBFS", err)[-1]))


def loudness_of(y, sr, tmp):
    sf.write(tmp / "lufs.wav", y, sr, subtype="FLOAT")
    return loudness(tmp / "lufs.wav")[0]


def true_peak(y):
    return 20 * np.log10(max(np.abs(resample_poly(y[:, c], 4, 1)).max() for c in range(y.shape[1])))


def afftdn(take, out, sr, runs, level):
    """afftdn with its noise profile sampled on the take's steady pauses, prepended and then cut off."""
    x = sf.read(take)[0]
    e = int(0.05 * sr)
    prefix = np.concatenate([x[a + e:b - e] for a, b in runs if abs(db(x[a + e:b - e]) - level) < 2])
    src = out.with_name("afftdn_in.wav")
    pad = np.zeros(sr // 2)                        # afftdn delays its output; the pad carries the take's end
    sf.write(src, np.concatenate([prefix, x, pad]), sr, subtype="FLOAT")
    t = len(prefix) / sr
    ffmpeg("-y", "-i", str(src), "-af",
           f"asendcmd=c='0.0 afftdn sn start; {t:.6f} afftdn sn stop',"
           f"afftdn=nr={AFFTDN_NR}:nf={max(-80, round(level))}", "-c:a", "pcm_f32le", str(out))
    y = sf.read(out)[0]
    seg = slice(len(prefix), len(prefix) + 10 * sr)     # delay = the lag of the best match on 10 s of the take
    xc = correlate(y[seg.start:seg.stop + sr // 2], x[:10 * sr], mode="valid", method="fft")
    lag = int(np.argmax(xc))
    y = y[len(prefix) + lag:len(prefix) + lag + len(x)]
    assert len(y) == len(x), (len(y), len(x))
    sf.write(out, y, sr, subtype="FLOAT")
    src.unlink()
    return {"prefix_s": round(t, 2), "nr": AFFTDN_NR, "nf": max(-80, round(level)), "delay_samples": lag}


def soundcraft(src, bounce, sr, eq, ceiling=None):
    cmds = [("session.new", {"name": bounce.stem, "sample_rate": sr, "bit_depth": 24}),
            ("file.import_audio", {"path": str(src)}),
            ("mix.insert", {"track": 2, "slot": 0, "plugin": "eq_7band", "params": eq})]
    if ceiling is not None:
        cmds.append(("mix.insert", {"track": 2, "slot": 1, "plugin": "maximizer",
                                    "params": {"threshold": 0, "ceiling": ceiling, "release": 50}}))
    cmds.append(("file.bounce_mix", {"path": str(bounce), "format": "wav", "bit_depth": "32f", "dither": False}))
    args = ["soundcraft-cli", "run"]
    for cid, params in cmds:
        args += ["--cmd", f"{cid}={json.dumps(params)}"]
    out = subprocess.run(args, capture_output=True, text=True, check=True).stdout
    assert 'track":2' in out, out
    y, bsr = sf.read(bounce, always_2d=True)
    assert bsr == sr and y.shape[1] == 2, y.shape
    return y


def pause_gain(n, sr, runs, atts):
    """Gain (linear) that is 1 outside the pauses and takes each pause down by its own amount: raised-cosine
    (in dB) release over RELEASE_S from the pause start, attack over ATTACK_S ending at the pause end, so
    the next word's onset and the word tail before the pause are untouched."""
    g = np.zeros(n)
    for (a, b), att in zip(runs, atts):
        k = np.arange(b - a)
        down = np.ones(b - a) if a == 0 else np.minimum(k / (RELEASE_S * sr), 1)
        up = np.ones(b - a) if b >= n else np.minimum((b - a - 1 - k) / (ATTACK_S * sr), 1)
        g[a:b] = -att * (0.5 - 0.5 * np.cos(np.pi * np.minimum(down, up)))
    return 10 ** (g / 20)


def master(setting, take, dest, tmp):
    take, dest, scene = Path(take), Path(dest), 0
    if dest.exists():
        sys.exit(f"{dest} exists; not overwriting")
    x, sr = sf.read(take)
    assert x.ndim == 1
    runs = pauses(x, sr)
    level = steady_pause_level(x, sr, runs)
    src, row = take, {"setting": setting, "take": str(take), "frames": len(x),
                      "take_pause_dbfs": round(level, 1)}
    if setting == "C":
        src = tmp / f"s{scene}_afftdn.wav"
        row["afftdn"] = afftdn(take, src, sr, runs, level)
    # pass 1, EQ only: the gain to -18 LUFS; pass 2 adds a brickwall ceiling at PEAK_CEILING after that gain
    gain = TARGET_LUFS - loudness_of(soundcraft(src, tmp / f"s{scene}_eq.wav", sr, EQ[setting]), sr, tmp)
    ceiling = round(PEAK_CEILING - PAN_LAW - gain, 2)
    voice = soundcraft(src, tmp / f"s{scene}_eqmax.wav", sr, EQ[setting], ceiling)[:len(x)]
    assert len(voice) == len(x), (len(voice), len(x))

    # each pause's own attenuation, so that every pause sits at PAUSE_TARGET after the gain
    e = int(0.05 * sr)
    atts = [max(-MAX_PAUSE_BOOST, db(voice[a + e:b - e, 0]) + gain - PAUSE_TARGET) for a, b in runs]
    voice = voice * pause_gain(len(x), sr, runs, atts)[:, None]

    target, probe = TARGET_LUFS, tmp / f"s{scene}_probe.wav"
    for _ in range(5):
        mix = voice * 10 ** (gain / 20)
        sf.write(probe, mix, sr, subtype="FLOAT")
        i, tp = loudness(probe)
        tp4 = true_peak(mix)
        if tp4 > MAX_TRUE_PEAK:
            target = max(TARGET_LUFS - 0.3, i - (tp4 - MAX_TRUE_PEAK))
        if abs(i - target) < 0.05 and tp4 <= MAX_TRUE_PEAK:
            break
        gain += target - i
    for f in tmp.iterdir():
        f.unlink()
    sf.write(dest, mix, sr, subtype="PCM_24")
    row.update({"eq_7band": EQ[setting], "maximizer_ceiling_dbfs": ceiling, "pauses": len(runs),
                "pause_att_db": [round(min(atts), 1), round(float(np.median(atts)), 1), round(max(atts), 1)],
                "gain_db": round(gain, 2), "lufs": i, "true_peak": tp, "true_peak_4x": round(tp4, 2),
                "out": str(dest)})
    print(json.dumps(row), flush=True)


def compare(dest, t0, t1, files):
    """The same excerpt of each file in turn; 10 ms edges; 1 s gap with an 880 Hz -30 dBFS beep between them."""
    dest = Path(dest)
    if dest.exists():
        sys.exit(f"exists, not overwriting: {dest}")
    parts, sr = [], None
    for p in files:
        y, sr = sf.read(p, always_2d=True)
        seg = y[int(t0 * sr):int(t1 * sr)].copy()
        fade = np.linspace(0, 1, int(0.01 * sr))[:, None]          # 10 ms edges, no click
        seg[:len(fade)] *= fade
        seg[-len(fade):] *= fade[::-1]
        parts.append(seg)
    t = np.arange(int(0.25 * sr)) / sr
    beep = 10 ** (-30 / 20) * np.sin(2 * np.pi * 880 * t) * np.hanning(len(t))
    gap = np.zeros((sr, parts[0].shape[1]))
    gap[int(0.375 * sr):int(0.375 * sr) + len(t)] = beep[:, None]
    res = parts[0]
    for seg in parts[1:]:
        res = np.concatenate([res, gap, seg])
    sf.write(dest, res, sr, subtype="PCM_24")
    print(dest, f"{len(res) / sr:.1f} s, order: {[str(f) for f in files]}")


def main():
    import argparse
    ap = argparse.ArgumentParser(description="scene master / listening comparison")
    sub = ap.add_subparsers(dest="cmd", required=True)
    m = sub.add_parser("master"); m.add_argument("--setting", choices=sorted(EQ), default="C")
    m.add_argument("--take", required=True); m.add_argument("--out", required=True)
    c = sub.add_parser("compare"); c.add_argument("--out", required=True)
    c.add_argument("--start", type=float, required=True); c.add_argument("--end", type=float, required=True)
    c.add_argument("files", nargs="+")
    a = ap.parse_args()
    if a.cmd == "compare":
        return compare(a.out, a.start, a.end, a.files)
    with tempfile.TemporaryDirectory() as tmp:
        master(a.setting, a.take, a.out, Path(tmp))


if __name__ == "__main__":
    main()
