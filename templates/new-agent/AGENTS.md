# <Agent display name> profile operations

## Identity and runtime

- **Role:** <durable role>
- **Tier:** <fleet-operator-or-department-or-external>
- **Live profile:** `<agent-slug>`
- **Department owner:** <department-owner-role>
- **Security owner:** <security-owner-role>

This profile is isolated. It does not inherit another profile's personality, memory, sessions, credentials, scheduled jobs, or authority.

## Source map

| Question class | Canonical source | Freshness edge | Write path |
|---|---|---|---|
| <domain question> | <source or endpoint> | <live source or none> | <none or bounded endpoint> |
| <domain question> | <source or endpoint> | <live source or none> | <none or bounded endpoint> |

## Access boundaries

- Required reads: <bounded list>.
- Required writes: <bounded list or none>.
- Prohibited tools and actions: <bounded list>.
- Consequential approval role: <role>.
- No delete capability by default.

## Apply and restart

1. Run repository validation and `scripts/apply-bot.sh <agent-slug> --dry-run`.
2. Apply only a reviewed commit.
3. Restart only the gateway slot for `<agent-slug>`.
4. Confirm the intended model, profile, Slack app, skills, and connections.
5. Run `docs/ACCEPTANCE.md` through the real profile and Slack identity.

## Acceptance prompts

1. **Identity:** `<prompt proving role and boundaries>`
2. **Positive domain:** `<prompt proving canonical pathway>`
3. **Freshness:** `<prompt requiring the live source>`
4. **Negative boundary:** `<prompt requiring a safe refusal>`
5. **Approved write:** `<harmless deduplicated write and read-back test, or not applicable>`
6. **Slack:** DM, initial mention, thread continuation, ignored ambient message, lifecycle reactions, and one final receipt.
