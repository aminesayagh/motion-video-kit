"""Gates G1-G6 for the assembled film. Heavy on memory: run it alone, nothing else rendering.

usage: film_gates.py --film film.mp4 --layout layout.json --voice voice_only.wav --bed bed_ducked.wav --mix mix.wav \
                     --renders scene01.mp4 scene02.mp4 ... [--lufs -16] [--music-under -32] --out gates.json

G1 format: h264 1920x1080 30 fps, AAC 48 kHz, duration = sum of the scene lengths (+-0.1 s).
G2 the voice in the film is each scene's master, sample-locked: correlation >= 0.99 at lag 0 per scene (8 kHz).
   A scene cut with cut_span.py is compared with its master minus the cut.
G3 loudness: integrated within +-0.5 LU of --lufs, true peak <= -1.5 dBTP.
G4 music under the voice: median (music - voice) on voiced 100 ms frames within +-4 dB of --music-under, per scene.
G5 (only when the layout has a cut) the join: 10 ms RMS steps and the largest sample jump within +-20 ms.
G6 cuts land on the right frame: PSNR of frame 15 of each scene, film vs the scene's own render, > 40 dB.
"""
import argparse, json, os, re, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *  # noqa: F401,F403

ap = argparse.ArgumentParser()
for k in ("film", "layout", "voice", "bed", "mix", "out"): ap.add_argument("--" + k, required=True)
ap.add_argument("--renders", nargs="+", required=True)
ap.add_argument("--lufs", type=float, default=-16.0); ap.add_argument("--music-under", type=float, default=-32.0)
A = ap.parse_args()
refuse_existing(A.out)
L = json.load(open(A.layout)); res = {}
cut = next((s for s in L["scenes"] if "cut_in_frame" in s), None)
spf = SR // FPS

# G1
pr = json.loads(subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                                "stream=codec_name,sample_rate,width,height,r_frame_rate:format=duration",
                                "-of", "json", A.film], capture_output=True, text=True).stdout)
d = float(pr["format"]["duration"]); v, a = pr["streams"][0], pr["streams"][1]
want = L["total"] / SR
ok = (abs(d - want) <= 0.1 and v["codec_name"] == "h264" and (v["width"], v["height"]) == (1920, 1080)
      and v["r_frame_rate"] == "30/1" and (a["codec_name"], a["sample_rate"]) == ("aac", "48000"))
res["G1"] = (f"{'PASS' if ok else 'FAIL'}: {v['width']}x{v['height']} {v['r_frame_rate']} fps {v['codec_name']}, "
             f"{a['codec_name']} {a['sample_rate']} Hz; film {d:.3f} s vs layout {want:.3f} s; video frames {nb_frames(A.film)}")

# G2
v48 = sf.read(A.voice, dtype="float64")[0][:, 0]; rs = []
for s in L["scenes"]:
    w, wsr = sf.read(s["wav"], dtype="float64"); w = w[:, 0] if w.ndim > 1 else w
    if "cut_in_frame" in s:
        k = wsr // FPS
        w = np.concatenate([w[: s["cut_in_frame"] * k], w[s["cut_out_frame"] * k:]])
    a8 = resample_poly(v48[s["start"]: s["start"] + s["voice_len"]], 8000, SR)
    b8 = resample_poly(w, 8000, wsr)
    rs.append(best_corr(a8, b8, 8000, 0.05))
del v48
res["G2"] = (f"{'PASS' if all(r >= 0.99 and k == 0 for r, k in rs) else 'FAIL'}: r per scene "
             + " ".join(f"{r:.5f}" for r, _ in rs) + f"; lags {[k for _, k in rs]}")

# G3
I, P, LRA = ebur128(A.film)
res["G3"] = f"{'PASS' if abs(I - A.lufs) <= 0.5 and P <= -1.5 else 'FAIL'}: I {I} LUFS, true peak {P} dBTP, LRA {LRA} LU"

# G4
voice = sf.read(A.voice, dtype="float32")[0]; bed = sf.read(A.bed, dtype="float32")[0]
n = SR // 10
fdb = lambda x: 10 * np.log10(np.mean(x.mean(1).astype(np.float64)[: len(x) // n * n].reshape(-1, n) ** 2, 1) + 1e-20)
vd, md = fdb(voice), fdb(bed); meds = []
for s in L["scenes"]:
    a_, b_ = s["start"] // n, (s["start"] + s["length"]) // n
    m = vd[a_:b_] > -45
    meds.append(float(np.median(md[a_:b_][m] - vd[a_:b_][m])))
res["G4"] = (f"{'PASS' if all(abs(x - A.music_under) <= 4 for x in meds) else 'FAIL'}: median music-voice per scene (dB) "
             + " ".join(f"{x:.1f}" for x in meds))
del voice, bed

# G5
if cut:
    j = L["cut_at"]
    mix = sf.read(A.mix, dtype="float64", start=j - SR, stop=j + SR)[0]
    m1 = mix.mean(1); n1 = SR // 100
    db = 10 * np.log10(np.mean(m1.reshape(-1, n1) ** 2, 1) + 1e-20)
    dif = np.abs(np.diff(m1))
    near = dif[SR - 2 * n1: SR + 2 * n1].max(); rest = np.median(np.abs(np.diff(m1[: SR - 4 * n1])))
    res["G5_audio"] = (f"join at film {j/SR:.3f} s: 10 ms RMS around the join {db[98:102].round(1).tolist()} dBFS "
                       f"(neighbours {db[90:98].round(1).tolist()}), max 10 ms step +-1 s {np.max(np.abs(np.diff(db))):.1f} dB; "
                       f"largest sample jump within +-20 ms {near:.2e} vs median jump {rest:.2e} (no click if similar)")


# G6
def psnr(t_film, src, t_src):
    o = subprocess.run(["ffmpeg", "-hide_banner", "-threads", "1", "-ss", f"{t_film:.4f}", "-i", A.film, "-ss", f"{t_src:.4f}",
                        "-i", src, "-lavfi", "[0:v][1:v]psnr", "-frames:v", "1", "-f", "null", "-"], capture_output=True, text=True).stderr
    return float(re.search(r"average:(\S+)", o).group(1).replace("inf", "99"))


ps = [psnr(s["start"] / SR + 15.5 / FPS, src, 15.5 / FPS) for s, src in zip(L["scenes"], A.renders)]
if cut:
    i = L["scenes"].index(cut)
    for film_f, src_f in ((cut["cut_in_frame"] - 30, cut["cut_in_frame"] - 30), (cut["cut_in_frame"] + 30, cut["cut_out_frame"] + 30)):
        ps.append(psnr(cut["start"] / SR + (film_f + 0.5) / FPS, A.renders[i], (src_f + 0.5) / FPS))
res["G6"] = (f"{'PASS' if all(p > 40 for p in ps) else 'FAIL'}: PSNR film vs scene render, frame 15 of each scene (dB) "
             + " ".join(f"{p:.1f}" for p in ps[:len(A.renders)])
             + (f"; one second before / after the join {ps[-2]:.1f} / {ps[-1]:.1f}" if cut else ""))
for k, v_ in res.items(): print(f"{k}: {v_}")
json.dump(res, open(A.out, "x"), indent=1)
