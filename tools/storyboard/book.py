"""Storybook (Markdown) -> A4 PDF with the project fonts and palette.

    python3 book.py examples/orbitrows/storybook.md --out storybook.pdf [--fonts fonts/]

A "# Scene N" heading starts a new page. Needs: the `markdown` package and google-chrome (headless).
"""
import argparse, os, re, subprocess, tempfile

import markdown

ap = argparse.ArgumentParser()
ap.add_argument("md")
ap.add_argument("--out", required=True)
ap.add_argument("--fonts", default=".")
a = ap.parse_args()

body = re.sub(r"<h1>(Scene \d)", r'<h1 class="scene">\1',
              markdown.markdown(open(a.md).read(), extensions=["tables", "sane_lists"]))
F = "file://" + os.path.abspath(a.fonts).replace(" ", "%20") + "/"
css = f"""@font-face{{font-family:Poppins;font-weight:400;src:url({F}Poppins-Regular.ttf)}}@font-face{{font-family:Poppins;font-weight:600;src:url({F}Poppins-SemiBold.ttf)}}@font-face{{font-family:Poppins;font-weight:700;src:url({F}Poppins-Bold.ttf)}}
@page{{size:A4;margin:18mm 17mm}}html{{-webkit-print-color-adjust:exact;print-color-adjust:exact}}
body{{font-family:Poppins,sans-serif;color:#2C353A;font-size:10.4pt;line-height:1.6;margin:0}}
h1{{font-size:21pt;color:#0A6E89;line-height:1.2;margin:0 0 6mm}}h1.scene{{page-break-before:always;border-top:2.4mm solid #0A6E89;padding-top:5mm}}h1:first-of-type{{font-size:27pt}}
h2{{font-size:12.5pt;margin:7mm 0 2.5mm;color:#0A6E89;font-weight:600}}p{{margin:0 0 3mm}}ol,ul{{margin:0 0 3mm;padding-left:6mm}}li{{margin-bottom:1.8mm}}
blockquote{{margin:0 0 4mm;padding:3mm 5mm;background:#F9FEF6;border-left:1.6mm solid #FB938F;font-weight:600;font-size:11.5pt}}
table{{border-collapse:collapse;margin:0 0 4mm;width:100%;font-size:9.6pt}}th,td{{border-bottom:.3mm solid #C9BCEB;padding:1.6mm 2.4mm;text-align:left}}th{{background:#0A6E89;color:#fff;font-weight:600}}
hr{{border:0;margin:0}}strong{{font-weight:600}}h1,h2{{page-break-after:avoid}}li,tr{{page-break-inside:avoid}}"""
with tempfile.TemporaryDirectory() as tmp:
    html = os.path.join(tmp, "book.html")
    open(html, "w").write(f'<!doctype html><html><head><meta charset="utf-8"><title>Storybook</title><style>{css}</style></head><body>{body}</body></html>')
    pdf = os.path.abspath(a.out)
    subprocess.run(["timeout", "120", "google-chrome", "--headless=new", "--no-sandbox", "--disable-gpu", "--no-pdf-header-footer",
                    f"--print-to-pdf={pdf}", "file://" + html], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
print(pdf, os.path.getsize(pdf) if os.path.exists(pdf) else "missing")
