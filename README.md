# Stayd Hermes fleet

Git-backed configuration for Hermes bots on the **Mr. Stayd** cloud host (option 1: one machine, many profiles).

## Quick start

```bash
cd /opt/data/fleet
./scripts/status.sh
# edit bots/don-draper/SOUL.md (etc.)
git add -A && git commit -m "don-draper: clarify external draft rules"
./scripts/apply-bot.sh don-draper
```

## Layout

```
bots/<bot>/
  profile.yaml   # role, live_profile name, shared_env_keys
  SOUL.md        # persona (applied to live profile)
scripts/
  apply-bot.sh   # git → live profile
  status.sh
  sync-shared-env.sh
POLICY.md
```

## Don Draper

- Live profile: `don-draper` → `/opt/data/profiles/don-draper`
- Gateway: stopped until Don’s own Slack tokens are set
- Shared app access: GitHub / Supabase / Vercel via host keys

## Mr. Stayd

- Live profile: `default` → `/opt/data`
- Fleet admin; applies commits
