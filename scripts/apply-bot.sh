#!/usr/bin/env bash
# Apply git-backed bot config to the live Hermes profile.
# Requires a clean worktree, or --commit <sha>.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BOT=""
COMMIT=""
RECORD=0
SYNC_ENV=1
DRY_RUN=0

usage() {
  echo "Usage: $0 <bot> [--commit SHA] [--record] [--no-sync-env] [--dry-run]"
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --commit) COMMIT="${2:?}"; shift 2 ;;
    --record) RECORD=1; shift ;;
    --no-sync-env) SYNC_ENV=0; shift ;;
    --dry-run) DRY_RUN=1; shift ;;
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
SKILL_STAGE=""
cleanup() {
  [[ -n "${WORK}" && -d "${WORK}" ]] && rm -rf -- "$WORK"
  [[ -n "${SKILL_STAGE}" && -d "${SKILL_STAGE}" ]] && rm -rf -- "$SKILL_STAGE"
  return 0
}
trap cleanup EXIT

if [[ -n "$COMMIT" ]]; then
  git cat-file -e "${COMMIT}^{commit}" 2>/dev/null || { echo "unknown commit $COMMIT" >&2; exit 1; }
  SHA=$(git rev-parse "$COMMIT")
  WORK=$(mktemp -d)
  ARCHIVE_PATHS=("bots/$BOT")
  if git cat-file -e "${SHA}:skills" 2>/dev/null; then
    ARCHIVE_PATHS+=("skills")
  fi
  git archive "$SHA" "${ARCHIVE_PATHS[@]}" | tar -x -C "$WORK"
  SRC="$WORK/bots/$BOT"
  SHARED_SKILLS="$WORK/skills"
else
  if [[ "$DRY_RUN" -eq 0 && -n $(git status --porcelain) ]]; then
    echo "ERROR: dirty worktree. Commit first, or pass --commit <sha>." >&2
    git status -sb >&2
    exit 1
  fi
  SHA=$(git rev-parse HEAD)
  SRC="$BOT_DIR"
  SHARED_SKILLS="$ROOT/skills"
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

LOCAL_SKILLS="$SRC/skills"
python3 "$ROOT/scripts/compose-skills.py" \
  --shared "$SHARED_SKILLS" \
  --bot "$LOCAL_SKILLS" \
  --check-only

if [[ "$DRY_RUN" -eq 1 ]]; then
  echo "DRY RUN OK: bot=$BOT live_profile=$LIVE_PROFILE shared_env_keys=${SHARED_KEYS:-none}"
  echo "No live profile, env, gateway, or apply marker was changed."
  exit 0
fi

# Materialize the full skill tree before any live profile file is changed.
if [[ -d "$SHARED_SKILLS" || -d "$LOCAL_SKILLS" ]]; then
  SKILL_STAGE=$(mktemp -d)
  python3 "$ROOT/scripts/compose-skills.py" \
    --shared "$SHARED_SKILLS" \
    --bot "$LOCAL_SKILLS" \
    --destination "$SKILL_STAGE"
fi

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

if [[ -f "$SRC/AGENTS.md" ]]; then
  cp "$SRC/AGENTS.md" "$LIVE_HOME/AGENTS.md"
  echo "applied AGENTS.md → $LIVE_HOME/AGENTS.md"
fi

# Runtime config hardening (providers/timeouts/compression/fallback/session_reset)
# Prefer runtime-config.yaml; keep legacy config.overlay.yaml name as alias.
OVERLAY=""
if [[ -f "$SRC/runtime-config.yaml" ]]; then
  OVERLAY="$SRC/runtime-config.yaml"
elif [[ -f "$SRC/config.overlay.yaml" ]]; then
  OVERLAY="$SRC/config.overlay.yaml"
fi
if [[ -n "$OVERLAY" ]]; then
  cp "$OVERLAY" "$LIVE_HOME/fleet-runtime-config.yaml"
  if [[ -f "$LIVE_HOME/config.yaml" ]]; then
    /opt/hermes/.venv/bin/python3 "$ROOT/scripts/merge-config-overlay.py" \
      "$LIVE_HOME/config.yaml" "$OVERLAY"
  else
    echo "WARN: no live config.yaml yet; skipped merge ($LIVE_HOME)" >&2
  fi
fi

cp "$SRC/profile.yaml" "$LIVE_HOME/fleet-profile.yaml"

# Compose shared fleet skills first, then the bot-local overlay. Name collisions
# are rejected before this point and before any skill reaches the live profile.
if [[ -n "$SKILL_STAGE" ]]; then
  mkdir -p "$LIVE_HOME/skills"
  cp -a "$SKILL_STAGE/." "$LIVE_HOME/skills/"
  echo "applied shared + bot-local skills/ → $LIVE_HOME/skills"
fi

if [[ "$SYNC_ENV" -eq 1 && -n "$SHARED_KEYS" ]]; then
  if [[ "$LIVE_PROFILE" == "default" ]]; then
    echo "skip env sync for default (source of shared keys)"
  else
    "$ROOT/scripts/sync-shared-env.sh" "$LIVE_HOME/.env" "/opt/data/.env" "$SHARED_KEYS"
  fi
fi

# Non-secret env defaults (stream watchdogs, etc.)
if [[ -f "$SRC/env.defaults" ]]; then
  bash "$ROOT/scripts/upsert-env-defaults.sh" "$LIVE_HOME/.env" "$SRC/env.defaults"
fi

# Best-effort: pin s6 gateway run script when fleet ships one
if [[ -f "$SRC/gateway-run.sh" ]]; then
  cp "$SRC/gateway-run.sh" "$LIVE_HOME/gateway-run.sh"
  chmod +x "$LIVE_HOME/gateway-run.sh"
  # s6 slot names: gateway-default for live_profile=default, else gateway-<profile>
  if [[ "$LIVE_PROFILE" == "default" ]]; then
    S6_NAME="gateway-default"
  else
    S6_NAME="gateway-${LIVE_PROFILE}"
  fi
  S6_RUN="/run/service/${S6_NAME}/run"
  if [[ -d "/run/service/${S6_NAME}" ]]; then
    cp "$SRC/gateway-run.sh" "$S6_RUN"
    chmod +x "$S6_RUN"
    echo "applied gateway-run.sh → $S6_RUN (restart gateway slot separately if needed)"
  else
    echo "gateway-run.sh saved to profile; s6 slot ${S6_NAME} not present yet"
  fi
fi

APPLIED_FILE="$BOT_DIR/.applied"
{
  echo "commit=$SHA"
  echo "bot=$BOT"
  echo "live_profile=$LIVE_PROFILE"
  echo "live_home=$LIVE_HOME"
  echo "applied_at=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "applied_by=${USER:-fleet-operator}"
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
