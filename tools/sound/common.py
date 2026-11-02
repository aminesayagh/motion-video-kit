"""Shared helpers for the film audio tools: ffmpeg decode, frame counts, loudness, best-lag correlation."""
import json, re, subprocess

import numpy as np
import soundfile as sf  # noqa: F401  (re-exported for the tools)
from scipy.signal import resample_poly  # noqa: F401

SR = 48000   # film audio rate
FPS = 30


def nb_frames(mp4):
    """Exact number of video frames (packets) of a file."""
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-count_packets",
                          "-show_entries", "stream=nb_read_packets", "-of", "csv=p=0", str(mp4)],
                         capture_output=True, text=True, check=True).stdout.strip()
    return int(out)


def decode(path, sr, mono=True, start=None, dur=None):
    """Any audio/video file's first audio stream as float32 at sr."""
    cmd = ["ffmpeg", "-v", "error", "-threads", "1"]
    if start is not None: cmd += ["-ss", str(start)]
    if dur is not None: cmd += ["-t", str(dur)]
    cmd += ["-i", str(path), "-map", "a:0", "-ac", "1" if mono else "2", "-ar", str(sr), "-f", "f32le", "-"]
    x = np.frombuffer(subprocess.run(cmd, capture_output=True, check=True).stdout, np.float32)
    return x if mono else x.reshape(-1, 2)


def ebur128(path):
    """(integrated LUFS, true peak dBTP, LRA LU) from ffmpeg's ebur128 summary."""
    e = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-threads", "1", "-i", str(path), "-map", "a:0",
                        "-af", "ebur128=peak=true", "-f", "null", "-"], capture_output=True, text=True).stderr
    s = e[e.rfind("Summary:"):]
    return (float(re.search(r"I:\s+(-?[\d.]+) LUFS", s).group(1)), float(re.search(r"Peak:\s+(-?[\d.]+) dBFS", s).group(1)),
            float(re.search(r"LRA:\s+(-?[\d.]+) LU", s).group(1)))


def best_corr(a, b, sr, maxlag_s=0.3):
    """Pearson correlation of a vs b at the best integer lag (b shifted). Returns (r, lag in samples)."""
    from scipy.signal import correlate
    n = min(len(a), len(b))
    a, b = a[:n] - a[:n].mean(), b[:n] - b[:n].mean()
    L = int(maxlag_s * sr)
    c = correlate(a, b, mode="full", method="fft")
    mid = n - 1
    k = int(np.argmax(c[mid - L: mid + L + 1])) - L
    x, y = (a[k:], b[:n - k]) if k >= 0 else (a[:n + k], b[-k:])
    return float(np.dot(x, y) / np.sqrt(np.dot(x, x) * np.dot(y, y))), k


def load_json(p): return json.load(open(p))


def refuse_existing(*paths):
    import os, sys
    for p in paths:
        if os.path.exists(p): sys.exit(f"exists, not overwriting: {p}")
