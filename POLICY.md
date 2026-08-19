# Stayd Hermes fleet policy

**Decided:** 2026-08-19 by Reid — architecture option 1 (one machine, many profiles) + **git audit trail**.

## Source of truth

| Layer | Location | In git? |
|-------|----------|---------|
| Bot identity / SOUL / role | `fleet/bots/<bot>/` | **Yes** |
| Apply scripts / policy | `fleet/scripts`, `fleet/POLICY.md` | **Yes** |
| Live Hermes profile runtime | `/opt/data/profiles/<live_profile>/` (default: `/opt/data`) | **No** (generated) |
| Secrets | runtime `.env` only | **Never** |
| Sessions / memory / state.db | live profile dirs | **No** |

## Rules

1. **No live bot config change without a git commit** in this repo (or a PR merge into the tracked branch).
2. Mr. Stayd (or an owner) edits `bots/<name>/` → `git commit` → `scripts/apply-bot.sh <name>`.
3. `apply-bot.sh` refuses to run if the worktree is dirty, unless `--commit <sha>` is passed.
4. Every apply writes `bots/<name>/.applied` (commit, time, actor) **and** commits that marker only if you use `apply-bot.sh --record` (optional). Prefer logging apply in the same change commit message: `apply(don-draper): <sha>`.
5. Secrets are never written into this repo. Apply may **sync allowlisted keys** from default host `.env` into a profile `.env` when `profile.yaml` lists `shared_env_keys`.
6. Slack tokens are **per bot**. Apply never copies `SLACK_*` from default → profile.
7. Deleting a bot: PR removes `bots/<name>/`, apply (or manual) runs `hermes profile delete` only with owner approval.

## Branch

- Default branch: `main`
- Remote (when connected): `StaydVR/hermes-fleet` (private)

## Who may apply

- Mr. Stayd on this host
- Reid (owner)
- Other owners if Reid delegates
