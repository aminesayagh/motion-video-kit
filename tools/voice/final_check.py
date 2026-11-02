"""Final checks on a finished scene take, written to sceneNN_<tag>_checks.json next to it.

  python final_check.py --config voice.json --scene 5 --tag v1

Reads (all in the config's out_dir): sceneNN_<tag>.wav (final), sceneNN_<tag>_pre.wav (built, before patches),
sceneNN_<tag>_pre.summary.json, sceneNN_<tag>_patched_patch_report.json, state.json, and the scene's text.
Prints one JSON line:
  len_equal       the patches changed no length (word times still valid)
  dead_runs_left  stretches under -80 dB lasting >= 100 ms (should be 0)
  stt_diffs       full-file Whisper vs the text, with the time of each difference (listen to each)
  watch_heard     each config "watch" phrase heard in the full file
  tails / fills   what patch_tails.py replaced or filled
  chunks_not_ok   chunks whose chosen take failed a check (the best of max_tries was used: listen)
  falls           paragraph-final pitch falls in semitones
"""
import argparse, difflib, json, os

import numpy as np
import scipy.signal as ss
import soundfile as sf

import qwen_takes as q
from hiss import env_db

ap = argparse.ArgumentParser()
ap.add_argument("--config", required=True); ap.add_argument("--scene", type=int, required=True); ap.add_argument("--tag", required=True)
a = ap.parse_args()
cfg = q.configure(a.config); n, S = a.scene, f"{a.scene:02d}"
final, pre = q.out(f"scene{S}_{a.tag}.wav"), q.out(f"scene{S}_{a.tag}_pre.wav")
dst = q.out(f"scene{S}_{a.tag}_checks.json"); assert not dst.exists(), f"exists, not overwriting: {dst}"
b, _ = sf.read(final, dtype="float32"); pa, _ = sf.read(pre, dtype="float32")
e = env_db(b)[5:-5]; runs = 0; i = 0
while i < len(e):
    if e[i] < -80:
        j = i
        while j < len(e) and e[j] < -80: j += 1
        runs += (j - i) >= 10; i = j
    else: i += 1
from faster_whisper import WhisperModel
m = WhisperModel(cfg["whisper_model"], device="cpu", compute_type="int8")
ws = [w for g in m.transcribe(ss.resample_poly(b, 2, 3).astype(np.float32), initial_prompt=cfg["prompt"] or None,
                              beam_size=5, word_timestamps=True)[0] for w in g.words]
h = [t for w in ws for t in q.toks(w.word)]
r = q.toks((cfg["text_dir"] / cfg["text_pattern"].format(scene=n)).read_text())
diffs = [(t, r[i1:i2], h[j1:j2], round(ws[min(j1, len(ws) - 1)].start, 2))
         for t, i1, i2, j1, j2 in difflib.SequenceMatcher(None, r, h, autojunk=False).get_opcodes() if t != "equal"]
sub = lambda qq, xs: any(xs[i:i + len(qq)] == qq for i in range(len(xs) - len(qq) + 1))
watch = {w: sub(q.toks(w), h) for w in cfg["watch"]}
st = q.load_state(); rows = []
for c in json.loads(q.out(f"scene{S}_{a.tag}_pre.summary.json").read_text())["chunks"]:
    rec = next(x for x in st.values() if x["id"] == c["chunk"] and x["scene"] == n and any(u["path"] == c["take"] for u in x["takes"]))
    t = next(u for u in rec["takes"] if u["path"] == c["take"])
    rows.append({"chunk": c["chunk"], "start_s": c["start_s"], "text": rec["text"], "spoken": t.get("spoken", rec["text"]),
                 "seed": t["seed"], "tries": len(rec["takes"]), "ok": t["ok"], "heard": t["heard"],
                 "first_alone": t["first_alone"], "end_alone": t["end_alone"],
                 "final_fall_st": t.get("final_fall_st"), "watch_missing": t.get("watch_missing")})
json.dump(rows, open(dst, "w"), indent=1)
rp = q.out(f"scene{S}_{a.tag}_patched_patch_report.json")
rep = json.loads(rp.read_text()) if rp.exists() else []
print(json.dumps({"scene": n, "dur": round(len(b) / q.SR, 3), "frames": len(b), "len_equal": len(pa) == len(b),
                  "dead_runs_left": runs, "stt_diffs": diffs, "watch_heard": watch,
                  "tails": [f for f in rep if f["kind"] != "dead silence filled"],
                  "fills": sum(f["kind"] == "dead silence filled" for f in rep),
                  "chunks_not_ok": [c["chunk"] for c in rows if not c["ok"]],
                  "falls": {c["chunk"]: c["final_fall_st"] for c in rows if c["final_fall_st"] is not None}}))
