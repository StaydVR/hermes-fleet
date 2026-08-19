# Shared host secrets (values live only in runtime `.env`, never in git)

## Shared across fleet profiles (same values OK)

- `GITHUB_TOKEN`
- `SUPABASE_ACCESS_TOKEN`
- `VERCEL_TOKEN`

## Per-bot only (never copy between bots)

- All `SLACK_*`
- `API_SERVER_KEY` (if used)
- Dashboard drain/replay secrets
