"""Shared helpers for the take repairs: 10 ms envelope, matched hiss, ramps, dead-silence fill.

A synthetic voice often has stretches of true digital silence (< -80 dBFS) between words. On a speaker they
sound like the sound "switching off". The fix is ADD-only: hiss with the spectrum of the voice's own noise floor,
at a constant -70 dBFS RMS, with 25 ms ramps inside the stretch. The speech samples are never touched, so the
length and every word time stay the same.
"""
import numpy as np

SR, HISS_DB, RAMP = 24000, -70.0, 0.025


def env_db(x, n=240):
    k = len(x) // n
    return 20 * np.log10(np.sqrt(np.mean(x[:k * n].reshape(k, n) ** 2, axis=1)) + 1e-12)


def hiss_like(x, e, length, rng):
    """Noise with the spectrum of the voice's hiss (frames between -75 and -55 dB), at HISS_DB RMS."""
    n = 1024
    f = np.lib.stride_tricks.sliding_window_view(x, n)[::n // 2]
    lv = 20 * np.log10(np.sqrt((f ** 2).mean(1)) + 1e-12)
    spec = np.sqrt((np.abs(np.fft.rfft(f[(lv > -75) & (lv < -55)] * np.hanning(n), axis=1)) ** 2).mean(0))
    X = np.fft.rfft(rng.standard_normal(length)) * np.interp(np.linspace(0, 1, length // 2 + 1), np.linspace(0, 1, len(spec)), spec)
    y = np.fft.irfft(X, length)
    return (y / np.sqrt((y ** 2).mean()) * 10 ** (HISS_DB / 20)).astype(np.float32)


def ramp_env(n, r):
    g = np.ones(n, np.float32); k = min(r, n // 2)
    g[:k] = np.sin(np.linspace(0, np.pi / 2, k)); g[n - k:] = np.cos(np.linspace(0, np.pi / 2, k))
    return g


def fill_dead(y, e, bed, skip=(), start_frame=5):
    """Add hiss to every interior run of 10 ms frames under -80 dB lasting >= 100 ms (in place).
    skip: spans (dicts with start/end seconds) already replaced; a run starting inside one is filled after it.
    Returns the filled spans."""
    r, filled, i = int(SR * RAMP), [], start_frame
    while i < len(e) - 5:
        if e[i] < -80:
            j = i
            while j < len(e) and e[j] < -80: j += 1
            if j - i >= 10 and j < len(e) - 5:
                a, b = i * 240, j * 240
                for f in skip:
                    if f["start"] * SR <= a < f["end"] * SR: a = int(f["end"] * SR)
                if b - a > 2 * r and not any(f["start"] * SR <= b <= f["end"] * SR for f in skip):
                    y[a:b] += bed[a:b] * ramp_env(b - a, r)
                    filled.append({"start": round(a / SR, 3), "end": round(b / SR, 3), "kind": "dead silence filled"})
            i = j
        else:
            i += 1
    return filled
