"""Natural-release check: after the last sound (> -40 dB, 10 ms frames), the level must not fall
more than 30 dB in under 40 ms (the model sometimes stops generating mid-release)."""
import numpy as np


def release_cut(seg, sr=24000):
    n = sr // 100; k = len(seg) // n
    e = 20 * np.log10(np.sqrt(np.mean(seg[:k * n].reshape(k, n) ** 2, axis=1)) + 1e-12)
    L = int(np.nonzero(e > -40)[0][-1]); p = float(e[max(0, L - 2):L + 1].max())
    k30 = next((j for j in range(L + 1, len(e)) if e[j] < p - 30), None)
    if k30 is None:  # never decays 30 dB before the file ends: truncated mid-decay
        return True, None, e[max(0, L - 4):L + 6].round(0).astype(int).tolist()
    return (k30 - L) * 10 < 40, (k30 - L) * 10, e[max(0, L - 4):L + 6].round(0).astype(int).tolist()
