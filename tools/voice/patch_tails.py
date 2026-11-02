"""Built take -> patched take: breath/artifact tails replaced by matched hiss, dead silence filled.

  python patch_tails.py <in.wav> <in.words.json> <out.wav>
Writes <out.wav>, <out>.words.json (a copy: times are unchanged) and <out>_patch_report.json. Never overwrites.

Tail rule (50 ms frames from a word's aligned end to the next word's aligned start, in every gap >= 0.2 s):
  1. the word's own end continues while a frame is a fricative (> 30 % energy above 4 kHz), or a voiced
     decay (> -60 dB with centroid < 2.5 kHz), or within 60 ms of the aligned end;
  2. after that, frames louder than -60 dB totalling >= 100 ms before the next onset = breath/artifact:
     replaced by the matched -70 dBFS hiss (30 ms crossfades), ending before the next onset's rise.
Then every remaining dead stretch (< -80 dB, >= 100 ms) gets hiss ADDED (hiss.fill_dead).
Calibrated on: a breath the user flagged (3.5 kHz), a final "s" that must be kept (5.7 kHz), a voiced burst
and a breath after a word. A flagged spot is a candidate: listen to the report's spots.
"""
import json, os, sys

import numpy as np
import soundfile as sf

from hiss import SR, env_db, fill_dead, hiss_like

F = int(0.05 * SR)


def frame_stats(x, t):
    f = x[int(t * SR):int(t * SR) + F]
    S = np.abs(np.fft.rfft(f * np.hanning(len(f)))) ** 2; fr = np.fft.rfftfreq(len(f), 1 / SR)
    lv = 20 * np.log10(np.sqrt(np.mean(f ** 2)) + 1e-12)
    return lv, float(np.sum(fr * np.sqrt(S)) / (np.sum(np.sqrt(S)) + 1e-12)), float(S[fr > 4000].sum() / (S.sum() + 1e-12))


def chunk_end_tails(x, words):
    """Breath/artifact spans in every word gap >= 0.2 s (chunk ends AND pauses inside a chunk)."""
    spans = []
    for nxt in range(1, len(words)):
        if words[nxt]["start"] - words[nxt - 1]["end"] < 0.2: continue
        last, t_end, t_next = words[nxt - 1], words[nxt - 1]["end"], words[nxt]["start"]
        t = t_end
        while t < t_next:
            lv, cen, hi = frame_stats(x, t)
            if hi > 0.3 or (lv > -60 and cen < 2500) or t - t_end < 0.06: t += 0.05  # fricative or voiced decay
            else: break
        a = t
        b = t_next - 0.03
        while b > a and frame_stats(x, b - 0.05)[0] > -50: b -= 0.01   # stay before the next onset's rise
        loud = sum(0.05 for u in np.arange(a, b - 0.049, 0.05) if frame_stats(x, u)[0] > -60)
        if b - a >= 0.1 and loud >= 0.1:
            spans.append({"start": round(a, 3), "end": round(b, 3), "after": last["word"], "before": words[nxt]["word"],
                          "loud_s": round(loud, 2), "kind": "tail replaced"})
    return spans


def replace_spans(x, y, bed, spans):
    k = int(0.03 * SR); tt = np.linspace(0, np.pi / 2, k, dtype=np.float32)
    for f in spans:
        a, b = int(f["start"] * SR), int(f["end"] * SR)
        y[a:a + k] = x[a:a + k] * np.cos(tt) + bed[a:a + k] * np.sin(tt)
        y[a + k:b - k] = bed[a + k:b - k]
        y[b - k:b] = bed[b - k:b] * np.cos(tt) + x[b - k:b] * np.sin(tt)


def main(src, wj, dst):
    outs = (dst, dst.replace(".wav", ".words.json"), dst.replace(".wav", "_patch_report.json"))
    for p in outs: assert not os.path.exists(p), f"exists, not overwriting: {p}"
    x, sr = sf.read(src, dtype="float32"); assert sr == SR
    words = json.load(open(wj))
    y, e = x.copy(), env_db(x)
    bed = hiss_like(x, e, len(x), np.random.default_rng(205))
    fixed = chunk_end_tails(x, words)
    replace_spans(x, y, bed, fixed)
    fixed += fill_dead(y, e, bed, skip=list(fixed))
    sf.write(dst, y, SR, subtype="PCM_24")
    open(outs[1], "w").write(open(wj).read())
    json.dump(sorted(fixed, key=lambda f: f["start"]), open(outs[2], "w"), indent=1)
    for f in fixed:
        if f["kind"] != "dead silence filled": print(f)
    print(len(fixed), "spots;", sum(f["kind"] == "dead silence filled" for f in fixed), "dead fills")


if __name__ == "__main__":
    if len(sys.argv) != 4: sys.exit(__doc__)
    main(*sys.argv[1:4])
