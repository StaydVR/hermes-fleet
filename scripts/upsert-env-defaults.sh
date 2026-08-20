#!/usr/bin/env bash
# Upsert KEY=VALUE pairs from a defaults file into a live .env without
# touching secrets or deleting unknown keys.
set -euo pipefail

LIVE_ENV="${1:?live .env path}"
DEFAULTS="${2:?env.defaults path}"

[[ -f "$DEFAULTS" ]] || { echo "missing defaults: $DEFAULTS" >&2; exit 1; }
mkdir -p "$(dirname "$LIVE_ENV")"
touch "$LIVE_ENV"
chmod 600 "$LIVE_ENV" 2>/dev/null || true

tmp=$(mktemp)
cp "$LIVE_ENV" "$tmp"

while IFS= read -r line || [[ -n "$line" ]]; do
  # skip blanks/comments
  [[ -z "${line// }" ]] && continue
  [[ "$line" =~ ^[[:space:]]*# ]] && continue
  [[ "$line" == *=* ]] || continue
  key="${line%%=*}"
  key="${key// /}"
  val="${line#*=}"
  if grep -qE "^${key}=" "$tmp"; then
    # portable in-place replace of that key line
    awk -v k="$key" -v v="$val" 'BEGIN{FS=OFS="="} $1==k {$0=k"="v} {print}' "$tmp" > "${tmp}.new"
    mv "${tmp}.new" "$tmp"
    echo "env upsert updated $key"
  else
    printf '%s=%s\n' "$key" "$val" >> "$tmp"
    echo "env upsert added $key"
  fi
done < "$DEFAULTS"

mv "$tmp" "$LIVE_ENV"
chmod 600 "$LIVE_ENV" 2>/dev/null || true
