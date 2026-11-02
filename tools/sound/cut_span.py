"""Cut a span out of one scene of the film's voice track (e.g. a section the user dropped after the film was built).
usage: cut_span.py --voice voice_only.wav --layout layout.json --scene 3 --in-frame 549 --out-frame 873 \
                   --out voice_only_cut.wav --out-layout layout_cut.json
The span is scene-local video frames [in, out).
The cut is frame-aligned (1600 samples per frame at 48 kHz) so picture and sound stay locked.
Join: 30 ms equal-power crossfade centred on the cut (the audio there is pause noise).
Nothing else changes: every other sample is v1's.
The picture needs the same cut (see docs/01-workflow.md, "Cutting a span after assembly").
Writes the new voice track and a new layout (the scene gets cut_in_frame/cut_out_frame, read by film_gates.py)."""
import argparse, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *  # noqa: F401,F403

ap = argparse.ArgumentParser()
for k in ("voice", "layout", "out", "out-layout"): ap.add_argument("--" + k, required=True)
ap.add_argument("--scene", type=int, required=True)
ap.add_argument("--in-frame", type=int, required=True); ap.add_argument("--out-frame", type=int, required=True)
A = ap.parse_args()
OUT, LAYOUT = A.out, A.out_layout
refuse_existing(OUT, LAYOUT)
IN_F, OUT_F = A.in_frame, A.out_frame
SPF = SR // FPS
L = json.load(open(A.layout))
s3 = next(s for s in L["scenes"] if s["scene"] == A.scene)
a = s3["start"] + IN_F * SPF          # film-v1 sample of the in-point
b = s3["start"] + OUT_F * SPF         # film-v1 sample of the out-point
cut = b - a
H = int(0.015 * SR)                   # half of the 30 ms crossfade

v, sr = sf.read(A.voice, dtype="float32")
assert sr == SR and len(v) == L["total"]
t = (np.arange(2 * H) + 0.5) / (2 * H)
fo, fi = np.cos(0.5 * np.pi * t)[:, None], np.sin(0.5 * np.pi * t)[:, None]
xf = v[a - H: a + H] * fo + v[b - H: b + H] * fi
out = np.concatenate([v[: a - H], xf.astype(np.float32), v[b + H:]])
del v
assert len(out) == L["total"] - cut

scenes, pos = [], 0
for s in L["scenes"]:
    s = dict(s); s["start"] = pos
    if s["scene"] == A.scene:
        s.update(frames=s["frames"] - (OUT_F - IN_F), length=s["length"] - cut, voice_len=s["voice_len"] - cut,
                 cut_in_frame=IN_F, cut_out_frame=OUT_F, cut_in_s=IN_F / FPS, cut_out_s=OUT_F / FPS)
    scenes.append(s); pos += s["length"]
assert pos == len(out)
print(f"cut scene-{A.scene} [{IN_F/FPS:.3f}, {OUT_F/FPS:.3f}) s = {cut/SR:.3f} s; film-v1 [{a/SR:.3f}, {b/SR:.3f}); total {pos/SR:.3f} s")
sf.write(str(OUT), out, SR, subtype="FLOAT")
json.dump(dict(sr=SR, total=pos, cut_scene=A.scene, cut_before=[a, b], cut_at=a, xfade_samples=2 * H, scenes=scenes),
          open(LAYOUT, "w"), indent=1)
