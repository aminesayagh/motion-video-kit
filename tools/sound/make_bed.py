"""Film music bed, synthesised locally in numpy (no samples, no downloads, nothing to license).

Recipe
  key        D major, I-vi-IV-V: D - Bm - G - A, 4 bars (16 beats) per chord
  tempo      chord length = film length / N chords (--chords, default 41; ~14 s each for a 9.5 min film, ~68 BPM),
             so the last chord is the tonic when N = 4k + 1 and rings to the end under the 3 s fade-out
  pad        3 detuned band-limited saws per note (-7/0/+7 cents, panned L/C/R), harmonics
             rolled off above ~1.4 kHz (warm low-pass), 2.5 s attack, 4.5 s release, chords overlap
  air        soft triangle an octave above on the chord's 3rd and 5th
  bass       sine (+ a little 2nd harmonic) on the root, D2/B1/G2/A2
  bell       3-note chord-tone figure (D5-A5 range) on bar 3 of every vi and V chord
             (every 8 bars), harmonic partials 1/2/4, 1.4 s decay, very quiet
  movement   slow amplitude drift (+-0.8 dB at 0.05 Hz), no drums, no vocals, no lead
  space      convolution reverb, synthetic stereo IR (RT60 ~3 s, darkened), 30% wet (bell 55%)
  ends       2 s fade-in at 0, 3 s fade-out ending exactly at the film's last sample
Run: python make_bed.py --layout film_layout.json --out bed.wav   (or --seconds 565.8 instead of --layout)
     -> 48 kHz stereo float, exactly the film's sample count, -20 dBFS RMS (the mix sets the real level)
"""
import argparse, json, os, sys
import numpy as np, soundfile as sf
from scipy.signal import oaconvolve, butter, sosfilt

ap = argparse.ArgumentParser()
ap.add_argument("--out", required=True); ap.add_argument("--layout"); ap.add_argument("--seconds", type=float)
ap.add_argument("--chords", type=int, default=41); ap.add_argument("--no-bell", action="store_true")
a = ap.parse_args()
OUT = a.out
if os.path.exists(OUT): sys.exit(f"exists, not overwriting: {OUT}")
SR = 48000
T = json.load(open(a.layout))["total"] if a.layout else int(round(a.seconds * SR))   # film length in samples
N_CHORDS = a.chords
CL = T / N_CHORDS                      # chord length in samples
BEAT = CL / 16
print(f"film {T/SR:.3f} s, chord {CL/SR:.3f} s, tempo {60*SR/BEAT:.2f} BPM")

hz = lambda m: 440.0 * 2 ** ((m - 69) / 12)
PROG = [  # name, pad voicing, air (3rd, 5th up an octave), bass, bell figure
    ("D",  [57, 62, 66, 69], [78, 81], 38, None),
    ("Bm", [54, 59, 62, 66], [74, 78], 35, [74, 78, 83]),   # D5 F#5 B5
    ("G",  [55, 59, 62, 67], [71, 74], 43, None),
    ("A",  [57, 61, 64, 69], [73, 76], 45, [76, 73, 81]),   # E5 C#5 A5
]

TN = 4096
def table(kind, f0, cutoff=1400.0, maxf=9000.0):
    k = np.arange(1, int(maxf // f0) + 1)
    if kind == "saw": a = 1.0 / k
    else:             a = np.where(k % 2 == 1, (1.0 / k ** 2) * (-1) ** ((k - 1) // 2), 0.0)
    a = a / (1 + (k * f0 / cutoff) ** 4)
    ph = np.arange(TN) / TN
    w = (a[:, None] * np.sin(2 * np.pi * k[:, None] * ph[None, :])).sum(0)
    w /= np.max(np.abs(w))
    return np.append(w, w[0])

def osc(tab, f, n, phase0):
    ph = (phase0 + f * np.arange(n) / SR) % 1.0
    return np.interp(ph * TN, np.arange(TN + 1), tab).astype(np.float32)

def env(n, att, rel_start, rel):
    """raised-cosine attack, sustain, raised-cosine release starting at rel_start."""
    t = np.arange(n) / SR
    e = np.ones(n, np.float32)
    a = t < att; e[a] = 0.5 - 0.5 * np.cos(np.pi * t[a] / att)
    r = t >= rel_start
    e[r] *= 0.5 + 0.5 * np.cos(np.pi * np.clip((t[r] - rel_start) / rel, 0, 1))
    return e

rng = np.random.default_rng(70)
dry = np.zeros((T, 2), np.float32)
bells = np.zeros((T, 2), np.float32)
ATT, REL = 2.5, 4.5
pans = {-7: (0.85, 0.35), 0: (0.7, 0.7), 7: (0.35, 0.85)}
for c in range(N_CHORDS):
    name, pad, air, bass, fig = PROG[c % 4]
    s0 = int(round(c * CL)); s1 = int(round((c + 1) * CL))
    hold = (s1 - s0) / SR
    last = c == N_CHORDS - 1
    n = min(T, s1 + int(REL * SR)) - s0
    if last: n = T - s0
    e = env(n, ATT, hold if not last else 1e9, REL)
    if c == 0: e = env(n, 0.05, hold, REL)          # film starts on the chord (fade-in shapes it)
    seg = np.zeros((n, 2), np.float32)
    for m in pad:
        f = hz(m); tab = table("saw", f)
        for cents, (gl, gr) in pans.items():
            v = osc(tab, f * 2 ** (cents / 1200), n, rng.random()) * 0.10
            seg[:, 0] += gl * v; seg[:, 1] += gr * v
    for j, m in enumerate(air):
        f = hz(m); v = osc(table("tri", f, cutoff=3000), f, n, rng.random()) * 0.035
        seg[:, j] += v; seg[:, 1 - j] += 0.5 * v
    fb = hz(bass); t = np.arange(n) / SR; ph = rng.random()
    b = (np.sin(2 * np.pi * (fb * t + ph)) + 0.15 * np.sin(4 * np.pi * (fb * t + ph))).astype(np.float32) * 0.16
    seg += b[:, None]
    dry[s0:s0 + n] += seg * e[:, None]
    if fig and not a.no_bell:                        # bar 3 of the chord: beats 8, 9, 10.5
        for k, (m, beat) in enumerate(zip(fig, (8, 9, 10.5))):
            b0 = s0 + int(round(beat * BEAT)); bn = min(int(5 * SR), T - b0)
            if bn <= 0: continue
            t = np.arange(bn) / SR; f = hz(m)
            v = (np.sin(2*np.pi*f*t) + 0.22*np.sin(2*np.pi*2*f*t)*np.exp(-t/0.5) + 0.05*np.sin(2*np.pi*4*f*t)*np.exp(-t/0.25))
            v *= np.exp(-t / 1.4) * np.minimum(1, t / 0.006) * (0.030 if k < 2 else 0.024)
            p = (0.35, 0.65, 0.5)[k]
            bells[b0:b0 + bn, 0] += (1 - p) * v; bells[b0:b0 + bn, 1] += p * v
    print(f"chord {c+1:2d} {name:2s} at {s0/SR:7.2f} s")

# slow drift
t = np.arange(T, dtype=np.float32) / SR
dry *= (10 ** (0.8 * np.sin(2 * np.pi * 0.05 * t) / 20))[:, None]
del t

# reverb: synthetic stereo IR, exponential decay (RT60 3 s), darkened
ir_n = int(3.2 * SR); ti = np.arange(ir_n) / SR
ir = rng.standard_normal((ir_n, 2)) * np.exp(-6.91 * ti / 3.0)[:, None]
ir = sosfilt(butter(2, 4500, fs=SR, output="sos"), ir, axis=0)
ir[: int(0.012 * SR)] = 0                       # 12 ms pre-delay
ir /= np.sqrt(np.sum(ir ** 2, 0))
out = np.empty((T, 2), np.float32)
for ch in range(2):
    wet_in = dry[:, ch] * 0.30 + bells[:, ch] * 0.55
    out[:, ch] = oaconvolve(wet_in, ir[:, ch], mode="full")[:T].astype(np.float32)
    out[:, ch] += dry[:, ch] * 0.70 + bells[:, ch] * 0.45
del dry, bells

# fades + level (bed alone at -20 dBFS RMS; the mix sets the real level)
fi, fo = int(2 * SR), int(3 * SR)
out[:fi] *= (0.5 - 0.5 * np.cos(np.pi * np.arange(fi) / fi))[:, None]
out[T - fo:] *= (0.5 + 0.5 * np.cos(np.pi * (np.arange(fo) + 1) / fo))[:, None]
out *= 10 ** (-20 / 20) / np.sqrt(np.mean(out[fi:T - fo].astype(np.float64) ** 2))
print(f"peak {20*np.log10(np.max(np.abs(out))):.2f} dBFS, last sample {np.max(np.abs(out[-1])):.2e}")
sf.write(OUT, out, SR, subtype="FLOAT")
