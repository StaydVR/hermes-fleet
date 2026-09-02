---
name: staydos-agent-api
description: "Use when an agent reads or changes StaydOS through a machine API, including scope resolution, authentication, bounded writes, deduplication, approval, and read-back verification."
version: 1.0.0
author: Stayd Fleet
license: MIT
metadata:
  hermes:
    tags: [staydos, agent-api, authorization, writes, verification]
---

# StaydOS agent API operations

Use this skill for machine access to StaydOS. It does not grant access. The target profile must have an approved dedicated credential and only the bounded endpoints required by its charter.

## Security model

- Treat every agent API key as a holdco-wide service credential even when requests are leaf-scoped.
- Store it in a dedicated runtime env variable, never in git, chat, memory, browser code, logs, or tool arguments that may be retained.
- Do not give an agent a database service-role credential.
- Use only documented endpoints. Do not convert a bounded API task into arbitrary database or provider access.
- No delete capability by default.

## Read workflow

1. Use the API's overview or discovery endpoint to resolve valid orgs, leaf brands, stages, and stable identifiers.
2. Resolve the exact requested scope. Rollup reads may use an org; writes require the endpoint's exact leaf or entity scope.
3. Apply documented filters, time windows, pagination, and result caps.
4. Record the source timestamp and relevant sync lag.
5. Return the minimum fields needed. Do not expose contact details or confidential fields in broad summaries.
6. Separate live fact from inference and say when the endpoint cannot establish freshness.

## Write workflow

Before any write:

1. confirm the action is inside the agent charter;
2. identify the required human approval or reviewed standing rail;
3. fetch the target and resolve its exact org, brand, stage, entity id, and current state;
4. search for an existing equivalent record and deduplicate;
5. construct the smallest supported request with expected-current values or idempotency controls where available;
6. dry-run or use a validation-only path when supported;
7. execute once;
8. read the record back through the authoritative API;
9. compare requested and actual state;
10. report one concise verified receipt.

If read-back fails or differs, report partial or failed status. Do not retry a create blindly and do not finalize success.

## Consequential actions

Spend, budget changes, publishing, sending, external contact, production mutation, permissions, credentials, standing rules, and bulk updates require explicit approval unless a reviewed server-enforced rail names the exact allowed action and limits.

Reduction-only or other constrained endpoints do not imply broader provider authority. Respect dry-run defaults, expected-current checks, brand allowlists, classification requirements, and saved caps. Never emulate a missing capability through a lower-level credential.

## Error handling

- Authentication failure: stop, disclose no credential material, and route to the security owner.
- Validation or scope failure: correct the exact input; do not probe unrelated ids.
- Conflict: refetch current state and ask for a new decision if intent may change.
- Provider or server fault: preserve the safe request summary and status, stop bounded retries, and do not claim the write happened.
- Unknown result: query by stable id or dedupe key before any retry.

## Receipt

Include action, exact non-sensitive scope, source/read-back result, and any remaining limitation. Never include secret values, personal records, raw provider payloads, or hidden reasoning.
