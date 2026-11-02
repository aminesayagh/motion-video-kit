"""Chatterbox generation phase (runs in the Chatterbox venv), driven by drive.py. Usage: python gen.py jobs.json

Reads a JSON list of {"spoken", "seed", "path"} and writes each missing attempt with the approved recipe:
torch.manual_seed(seed), generate(spoken, exaggeration=0.4, cfg_weight=0.1), PCM_16 at 24 kHz.
Whisper is not loaded here: on this shared machine both models together exhaust memory. Torch threads are
capped (CB_THREADS, default 6): with the default (51 threads) beside other jobs, sampling fell to 0.4 it/s.
"""

import json
import os
import sys
from pathlib import Path

import soundfile as sf
import torch
from chatterbox.tts import ChatterboxTTS


def main():
    jobs = [j for j in json.loads(Path(sys.argv[1]).read_text()) if not Path(j["path"]).exists()]
    if not jobs:
        return
    torch.set_num_threads(int(os.environ.get("CB_THREADS", "6")))
    model = ChatterboxTTS.from_pretrained(device="cpu")
    assert model.sr == 24000
    for job in jobs:
        torch.manual_seed(job["seed"])
        audio = model.generate(job["spoken"], exaggeration=0.4, cfg_weight=0.1).squeeze().cpu().numpy()
        sf.write(job["path"], audio, 24000, subtype="PCM_16")
        print(f"wrote {job['path']}", flush=True)


if __name__ == "__main__":
    main()
