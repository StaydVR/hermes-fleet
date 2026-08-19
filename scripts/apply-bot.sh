#!/usr/bin/env bash
# Apply git-backed bot config to the live Hermes profile.
# Requires a clean worktree, or --commit <sha>.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BOT=""
COMMIT=""
RECORD=0
SYNC_ENV=1

usage() {
  echo "Usage: $0 <bot> [--commit SHA] [--record] [--no-sync-env]"
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --commit) COMMIT="${2:?}"; shift 2 ;;
    --record) RECORD=1; shift ;;
    --no-sync-env) SYNC_ENV=0; shift ;;
    -h|--help) usage; exit 0 ;;
    *)
      if [[ -z "$BOT" ]]; then BOT="$1"; shift
      else echo "unknown arg: $1" >&2; usage >&2; exit 2
      fi ;;
  esac
done

[[ -n "$BOT" ]] || { usage >&2; exit 2; }

BOT_DIR="$ROOT/bots/$BOT"
[[ -d "$BOT_DIR" ]] || { echo "no such bot in fleet repo: $BOT" >&2; exit 1; }

cd "$ROOT"
WORK=""
cleanup() { [[ -n "${WORK}" && -d "${WORK}" ]] && rm -rf "$WORK"; }
trap cleanup EXIT

if [[ -n "$COMMIT" ]]; then
  git cat-file -e "${COMMIT}^{commit}" 2>/dev/null || { echo "unknown commit $COMMIT" >&2; exit 1; }
  SHA=$(git rev-parse "$COMMIT")
  WORK=$(mktemp -d)
  git archive "$SHA" "bots/$BOT" | tar -x -C "$WORK"
  SRC="$WORK/bots/$BOT"
else
  if [[ -n $(git status --porcelain) ]]; then
    echo "ERROR: dirty worktree. Commit first, or pass --commit <sha>." >&2
    git status -sb >&2
    exit 1
  fi
  SHA=$(git rev-parse HEAD)
  SRC="$BOT_DIR"
fi

[[ -f "$SRC/profile.yaml" ]] || { echo "missing profile.yaml" >&2; exit 1; }
[[ -f "$SRC/SOUL.md" ]] || { echo "missing SOUL.md" >&2; exit 1; }

# Minimal YAML field extract (no PyYAML required)
parse_out=$(python3 - "$SRC/profile.yaml" <<'PY'
import re, sys, shlex
text = open(sys.argv[1]).read().splitlines()
live = name = None
keys = []
in_keys = False
for raw in text:
    line = raw.split("#", 1)[0].rstrip()
    if not line.strip():
        continue
    m = re.match(r"^([A-Za-z0-9_]+):\s*(.*)$", line)
    if m:
        k, v = m.group(1), m.group(2).strip().strip("'\"")
        in_keys = (k == "shared_env_keys")
        if k == "live_profile" and v:
            live = v
        elif k == "name" and v:
            name = v
        continue
    if in_keys:
        m = re.match(r"^-\s*(\S+)\s*$", line.strip())
        if m:
            keys.append(m.group(1).strip("'\""))
        else:
            in_keys = False
live = live or name or ""
print(live)
print(",".join(keys))
PY
)
LIVE_PROFILE=$(printf '%s\n' "$parse_out" | sed -n '1p')
SHARED_KEYS=$(printf '%s\n' "$parse_out" | sed -n '2p')

if [[ "$LIVE_PROFILE" == "default" ]]; then
  LIVE_HOME="/opt/data"
else
  LIVE_HOME="/opt/data/profiles/$LIVE_PROFILE"
fi
[[ -d "$LIVE_HOME" ]] || {
  echo "live profile home missing: $LIVE_HOME (create with hermes profile create first)" >&2
  exit 1
}

cp "$SRC/SOUL.md" "$LIVE_HOME/SOUL.md"
echo "applied SOUL.md → $LIVE_HOME/SOUL.md"

if [[ -f "$SRC/config.overlay.yaml" ]]; then
  cp "$SRC/config.overlay.yaml" "$LIVE_HOME/config.overlay.yaml"
  echo "copied config.overlay.yaml (manual merge into config.yaml if needed)"
fi

cp "$SRC/profile.yaml" "$LIVE_HOME/fleet-profile.yaml"

if [[ "$SYNC_ENV" -eq 1 && -n "$SHARED_KEYS" ]]; then
  if [[ "$LIVE_PROFILE" == "default" ]]; then
    echo "skip env sync for default (source of shared keys)"
  else
    "$ROOT/scripts/sync-shared-env.sh" "$LIVE_HOME/.env" "/opt/data/.env" "$SHARED_KEYS"
  fi
fi

APPLIED_FILE="$BOT_DIR/.applied"
{
  echo "commit=$SHA"
  echo "bot=$BOT"
  echo "live_profile=$LIVE_PROFILE"
  echo "live_home=$LIVE_HOME"
  echo "applied_at=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "applied_by=${USER:-mr-stayd}"
} > "$APPLIED_FILE"

cp "$APPLIED_FILE" "$LIVE_HOME/.fleet-applied"
echo "OK applied $BOT @ ${SHA:0:12} → $LIVE_HOME"

if [[ "$RECORD" -eq 1 ]]; then
  # force-add ignored .applied for audit marker commits
  git add -f "bots/$BOT/.applied"
  if [[ -n $(git status --porcelain "bots/$BOT/.applied") ]]; then
    git commit -m "apply($BOT): ${SHA:0:12}"
    echo "recorded apply marker commit"
  fi
fi
