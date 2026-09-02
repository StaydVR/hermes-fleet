# Security and access rules

## Default posture

Grant the least access that can complete the charter. Prefer dedicated profile credentials, bounded APIs, server-side scope checks, reversible actions, and explicit approval for consequential writes.

Skills and SOUL files are guidance. Security boundaries live in credentials, API authorization, database policies, tool availability, gateway configuration, and human access controls.

## Data classes

| Class | Examples | Repository rule | Agent rule |
|---|---|---|---|
| Public | published company information | allowed when useful | cite current source |
| Internal | operating procedures, non-sensitive metrics | reviewed class-level guidance allowed | share only in approved company contexts |
| Confidential | customer, employee, lead, financial, or contract detail | no examples or records | minimum fields, minimum audience |
| Secret | tokens, keys, passwords, signing material | never | runtime secret store only; never print or relay |

This repository must not contain personal emails, phone numbers, contacts, customer or lead examples, credentials, home-directory paths, Slack IDs, or production project/deployment IDs.

## Credentials

- Store secrets only in the target profile's protected `.env` or an approved provider secret store.
- Keep profile-specific Slack tokens isolated. Never sync or copy them across profiles.
- Prefer dedicated service credentials. When sharing is necessary, record the scope and reason without recording the value.
- Verify credentials through the target runtime. A variable on the host does not prove a container, MCP server, or agent can use it.
- Print only presence, safe identifiers, counts, status codes, and boolean verification results.
- Rotate credentials after suspected exposure, audience change, or role removal.
- Never send service-role credentials to a browser or an agent.

## StaydOS access

StaydOS uses `orgId` as the scope spine. Resolve the exact org, brand, stage, and entity before any write.

- New live data uses `org_id` with row-level security.
- Grandfathered CRM paths use `company_id` or `brand_id`; do not invent another tenant key.
- Holdco-wide agent API keys are service credentials. Put them in dedicated env variables and expose only bounded endpoints.
- Live actions must authorize the exact leaf scope server-side.
- External providers remain the source of record for their systems.
- Do not add delete capability by default.

## Write control

Before a consequential write:

1. establish that the requester's role can request it;
2. obtain approval from the role named by policy when required;
3. resolve the exact org, brand, entity, and current state;
4. use the narrowest supported endpoint or tool;
5. deduplicate or use an idempotency key;
6. execute only the approved change;
7. read the result back from the authoritative source;
8. report the verified outcome once.

Spend, external sends, publishing, production changes, permissions, credentials, standing rules, deletion, and new powers require explicit approval unless a reviewed standing rail names the exact action and limits.

## Slack access

- Use a separate app identity per durable agent.
- Invite it only to approved rooms.
- Require an initial channel mention and keep replies in non-broadcast threads.
- Treat operator-audience access as a security boundary and review it regularly.
- OAuth scope configuration is not proof of the installed grant; reinstall and inspect the live grant after changes.
- `reactions:write` is required for verified lifecycle reactions.

## Incidents

If access or a credential may be compromised:

1. contain the affected integration or profile;
2. revoke or rotate credentials in the runtime secret store;
3. preserve logs and identify the scope of exposure;
4. notify the security owner and relevant department owner;
5. repair reviewed configuration;
6. re-run negative and positive acceptance tests before restoring service;
7. record the durable lesson without copying sensitive incident details into this repository.
