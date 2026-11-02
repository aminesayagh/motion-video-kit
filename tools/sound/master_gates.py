"""Gates for master.py. usage: master_gates.py --take take.wav current=old_mix.wav A=a.wav B=b.wav C=c.wav
The first labelled file is the reference ("current") for the band comparison.
G1 frames = take, G2 ebur128, G3 pauses (each within 3 dB of -75 dBFS?), gaps between words,
G5 octave-band energy on voiced frames vs the previous and the first file.
G4 (words intact) loads Whisper: run it on its own (see docs/07-gates-catalog.md)."""
import re
import subprocess
import sys
from pathlib import Path

import numpy as np
import soundfile as sf

sys.path.insert(0, str(Path(__file__).parent))
from master import db, pauses  # noqa: E402

PAUSE_TARGET = -75.0
OCTAVES = [125, 250, 500, 1000, 2000, 4000, 8000]


def ebur(p):
    err = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(p), "-af", "ebur128=peak=true",
                          "-f", "null", "-"], capture_output=True, text=True).stderr
    return (float(re.findall(r"I:\s+(-?[\d.]+) LUFS", err)[-1]),
            float(re.findall(r"Peak:\s+(-?[\d.]+) dBFS", err)[-1]))


def pause_levels(y, sr, runs):
    """Each pause's interior (100 ms in from its start, 50 ms before its end), channel 0."""
    return np.array([db(y[a + int(0.1 * sr):b - int(0.05 * sr), 0]) for a, b in runs])


def short_gaps(x, sr):
    """Gaps between words: runs of 25 ms frames under -60 dBFS lasting 0.1-0.3 s (the pause gate skips them)."""
    F = int(0.025 * sr)
    q = 10 * np.log10(np.mean(x[:len(x) // F * F].reshape(-1, F) ** 2, 1) + 1e-30) < -60
    runs, k = [], 0
    while k < len(q):
        j = k
        while j < len(q) and q[j] == q[k]:
            j += 1
        if q[k] and 0.1 * sr <= (j - k) * F <= 0.3 * sr:
            runs.append((k * F, j * F))
        k = j
    return runs


def p10(y, sr):
    F = int(0.01 * sr)
    n = len(y) // F
    return np.percentile(10 * np.log10(np.mean(y[:n * F, 0].reshape(n, F) ** 2, 1) + 1e-30), 10)


def bands(y, sr, voiced):
    """Energy (dB) per octave band over the voiced 25 ms frames, channel 0."""
    F = int(0.025 * sr)
    fr = y[:len(voiced) * F, 0].reshape(-1, F)[voiced] * np.hanning(F)
    P = np.sum(np.abs(np.fft.rfft(fr, axis=1)) ** 2, 0)
    f = np.fft.rfftfreq(F, 1 / sr)
    return np.array([10 * np.log10(P[(f >= c / 2 ** .5) & (f < c * 2 ** .5)].sum() + 1e-30) for c in OCTAVES]
                    + [10 * np.log10(P[(f >= 200) & (f < 4000)].sum())])


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--take", required=True)
    ap.add_argument("files", nargs="+", help="label=path")
    a = ap.parse_args()
    files = dict(f.split("=", 1) for f in a.files)
    files = {k: Path(p) for k, p in files.items() if Path(p).exists()}
    x, sr = sf.read(a.take)
    runs = pauses(x, sr)
    F = int(0.025 * sr)
    lv = 10 * np.log10(np.mean(x[:len(x) // F * F].reshape(-1, F) ** 2, 1) + 1e-30)
    voiced = lv > lv.max() - 30                       # frames within 30 dB of the loudest
    print(f"== take {a.take}: {len(x)} frames, {len(runs)} pauses > 0.3 s")
    gaps = short_gaps(x, sr)
    ref, prev = None, None
    for k, p in files.items():
        y = sf.read(p, always_2d=True)[0]
        I, tp = ebur(p)
        pl = pause_levels(y, sr, runs)
        off = pl - PAUSE_TARGET
        b = bands(y, sr, voiced)
        gl = np.median([db(y[g0 + int(.025 * sr):g1 - int(.025 * sr), 0]) for g0, g1 in gaps]) if gaps else float("nan")
        print(f"  {k:7s} {p.name}: frames {len(y)} ({'=' if len(y) == len(x) else '!='} take), "
              f"I {I} LUFS, TP {tp} dBTP | pauses p10 {p10(y, sr):.1f}, median {np.median(pl):.1f}, "
              f"min {pl.min():.1f}, max {pl.max():.1f}, within 3 dB of {PAUSE_TARGET:.0f}: "
              f"{np.sum(abs(off) <= 3)}/{len(pl)} | {len(gaps)} gaps between words, median {gl:.1f}")
        if ref is not None:
            print("          outside:", [(round(runs[i][0] / sr, 2), round(pl[i], 1)) for i in np.where(abs(off) > 3)[0]])
            print("          voiced band diff vs previous (dB) "
                  + " ".join(f"{c}:{v:+.2f}" for c, v in zip(OCTAVES + ["200-4k"], b - prev)))
            print("          voiced band diff vs first (dB) "
                  + " ".join(f"{c}:{v:+.2f}" for c, v in zip(OCTAVES + ["200-4k"], b - ref)))
        ref = b if ref is None else ref
        prev = b


if __name__ == "__main__":
    main()
