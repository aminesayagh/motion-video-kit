#!/usr/bin/env bash
# One scene, end to end: generate + check rounds, build, patch tails/dead silence, soften, final check.
#   tools/voice/run_scene.sh <config.json> <scene> <tag> [rounds]
# Run it in the TTS venv (qwen-tts + faster-whisper + librosa). Each gen and each check is its own process,
# so the GPU model and Whisper are never loaded together. Outputs land in the config's out_dir:
#   sceneNN_<tag>.wav + sceneNN_<tag>.words.json   (deliver these)
#   sceneNN_<tag>_checks.json, *_patch_report.json, *_pre.summary.json  (evidence for the report)
set -euo pipefail
CFG=$1 N=$2 TAG=$3 ROUNDS=${4:-8}
HERE="$(cd "$(dirname "$0")" && pwd)"
S=$(printf %02d "$N")
OUT=$(python3 -c 'import json,os,sys; p=sys.argv[1]; c=json.load(open(p)); print(os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(p)), c.get("out_dir","out/voice"))))' "$CFG")
for r in $(seq "$ROUNDS"); do
  python "$HERE/qwen_takes.py" gen   --config "$CFG" --scenes "$N" 2>&1 | grep -E "seed|nothing|Error" || true
  python "$HERE/qwen_takes.py" check --config "$CFG" --scenes "$N" 2>&1 | grep -E "ratio=|Error" | cut -c1-420 || true
done
python "$HERE/qwen_takes.py" build --config "$CFG" --scenes "$N" --tag "$TAG" 2>&1 | grep -E '^\{|Error'
python "$HERE/patch_tails.py" "$OUT/scene${S}_${TAG}_pre.wav" "$OUT/scene${S}_${TAG}_pre.words.json" "$OUT/scene${S}_${TAG}_patched.wav"
python "$HERE/soften.py" "$OUT/scene${S}_${TAG}_patched.wav" "$OUT/scene${S}_${TAG}_pre.words.json" "$OUT/scene${S}_${TAG}.wav"
cp -n "$OUT/scene${S}_${TAG}_pre.words.json" "$OUT/scene${S}_${TAG}.words.json"
python "$HERE/final_check.py" --config "$CFG" --scene "$N" --tag "$TAG" 2>/dev/null
