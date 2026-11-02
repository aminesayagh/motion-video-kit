"""Soften abrupt word-tail endings into the hiss fill, add-only (onsets and word times untouched).

  python soften.py <in.wav> <words.json> <out.wav>
Only drops in a gap between words count (>= word end - 0.1 s, next word >= 60 ms later): no plosive
closures inside words.

Spot: on a 5 ms envelope, a word tail above -55 dB that drops by more than 15 dB within 20 ms into the
hiss level (next 40 ms between -76 and -60 dB). Fix: ADD 40 ms of noise shaped like the tail's last
20 ms, decaying exponentially from the tail's level to the hiss level (a natural release).
"""
import json, os, sys

import numpy as np
import soundfile as sf

SR, W = 24000, 120  # 5 ms


def env5(x):
    k = len(x) // W
    return 20 * np.log10(np.sqrt(np.mean(x[:k * W].reshape(k, W) ** 2, axis=1)) + 1e-12)


def in_gap(t, words):
    for a, b in zip(words, words[1:]):
        if a["end"] - 0.1 <= t and t + 0.06 <= b["start"]: return True
    return False


def find_drops(x, words):
    e, out, i = env5(x), [], 0
    while i < len(e) - 13:
        if e[i] > -55:
            j = next((j for j in range(i + 1, i + 5) if e[j] < e[i] - 15), None)
            if j is not None and -76 < e[j:j + 8].mean() < -60 and e[j:j + 8].max() < -55:
                if in_gap(j * W / SR, words): out.append(j * W)
                i = j + 8; continue
        i += 1
    return out


def main(src, wj, dst):
    assert not os.path.exists(dst), dst
    x, sr = sf.read(src, dtype="float32"); assert sr == SR
    y, rng, L = x.copy(), np.random.default_rng(7), int(0.04 * SR)
    words = json.load(open(wj)); drops = find_drops(x, words)
    for d in drops:
        ref = x[d - int(0.02 * SR):d]
        spec = np.abs(np.fft.rfft(ref * np.hanning(len(ref))))
        X = np.fft.rfft(rng.standard_normal(L)) * np.interp(np.linspace(0, 1, L // 2 + 1), np.linspace(0, 1, len(spec)), spec)
        n = np.fft.irfft(X, L); n /= np.sqrt(np.mean(n ** 2))
        a0 = np.sqrt(np.mean(x[d - int(0.01 * SR):d] ** 2)); a1 = 10 ** (-70 / 20)
        g = a0 * (a1 / a0) ** np.linspace(0, 1, L)          # exponential decay tail level -> hiss level
        y[d:d + L] += (n * g).astype(np.float32)
    sf.write(dst, y, SR, subtype="PCM_24")
    left = find_drops(y, words)
    print(json.dumps({"softened": len(drops), "spots_s": [round(d / SR, 3) for d in drops], "left": len(left),
                      "frames_equal": len(x) == len(y)}))


if __name__ == "__main__":
    main(*sys.argv[1:4])
