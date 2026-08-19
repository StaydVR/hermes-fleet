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
  live=$(python3 -c "import yaml,sys; print(yaml.safe_load(open(sys.argv[1])).get('live_profile',''))" "$d/profile.yaml" 2>/dev/null || echo "?")
  applied=""
  [ -f "$d/.applied" ] && applied=$(head -1 "$d/.applied")
  echo "  $name  live_profile=$live  applied=${applied:-none}"
done
