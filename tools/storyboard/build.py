"""Build one storyboard version from story.js: an HTML page, one SVG per screen, and a PDF.

    python3 build.py --version 1 --out storyboard/ [--icons icons/] [--fonts fonts/] [--story story.js]

Writes <out>/storyboard_v<N>.html, <out>/storyboard_v<N>.pdf and <out>/v<N>_sceneNN/sN_MM.svg.
Each SVG is the stage at the END of its moment (960x540); the editor animates the way in.

Inputs next to this script: helpers.js (drawing helpers), page.css (fonts and page layout), intro.html
(text above the frames). story.js is the example storyboard of the OrbitRows video; write your own with the
same shape (const S = [{n, title, frames: [{cap, ...}]}] and a frame(fr, sc) function).
--icons: a folder of versioned icon sets (v1/, v2/, ...: later versions override earlier ones).
--fonts: the folder holding Poppins-Regular.ttf etc. (used by the page and to measure word widths).
Needs: node, google-chrome (headless, for the PDF), Pillow.
"""
import argparse, ast, json, os, re, subprocess, xml.dom.minidom

HERE = os.path.dirname(os.path.abspath(__file__))
ap = argparse.ArgumentParser()
ap.add_argument("--version", required=True)
ap.add_argument("--out", required=True)
ap.add_argument("--icons", default=None)
ap.add_argument("--fonts", default=None)
ap.add_argument("--story", default=os.path.join(HERE, "story.js"))
a = ap.parse_args()
V, OUT = a.version, os.path.abspath(a.out)
os.makedirs(OUT, exist_ok=True)
read = lambda f: open(os.path.join(HERE, f)).read()

icons = {}
if a.icons:
    for v in sorted(os.listdir(a.icons)):                  # later versions override earlier ones (v1, v2, v3...)
        d = os.path.join(a.icons, v)
        if not (v.startswith("v") and os.path.isdir(d)):
            continue
        for f in os.listdir(d):
            if f.endswith(".svg"):
                m = re.search(r"<g[^>]*>(.*)</g>", open(os.path.join(d, f)).read(), re.S)
                if m:
                    icons[f[:-4]] = re.sub(r"\s+", " ", m.group(1)).strip()

story = open(a.story).read()
widths = ""
sent = re.search(r"const SENT=(\[.*?\]);", story)
if sent and a.fonts:                                         # real glyph widths for the panel's markers and tags
    from PIL import ImageFont
    words = ast.literal_eval(sent.group(1))
    f15 = ImageFont.truetype(os.path.join(a.fonts, "Poppins-Regular.ttf"), 15)
    widths = f"const W15={json.dumps([round(f15.getlength(w), 2) for w in words])};const SP15={f15.getlength(' ')};\n"
js = widths + f"const ICONS={json.dumps(icons)};\n" + read("helpers.js") + "\n" + story
css = read("page.css").replace("{{FONTS}}", "file://" + os.path.abspath(a.fonts or ".").replace(" ", "%20"))
page = ("\ndocument.getElementById('app').innerHTML=S.map(sc=>`<section class=\"scene\"><h2>${esc(sc.title)}</h2><div class=\"grid\">"
        "${sc.frames.map((fr,i)=>`<figure><div class=\"fr\">${frame(fr,sc)}</div><figcaption><b>${sc.n}.${i+1}</b> ${esc(fr.cap)}"
        "</figcaption></figure>`).join('')}</div></section>`).join('');\n")
html = (f'<!doctype html><html><head><meta charset="utf-8"><title>Storyboard v{V}</title><style>{css}</style></head>'
        f'<body>{read("intro.html")}<div id="app"></div><script>{js}{page}</script></body></html>')
out_html = os.path.join(OUT, f"storyboard_v{V}.html")
open(out_html, "w").write(html)

# one SVG per screen, through node (the same code the page runs)
frames_js = os.path.join(OUT, f"_frames_v{V}.js")
open(frames_js, "w").write(js + """
const fs=require('fs'),path=require('path');const out=process.argv[2];
for(const sc of S){const d=path.join(out,`v${process.argv[3]}_scene${String(sc.n).padStart(2,'0')}`);fs.mkdirSync(d,{recursive:true});
 sc.frames.forEach((fr,i)=>fs.writeFileSync(path.join(d,`s${sc.n}_${String(i+1).padStart(2,'0')}.svg`),frame(fr,sc)));}
""")
subprocess.run(["node", frames_js, OUT, V], check=True)
os.remove(frames_js)
bad = []
for root, _, files in os.walk(OUT):
    if os.path.basename(root).startswith(f"v{V}_scene"):
        for f in files:
            try:
                xml.dom.minidom.parse(os.path.join(root, f))
            except Exception as e:
                bad.append((f, e))
print("frames ok" if not bad else f"BAD frames: {bad}")

pdf = os.path.join(OUT, f"storyboard_v{V}.pdf")
subprocess.run(["timeout", "150", "google-chrome", "--headless=new", "--no-sandbox", "--disable-gpu", "--no-pdf-header-footer",
                "--virtual-time-budget=8000", f"--print-to-pdf={pdf}", "file://" + out_html.replace(" ", "%20")],
               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
print("pdf", os.path.getsize(pdf) if os.path.exists(pdf) else "missing")
