"""Chatterbox narration of one scene in phases (the engine used before Qwen3-TTS; kept for its method).

  python drive.py --text scene06.txt --out out/cb/scene06_v1.wav \
      --cb-python .venv-cb/bin/python --stt-python .venv/bin/python [--hint "Step five: parameter. September."]

Recipe (approved for this engine): default voice, torch.manual_seed(seed) before each chunk,
generate(chunk, exaggeration=0.4, cfg_weight=0.1), each paragraph cut at sentence ends into chunks of up to
300 characters joined with no gap, 0.6 s of silence between paragraphs, 24 kHz PCM 16.

Why phases: Chatterbox (~4 GB) and Whisper (~1.6 GB) loaded together made a shared 15 GB machine page heavily.
Per seed round, gen.py generates every chunk still failing and EXITS, then the Whisper worker checks them all.
Each attempt is seeded alone, so the audio is the same as checking right after each generation.
Check rule: a chunk passes when Whisper, given --hint (the scene's unusual words), hears every word; otherwise
seeds 1, 2, 3; then the attempt with the fewest wrong words is used and FLAGGED for a human listen.
Writes <out>, <out>.aligned.words.json (known-text alignment per chunk, offset by sample position) and
<out>.checks.json (every attempt with what Whisper heard). Never overwrites.
"""
import argparse, json, re, subprocess
from pathlib import Path

import numpy as np
import soundfile as sf

HERE = Path(__file__).resolve().parent
SR = 24000
GAP = np.zeros(round(0.6 * SR), dtype=np.int16)
SPOKEN = {"Jev": "Jehv"}   # display -> spoken (edit per project); chunks are cut on the spoken text


def chunks(text, limit=300):
    res, buf = [], ""
    for sentence in re.split(r"(?<=[.?!])\s+", text):
        if buf and len(buf) + len(sentence) > limit:
            res.append(buf); buf = sentence
        else:
            buf = f"{buf} {sentence}".strip()
    return res + [buf]


def chunk_texts(paragraphs):
    """{(p, c): (display, spoken)}."""
    res = {}
    for pi, paragraph in enumerate(paragraphs, 1):
        spoken_p = paragraph
        for k, v in SPOKEN.items(): spoken_p = spoken_p.replace(k, v)
        for ci, spoken in enumerate(chunks(spoken_p), 1):
            display = spoken
            for k, v in SPOKEN.items(): display = display.replace(v, k)
            res[(pi, ci)] = (display, spoken)
    return res


def read16(path):
    audio, sr = sf.read(path, dtype="int16")
    assert sr == SR and audio.ndim == 1, path
    return audio


class Worker:
    def __init__(self, python, log):
        self.python, self.log_path = python, log

    def __enter__(self):
        self.log = open(self.log_path, "a")
        self.proc = subprocess.Popen([self.python, "-u", str(HERE / "stt_worker.py")], stdin=subprocess.PIPE,
                                     stdout=subprocess.PIPE, stderr=self.log, text=True, bufsize=1)
        assert json.loads(self.proc.stdout.readline()).get("ready")
        return self

    def ask(self, payload):
        self.proc.stdin.write(json.dumps(payload) + "\n"); self.proc.stdin.flush()
        line = self.proc.stdout.readline()
        if not line: raise RuntimeError("Whisper worker exited")
        answer = json.loads(line)
        if "error" in answer: raise RuntimeError(answer["error"])
        return answer

    def __exit__(self, *exc):
        self.proc.stdin.close(); self.proc.wait(timeout=60); self.log.close()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--text", required=True); ap.add_argument("--out", required=True)
    ap.add_argument("--cb-python", required=True); ap.add_argument("--stt-python", required=True)
    ap.add_argument("--hint", default=None); ap.add_argument("--seeds", type=int, default=4)
    a = ap.parse_args()
    take = Path(a.out).resolve(); parts = take.with_name(take.stem + "_chunks")
    words_p, checks_p = take.with_suffix(".aligned.words.json"), take.with_name(take.stem + ".checks.json")
    for p in (take, words_p, checks_p): assert not p.exists(), f"exists, not overwriting: {p}"
    parts.mkdir(parents=True, exist_ok=True)
    worker = lambda: Worker(a.stt_python, take.with_name(take.stem + ".stt_worker.log"))
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", Path(a.text).read_text().strip())]
    new = chunk_texts(paragraphs)
    path_of = lambda key, seed: parts / f"p{key[0]}_c{key[1]}_seed{seed}.wav"

    attempts, chosen = {key: [] for key in new}, {}
    for seed in range(a.seeds):
        todo = [key for key in new if key not in chosen]
        if not todo: break
        jobs = parts / f"jobs_seed{seed}.json"
        jobs.write_text(json.dumps([{"spoken": new[k][1], "seed": seed, "path": str(path_of(k, seed))} for k in todo], indent=2))
        subprocess.run([a.cb_python, "-u", str(HERE / "gen.py"), str(jobs)], check=True)
        with worker() as w:
            for key in todo:
                spoken, path = new[key][1], path_of(key, seed)
                chk = w.ask({"op": "check", "path": str(path), "text": spoken, "prompt": a.hint})
                ok = not chk["edits"]
                attempts[key].append({"path": str(path), "seed": seed, "sent": spoken, "heard": chk["heard"],
                                      "edits": chk["edits"], "duration": round(len(read16(path)) / SR, 3), "pass": ok})
                print(f"p{key[0]} c{key[1]} seed{seed}: pass={ok} edits={chk['edits']} | {chk['heard']}", flush=True)
                if ok: chosen[key] = attempts[key][-1]

    record, audio_of = {"take": str(take), "chunks": []}, {}
    cost = lambda edits: sum(max(len(x), len(y)) for _, x, y in edits)
    with worker() as w:
        for key, (display, spoken) in new.items():
            flagged = key not in chosen
            if flagged: chosen[key] = min(attempts[key], key=lambda t: cost(t["edits"]))
            c = chosen[key]; audio_of[key] = read16(c["path"])
            record["chunks"].append({"paragraph": key[0], "chunk": key[1], "display": display, "source": c["path"],
                                     "seed": c["seed"], "sent": c["sent"], "flagged": flagged, "attempts": attempts[key]})
        seq, last_p = [], None
        for key in new:
            if last_p is not None and key[0] != last_p: seq.append(GAP)
            seq.append(audio_of[key]); last_p = key[0]
        full = np.concatenate(seq)
        sf.write(take, full, SR, subtype="PCM_16")
        words, offset, last_p = [], 0, None
        for key, entry in zip(new, record["chunks"]):
            if last_p is not None and key[0] != last_p: offset += len(GAP)
            for x in w.ask({"op": "align", "path": entry["source"], "text": entry["display"]})["words"]:
                words.append({"word": x["word"], "start": round(x["start"] + offset / SR, 3), "end": round(x["end"] + offset / SR, 3)})
            offset += len(audio_of[key]); last_p = key[0]
        assert offset == len(full)
        words_p.write_text(json.dumps(words, indent=2) + "\n")
        spoken_all = " ".join(e["sent"] for e in record["chunks"])
        final = w.ask({"op": "check", "path": str(take), "text": spoken_all, "prompt": a.hint})
        plain = w.ask({"op": "check", "path": str(take), "text": spoken_all})      # for information only
    record.update(final_heard=final["heard"], final_edits=final["edits"], final_hint=a.hint,
                  final_edits_without_hint=plain["edits"], duration=round(len(full) / SR, 3), frames=len(full))
    checks_p.write_text(json.dumps(record, indent=2) + "\n")
    print(f"{take.name}: {len(full) / SR:.3f}s, {len(words)} words, final edits={final['edits']}", flush=True)


if __name__ == "__main__":
    main()
