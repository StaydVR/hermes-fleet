#!/usr/bin/env bash
# Apply git-backed bot config to the live Hermes profile. Requires clean tree or --commit SHA.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BOT=""
COMMIT=""
RECORD=0
SYNC_ENV=1
while [[ $# -gt 0 ]]; do
  case "$1" in
    --commit) COMMIT="${2:?}"; shift 2 ;;
    --record) RECORD=1; shift ;;
    --no-sync-env) SYNC_ENV=0; shift ;;
    -h|--help)
      echo "Usage: $0 <bot> [--commit SHA] [--record] [--no-sync-env]"
      exit 0 ;;
    *)
      if [[ -z "$BOT" ]]; then BOT="$1"; shift; else echo "unknown arg: $1" >&2; exit 2; fi ;;
  esac
done
[[ -n "$BOT" ]] || { echo "Usage: $0 <bot> [--commit SHA]" >&2; exit 2; }

BOT_DIR="$ROOT/bots/$BOT"
[[ -d "$BOT_DIR" ]] || { echo "no such bot in fleet repo: $BOT" >&2; exit 1; }
[[ -f "$BOT_DIR/profile.yaml" ]] || { echo "missing profile.yaml" >&2; exit 1; }
[[ -f "$BOT_DIR/SOUL.md" ]] || { echo "missing SOUL.md" >&2; exit 1; }

cd "$ROOT"
if [[ -n "$COMMIT" ]]; then
  git cat-file -e "${COMMIT}^{commit}" 2>/dev/null || { echo "unknown commit $COMMIT" >&2; exit 1; }
  SHA=$(git rev-parse "$COMMIT")
  # extract files from that commit into temp and apply from there
  WORK=$(mktemp -d)
  trap 'rm -rf "$WORK"' EXIT
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

# parse live_profile + shared keys with python
eval "$(python3 - "$SRC/profile.yaml" <<'PY'
import yaml,sys,shlex
p=yaml.safe_load(open(sys.argv[1]))
live=p.get('live_profile') or p.get('name')
keys=p.get('shared_env_keys') or []
print(f"LIVE_PROFILE={shlex.quote(str(live))}")
print(f"SHARED_KEYS={shlex.quote(','.join(keys))}")
PY
)"

if [[ "$LIVE_PROFILE" == "default" ]]; then
  LIVE_HOME="/opt/data"
else
  LIVE_HOME="/opt/data/profiles/$LIVE_PROFILE"
fi
[[ -d "$LIVE_HOME" ]] || { echo "live profile home missing: $LIVE_HOME (create with hermes profile create first)" >&2; exit 1; }

# Apply SOUL
cp "$SRC/SOUL.md" "$LIVE_HOME/SOUL.md"
echo "applied SOUL.md → $LIVE_HOME/SOUL.md"

# Optional config overlay (non-secret yaml merge not implemented — copy if present as config.overlay.yaml notes only)
if [[ -f "$SRC/config.overlay.yaml" ]]; then
  cp "$SRC/config.overlay.yaml" "$LIVE_HOME/config.overlay.yaml"
  echo "copied config.overlay.yaml (manual merge into config.yaml if needed)"
fi

# profile.yaml copy for inspection
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

# Also stamp live home
cp "$APPLIED_FILE" "$LIVE_HOME/.fleet-applied"

echo "OK applied $BOT @ ${SHA:0:12} → $LIVE_HOME"

if [[ "$RECORD" -eq 1 ]]; then
  git add "bots/$BOT/.applied"
  if [[ -n $(git status --porcelain "bots/$BOT/.applied") ]]; then
    git commit -m "apply($BOT): ${SHA:0:12}"
    echo "recorded apply marker commit"
  fi
fi
