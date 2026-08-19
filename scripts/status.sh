#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "== fleet git =="
git -C "$ROOT" rev-parse --short HEAD 2>/dev/null || echo "(no commits)"
git -C "$ROOT" status -sb
echo
echo "== hermes profiles =="
/opt/hermes/bin/hermes profile list || true
echo
echo "== bots in repo =="
for d in "$ROOT"/bots/*/; do
  [ -d "$d" ] || continue
  name=$(basename "$d")
  live=$(python3 -c '
import re, sys
live = name = ""
for raw in open(sys.argv[1]):
    line = raw.split("#", 1)[0].rstrip()
    m = re.match(r"^([A-Za-z0-9_]+):\s*(.*)$", line)
    if not m:
        continue
    k, v = m.group(1), m.group(2).strip().strip("\"'\''")
    if k == "live_profile" and v:
        live = v
    if k == "name" and v:
        name = v
print(live or name or "?")
' "$d/profile.yaml" 2>/dev/null || echo "?")
  applied="none"
  if [ -f "$d/.applied" ]; then
    applied=$(grep '^commit=' "$d/.applied" | head -1 | cut -d= -f2 | cut -c1-12)
  fi
  echo "  $name  live_profile=$live  applied=$applied"
done
