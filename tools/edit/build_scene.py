"""Build one scene into its own EffectCraft project, then (optionally) render its review stills and 720p preview.

  python build_scene.py --scene templates/code_editor.jsx --words scene08_v1.words.json --audio scene08_master_C.wav \
      --icons icons/ --out build/s08_v1.jsx [--project OrbitRows_s08.ecproj --stills preview/s08_v1 --preview preview/s08_v1.mp4]

Writes one self-contained script: `var WORDS = <words.json>; var ICONS = {...}; var AUDIO = "<full path>";`
+ kit.jsx + the scene file. The scene file reads beat times with cue('phrase') from WORDS, so a new voice
take only needs a rebuild, never a hand edit of times.
With --project: runs `effectcraft-cli script <jsx> <project>` (the scene must end with app.project.save():
a script does NOT save the project by itself), then
  --stills DIR    one 1080p PNG per line `STILL <name> <seconds>` the script printed with writeLn,
  --preview FILE  a 720p H.264 preview with audio (--resolution 0.6666667 of the 1920x1080 comp).
Renders run one at a time, in this process; never start a second effectcraft-cli render beside it.
Never overwrites an output: pick a new version name.
"""
import argparse, glob, json, os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ap = argparse.ArgumentParser()
ap.add_argument("--scene", required=True); ap.add_argument("--words", required=True); ap.add_argument("--audio", required=True)
ap.add_argument("--icons", help="folder of versioned icon sets (v1/, v2/...; later override earlier) or of .svg files")
ap.add_argument("--kit", default=os.path.join(HERE, "kit.jsx")); ap.add_argument("--out", required=True)
ap.add_argument("--project"); ap.add_argument("--comp", help="comp name (default: the first addComp/newScene name in the scene)")
ap.add_argument("--stills"); ap.add_argument("--preview")
a = ap.parse_args()
for p in (a.out, a.preview):
    if p and os.path.exists(p): sys.exit(f"exists, not overwriting: {p}")

icons = {}
if a.icons:
    dirs = sorted(d for d in glob.glob(os.path.join(a.icons, "v*")) if os.path.isdir(d)) or [a.icons]
    for d in dirs:
        for f in glob.glob(os.path.join(d, "*.svg")):
            icons[os.path.basename(f)[:-4]] = open(f).read()
words = json.load(open(a.words))
assert all({"word", "start", "end"} <= set(w) for w in words), "words.json must be [{word, start, end}]"
scene = open(a.scene).read()
os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
with open(a.out, "w") as f:
    f.write(f"var WORDS={json.dumps(words)};\nvar ICONS={json.dumps(icons)};\nvar AUDIO={json.dumps(os.path.abspath(a.audio))};\n")
    f.write(open(a.kit).read() + "\n\n" + scene)
if "app.project.save()" not in scene:
    print("warning: the scene does not call app.project.save(); the project will not keep the comp", file=sys.stderr)
print("wrote", a.out)
if not a.project:
    sys.exit(0)

log = subprocess.run(["effectcraft-cli", "script", a.out, a.project], capture_output=True, text=True)
print(log.stdout + log.stderr)
if log.returncode:
    sys.exit(log.returncode)
comp = a.comp or (re.search(r"(?:addComp|newScene)\(\s*['\"]([^'\"]+)", scene) or [None, None])[1]
assert comp, "pass --comp"
if a.stills:
    os.makedirs(a.stills, exist_ok=True)
    for name, t in re.findall(r"^STILL (\S+) ([\d.]+)", log.stdout, re.M):
        png = os.path.join(a.stills, f"{name}.png")
        if os.path.exists(png): sys.exit(f"exists, not overwriting: {png}")
        subprocess.run(["effectcraft-cli", "--project", a.project, "render-frame", "--comp", comp, "--time", t, "--out", png],
                       check=True, stdout=subprocess.DEVNULL)
        print("still", png)
if a.preview:
    subprocess.run(["effectcraft-cli", "--project", a.project, "render", "--comp", comp, "--format", "h264",
                    "--resolution", "0.6666667", "--audio", "on", "--out", a.preview], check=True)
    print("preview", a.preview)
