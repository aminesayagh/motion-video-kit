"""Film step 3: clean + duck the music bed under the voice, master the film mix.
usage: film_mix.py --voice voice_only.wav --bed bed.wav --layout layout.json --out-mix mix.wav --out-bed bed_ducked.wav
                   --stats stats.json [--music-under -32] [--lufs -16] [--ceiling -1.8]
- music clean: 2nd-order high-pass 60 Hz, peaking -3 dB at 2 kHz, Q 0.7 (about 1-4 kHz)
- ducker (numpy, look-ahead, driven by the voice track): music sits --music-under dB under the voice
  (median on voiced frames; -22 was judged too loud, -32 was approved);
  in pauses > 1.5 s and in the scene holds (unvoiced > 1.0 s across a cut) it rises
  toward +6 dB: up over 1.2 s starting 0.05 s into
  the pause, back down over 0.6 s finishing exactly when the voice returns
- mix = voice (untouched) + music; one constant gain to -16 LUFS; a gentle true-peak
  limiter (ceiling -1.8 dBTP, 25 ms ramps) only where peaks exceed it
--out-bed is the processed bed at its mix level, before the master gain (voice + bed, x master gain, limited = mix):
the gates measure music-vs-voice on it."""
import argparse, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *  # noqa: F401,F403
from scipy.signal import butter, sosfilt
from scipy.ndimage import minimum_filter1d, uniform_filter1d
import pyloudnorm as pyln

ap = argparse.ArgumentParser()
for k in ("voice", "bed", "layout", "out-mix", "out-bed", "stats"): ap.add_argument("--" + k, required=True)
ap.add_argument("--music-under", type=float, default=-32.0); ap.add_argument("--lufs", type=float, default=-16.0)
ap.add_argument("--ceiling", type=float, default=-1.8)
A = ap.parse_args()
OUT_MIX, OUT_BED, STATS = A.out_mix, A.out_bed, A.stats
refuse_existing(OUT_MIX, OUT_BED, STATS)
TARGET_REL, TARGET_LUFS, CEIL_DBTP = A.music_under, A.lufs, A.ceiling
cuts = [sc["start"] / SR for sc in json.load(open(A.layout))["scenes"]][1:]

voice, sr = sf.read(A.voice, dtype="float32")
bed, sr2 = sf.read(A.bed, dtype="float32")
assert sr == sr2 == SR and voice.shape == bed.shape
T = len(voice)

# --- clean the music
def peaking(f0, gain_db, q):
    A = 10 ** (gain_db / 40); w = 2 * np.pi * f0 / SR; al = np.sin(w) / (2 * q)
    b = [1 + al * A, -2 * np.cos(w), 1 - al * A]; a = [1 + al / A, -2 * np.cos(w), 1 - al / A]
    return np.array([[b[0]/a[0], b[1]/a[0], b[2]/a[0], 1, a[1]/a[0], a[2]/a[0]]])
sos = np.vstack([butter(2, 60, "highpass", fs=SR, output="sos"), peaking(2000, -3.0, 0.7)])
music = sosfilt(sos, bed, axis=0).astype(np.float32); del bed

# --- voice activity (10 ms) and the duck curve
hop = SR // 100
v = voice[:, 0].astype(np.float64)
vdb = 10 * np.log10(np.mean(v[: T // hop * hop].reshape(-1, hop) ** 2, 1) + 1e-20)
voiced = vdb > -55
tf = (np.arange(len(vdb)) + 0.5) / 100
up = np.zeros(len(vdb))
pauses, i = [], 0
while i < len(voiced):
    if not voiced[i]:
        j = i
        while j < len(voiced) and not voiced[j]: j += 1
        s, e = i / 100, j / 100
        if e - s > 1.5 or (e - s > 1.0 and any(s <= c <= e for c in cuts)):   # long pause or scene hold
            pauses.append((s, e))
            m = (tf >= s) & (tf < e)
            up[m] = np.clip(np.minimum.reduce([np.full(m.sum(), 6.0), 6 * (tf[m] - s - 0.05) / 1.2,
                                               6 * (e - tf[m]) / 0.6]), 0, 6)
        i = j
    else: i += 1
up = uniform_filter1d(up, 5)                         # round the corners (50 ms)
gain_db = np.interp((np.arange(T) + 0.5) / SR, tf, up).astype(np.float32)
music *= (10 ** (gain_db / 20))[:, None]

# --- base level: median(music - voice) on voiced 100 ms frames = TARGET_REL dB
n = SR // 10
def fdb(x): return 10 * np.log10(np.mean(x[: T // n * n].reshape(-1, n) ** 2, 1) + 1e-20)
vd, md = fdb(v), fdb(music[:, 0].astype(np.float64) * 0.5 + music[:, 1] * 0.5)
vm = vd > -45
base = TARGET_REL - float(np.median(md[vm] - vd[vm]))
music *= 10 ** (base / 20)
print(f"rises: {[(round(a,2),round(b-a,2)) for a,b in pauses]} peak +{up.max():.2f} dB; long pauses: {len(pauses)}, base music gain {base:+.2f} dB")

# --- master gain + true-peak limiter
meter = pyln.Meter(SR)
mix = voice + music
g = TARGET_LUFS - meter.integrated_loudness(mix)
def tp_env(x):
    """per-sample true-peak (4x oversampled), max over channels."""
    out = np.zeros(len(x), np.float32); C, O = 1 << 20, 256
    for ch in range(x.shape[1]):
        for a in range(0, len(x), C):
            lo, hi = max(0, a - O), min(len(x), a + C + O)
            u = np.abs(resample_poly(x[lo:hi, ch].astype(np.float64), 4, 1)).reshape(-1, 4).max(1)
            out[a:a + C] = np.maximum(out[a:a + C], u[a - lo: a - lo + min(C, len(x) - a)])
    return out
lim_stats = {}
for it in range(3):
    y = mix * (10 ** (g / 20))
    pk = tp_env(y); c = 10 ** (CEIL_DBTP / 20)
    req = np.minimum(1.0, c / np.maximum(pk, 1e-9))
    H = int(0.025 * SR)
    gl = uniform_filter1d(minimum_filter1d(req, 2 * H + 1), 2 * H + 1)
    gl = np.minimum(gl, 1.0).astype(np.float32)
    y *= gl[:, None]
    L = meter.integrated_loudness(y)
    red = -20 * np.log10(gl.min())
    lim_stats = dict(iteration=it, gain_db=g, lufs=L, max_reduction_db=red,
                     seconds_reduced_over_0p5db=float(np.sum(gl < 10 ** (-0.5 / 20)) / SR),
                     pre_limit_peak_dbtp=float(20 * np.log10(pk.max())))
    print(lim_stats)
    if abs(L - TARGET_LUFS) < 0.05: break
    g += TARGET_LUFS - L
post = 20 * np.log10(tp_env(y).max())
print(f"post-limit true peak {post:.2f} dBTP")
sf.write(OUT_MIX, y, SR, subtype="FLOAT")
sf.write(OUT_BED, music, SR, subtype="FLOAT")
json.dump(dict(base_music_gain_db=base, long_pauses=pauses, peak_rise_db=float(up.max()), master={k: float(v) for k, v in lim_stats.items()}, post_tp=float(post)), open(STATS, "w"), indent=1)
