#!/usr/bin/env bash
# Final 1080p renders of the approved scene comps, ONE AT A TIME (two parallel renders exhausted WSL's memory),
# without audio: the film mix is muxed in at assembly.
#   tools/edit/render_final.sh <list.txt> <out_dir>
# list.txt: one scene per line, "NN|project.ecproj|Comp name" (see examples/orbitrows/render_list.txt).
# An existing output is skipped, so the script can be re-run after a failure.
set -u
LIST=$1 OUT=$2
mkdir -p "$OUT"
while IFS='|' read -r n proj comp; do
  [ -z "$n" ] && continue
  case "$n" in \#*) continue;; esac
  out="$OUT/scene${n}_1080.mp4"
  [ -e "$out" ] && { echo "skip $out"; continue; }
  if effectcraft-cli --project "$proj" render --comp "$comp" --out "$out" --format h264 --resolution full \
       --quality best --audio off --bitrate 14000 > "$OUT/scene${n}.log" 2>&1; then
    echo "done $n $(ffprobe -v error -show_entries format=duration -of csv=p=0 "$out")"
  else
    echo "FAILED $n (see $OUT/scene${n}.log)"
  fi
done < "$LIST"
