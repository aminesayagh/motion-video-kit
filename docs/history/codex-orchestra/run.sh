#!/usr/bin/env bash
# Orchestra: one local Codex session per role (illustrator, editor, voice, sound).
#   run.sh brief <role> <brief.md>   send a brief headless; the role's session is resumed (same folder = same session)
#   run.sh open  <role>              open the role's Codex interactively, to watch it or talk to it
#   run.sh status                    briefs and reports per role
set -euo pipefail
O="$(cd "$(dirname "$0")" && pwd)"; ROOT="$(dirname "$O")"
ROLES="${ROLES_DIR:-$O/roles}"
TW="$ROOT"                                                     # the shared folder, passed to the MCP tools
cmd="${1:-status}"; role="${2:-}"

if [ "$cmd" = status ]; then
  for d in "$ROLES"/*/; do r="$(basename "$d")"
    printf '%-12s briefs %s  reports %s\n' "$r" "$(ls "$d/inbox" 2>/dev/null | wc -l)" "$(ls "$d/outbox" 2>/dev/null | grep -c '_report.md' || true)"
  done; exit 0
fi

D="$ROLES/$role"; [ -d "$D" ] || { echo "unknown role: $role" >&2; exit 1; }
cat "$O/common.md" "$D/role.md" > "$D/AGENTS.md"            # one source of rules, rebuilt before every use

# Each role gets only its own tool: every other MCP server of the base config is switched off (context7 stays).
keep=""; F=(--sandbox workspace-write)
case "$role" in
  illustrator) keep=vectorcraft
    F+=(--add-dir "$ROOT/icons" -c 'mcp_servers.vectorcraft.command="vectorcraft-cli"'
        -c "mcp_servers.vectorcraft.args=[\"mcp\",\"--headless\",\"--automation-read-root\",\"$TW\",\"--automation-write-root\",\"$TW/icons\"]");;
  editor) keep=effectcraft                                   # its own server, bound to the current project (the old global one stays off)
    F+=(--add-dir "$ROOT" -c 'mcp_servers.effectcraft.command="effectcraft-cli"'
        -c "mcp_servers.effectcraft.args=[\"mcp\",\"--project\",\"$ROOT/OrbitRows_v2.ecproj\"]");;
  sound) keep=soundcraft
    mkdir -p "$ROOT/audio/mixed"
    F+=(--add-dir "$ROOT/audio/mixed" -c "mcp_servers.soundcraft.command=\"soundcraft-cli\"" -c 'mcp_servers.soundcraft.args=["mcp"]');;
  voice) F+=(--add-dir "${VOICE_DIR:-$ROOT/../voicer}");;
  *) echo "no tool set for role: $role" >&2; exit 1;;
esac
for s in code-review-graph excalidraw serena effectcraft-orbit-rows; do   # only servers the base config already defines
  [ "$s" = "$keep" ] || F+=(-c "mcp_servers.$s.enabled=false")
done

B=""; [ -n "${3:-}" ] && B="$(realpath "$3")"        # resolve the brief path before changing folder
cd "$D"
case "$cmd" in
  brief)
    f="$B"; n="$(basename "$f" .md)"; mkdir -p "$D/outbox"
    p="New brief from the orchestrator: $f. Read it and carry it out, following AGENTS.md. When you finish, or if you are blocked, write your report to $D/outbox/${n}_report.md: the deliverables with full paths, what you changed from the brief and why, anything you could not do."
    if [ -f "$D/.session" ]; then codex exec "${F[@]}" --skip-git-repo-check resume --last "$p" </dev/null | tee "$D/outbox/${n}_log.txt"
    else codex exec "${F[@]}" --skip-git-repo-check "$p" </dev/null | tee "$D/outbox/${n}_log.txt"; touch "$D/.session"; fi;;
  open)
    if [ -f "$D/.session" ]; then exec codex "${F[@]}" resume --last; else exec codex "${F[@]}"; fi;;
  *) echo "usage: run.sh brief <role> <brief.md> | open <role> | status" >&2; exit 1;;
esac
