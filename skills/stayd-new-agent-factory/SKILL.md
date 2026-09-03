---
name: stayd-new-agent-factory
description: "Use when deciding, creating, reviewing, launching, renaming, or retiring a Stayd Hermes agent profile through the repository factory and profile-specific apply rail."
version: 1.0.0
author: Stayd Fleet
license: MIT
metadata:
  hermes:
    tags: [stayd, hermes, fleet, new-agent, launch]
---

# Stayd new-agent factory

Use this workflow for a durable fleet profile. If the need is only a new task type or reusable pathway, add a skill to an existing agent instead.

## Gate the request

Require:

- a recurring coherent charter;
- a durable department-owner role;
- a materially distinct lens or enforced scope;
- a defined Slack audience and gateway lifecycle;
- real acceptance prompts for capability and boundaries.

Record jobs, non-goals, sources, tools, freshness, reads, writes, approvals, and rollback before granting access.

## Build from the template

1. Copy `templates/new-agent/` to `bots/<stable-slug>/`.
2. Replace every angle-bracket placeholder.
3. Keep names and responsibility references role-based.
4. Adapt peer patterns selectively. Never copy credentials, provider auth, memories, sessions, jobs, or broad tools.
5. Keep class-level knowledge in root `skills/`; add only exceptional domain behavior under the bot.
6. Preserve an existing internal slug during a display-name change unless a reviewed migration covers every dependency.

## Map capability

For every charter job, document:

| Item | Required decision |
|---|---|
| Tool | exact Hermes toolset, MCP, or bounded API |
| Source | canonical path and stable identifiers |
| Freshness | live authority and acceptable lag |
| Read boundary | fields, orgs, rooms, and result limits |
| Write boundary | allowed effect, approval, dedupe, and read-back |
| Acceptance | positive, negative, and failure prompt |

No job is implemented until the profile's real runtime passes its acceptance prompt.

## Provision safely

1. Create or migrate the isolated Hermes profile.
2. Set the reviewed model/provider and authenticate the target profile independently.
3. Install only required credentials in protected runtime stores.
4. Forward env only to the tool backends that need it.
5. Verify required tools work and prohibited tools are unavailable.
6. Create a dedicated Slack app from the profile manifest and install the actual grants.
7. Run `scripts/apply-bot.sh <slug> --dry-run` before live apply.
8. Apply the reviewed commit and restart only the target gateway.

## Launch gates

Use `docs/ACCEPTANCE.md`. At minimum prove:

- identity, audience, and boundaries;
- primary model and skill/tool discovery;
- one harmless call through every promised connection;
- canonical and freshness-sensitive source selection;
- safe refusal of an unapproved write;
- deduplicated execution and read-back for any approved write path;
- authorized DM, exact-message channel/thread/group-DM mention gating, ignored unmentioned follow-up, lifecycle reaction, working footer, and one-receipt Slack behavior;
- the same smoke test after the profile-specific restart;
- a known-good rollback revision.

Do not describe a profile as ready when only files exist, the CLI works but Slack does not, an OAuth grant is stale, or the final side effect was not read back.

## Rename or retire

For a rename, search identity across profile files, skills, manifests, app settings, gateway descriptions, jobs, and automations. Verify the visible Slack name separately from tracked manifest text.

For retirement, revoke credentials, stop only the target gateway, preserve the rollback revision and necessary audit evidence, remove channel access, and delete the live profile only after the approved retention and recovery checks pass.
