# Runtime environment inventory

Values live only in a protected runtime env or approved provider secret store. This repository documents names and scope, never values.

## Shared across fleet profiles (same values OK)

- `GITHUB_TOKEN`
- `SUPABASE_ACCESS_TOKEN`
- `VERCEL_TOKEN`

## Per-bot only (never copy between bots)

- All `SLACK_*`
- `STAYDOS_AGENT_API_KEY` when the role has approved bounded StaydOS access
- Any dashboard drain or replay credential

`SLACK_REACTIONS=true` is a safe non-secret runtime default managed by each profile's `env.defaults`. Bot and app tokens remain profile-specific secrets. `scripts/sync-shared-env.sh` rejects every `SLACK_*` variable.
