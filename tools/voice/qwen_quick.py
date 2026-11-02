"""Quick narration from a storybook, one script (the first Qwen3-TTS pipeline: good for a first listen).

  python qwen_quick.py --story storybook.md --voice voice/reference --out out/quick generate [--scenes 1,2]
  python qwen_quick.py --story storybook.md --voice voice/reference --out out/quick regenerate --chunk scene_03_chunk_02
  python qwen_quick.py --story storybook.md --voice voice/reference --out out/quick check      # Whisper screening (CPU)

The storybook is Markdown: "# Scene N · Title" starts a scene and the paragraphs under "## Narration" are spoken.
--voice is a folder with reference.wav (a clean clip, 10-15 s, one speaker) and reference.txt (its exact words).
Generation resumes: a chunk is redone only when its text, the voice or the settings changed (hash in state.json).
For the final takes use qwen_takes.py: it checks each take far more strictly (first/last word alone, release,
falling close) and fills pauses with matched hiss instead of digital silence.
"""
import argparse, hashlib, json, re, sys, time
from pathlib import Path

import numpy as np
import soundfile as sf

STORY = VOICE = OUT = None   # set from the command line
MODEL = "Qwen/Qwen3-TTS-12Hz-0.6B-Base"
LANG = "English"
SETTINGS = dict(temperature=0.8, top_k=50, repetition_penalty=1.05)
MAX_CHARS = 260          # group sentences up to this length (tuning choice, plan step 9)
PAUSE_SENT, PAUSE_PARA = 0.35, 0.7  # seconds of silence between chunks / paragraphs
# Written form -> spoken form. The on-screen script stays untouched (plan step 14).
SPOKEN = {"AI tools": "A.I. tools", "GLiNER2": "Gliner two"}  # example entries


def load_scenes():
    """Narration paragraphs per scene from the storybook."""
    scenes, cur, in_narr = [], None, False
    for line in STORY.read_text().splitlines():
        m = re.match(r"# Scene (\d+) · (.+)", line)
        if m:
            cur = {"id": f"scene_{int(m[1]):02d}", "title": m[2], "paragraphs": []}
            scenes.append(cur); in_narr = False
        elif line.startswith("## "):
            in_narr = line.strip() == "## Narration"
        elif in_narr and cur and line.strip():
            cur["paragraphs"].append(line.strip())
    return scenes


def segment(scene):
    # ponytail: regex sentence split; storybook has no abbreviations like "e.g." — revisit if it gains them
    chunks = []
    for p in scene["paragraphs"]:
        sents = re.split(r"(?<=[.?!])\s+(?=[A-Z\"'])", p)
        group = ""
        for s in sents:
            if group and len(group) + len(s) + 1 > MAX_CHARS:
                chunks.append({"text": group, "pause": PAUSE_SENT}); group = s
            else:
                group = f"{group} {s}".strip()
        chunks.append({"text": group, "pause": PAUSE_PARA})
    for i, c in enumerate(chunks, 1):
        c["id"] = f"{scene['id']}_chunk_{i:02d}"
        spoken = c["text"]
        for k, v in SPOKEN.items():
            spoken = spoken.replace(k, v)
        c["spoken"] = spoken
        c["long"] = len(c["text"]) > MAX_CHARS  # single over-long sentence: flagged, not split blindly
    return chunks


def chunk_hash(spoken):
    ref = (VOICE / "reference.wav").read_bytes() + (VOICE / "reference.txt").read_bytes()
    key = json.dumps([spoken, MODEL, LANG, SETTINGS]).encode() + hashlib.sha256(ref).digest()
    return hashlib.sha256(key).hexdigest()[:16]


def check_audio(wav, sr, text):
    """Basic checks (plan step 16). Returns list of flags."""
    flags, dur = [], len(wav) / sr
    words = len(text.split())
    if dur == 0: return ["empty"]
    if np.sqrt(np.mean(wav ** 2)) < 0.005: flags.append("silent")
    if np.mean(np.abs(wav) > 0.99) > 0.001: flags.append("clipping")
    wps = words / dur
    if wps > 4.5: flags.append(f"too_fast({wps:.1f} w/s, words may be missing)")
    if wps < 1.4: flags.append(f"too_slow({wps:.1f} w/s, possible stall/repeat)")
    return flags


class Engine:
    def __init__(self):
        import torch
        from qwen_tts import Qwen3TTSModel
        t = time.time()
        self.tts = Qwen3TTSModel.from_pretrained(MODEL, device_map="cuda:0", dtype=torch.bfloat16)
        self.prompt = self.tts.create_voice_clone_prompt(  # reused for every chunk (plan step 15)
            ref_audio=str(VOICE / "reference.wav"), ref_text=(VOICE / "reference.txt").read_text())
        self.load_s = time.time() - t
        self.torch = torch

    def say(self, text):
        # 12 codec frames/s; ~15 chars/s of speech -> ~0.8 frames/char; 2x headroom stops runaway generations
        limit = int(len(text) * 1.6) + 80
        wavs, sr = self.tts.generate_voice_clone(text=text, language=LANG, voice_clone_prompt=self.prompt,
                                                 max_new_tokens=limit, **SETTINGS)
        return wavs[0].astype(np.float32), sr


def gen_chunk(eng, c, attempts=3):
    """Generate one chunk, retrying when checks flag it. Returns record."""
    best = None
    for a in range(1, attempts + 1):
        t = time.time()
        wav, sr = eng.say(c["spoken"])
        gt = time.time() - t
        flags = check_audio(wav, sr, c["spoken"])
        rec = {"attempts": a, "gen_s": round(gt, 2), "dur_s": round(len(wav) / sr, 2), "flags": flags}
        if best is None or len(flags) < len(best[2]["flags"]):
            best = (wav, sr, rec)
        if not flags:
            break
    wav, sr, rec = best
    rec["gen_s"] = rec["gen_s"]
    return wav, sr, rec


def assemble(scene_id, chunks, state):
    parts, sr = [], 24000
    for c in chunks:
        wav, sr = sf.read(OUT / "chunks" / f"{c['id']}.wav", dtype="float32")
        parts += [wav, np.zeros(int(sr * c["pause"]), np.float32)]
    full = np.concatenate(parts[:-1])  # drop trailing pause
    path = OUT / "scenes" / f"{scene_id}.wav"
    sf.write(path, full, sr)
    return round(len(full) / sr, 2)


def run(args):
    (OUT / "chunks").mkdir(parents=True, exist_ok=True); (OUT / "scenes").mkdir(exist_ok=True)
    state_p = OUT / "state.json"
    state = json.loads(state_p.read_text()) if state_p.exists() else {}
    scenes = load_scenes()
    want = {f"scene_{int(s):02d}" for s in args.scenes.split(",")} if getattr(args, "scenes", None) else None
    eng, t0, gen_total, audio_total = None, time.time(), 0.0, 0.0
    report = {"model": MODEL, "voice": str(VOICE), "scenes": []}
    for sc in scenes:
        chunks = segment(sc)
        if want and sc["id"] not in want:
            continue
        for c in chunks:
            h = chunk_hash(c["spoken"])
            wav_p = OUT / "chunks" / f"{c['id']}.wav"
            force = args.cmd == "regenerate" and c["id"] == args.chunk
            if not force and wav_p.exists() and state.get(c["id"], {}).get("hash") == h:
                continue
            if args.cmd == "regenerate" and not force:
                continue
            if eng is None:
                eng = Engine(); report["model_load_s"] = round(eng.load_s, 1)
                print(f"model loaded in {eng.load_s:.1f}s", flush=True)
            try:
                wav, sr, rec = gen_chunk(eng, c)
            except Exception as e:  # record and continue; rerun resumes
                state[c["id"]] = {"error": repr(e)}; print(f"{c['id']} ERROR {e!r}", flush=True)
                state_p.write_text(json.dumps(state, indent=1)); continue
            sf.write(wav_p, wav, sr)
            state[c["id"]] = {**rec, "hash": h, "text": c["text"], "spoken": c["spoken"], "long": c["long"]}
            state_p.write_text(json.dumps(state, indent=1))  # save as soon as it succeeds
            gen_total += rec["gen_s"]; audio_total += rec["dur_s"]
            print(f"{c['id']} {rec['dur_s']:5.1f}s audio in {rec['gen_s']:5.1f}s "
                  f"(try {rec['attempts']}) {rec['flags'] or ''}", flush=True)
        ready = all((OUT / "chunks" / f"{c['id']}.wav").exists() and "hash" in state.get(c["id"], {}) for c in chunks)
        entry = {"id": sc["id"], "title": sc["title"], "status": "missing_chunks"}
        if ready:
            review = [c["id"] for c in chunks if state[c["id"]]["flags"] or state[c["id"]]["long"]
                      or state[c["id"]].get("asr_flag")]
            entry.update(audio_file=f"scenes/{sc['id']}.wav",
                         audio_duration_seconds=assemble(sc["id"], chunks, state),
                         status="needs_review" if review else "ready", review_chunks=review)
        report["scenes"].append(entry)
    report["this_run"] = {"wall_s": round(time.time() - t0, 1), "generation_s": round(gen_total, 1),
                          "audio_generated_s": round(audio_total, 1),
                          "real_time_factor": round(gen_total / audio_total, 2) if audio_total else None}
    if eng:
        report["this_run"]["peak_gpu_mb"] = round(eng.torch.cuda.max_memory_allocated() / 2**20)
    # merge with previous report so partial runs keep other scenes' timing
    rp = OUT / "report.json"
    if rp.exists() and want:
        old = {s["id"]: s for s in json.loads(rp.read_text())["scenes"]}
        old.update({s["id"]: s for s in report["scenes"]})
        report["scenes"] = [old[k] for k in sorted(old)]
    rp.write_text(json.dumps(report, indent=1))
    print(json.dumps(report["this_run"]))


def asr_check(_):
    """Optional Whisper screening (plan step 17). A flag means: listen. No flag is not proof."""
    import difflib, scipy.signal as ss
    from faster_whisper import WhisperModel
    state_p = OUT / "state.json"; state = json.loads(state_p.read_text())
    m = WhisperModel("medium.en", device="cpu", compute_type="int8")
    norm = lambda s: re.sub(r"[^a-z0-9 ]", "", s.lower().replace("-", " ")).split()
    for cid, rec in sorted(state.items()):
        if "hash" not in rec: continue
        wav, sr = sf.read(OUT / "chunks" / f"{cid}.wav", dtype="float32")
        heard = " ".join(s.text for s in m.transcribe(ss.resample_poly(wav, 2, 3).astype(np.float32))[0])
        ratio = difflib.SequenceMatcher(None, norm(rec["text"]), norm(heard)).ratio()
        rec["asr_ratio"], rec["asr_heard"] = round(ratio, 3), heard.strip()
        rec["asr_flag"] = ratio < 0.85
        print(f"{cid} {ratio:.2f}{'  <-- listen' if rec['asr_flag'] else ''}", flush=True)
    state_p.write_text(json.dumps(state, indent=1))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--story", required=True); ap.add_argument("--voice", required=True); ap.add_argument("--out", required=True)
    sub = ap.add_subparsers(dest="cmd", required=True)
    g = sub.add_parser("generate"); g.add_argument("--scenes")
    r = sub.add_parser("regenerate"); r.add_argument("--chunk", required=True)
    sub.add_parser("check")
    a = ap.parse_args()
    STORY, VOICE, OUT = Path(a.story), Path(a.voice), Path(a.out)
    asr_check(a) if a.cmd == "check" else run(a)
