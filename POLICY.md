# Stayd Hermes fleet policy

This policy is binding for every profile managed by this repository. The architecture is one host with isolated Hermes profiles and a git audit trail.

## Source of truth

| Layer | Source | Tracked? |
|---|---|---|
| Agent identity, role, and profile metadata | `bots/<slug>/` | Yes |
| Fleet standards and shared skills | `docs/`, `skills/`, `POLICY.md` | Yes |
| Apply and validation tooling | `scripts/`, `tools/`, `tests/` | Yes |
| Live Hermes profile | `/opt/data` or `/opt/data/profiles/<live-profile>` | No; generated |
| Credentials | protected runtime env or provider secret store | Never |
| Sessions, memory, and runtime state | live profile only | Never |

## Governance roles

- **Fleet operator:** runs preflight, apply, profile-specific restarts, and operational acceptance.
- **Repository maintainer:** reviews tracked changes and protects the source-to-live mechanism.
- **Security owner:** approves credentials, permissions, new powers, external access, and incident response.
- **Department owner:** owns the agent charter, domain accuracy, audience, and acceptance prompts.
- **Requester:** defines the outcome and supplies business context; request authority is not automatically approval authority.
- **Reviewer:** independently checks the diff, evidence, and rollback path.

One person may hold more than one role, but approvals must still be made in the capacity named above.

## Change rules

1. Live configuration is applied from a reviewed commit. A normal apply refuses a dirty worktree; `--commit <sha>` applies an immutable reviewed revision.
2. Every agent must have a durable department owner role. The fleet operator does not silently inherit domain ownership.
3. `scripts/apply-bot.sh` is the only normal source-to-live path. Manual emergency changes must be captured in git or reverted immediately after containment.
4. Shared skills install for every bot. Bot-local skills may add narrower behavior, but duplicate skill names are rejected.
5. Secrets, personal data, production identifiers, sessions, and memories never enter this repository.
6. Slack credentials are profile-specific. Shared env sync refuses every `SLACK_*` key.
7. New credentials, permissions, channels, standing rules, consequential write powers, public actions, spend, deletion, and profile shutdown require the responsible security or department approval.
8. Deleting a bot requires an approved removal plan, credential rotation or revocation, runtime verification, and a recoverable rollback point.
9. A successful command is not proof of completion. The fleet operator must verify the real outcome from the authoritative system before the agent or operator finalizes success.
10. Do not commit or push an apply marker automatically unless the change process explicitly calls for an audited marker update.

## Slack contract

Every profile follows [`docs/SLACK_STANDARD.md`](docs/SLACK_STANDARD.md). Authorized 1:1 DMs work normally; channels, existing threads, and group DMs require an explicit bot mention on each exact message. Runtime overlays enable only Slack's normal thinking indicator and argument-free verb footer while disabling thought/reasoning exposure, streaming, interim assistant text, tool-progress messages, long-running notices, native task cards, and heartbeat noise. Eligible work starts with `:eyes:`; independently verified `SUCCESS` receives `:white_check_mark:` and `FAILURE` receives `:x:`. Shared-surface responses remain in non-broadcast source threads and end with exactly one concise final receipt.

## Branch and review

- Default branch: `main`.
- Durable policy, security, source hierarchy, factory, validator, and apply-tool changes require repository-maintainer review.
- Credential or permission changes also require security-owner review.
- Agent charter or source-semantics changes also require department-owner review.

See [`docs/CONTRIBUTING.md`](docs/CONTRIBUTING.md) for the complete process.
