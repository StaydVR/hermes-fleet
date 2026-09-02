# Stayd Hermes fleet

This repository is the reviewed source of truth for Stayd's Hermes agent profiles. It keeps identity, runtime overlays, shared operating skills, and host apply tooling in git while leaving credentials, sessions, memory, and live runtime state on the cloud host.

The operating model remains one host with isolated Hermes profiles. A change moves through this path:

```text
reviewed repository files -> apply preflight -> isolated live profile -> profile gateway -> Slack acceptance test
```

## Start here

Read these in order before changing a profile:

1. [`POLICY.md`](POLICY.md) — binding fleet governance and apply rules.
2. [`docs/FLEET_PRINCIPLES.md`](docs/FLEET_PRINCIPLES.md) — tiers, scope, ownership, and agent design.
3. [`docs/SECURITY.md`](docs/SECURITY.md) — access, credentials, write boundaries, and incident handling.
4. [`docs/SOURCE_HIERARCHY.md`](docs/SOURCE_HIERARCHY.md) — evidence, freshness, and StaydOS architecture rules.
5. [`docs/SLACK_STANDARD.md`](docs/SLACK_STANDARD.md) — the required Slack behavior and configuration.
6. [`docs/ACCEPTANCE.md`](docs/ACCEPTANCE.md) — launch and regression gates.
7. [`docs/CONTRIBUTING.md`](docs/CONTRIBUTING.md) — the change, review, rollout, and rollback process.

## Repository map

```text
bots/<slug>/                 reviewed profile-specific source
  profile.yaml               role, live profile, env allowlists
  SOUL.md                    identity, judgment, and authority
  AGENTS.md                  optional profile operations and governance
  runtime-config.yaml        deep-merged Hermes runtime overlay
  env.defaults               non-secret runtime defaults only
  gateway-run.sh             profile-specific s6 entrypoint
  skills/                    bot-local skill overlays
docs/                        durable fleet standards and runbooks
skills/                      shared skills applied to every bot
templates/new-agent/         placeholder-only profile factory
scripts/apply-bot.sh         reviewed source -> live profile
scripts/compose-skills.py     shared + local skill composition guard
scripts/status.sh            git, Hermes profile, and apply status
tools/validate_repo.py       CI standards and privacy validator
tests/                       validator and composition tests
shared/env.keys.example      safe variable-name inventory
```

Shared skills are installed first. Bot-local `skills/` content is then overlaid by relative path. Skill `name` values must remain unique across both layers; `apply-bot.sh` refuses a collision before touching a live profile.

## 1. Check out and inspect

On the Hermes host, use the fleet directory managed by the host operator:

```bash
git clone <fleet-repository-url> fleet
cd fleet
git status --short
./scripts/status.sh
python3 tools/validate_repo.py .
```

Do not place the repository inside a live Hermes profile. Do not copy `.env`, sessions, memories, or state databases into git.

Before editing, identify:

- the agent tier and department owner;
- the exact live profile slug and gateway slot;
- the minimum sources, tools, and write boundaries required;
- the human approval point for consequential actions;
- the acceptance prompts that will prove the role works.

## 2. Design the agent before creating it

Use [`docs/FLEET_PRINCIPLES.md`](docs/FLEET_PRINCIPLES.md) to decide whether the request needs a durable agent or a skill on an existing agent. A new agent needs a durable role owner, a materially different lens or access boundary, and enough recurring work to justify a new operational surface.

Write a short charter with:

- jobs and non-goals;
- audience and tier;
- canonical sources and freshness expectations;
- allowed reads, allowed writes, and forbidden actions;
- approval and escalation roles;
- Slack rooms and mention behavior;
- positive, negative, freshness, and write-path acceptance cases.

If those items are not clear, keep the agent in design rather than granting credentials.

## 3. Create a profile from the factory

Copy the factory and choose a stable lowercase slug:

```bash
cp -R templates/new-agent bots/<agent-slug>
```

Then replace every angle-bracket field in:

- `profile.yaml` with role-based metadata and the live profile name;
- `SOUL.md` with the durable role charter;
- `AGENTS.md` with profile-specific operations and boundaries;
- `runtime-config.yaml` only where the approved model or runtime differs;
- `env.defaults` with non-secret defaults only;
- `slack-app-manifest.yaml` with display text and request URLs supported by the deployment;
- `CHECKLIST.md` with the launch evidence.

Never copy a peer profile wholesale. In particular, do not copy its `.env`, Slack tokens, provider authentication, memories, sessions, scheduled jobs, or broad tool access. Preserve an existing slug when changing only a display name, because slugs are coupled to live profile paths and gateway slots.

Run the placeholder and standards check:

```bash
python3 tools/validate_repo.py .
./scripts/apply-bot.sh <agent-slug> --dry-run
```

## 4. Prepare secrets and access

Repository files contain secret names, never secret values. Use [`shared/env.keys.example`](shared/env.keys.example) as the safe inventory.

On the host:

1. Create or identify the isolated Hermes profile.
2. Put profile-specific credentials only in that profile's protected runtime `.env` or the provider's approved secret store.
3. Keep the runtime `.env` and Hermes config owner-readable only.
4. Give every distinct Slack bot its own bot and app tokens.
5. Use dedicated service credentials where practical; otherwise document why a shared credential's scope is appropriate.
6. Forward only required variables into isolated tool backends.
7. Verify credential presence and a harmless live call from the agent's real runtime. Host-side presence alone is not proof.

`profile.yaml.shared_env_keys` is an explicit allowlist copied from the default host env into a non-default profile. `sync-shared-env.sh` rejects every `SLACK_*` key. `required_env_keys` is the launch inventory, not a source of values.

For StaydOS API access, use a dedicated env variable, bounded endpoints, least privilege, deduplication, and read-back verification. Never expose service-role credentials to a browser or agent. See [`skills/staydos-agent-api/SKILL.md`](skills/staydos-agent-api/SKILL.md).

## 5. Create and install the Slack app

Create one Slack app per durable agent identity from the reviewed `slack-app-manifest.yaml`.

1. In Slack app administration, choose creation from an app manifest.
2. Review the bot display text and keep it role-based.
3. Enable Socket Mode.
4. Request only the events the role needs. The normal baseline is app mentions, public/private channel messages where invited, and direct messages.
5. Include `chat:write` for the final receipt and `reactions:write` for lifecycle reactions.
6. Avoid admin, deletion, channel-management, workflow-management, and user-management scopes unless separately approved.
7. Install or reinstall the app after scope changes.
8. Store `SLACK_BOT_TOKEN` and `SLACK_APP_TOKEN` only in the target profile's runtime `.env`.
9. Confirm the installed token grants match the manifest; configured scopes without a reinstall are not sufficient.
10. Invite the bot only to approved channels.

The required interaction contract is in [`docs/SLACK_STANDARD.md`](docs/SLACK_STANDARD.md). Channels require an initial explicit mention; DMs work normally; a thread can continue without repeated mentions; replies stay in the thread and are not broadcast.

## 6. Create or migrate the Hermes profile

Run these commands on the host using the exact target slug:

```bash
hermes profile create <agent-slug> --description "<role description>"
hermes -p <agent-slug> config migrate
hermes -p <agent-slug> config check
```

For the default profile, follow the host's established default-profile command form. Do not create a second default profile. Confirm that the profile root exists before applying.

Verify model authentication in the target profile with the intended primary model. A successful fallback response does not prove primary-model parity. Do not solve missing authentication by copying another profile's refresh tokens.

## 7. Validate, review, and apply

Before review:

```bash
python3 tools/validate_repo.py .
python3 -m unittest discover -s tests -v
find . -type f -name '*.sh' -not -path './.git/*' -exec bash -n {} +
python3 -m compileall -q scripts tools tests
git diff --check
./scripts/apply-bot.sh <agent-slug> --dry-run
```

After the change is reviewed and committed, apply exactly the reviewed state:

```bash
./scripts/apply-bot.sh <agent-slug>
```

If the checkout contains unrelated work, apply a reviewed commit without using working-tree files:

```bash
./scripts/apply-bot.sh <agent-slug> --commit <reviewed-sha>
```

The apply script:

1. validates the profile source;
2. preflights shared and bot-local skill names;
3. verifies the live profile exists;
4. copies identity and governance files;
5. deep-merges the runtime overlay into live Hermes config;
6. installs the composed shared and local skill tree;
7. syncs only allowlisted non-Slack shared env keys;
8. upserts non-secret env defaults;
9. stages the exact profile gateway entrypoint;
10. records the applied revision in live state.

Applying configuration does not by itself prove the agent is healthy.

## 8. Restart only the target gateway

Map `live_profile: default` to the default gateway slot. Other profiles map to their own `gateway-<live-profile>` slot.

On an s6 host, restart only the resolved service directory:

```bash
s6-svc -r /run/service/gateway-<live-profile>
```

Never restart a generic or unrelated gateway as a shortcut. Confirm:

- the service has a current process;
- logs identify the expected Hermes profile;
- Socket Mode connects as the intended Slack app;
- required skills and tools are visible;
- other profile gateways stayed healthy.

## 9. Run acceptance tests

Use [`docs/ACCEPTANCE.md`](docs/ACCEPTANCE.md) and record evidence for every promised capability. At minimum, test through the real Slack identity:

- authorized DM;
- initial channel mention;
- unmentioned channel message is ignored;
- thread continuation remains in-thread without broadcast;
- correct identity, scope, sources, and uncertainty language;
- a freshness-sensitive question selects the live source;
- an unapproved consequential write is refused with a useful next step;
- an approved write, if the role has one, deduplicates and reads back;
- one and only one concise final receipt;
- `:eyes:` at start, removed at completion, then `:white_check_mark:` only after verified success;
- failure does not receive a check reaction.

Do not mark the launch complete from config inspection, a process exit code, or an intermediate status. Read the agent's persisted final response and verify the side effect from the authoritative source.

## 10. Roll back safely

Choose a previously accepted commit, inspect its profile diff, and apply that immutable revision:

```bash
git show --stat <known-good-sha>
./scripts/apply-bot.sh <agent-slug> --commit <known-good-sha>
s6-svc -r /run/service/gateway-<live-profile>
```

Then repeat the identity, connection, Slack, and domain smoke tests. A rollback does not delete profile secrets, sessions, or runtime data. Destructive cleanup, credential rotation, profile deletion, or channel removal requires the relevant security or department approval.

If the incident involves a credential, remove or rotate it in the runtime secret store first, contain the affected integration, and only then repair tracked configuration.

## 11. Maintain the fleet

For every change:

- update durable standards only when the policy changes;
- update profile files when one agent's lens or runtime changes;
- put reusable operating knowledge in root `skills/`;
- put exceptional domain behavior in the bot-local skill tree;
- update source freshness notes when a system of record or sync lag changes;
- run the full acceptance set after permissions, providers, Slack scopes, or gateways change;
- review role ownership and access regularly;
- remove obsolete capabilities deliberately, with rollback and verification.

Use `./scripts/status.sh` for host state. Treat generated live state as evidence, not as a replacement for the reviewed files in this repository.
