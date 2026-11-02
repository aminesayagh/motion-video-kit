# 7. Gates catalog

Reusable checks for briefs. Each has a command and what to expect. Paths are examples. Run the heavy ones (Whisper, film gates, PSNR on the film) one at a time.

## Files and format

**Exists, size, no overwrite**
```bash
ls -la out/voice/scene05_v1.wav out/voice/scene05_v1.words.json
```
EXPECT: both exist; the version name is new (the brief names the previous ones that must stay untouched).

**Duration and sample count**
```bash
ffprobe -v error -show_entries stream=sample_rate,channels,duration_ts:format=duration -of default=nw=1 out/sound/scene05_master_C.wav
```
EXPECT: `duration_ts` (frames) equal to the take's; 24000 Hz; 2 channels for a master.

**Video format and frame count**
```bash
ffprobe -v error -select_streams v:0 -count_packets -show_entries stream=codec_name,width,height,r_frame_rate,nb_read_packets -of csv=p=0 preview.mp4
```
EXPECT: `h264,1280,720,30/1,<frames>` for a preview; `1920,1080` for a final render.

## Loudness

**Integrated loudness and true peak**
```bash
ffmpeg -hide_banner -nostats -i master.wav -af ebur128=peak=true -f null - 2>&1 | grep -A12 Summary
```
EXPECT (scene master): I between -18.3 and -17.7 LUFS, Peak ≤ -1.0 dBFS. (Film): I -16.0 ± 0.5, Peak ≤ -1.5.

**Pauses on target** (scene master)
```bash
python tools/sound/master_gates.py --take take.wav C=master_C.wav
```
EXPECT: pauses median ≈ -75 dBFS, most "within 3 dB of -75"; voiced band differences < 1 dB.

## Audio identity

**The preview carries the right soundtrack** (correlation of the first 20 s, 8 kHz mono)
```bash
python3 - <<'EOF'
import subprocess, numpy as np
from scipy.signal import correlate
def dec(p): return np.frombuffer(subprocess.run(["ffmpeg","-v","error","-t","20","-i",p,"-map","a:0","-ac","1","-ar","8000","-f","f32le","-"],capture_output=True,check=True).stdout,np.float32)
a, b = dec("preview/s05_v1.mp4"), dec("out/sound/scene05_master_C.wav"); n = min(len(a), len(b)); a, b = a[:n]-a[:n].mean(), b[:n]-b[:n].mean()
c = correlate(a, b, "full", method="fft"); L = 2400; k = int(np.argmax(c[n-1-L:n+L])) - L
x, y = (a[k:], b[:n-k]) if k >= 0 else (a[:n+k], b[-k:])
print("r", round(float(x@y/np.sqrt((x@x)*(y@y))), 5), "lag", k)
EOF
```
EXPECT: r ≥ 0.99, lag 0 (± a few samples for an AAC encode).

**A repair changed nothing it shouldn't** (sample-exact prefix)
```bash
python3 -c "import soundfile as sf, numpy as np; a=sf.read('scene09_v9.wav')[0]; b=sf.read('scene09_v10.wav')[0]; n=int(118.2*24000); print(np.array_equal(a[:n], b[:n]))"
```
EXPECT: True.

## Words

**Every word heard** (Whisper on the full file, with a hint prompt; listen at each difference)
```bash
python3 - <<'EOF'
import difflib, re
from faster_whisper import WhisperModel
m = WhisperModel("medium.en", device="cpu", compute_type="int8")
text = open("examples/orbitrows/narration/scene05.txt").read()
heard = " ".join(s.text for s in m.transcribe("out/voice/scene05_v1.wav", initial_prompt="Jev, Casa, SQLite", beam_size=5)[0])
t = lambda s: re.sub(r"[^a-z0-9 ]", " ", s.lower().replace("-", " ")).split()
for op in difflib.SequenceMatcher(None, t(text), t(heard), autojunk=False).get_opcodes():
    if op[0] != "equal": print(op[0], t(text)[op[1]:op[2]], "->", t(heard)[op[3]:op[4]])
EOF
```
EXPECT: no differences, or only spellings (digits, name variants) the brief lists as accepted. `tools/voice/final_check.py` does this with timestamps and number normalisation.

**Same words before and after processing** (master vs take): run the block above on both files; EXPECT the same word list.

**Word times valid**
```bash
python3 -c "import json; w=json.load(open('scene05_v1.words.json')); print(len(w), all(a['start']<=a['end']<=b['start']+1e-3 for a,b in zip(w,w[1:])), w[-1]['end'])"
```
EXPECT: the script's word count, True, last end < the file's duration.

## Voice take quality

**No dead silence, endings released** (`final_check.py`)
```bash
python tools/voice/final_check.py --config voice.json --scene 5 --tag v1
```
EXPECT: `len_equal: true`, `dead_runs_left: 0`, `chunks_not_ok: []` (or each listed with a time to listen to), every paragraph fall ≤ -3 st.

## Picture

**Element present at its cue** (a frame 0.2–0.3 s after the cue word, one before)
```bash
effectcraft-cli --project P.ecproj render-frame --comp "S05 v1" --time 31.58 --out /tmp/check_after.png
```
EXPECT: look at it; the element is there (and absent in the frame before the cue).

**SVG side by side** (render a storyboard screen to PNG for comparison)
```bash
google-chrome --headless=new --no-sandbox --screenshot=s5_03.png --window-size=960,540 file:///abs/storyboard/v1_scene05/s5_03.svg
```

**Cuts land on the right frame** (PSNR of one frame, film vs the scene's own render)
```bash
ffmpeg -hide_banner -ss 239.7167 -i film.mp4 -ss 0.5167 -i scene05_1080.mp4 -lavfi "[0:v][1:v]psnr" -frames:v 1 -f null - 2>&1 | grep -o "average:[^ ]*"
```
EXPECT: > 40 dB (identical frames after two encodes give 55–70 dB).

**Two frames identical** (nothing moved that shouldn't)
```bash
ffmpeg -v error -i a.png -i b.png -lavfi "[0][1]psnr" -f null - 2>&1 | grep -o "average:[^ ]*"
```
EXPECT: `average:inf` for pixel-identical stills.

## Film

All at once (G1 format, G2 voice lock per scene, G3 loudness, G4 music under voice, G5 join, G6 PSNR per cut):
```bash
python tools/sound/film_gates.py --film film.mp4 --layout layout.json --voice voice.wav --bed bed_ducked.wav \
  --mix mix.wav --renders out/1080/scene0*_1080.mp4 --out gates.json
```
EXPECT: every line PASS. Run it alone: it reads the full film audio into memory.

**No click at a join** (largest sample step within ±20 ms vs the median step): part of G5 above; EXPECT the two of the same order.

## Repository hygiene (for this kit)

```bash
python3 -m py_compile $(git ls-files '*.py')                        # no errors
for f in $(git ls-files 'tools/*.js'); do node --check "$f"; done   # no errors
grep -rIl "/home/" tools templates                                   # nothing
```
