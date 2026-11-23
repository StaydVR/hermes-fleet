# AGENTS.md — hermes-fleet

Read first: [`README.md`](README.md) (checkout, profile factory, apply path), [`POLICY.md`](POLICY.md) (binding governance), [`docs/CONTRIBUTING.md`](docs/CONTRIBUTING.md) (review and local verification). This file is the repo guide for coding agents. `bots/<slug>/AGENTS.md` is a different file: profile operations that `scripts/apply-bot.sh` copies onto the live Hermes profile.

## What this repo is

Reviewed source of truth for Stayd's Hermes agent profiles. Git holds identity, runtime overlays, shared skills, and the host apply tooling. Credentials, sessions, memory, and live runtime state stay on the host.

Tracked profiles today:

| Directory | `live_profile` | Role in `profile.yaml` |
|---|---|---|
| `bots/mr-stayd` | `default` | `fleet_chief` |
| `bots/don-draper` | `don-draper` | `brand_comms` |

There is no application server, package manifest, or lockfile. The language is Python 3 plus bash. CI pins Python 3.12. The validator and unit tests import PyYAML. The apply scripts use the Python standard library.

A normal change stays in git until a human applies a reviewed commit on the host. See Deploys and production below.

## Setup, run, and test

Clone the repo. Do not put the checkout inside a live Hermes profile, and do not copy a runtime `.env`, sessions, memories, or state databases into git.

```bash
python3 -m pip install --disable-pip-version-check PyYAML
```

That is the install step from [`.github/workflows/validate.yml`](.github/workflows/validate.yml). PyYAML has no pinned version in the repo. There is no `requirements.txt`, `pyproject.toml`, or `package.json`.

Checks the workflow runs on every pull request and on every push to `main`:

```bash
python3 tools/validate_repo.py .
python3 tools/validate_repo.py --self-test
python3 -m unittest discover -s tests -v
```

[`docs/CONTRIBUTING.md`](docs/CONTRIBUTING.md) also requires these before review. CI does not run them:

```bash
find . -type f -name '*.sh' -not -path './.git/*' -exec bash -n {} +
python3 -m compileall -q scripts tools tests
git diff --check
./scripts/apply-bot.sh <agent-slug> --dry-run
```

`--dry-run` checks that `bots/<agent-slug>` exists, parses `profile.yaml`, and runs `scripts/compose-skills.py --check-only`. It then exits. The script prints `No live profile, env, gateway, or apply marker was changed.`

On the Hermes host, `./scripts/status.sh` prints git status, `hermes profile list` via `/opt/hermes/bin/hermes`, and each bot's live profile and apply marker. The `hermes` invocation is allowed to fail without stopping the script.

There is nothing else to start. Creating a profile, applying it, and restarting its gateway are host actions in the README, not local run steps.

## Directory map

```text
bots/<slug>/                  reviewed profile source
  profile.yaml                role, live profile, env allowlists
  SOUL.md                     identity and authority
  AGENTS.md                   profile operations copied to the live profile
  runtime-config.yaml         Hermes runtime overlay
  env.defaults                non-secret defaults only
  gateway-run.sh              profile s6 entrypoint
  skills/                     bot-local skill overlay (don-draper only today)
docs/                         fleet standards
  ACCEPTANCE.md               launch and regression gates
  CONTRIBUTING.md             change classes, review, local verification
  FLEET_PRINCIPLES.md         tiers, ownership, when to add an agent
  SECURITY.md                 credentials, writes, incidents
  SLACK_STANDARD.md           Slack behavior and configuration
  SOURCE_HIERARCHY.md         evidence and freshness
skills/                       shared skills applied to every bot
  stayd-new-agent-factory
  stayd-slack-standard
  staydos-agent-api
  staydos-platform-architecture
templates/new-agent/          placeholder factory, including slack-app-manifest.yaml
scripts/apply-bot.sh          reviewed source to live profile
scripts/compose-skills.py     shared plus local skill composition
scripts/merge-config-overlay.py
scripts/status.sh
scripts/sync-shared-env.sh    allowlisted keys only; refuses every SLACK_* key
scripts/upsert-env-defaults.sh
shared/env.keys.example       variable-name inventory, empty values
shared/env.keys.md            which names are shared and which are per bot
tools/validate_repo.py        standards and privacy validator
tests/test_validate_repo.py   validator and composition tests
.github/workflows/validate.yml
POLICY.md
```

Shared skills install first. Bot-local `skills/` overlay by relative path. Duplicate skill `name` values fail validation and fail apply before a live profile is touched.

## Secrets

Never commit secret values. Commit variable names only.

Names documented in [`shared/env.keys.example`](shared/env.keys.example) and [`shared/env.keys.md`](shared/env.keys.md):

- Shared across profiles: `GITHUB_TOKEN`, `SUPABASE_ACCESS_TOKEN`, `VERCEL_TOKEN`
- Per bot, never copied between bots: every `SLACK_*` key, including `SLACK_BOT_TOKEN`, `SLACK_APP_TOKEN`, and `SLACK_ALLOWED_USERS`; `STAYDOS_AGENT_API_KEY` when that role has approved StaydOS access
- Non-secret runtime toggle in each `env.defaults`: `SLACK_REACTIONS=true`
- Non-secret watchdog defaults also present in `env.defaults`: `HERMES_CODEX_EVENT_STALE_TIMEOUT_SECONDS`, `HERMES_CODEX_TTFB_TIMEOUT_SECONDS`, `HERMES_CODEX_TTFB_MAX_SECONDS`

[`.gitignore`](.gitignore) ignores `.env`, `**/.env`, `*.pem`, `*.key`, `handoff*.env`, and `bots/*/.applied`. `tools/validate_repo.py` fails the repo on credential-shaped strings, private keys, home-directory paths, phone numbers, personal or non-example email addresses, Slack workspace identifiers, and production project identifiers. `env.defaults` and `shared/env.keys.example` may only contain empty values, `<placeholder>` values, or the small allowlist in `SAFE_ENV_VALUES`.

Values belong in the target profile's protected runtime `.env` or the provider's secret store. `scripts/sync-shared-env.sh` refuses every `SLACK_*` key.

## Work tracking (Linear)

- Team: Stayd, key `STA`.
- Branch: `STA-###-short-kebab`.
- PR title: `STA-###: summary`.
- Label: `agent:venusaur`.

TODO: tracked docs in this repo do not say when a Linear issue is required, how issue status moves, or whether any label besides `agent:venusaur` is required.

## Deploys and production

Do not deploy or change production unless a human has explicitly said yes to that action.

This repo has no deploy workflow. The production path is on the host, from a reviewed commit:

- `./scripts/apply-bot.sh <agent-slug>` without `--dry-run` copies identity files into `/opt/data` (when `live_profile` is `default`) or `/opt/data/profiles/<live-profile>`, deep-merges `runtime-config.yaml` into the live `config.yaml`, installs the composed skill tree, syncs allowlisted env keys, upserts `env.defaults`, and can copy `gateway-run.sh` into `/run/service/gateway-<live-profile>/run`. It also writes `bots/<slug>/.applied`.
- `./scripts/apply-bot.sh <agent-slug> --record` can create an apply-marker commit.
- `./scripts/sync-shared-env.sh`, `./scripts/upsert-env-defaults.sh`, and `./scripts/merge-config-overlay.py` write live env or live Hermes config when given live paths.
- README host setup (`hermes profile create`, `hermes -p <agent-slug> config migrate`, `hermes -p <agent-slug> config check`) and the gateway restart `s6-svc -r /run/service/gateway-<live-profile>` change the running fleet.
- Slack app creation, install, scope changes, and token placement change a live identity. Tokens stay in the profile `.env`.

`--dry-run` is the local check above. A clean validator run does not apply a profile. A merge to `main` does not apply a profile either. Applying is a separate host command and still needs an explicit human yes.

## Pull requests and CI

Default branch is `main` ([`POLICY.md`](POLICY.md)).

[`.github/workflows/validate.yml`](.github/workflows/validate.yml) is the only workflow. It is named `Validate fleet standards`. Job `validate` runs on `ubuntu-latest` with `contents: read` for every pull request and for pushes to `main`:

1. `actions/checkout@v4`
2. `actions/setup-python@v5` with Python `3.12`
3. `python -m pip install --disable-pip-version-check PyYAML`
4. `python tools/validate_repo.py .`
5. `python tools/validate_repo.py --self-test`
6. `python -m unittest discover -s tests -v`

Run those three Python commands before opening a PR. For a profile, runtime, skill, policy, or script change, also run the shell syntax check, `compileall`, `git diff --check`, and `./scripts/apply-bot.sh <agent-slug> --dry-run` from [`docs/CONTRIBUTING.md`](docs/CONTRIBUTING.md).

Review required by that doc:

| Change | Review |
|---|---|
| Documentation wording with no policy effect | repository maintainer |
| Profile lens, sources, or domain skill | repository maintainer and department owner |
| Runtime, apply tooling, shared skills, or fleet policy | repository maintainer and fleet operator |
| Credentials, permissions, channels, write powers, or security controls | repository maintainer and security owner |
| External audience, spend, publish/send, deletion, or production authority | security owner and department owner, with an explicit rollout plan |

`gh api repos/StaydVR/hermes-fleet/rulesets` returned an empty list. Classic branch protection on `main` returned HTTP 403, so it was not readable from this environment.

TODO: confirm whether job `validate` is a required check before merge, and whether pushes straight to `main` are blocked. Until that is confirmed, open a pull request and get `validate` green anyway.
