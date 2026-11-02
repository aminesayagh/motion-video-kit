#!/usr/bin/env bash
# Film assembly: the scene renders joined end to end (re-encoded), with the film mix as the only audio.
#   tools/assemble/concat_film.sh <film_mix.wav> <out.mp4> <scene01.mp4> <scene02.mp4> ...
# Why the concat FILTER and a re-encode: scene renders from different encoder versions carried different time
# bases (1/15360 and 1/30); the concat demuxer with stream copy silently dropped 5963 frames. The filter keeps
# every frame. Video H.264 CRF 16 preset slow yuv420p, audio AAC 256 kbps 48 kHz.
# Check afterwards with tools/sound/film_gates.py (frame count, audio lock, loudness, PSNR per cut).
set -euo pipefail
MIX=$1 OUT=$2; shift 2
[ -e "$OUT" ] && { echo "exists, not overwriting: $OUT"; exit 1; }
args=(); filt=""; i=0
for f in "$@"; do args+=(-i "$f"); filt+="[$i:v:0]"; i=$((i+1)); done
args+=(-i "$MIX")
ffmpeg -hide_banner -threads 2 "${args[@]}" \
  -filter_complex "${filt}concat=n=$#:v=1:a=0,format=yuv420p[v]" \
  -map "[v]" -map "$#:a:0" -r 30 -c:v libx264 -preset slow -crf 16 -c:a aac -b:a 256k -ar 48000 \
  -movflags +faststart "$OUT"
ffprobe -v error -show_entries format=duration -of csv=p=0 "$OUT"
