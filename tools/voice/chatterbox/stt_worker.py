"""Persistent local Whisper checker and known-text aligner (runs in the Whisper venv), driven by drive.py.

Protocol: one JSON request per stdin line, one JSON answer per stdout line.
  {"op": "check", "path": a.wav, "text": "...", "prompt": "hint"} -> {"heard": "...", "edits": [[tag, expected, heard], ...]}
  {"op": "align", "path": a.wav, "text": "..."}                    -> {"words": [{word, start, end}, ...]}
Harmless spellings are normalised before comparing: digits and ordinals as words (num2words), "10%" as
"ten percent", "request1" as "request one", "A I"/"A.I." as "AI", and the SAME table (name spellings).
Model: WHISPER_MODEL env (default medium.en), CPU int8."""

import difflib
import json
import os
import re
import sys

import soundfile as sf
from num2words import num2words
from scipy.signal import resample_poly
from faster_whisper import WhisperModel
from faster_whisper.audio import pad_or_trim
from faster_whisper.tokenizer import Tokenizer


# Spellings Whisper writes for the same spoken word; anything else is a real difference.
# Edit per project: e.g. a made-up name sent to the model as "Jehv" that Whisper writes several ways.
SAME = {"1": "one", "2": "two", "3": "three", "4": "four", "6": "six", "10": "ten",
        "jev": "jehv", "jeff": "jehv", "jhev": "jehv"}


def norm(word):
    word = re.sub(r"[^a-z0-9']", "", word.lower()).strip("'")
    return SAME.get(word, word)


def normalized_stream(text):
    text = re.sub(r"\bA\.?\s?I\b\.?", "AI", text)          # "A I", "A.I.", "AI" are one word
    text = re.sub(r"(\d+)\s?%", r"\1 percent", text)       # "10%" is "ten percent"
    text = re.sub(r"\b(\d+)(?:st|nd|rd|th)\b", lambda m: num2words(int(m.group(1)), to="ordinal"), text)  # "1st" is "first"
    text = re.sub(r"(?<=[A-Za-z])(?=\d)|(?<=\d)(?=[A-Za-z])", " ", text)  # "request1" is "request one"
    text = re.sub(r"\d+", lambda m: num2words(int(m.group())), text)   # "682" is "six hundred and eighty-two"
    return [norm(w) for w in re.findall(r"[A-Za-z0-9]+(?:'[A-Za-z0-9]+)?", text)]


def word_map(expected, aligned):
    key = lambda w: re.sub(r"[^a-z0-9]", "", w.lower())
    heard = [x for x in aligned if key(x["word"])]
    ops = difflib.SequenceMatcher(None, [key(x) for x in expected],
                                  [key(x["word"]) for x in heard], autojunk=False).get_opcodes()
    words = []
    for _, a, b, c, d in ops:
        if b == a:
            continue
        if d == c:
            raise ValueError(f"No timing for {expected[a:b]}")
        if b - a == d - c:
            for source, timing in zip(expected[a:b], heard[c:d]):
                words.append({"word": source, "start": round(float(timing["start"]), 3),
                              "end": round(float(timing["end"]), 3)})
        else:
            start, end = float(heard[c]["start"]), float(heard[d - 1]["end"])
            for i, source in enumerate(expected[a:b]):
                words.append({"word": source, "start": round(start + (end - start) * i / (b - a), 3),
                              "end": round(start + (end - start) * (i + 1) / (b - a), 3)})
    if len(words) != len(expected):
        raise ValueError(f"Aligned {len(words)} of {len(expected)} words")
    return words


def main():
    model = WhisperModel(os.environ.get("WHISPER_MODEL", "medium.en"), device="cpu", compute_type="int8")
    tokenizer = Tokenizer(model.hf_tokenizer, multilingual=model.model.is_multilingual,
                          task="transcribe", language="en")
    print(json.dumps({"ready": True}), flush=True)
    for line in sys.stdin:
        try:
            request = json.loads(line)
            audio, sr = sf.read(request["path"], dtype="float32")
            assert sr == 24000 and audio.ndim == 1
            audio16 = resample_poly(audio, 2, 3).astype("float32")
            if request["op"] == "check":
                segments, _ = model.transcribe(audio16, beam_size=5, vad_filter=False,
                                                initial_prompt=request.get("prompt"))
                heard_text = " ".join(segment.text for segment in segments).strip()
                expected, heard = normalized_stream(request["text"]), normalized_stream(heard_text)
                ops = [(tag, expected[a:b], heard[c:d])
                       for tag, a, b, c, d in difflib.SequenceMatcher(
                           None, expected, heard, autojunk=False).get_opcodes() if tag != "equal"]
                answer = {"heard": heard_text, "edits": ops}
            elif request["op"] == "align":
                features = model.feature_extractor(audio16)
                encoder = model.encode(pad_or_trim(features))
                tokens = tokenizer.encode(" " + request["text"])
                aligned = model.find_alignment(tokenizer, [tokens], encoder, features.shape[-1])[0]
                answer = {"words": word_map(request["text"].split(), aligned)}
            else:
                raise ValueError(request["op"])
            print(json.dumps(answer), flush=True)
        except Exception as error:
            print(json.dumps({"error": repr(error)}), flush=True)


if __name__ == "__main__":
    main()
