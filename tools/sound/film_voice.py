"""Film step 1: one continuous 48 kHz stereo voice track for the whole film.
usage: film_voice.py --scenes scenes.json --out voice_only.wav --layout layout.json
  scenes.json: [{"video": "final/1080/scene01_1080.mp4", "wav": "audio/scene01_master_C.wav"}, ...] in film order
  (relative paths are relative to scenes.json). Each scene lasts exactly its video's frame count.
Each scene's master is placed at its scene start (video frames * 1600 samples) untouched
(only resampled 24k -> 48k), and padded to the scene's exact length with a constant noise floor
shaped like and as loud as the masters' own pauses (never digital silence).
Writes the voice-only track and a layout JSON (sample start/length of every scene), which the music bed,
the mix, the cut tool and the gates all read."""
import argparse, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *  # noqa: F401,F403
from scipy.signal import welch

ap = argparse.ArgumentParser()
ap.add_argument("--scenes", required=True); ap.add_argument("--out", required=True); ap.add_argument("--layout", required=True)
a = ap.parse_args()
OUT, LAYOUT = a.out, a.layout
refuse_existing(OUT, LAYOUT)
base = os.path.dirname(os.path.abspath(a.scenes))
SCENES = [(os.path.join(base, s["video"]), os.path.join(base, s["wav"])) for s in json.load(open(a.scenes))]

# --- noise floor: level and spectrum of the masters' pauses (50 ms frames < -60 dBFS)
lvls, chunks = [], []
for _, wav in SCENES:
    x, sr = sf.read(str(wav), dtype="float64"); m = x[:, 0]
    n = sr // 20; f = m[: len(m) // n * n].reshape(-1, n)
    db = 10 * np.log10(np.mean(f ** 2, 1) + 1e-20)
    lvls += list(db[db < -60])
    chunks.append(f[(db > -80) & (db < -70)].ravel())
floor_db = float(np.median(lvls))
fr, psd = welch(np.concatenate(chunks), fs=24000, nperseg=2048)
print(f"pause floor median {floor_db:.2f} dBFS RMS over {len(lvls)} frames")

rng = np.random.default_rng(20261101)
def floor_noise(n):
    w = np.fft.rfft(rng.standard_normal(n))
    f = np.fft.rfftfreq(n, 1 / SR)
    mag = np.sqrt(np.interp(f, fr, psd, right=0.0))   # nothing above 12 kHz, like the masters
    y = np.fft.irfft(w * mag, n)
    return y * (10 ** (floor_db / 20) / np.sqrt(np.mean(y ** 2)))

# --- layout
scenes, pos = [], 0
for i, (mp4, wav) in enumerate(SCENES, 1):
    fr_v = nb_frames(mp4); n = fr_v * (SR // FPS)
    scenes.append(dict(scene=i, mp4=str(mp4), wav=str(wav), frames=fr_v, start=pos, length=n))
    pos += n
total = pos
voice = np.zeros((total, 2), np.float32)
for s in scenes:
    x, sr = sf.read(s["wav"], dtype="float64")
    y = resample_poly(x[:, 0], SR, sr)                # masters are L == R (checked); 24 kHz -> 48 kHz
    n = s["length"]
    used = min(len(y), n)
    s["voice_len"] = used; s["trimmed"] = max(0, len(y) - n)
    seg = np.empty(n)
    seg[:used] = y[:used]
    if n > used: seg[used:] = floor_noise(n - used)
    s["pad"] = n - used
    voice[s["start"]: s["start"] + n] = seg[:, None]
    print(f"scene{s['scene']:02d} start {s['start']/SR:8.3f}s len {n/SR:7.3f}s voice {used/SR:7.3f}s pad {(n-used)/SR:.3f}s trimmed {s['trimmed']} samples@48k")
print(f"total {total} samples = {total/SR:.4f} s")
sf.write(str(OUT), voice, SR, subtype="FLOAT")
json.dump(dict(sr=SR, total=total, floor_db=floor_db, scenes=scenes), open(LAYOUT, "w"), indent=1)
