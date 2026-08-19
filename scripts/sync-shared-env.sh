#!/usr/bin/env bash
# Sync allowlisted keys from host default .env into a profile .env (no SLACK_*).
set -euo pipefail
PROFILE_ENV="${1:?profile .env path}"
HOST_ENV="${2:-/opt/data/.env}"
KEYS_CSV="${3:?comma-separated keys}"
python3 - "$PROFILE_ENV" "$HOST_ENV" "$KEYS_CSV" <<'PY'
import sys
from pathlib import Path
prof_path, host_path, keys_csv = sys.argv[1], sys.argv[2], sys.argv[3]
keys = [k.strip() for k in keys_csv.split(',') if k.strip()]
host = {}
for line in Path(host_path).read_text().splitlines():
    s=line.strip()
    if not s or s.startswith('#') or '=' not in s: continue
    k,v=s.split('=',1); host[k]=v
prof_path = Path(prof_path)
existing = {}
order = []
if prof_path.exists():
    for line in prof_path.read_text().splitlines():
        s=line.strip()
        if not s or s.startswith('#') or '=' not in s:
            order.append(('raw', line)); continue
        k,v=s.split('=',1)
        existing[k]=v
        order.append(('key', k))
for k in keys:
    if k.startswith('SLACK_'):
        raise SystemExit(f'refuse SLACK key in shared sync: {k}')
    if k not in host:
        print(f'warn: missing on host: {k}', file=sys.stderr)
        continue
    existing[k]=host[k]
    if ('key', k) not in order:
        order.append(('key', k))
out=[]
seen=set()
for kind, val in order:
    if kind=='raw':
        out.append(val); continue
    k=val
    if k in seen: continue
    seen.add(k)
    if k in existing:
        out.append(f'{k}={existing[k]}')
for k,v in existing.items():
    if k not in seen:
        out.append(f'{k}={v}')
prof_path.parent.mkdir(parents=True, exist_ok=True)
prof_path.write_text('\n'.join(out).rstrip()+'\n')
prof_path.chmod(0o600)
print(f'synced {len(keys)} allowlisted keys → {prof_path}')
PY
