"""Regenerate one chunk in place: a new take of the LAST chunk(s) of a finished scene, everything before it bit-identical.

  python replace_chunk.py --config voice.json --scene 9 --base v9 --new v10 --chunk scene09_p4_c1 --seed 3 [--tail 0.6]

Use when the user asks for one line again (new wording or a better ending) and approved the rest. Steps:
  1. edit the scene's text file (only that chunk's text), then make takes for it:
     qwen_takes.py gen/check --scenes N  (only chunks without an accepted take are generated) and pick a seed;
  2. this script keeps <base> up to the chunk's start, appends the chosen take's checked segment with a 25 ms
     crossfade, then a tail of matched hiss (--tail seconds after the last sound in total);
  3. on the new part only: breath tails replaced, dead silence filled, abrupt word tails softened;
  4. the file end: the take's own tail is often dead (-93 dB), so -70 dBFS hiss is added from 25 ms before the
     release reaches -60 dB to the end (add-only: the release samples stay).
It asserts that every sample before the chunk is identical to <base>, so the approved part cannot change.
Here the chunk is the scene's last; for a chunk in the middle, rebuild the scene instead (later words would move).
Writes sceneNN_<new>.wav and .words.json in out_dir. Never overwrites.
"""
import argparse, json

import numpy as np
import soundfile as sf

import patch_tails, qwen_takes as q, soften
from hiss import env_db, fill_dead, hiss_like, ramp_env

ap = argparse.ArgumentParser()
for k in ("config", "base", "new", "chunk"): ap.add_argument("--" + k, required=True)
ap.add_argument("--scene", type=int, required=True); ap.add_argument("--seed", type=int, required=True)
ap.add_argument("--tail", type=float, default=0.6)
a = ap.parse_args()
q.configure(a.config); SR, S = q.SR, f"{a.scene:02d}"
dst, wjd = q.out(f"scene{S}_{a.new}.wav"), q.out(f"scene{S}_{a.new}.words.json")
for p in (dst, wjd): assert not p.exists(), f"exists, not overwriting: {p}"
base, _ = sf.read(q.out(f"scene{S}_{a.base}.wav"), dtype="float32")
wbase = json.loads(q.out(f"scene{S}_{a.base}.words.json").read_text())
chunk = next(c for c in json.loads(q.out(f"scene{S}_{a.base}_pre.summary.json").read_text())["chunks"] if c["chunk"] == a.chunk)
plan_c = next(c for c in q.plan([a.scene]) if c["id"] == a.chunk)          # the chunk's CURRENT text
rec = q.load_state()[q.key(plan_c)]
take = next(t for t in rec["takes"] if t["seed"] == a.seed)
raw = sf.read(take["path"], dtype="float32")[0]; seg = q.segment(raw)
start = int(round(chunk["start_s"] * SR)); k = int(SR * q.XF)
acc, s0 = q.append_xf(base[:start + k].copy(), seg); assert s0 == start
_, tail_s, _, tail_rms = q.margins(raw)
bed, _ = q.noise_bed([seg], max(a.tail - tail_s, 0.05) + q.XF, np.random.default_rng(509), tail_rms, tail_rms)
acc, _ = q.append_xf(acc, bed)
_, align = q.whisper_aligner()
words = [w for w in wbase if w["start"] < chunk["start_s"] - 0.005] + align(seg, rec["text"], start / SR)
new_words = [w for w in words if w["start"] >= chunk["start_s"] - 0.005]

y, e = acc.copy(), env_db(acc)
bedh = hiss_like(acc, e, len(acc), np.random.default_rng(905))
tails = patch_tails.chunk_end_tails(acc, new_words)
patch_tails.replace_spans(acc, y, bedh, tails)
fills = fill_dead(y, e, bedh, skip=tails, start_frame=start // 240 + 5)
drops = [d for d in soften.find_drops(y, words) if d >= start]
rng, L = np.random.default_rng(77), int(0.04 * SR)
for d in drops:                                   # same shaping as soften.py, on the new part only
    ref = y[d - int(0.02 * SR):d]; spec = np.abs(np.fft.rfft(ref * np.hanning(len(ref))))
    X = np.fft.rfft(rng.standard_normal(L)) * np.interp(np.linspace(0, 1, L // 2 + 1), np.linspace(0, 1, len(spec)), spec)
    nz = np.fft.irfft(X, L); nz /= np.sqrt(np.mean(nz ** 2))
    a0 = np.sqrt(np.mean(y[d - int(0.01 * SR):d] ** 2))
    y[d:d + L] += (nz * a0 * (10 ** (-70 / 20) / a0) ** np.linspace(0, 1, L)).astype(np.float32)
ez = env_db(y); last = np.nonzero(ez > -40)[0][-1]; floor = last + int(np.argmax(ez[last:] < -60))
s_end = floor * 240 - int(0.025 * SR)              # end fix: hiss to the file end, under the release
hb = hiss_like(y, ez, len(y), np.random.default_rng(910))
y[s_end:] += hb[s_end:] * ramp_env(len(y) - s_end, int(0.025 * SR))
assert np.array_equal(y[:start], base[:start]), "the approved part changed"
sf.write(dst, y, SR, subtype="PCM_24"); json.dump(words, open(wjd, "w"), indent=1)
print(json.dumps({"dur": round(len(y) / SR, 3), "frames": len(y), "chunk_start": start / SR, "tails": tails,
                  "fills": len(fills), "softened": [round(d / SR, 3) for d in drops], "end_hiss_from": round(s_end / SR, 3),
                  "new_words": new_words}))
