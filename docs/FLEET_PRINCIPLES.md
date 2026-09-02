# Fleet principles

## Purpose

The fleet exists to move recurring company work from question to verified outcome without creating a maze of overlapping agents. Success is reliable adoption and reduced manual coordination, not agent count.

## Agent tiers

| Tier | Purpose | Typical audience | Default risk posture |
|---|---|---|---|
| Fleet operator | Profile, host, cross-system, and fleet operations | tightly limited operational roles | broad internal reach, attended use, exact audit trail |
| Department agent | One durable front door for a business function | approved internal teams | narrow domain scope, bounded writes, clear escalation |
| External agent | Interaction with customers, partners, or the public | external parties | separate identity and infrastructure; explicit approval and stronger controls |

External agents are a different risk class. Do not turn an internal department profile outward by adding a channel or prompt line.

## Shared floor, role lens, enforced scope

- **Shared floor:** common operating knowledge and class-level skills every agent needs. It belongs in root `skills/` and must compute common facts consistently.
- **Role lens:** what the agent notices first, how it prioritizes, and how it communicates. It belongs in the profile's `SOUL.md` and bot-local skills.
- **Enforced scope:** the data, tools, people, and side effects the profile can reach. It belongs in credentials, API boundaries, grants, tool configuration, and server-side authorization—not only in prose.

The same source can support different lenses. Different answers are acceptable when they reflect role priorities; different underlying facts are not.

## When to create a new agent

Create a durable profile only when all are true:

1. A department-owner role will keep its context current.
2. The work has a recurring, coherent charter.
3. Its lens or enforced access boundary is materially different from an existing agent.
4. It needs a distinct Slack identity or gateway lifecycle.
5. Real acceptance prompts can prove its value and limits.

Otherwise add or improve a skill on an existing agent. A new task type alone is not a reason for a new profile.

## Authority levels

| Level | Meaning | Default |
|---|---|---|
| Observe | Read approved sources and capture evidence | allowed within scope |
| Recommend | Diagnose and propose a next action | allowed within scope |
| Draft | Create reversible internal or paused artifacts | allowed when the charter says so |
| Approve | Authorize money, external effects, standing rules, or expanded access | human role only |
| Execute | Perform an approved or pre-authorized bounded action | only through an enforced rail |

“Accept,” “looks good,” or a task assignment means work the item. It does not automatically authorize publishing, sending, spending, deleting, deploying, or changing access.

## Ownership

- The department owner maintains domain truth, role priorities, and the acceptance set.
- The fleet operator maintains profile health and applies reviewed changes.
- The repository maintainer protects standards and the source-to-live rail.
- The security owner controls credentials, permissions, and incident response.
- The requester supplies context but does not gain approval power outside their role.
- The reviewer verifies the change and its evidence independently.

Record roles in durable documents, not individual names. If no role owns an agent, the profile is a known risk and should not gain new capability.

## Design rules

1. Reliability before personality. A plain verified answer beats a distinctive unsupported one.
2. Target the narrowest authoritative source first. Do not explore broadly when a registered path exists.
3. Prompts and skills guide behavior; credentials, server checks, and constrained tools enforce it.
4. Attended and unattended work have different risk. Scheduled work needs stricter bounds, cost controls, and deterministic paths.
5. Reversibility and audience define risk more accurately than “read” versus “write.”
6. Every consequential write resolves the exact scope and entity, deduplicates, obtains required approval, and reads back.
7. Do not add delete capability by default.
8. An agent never claims success until its real verification gates pass.
9. Limits must be explained with the safe next path. Silent refusal destroys trust.
10. Shared facts come from shared skills; exceptional behavior stays local to the profile.
