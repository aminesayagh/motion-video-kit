"""Narration takes with Qwen3-TTS voice cloning, checked word by word with faster-whisper (the approved method).

One model per process (the GPU model and Whisper never share memory):
  python qwen_takes.py gen   --config voice.json --scenes 1,2     # Qwen, GPU: one new take per chunk still failing
  python qwen_takes.py check --config voice.json --scenes 1,2     # Whisper, CPU: checks every unchecked take
  python qwen_takes.py build --config voice.json --scenes 1 --tag v1   # best takes -> one scene file + word times

Repeat gen + check until every chunk has an accepted take or hits max_tries (run_scene.sh does this), then build.

What a take must pass (check):
  - the whole chunk heard right (token ratio >= 0.93, numbers compared as words),
  - the FIRST word heard alone (first 1.2 s, no prompt, no context to guess it from),
  - the LAST word heard alone (last 1.5 s; catches a swallowed final "s") and the last two words in context,
  - a natural release after the last sound (release.py: no 30 dB fall in under 40 ms; step names >= 100 ms),
  - the level falls at the end (end_drop_db < -25),
  - paragraph-final chunks close with a falling pitch (>= 3 semitones down over the last words),
  - watch phrases heard word for word (config "watch"; "watch_plain" also without the prompt).

Build: the exact checked segment of each take (150 ms kept before the first sound, 180 ms after the last), joined
with pauses filled by noise matched to the voice's own hiss (never digital silence), 25 ms equal-power crossfades.
Word times come from Whisper's aligner on the known text, per chunk, offset by sample position.

Config (JSON; relative paths are relative to the config file): see examples/orbitrows/voice.json.
"""
import argparse, difflib, hashlib, json, os, re, sys
from pathlib import Path

import numpy as np
import soundfile as sf

sys.path.insert(0, str(Path(__file__).parent))
import release  # noqa: E402

SR = 24000
LEAD, TAIL, XF = 0.15, 0.18, 0.025
CFG = {}
DEFAULTS = {
    "text_pattern": "scene{scene:02d}.txt", "out_dir": "out/voice",
    "model": "Qwen/Qwen3-TTS-12Hz-0.6B-Base", "language": "English", "whisper_model": "medium.en",
    "max_chars": 260, "max_tries": 6,
    "pause": {"para": 0.84, "sent": 0.49, "step": 0.5},   # last sound -> next first sound, seconds
    "prompt": "",                                          # Whisper hint: names and unusual words of the script
    "spoken": {},                                          # written form -> form sent to the model
    "break_after": [],                                     # sentences followed by a ~0.5 s pause
    "step_regex": r"Step \w+: \w+\.",                     # step-name sentences: own chunk, short pause after
    "watch": [], "watch_plain": [], "drop": "",
    "settings": {"temperature": 0.8, "top_k": 50, "repetition_penalty": 1.05},
}


def configure(path):
    """Load a config file into CFG; paths become absolute (relative to the config file)."""
    p = Path(path).resolve()
    CFG.clear(); CFG.update(DEFAULTS); CFG.update(json.loads(p.read_text()))
    for k in ("text_dir", "out_dir", "reference_wav", "reference_txt"):
        CFG[k] = (p.parent / CFG[k]).resolve()
    CFG["out_dir"].mkdir(parents=True, exist_ok=True)
    (CFG["out_dir"] / "chunks").mkdir(exist_ok=True)
    return CFG


def state_path(): return CFG["out_dir"] / "state.json"
def out(name): return CFG["out_dir"] / name


ONES = "zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen seventeen eighteen nineteen".split()
TENS = "_ _ twenty thirty forty fifty sixty seventy eighty ninety".split()
NUM = {"1": "one", "2": "two", "3": "three", "4": "four", "5": "five", "6": "six", "7": "seven",
       "8": "eight", "9": "nine", "10": "ten"}


def num_words(n):
    if n < 20: return [ONES[n]]
    if n < 100: return [TENS[n // 10]] + ([ONES[n % 10]] if n % 10 else [])
    return [ONES[n // 100], "hundred"] + (["and"] + num_words(n % 100) if n % 100 else [])


def toks(text):
    """Comparable tokens: hyphens split, numbers up to 999 spelled out ("682" == "six hundred and eighty-two")."""
    res = []
    for w in text.replace("-", " ").replace("%", " percent").split():
        w = re.sub(r"[^a-z0-9]", "", w.lower())
        if w.isdigit() and int(w) < 1000: res += num_words(int(w))
        elif w: res.append(w)
    return res


def norm(w):
    w = re.sub(r"[^a-z0-9]", "", w.lower())
    return NUM.get(w, w)


def spoken_form(text):
    for k, v in CFG["spoken"].items():
        text = text.replace(k, v)
    return text


def plan(scenes):
    """Chunks of the scenes' narration: sentence ends, up to max_chars; step names and break_after sentences alone."""
    chunks = []
    for s in scenes:
        text = (CFG["text_dir"] / CFG["text_pattern"].format(scene=s)).read_text()
        paras = [p.strip() for p in text.split("\n\n") if p.strip()]
        if CFG["drop"]:
            paras = [q for q in (p.replace(CFG["drop"], "").strip() for p in paras) if q]
        for pi, p in enumerate(paras, 1):
            res, buf = [], ""
            for sent in re.split(r"(?<=[.?!])\s+(?=[A-Z\"'])", p):
                if CFG["step_regex"] and re.fullmatch(CFG["step_regex"], sent):
                    if buf: res.append((buf, "sent")); buf = ""
                    res.append((sent, "step")); continue
                if sent in CFG["break_after"]:
                    res.append((f"{buf} {sent}".strip(), "step")); buf = ""; continue
                if buf and len(buf) + len(sent) + 1 > CFG["max_chars"]:
                    res.append((buf, "sent")); buf = sent
                else:
                    buf = f"{buf} {sent}".strip()
            if buf: res.append((buf, "sent"))
            for ci, (t, kind) in enumerate(res, 1):
                chunks.append({"id": f"scene{s:02d}_p{pi}_c{ci}", "scene": s, "para": pi, "text": t, "kind": kind})
    return chunks


def key(c): return f"{c['scene']}|{c['text']}"
def load_state(): return json.loads(state_path().read_text()) if state_path().exists() else {}
def save_state(st): state_path().write_text(json.dumps(st, indent=1))
def accepted(rec): return any(t.get("ok") for t in rec.get("takes", []))


def gen(scenes):
    import torch
    from qwen_tts import Qwen3TTSModel
    st, todo = load_state(), []
    for c in plan(scenes):
        rec = st.setdefault(key(c), {**c, "takes": []}); rec.update(id=c["id"], kind=c["kind"], para=c["para"])
        if not accepted(rec) and len(rec["takes"]) < CFG["max_tries"] and all("ok" in t for t in rec["takes"]):
            todo.append(rec)
    save_state(st)
    if not todo: print("nothing to generate"); return
    tts = Qwen3TTSModel.from_pretrained(CFG["model"], device_map="cuda:0", dtype=torch.bfloat16)
    prompt = tts.create_voice_clone_prompt(ref_audio=str(CFG["reference_wav"]),     # reused for every chunk
                                           ref_text=CFG["reference_txt"].read_text())
    for rec in todo:
        seed = max([t["seed"] for t in rec["takes"]], default=0) + 1
        torch.manual_seed(seed)
        spoken = spoken_form(rec["text"])
        wavs, sr = tts.generate_voice_clone(text=spoken, language=CFG["language"], voice_clone_prompt=prompt,
                                            max_new_tokens=int(len(rec["text"]) * 2) + 120,  # stops runaway takes
                                            **CFG["settings"])
        assert sr == SR
        h = hashlib.sha1(rec["text"].encode()).hexdigest()[:6]   # ids shift when text changes; names must not collide
        path = out("chunks") / f"{rec['id']}_{h}_s{seed}.wav"
        assert not path.exists(), path
        sf.write(path, wavs[0].astype(np.float32), SR)
        rec["takes"].append({"seed": seed, "path": str(path), "spoken": spoken})
        save_state(st)
        print(f"{rec['id']} seed {seed}: {len(wavs[0]) / SR:.1f}s", flush=True)


def env_db(x, win=0.01):
    n = int(SR * win); k = len(x) // n
    return 20 * np.log10(np.sqrt(np.mean(x[:k * n].reshape(k, n) ** 2, axis=1)) + 1e-9)


def segment(x):
    """The exact part of a raw take that goes into the file: LEAD before first sound, TAIL after last."""
    e = env_db(x); thr = max(np.percentile(e, 10) + 12, -50)
    loud = np.nonzero(e > thr)[0]; n = int(SR * 0.01)
    a = max(0, loud[0] * n - int(SR * LEAD)); b = min(len(x), (loud[-1] + 1) * n + int(SR * TAIL))
    return x[a:b]


def margins(x):
    """Actual kept lead/tail (s) of a raw take's segment, and RMS of those edges (what the joins touch)."""
    e = env_db(x); thr = max(np.percentile(e, 10) + 12, -50)
    loud = np.nonzero(e > thr)[0]; n = int(SR * 0.01)
    on, off = loud[0] * n, (loud[-1] + 1) * n
    a = max(0, on - int(SR * LEAD)); b = min(len(x), off + int(SR * TAIL))
    rms = lambda y: float(np.sqrt(np.mean(y ** 2))) if len(y) > 120 else None
    tail = rms(x[off + int(SR * 0.08):b])  # past the decay of the last sound
    lead = rms(x[a:max(a, on - int(SR * 0.02))])
    return (on - a) / SR, (b - off) / SR, lead, tail


def final_fall(seg):
    """Pitch movement (semitones) over the last ~1.2 s: median of the last fifth vs the first half. None if unvoiced."""
    import librosa
    e2 = env_db(seg); end_i = np.nonzero(e2 > -40)[0][-1] * 240
    f0 = librosa.pyin(seg[max(0, end_i - int(1.2 * SR)):end_i], fmin=60, fmax=300, sr=SR,
                      frame_length=1024, hop_length=240)[0]
    v = f0[~np.isnan(f0)]
    if len(v) < 10: return None
    q = 12 * np.log2(v / np.median(v))
    return float(np.median(q[-max(5, len(q) // 5):]) - np.median(q[:len(q) // 2]))


def check(scenes):
    import scipy.signal as ss
    from faster_whisper import WhisperModel
    st, m = load_state(), WhisperModel(CFG["whisper_model"], device="cpu", compute_type="int8")
    pl = plan(scenes); ids = {c["id"] for c in pl}
    para_last = {c["id"]: not any(d["scene"] == c["scene"] and d["para"] == c["para"] and d["id"] > c["id"] for d in pl)
                 for c in pl if c["kind"] != "step"}
    to16 = lambda y: ss.resample_poly(y, 2, 3).astype(np.float32)
    pad = lambda y: np.concatenate([np.zeros(4800, np.float32), y, np.zeros(4800, np.float32)])
    alone = lambda y: " ".join(g.text for g in m.transcribe(to16(pad(y)), beam_size=5, condition_on_previous_text=False)[0]).strip()
    sub = lambda q, xs: any(xs[i:i + len(q)] == q for i in range(len(xs) - len(q) + 1))
    for rec in st.values():
        if rec["id"] not in ids: continue
        for t in rec["takes"]:
            if "ok" in t: continue
            raw, _ = sf.read(t["path"], dtype="float32")
            seg = segment(raw)
            heard = " ".join(s.text for s in m.transcribe(to16(seg), initial_prompt=CFG["prompt"] or None, beam_size=5)[0]).strip()
            ref, hyp = toks(rec["text"]), toks(heard)
            ratio = difflib.SequenceMatcher(None, ref, hyp, autojunk=False).ratio()
            e = env_db(raw); drop = float(np.mean(e[-3:]) - np.percentile(e, 90))
            t["first_alone"] = alone(seg[:int(SR * 1.2)])         # first word heard ALONE
            first_ok = toks(t["first_alone"])[:1] == ref[:1] and hyp[:1] == ref[:1]
            cut, rel_ms, _ = release.release_cut(seg)            # model stopped mid-release
            t["release_ms"] = rel_ms
            end_ok = hyp[-2:] == ref[-2:] and not cut
            if rec["kind"] == "step": end_ok = end_ok and rel_ms is not None and rel_ms >= 100  # "operati" was 70 ms
            t["end_alone"] = alone(seg[-int(SR * 1.5):])         # last word heard ALONE
            end_ok = end_ok and toks(t["end_alone"])[-1:] == ref[-1:]
            fall = final_fall(seg) if para_last.get(rec["id"]) else None
            if para_last.get(rec["id"]): end_ok = end_ok and fall is not None and fall <= -3
            t["final_fall_st"] = None if fall is None else round(fall, 1)
            missing = [w for w in CFG["watch"] if sub(toks(w), ref) and not sub(toks(w), hyp)]
            plain_w = [w for w in CFG["watch_plain"] if sub(toks(w), ref)]
            if plain_w:  # short function words: must survive an UNPROMPTED transcription
                t["heard_plain"] = " ".join(g.text for g in m.transcribe(to16(seg), beam_size=5, condition_on_previous_text=False)[0]).strip()
                missing += [f"plain:{w}" for w in plain_w
                            if not sub(toks(w), toks(t["heard_plain"].replace("-", "").replace(".", "")))]  # "S-Q-L" == "SQL"
            t.update(heard=heard, ratio=round(ratio, 3), first_ok=first_ok, end_ok=end_ok, end_drop_db=round(drop, 1),
                     watch_missing=missing,
                     ok=bool(ratio >= 0.93 and first_ok and end_ok and drop < -25 and not missing))
            print(f"{rec['id']} s{t['seed']} ratio={ratio:.2f} missing={missing} fall={t['final_fall_st']} rel={rel_ms} "
                  f"first={first_ok} end={end_ok} drop={drop:.0f}dB {'OK' if t['ok'] else 'RETRY'} | "
                  f"alone={t['first_alone']!r} end_alone={t['end_alone']!r} | {heard}", flush=True)
            save_state(st)


def pick(rec):
    oks = [t for t in rec["takes"] if t.get("ok")]
    return oks[0] if oks else max(rec["takes"], key=lambda t: (t["first_ok"], t["end_ok"], t["ratio"]))


def map_words(expected, aligned, offset):
    """Script words with times from the aligner's words (equal runs 1:1, others spread evenly)."""
    rec = [w for w in aligned if norm(w["word"])]
    ref, hyp = [norm(w) for w in expected], [norm(w["word"]) for w in rec]
    res = []
    for tag, a, b, c, d in difflib.SequenceMatcher(None, ref, hyp, autojunk=False).get_opcodes():
        if b == a: continue
        s0, s1 = float(rec[c]["start"]), float(rec[max(c, d - 1)]["end"])
        for i, w in enumerate(expected[a:b]):
            if b - a == d - c: s, e = float(rec[c + i]["start"]), float(rec[c + i]["end"])
            else: s, e = s0 + (s1 - s0) * i / (b - a), s0 + (s1 - s0) * (i + 1) / (b - a)
            res.append({"word": w, "start": round(offset + s, 3), "end": round(offset + e, 3)})
    assert len(res) == len(expected)
    return res


def noise_bed(segs, seconds, rng, lv0=None, lv1=None):
    """Stationary noise with the spectrum and level of the quietest frames of the voice (its hiss)."""
    n = 1024
    f = np.concatenate([np.lib.stride_tricks.sliding_window_view(x, n)[::n // 2] for x in segs])
    rms = np.sqrt((f ** 2).mean(1))
    quiet = f[rms <= np.percentile(rms, 10)]
    spec = np.sqrt((np.abs(np.fft.rfft(quiet * np.hanning(n), axis=1)) ** 2).mean(0))
    floor_rms = float(np.sqrt((quiet ** 2).mean()))
    L = int(SR * seconds)
    X = np.fft.rfft(rng.standard_normal(L)) * np.interp(np.linspace(0, 1, L // 2 + 1), np.linspace(0, 1, len(spec)), spec)
    y = np.fft.irfft(X, L)
    y = y / np.sqrt((y ** 2).mean())
    g = np.linspace(lv0 or floor_rms, lv1 or lv0 or floor_rms, L)  # ramp from previous edge level to next
    return (y * g).astype(np.float32), floor_rms


def append_xf(acc, seg):
    """Equal-power 25 ms crossfade; returns new array and the start index of seg in it."""
    k = int(SR * XF); t = np.linspace(0, np.pi / 2, k, dtype=np.float32)
    mid = acc[-k:] * np.cos(t) + seg[:k] * np.sin(t)
    return np.concatenate([acc[:-k], mid, seg[k:]]), len(acc) - k


def whisper_aligner():
    from faster_whisper import WhisperModel
    from faster_whisper.audio import pad_or_trim
    from faster_whisper.tokenizer import Tokenizer
    import scipy.signal as ss
    m = WhisperModel(CFG["whisper_model"], device="cpu", compute_type="int8")
    tok = Tokenizer(m.hf_tokenizer, m.model.is_multilingual, task="transcribe", language="en")

    def align(seg, text, offset_s):
        x16 = ss.resample_poly(seg, 2, 3).astype(np.float32); feats = m.feature_extractor(x16)
        al = m.find_alignment(tok, [tok.encode(" " + text)], m.encode(pad_or_trim(feats)), feats.shape[-1])[0]
        return map_words(text.split(), al, offset_s)
    return m, align


def build(scenes, tag):
    import scipy.signal as ss
    st, chunks = load_state(), plan(scenes)
    m, align = whisper_aligner()
    for s in scenes:
        cs = [c for c in chunks if c["scene"] == s]
        picks = [pick(st[key(c)]) for c in cs]
        raws = [sf.read(t["path"], dtype="float32")[0] for t in picks]
        segs, marg = [segment(r) for r in raws], [margins(r) for r in raws]
        rng = np.random.default_rng(s)
        _, floor = noise_bed(segs, 1, rng)
        acc, words, used = None, [], []
        for i, (c, t, seg) in enumerate(zip(cs, picks, segs)):
            if acc is None: acc, start = seg.copy(), 0
            else: acc, start = append_xf(acc, seg)
            words += align(seg, c["text"], start / SR)
            used.append({"chunk": c["id"], "kind": c["kind"], "take": t["path"], "ok": t["ok"], "heard": t["heard"],
                         "first_ok": t["first_ok"], "end_ok": t["end_ok"], "start_s": round(start / SR, 3)})
            if i + 1 < len(cs):
                kind = "para" if cs[i + 1]["para"] != c["para"] else c["kind"]
                tail_s, lead_s = marg[i][1], marg[i + 1][0]
                lv0, lv1 = marg[i][3], marg[i + 1][2] or marg[i + 1][3]
                bed, _ = noise_bed(segs, max(CFG["pause"][kind] - tail_s - lead_s, 0.06) + 2 * XF, rng, lv0, lv1)
                acc, _ = append_xf(acc, bed)
        take, wj, sj = out(f"scene{s:02d}_{tag}_pre.wav"), out(f"scene{s:02d}_{tag}_pre.words.json"), out(f"scene{s:02d}_{tag}_pre.summary.json")
        for p in (take, wj, sj): assert not p.exists(), f"exists, not overwriting: {p}"
        sf.write(take, acc, SR, subtype="PCM_24"); wj.write_text(json.dumps(words, indent=1))
        heard = " ".join(g.text for g in m.transcribe(ss.resample_poly(acc, 2, 3).astype(np.float32),
                                                      initial_prompt=CFG["prompt"] or None, beam_size=5)[0])
        ref = toks(" ".join(c["text"] for c in cs)); hyp = toks(heard)
        diffs = [(tg, ref[a:b], hyp[c:d]) for tg, a, b, c, d in
                 difflib.SequenceMatcher(None, ref, hyp, autojunk=False).get_opcodes() if tg != "equal"]
        summary = {"scene": s, "take": str(take), "words": str(wj), "duration_s": round(len(acc) / SR, 3),
                   "frames": len(acc), "noise_floor_dbfs_rms": round(20 * np.log10(floor), 1),
                   "full_file_stt_diffs": diffs, "chunks": used}
        sj.write_text(json.dumps(summary, indent=1))
        print(json.dumps({k: v for k, v in summary.items() if k != "chunks"}), flush=True)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("cmd", choices=["gen", "check", "build"])
    ap.add_argument("--config", required=True)
    ap.add_argument("--scenes", required=True, help="comma list, e.g. 1,2,3")
    ap.add_argument("--tag", default="v1", help="build: version tag of the output files")
    a = ap.parse_args()
    configure(a.config)
    sc = [int(x) for x in a.scenes.split(",")]
    {"gen": lambda: gen(sc), "check": lambda: check(sc), "build": lambda: build(sc, a.tag)}[a.cmd]()
