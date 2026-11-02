"""Chapter list from the film layout (scene start times), for the video description or a player.

  python chapters.py layout.json [--titles "Introduction" "Coreference" ...] > chapters.txt

Prints one line per scene: number, h:mm:ss.mmm start, start in seconds, length, frames, and title or source.
YouTube-style chapters need only the "m:ss title" part; the first must be 0:00.
"""
import argparse, json

ap = argparse.ArgumentParser()
ap.add_argument("layout"); ap.add_argument("--titles", nargs="*", default=[])
a = ap.parse_args()
L = json.load(open(a.layout)); sr = L["sr"]


def hms(t):
    h, r = divmod(t, 3600); m, s = divmod(r, 60)
    return f"{int(h)}:{int(m):02d}:{s:06.3f}"


print(f"# film {L['total'] / sr:.3f} s; scene  start(h:mm:ss.mmm)  start_s  length_s  frames  title")
for i, s in enumerate(L["scenes"]):
    title = a.titles[i] if i < len(a.titles) else s.get("mp4", "")
    print(f"{s['scene']:02d}  {hms(s['start'] / sr)}  {s['start'] / sr:8.3f}  {s['length'] / sr:7.3f}  {s['frames']:5d}  {title}")
