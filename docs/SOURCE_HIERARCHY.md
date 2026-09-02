# Source hierarchy and evidence rules

## General hierarchy

Use the narrowest current authoritative source that can answer the question:

1. live provider or transaction system for current external state;
2. live StaydOS record or bounded agent endpoint for current internal state;
3. approved product contract, architecture document, or module registry for intended behavior;
4. reviewed fleet skill or profile instruction for operating method;
5. durable agent memory for context only;
6. conversation history for leads, never proof.

A lower source cannot overrule a higher one. If sources conflict, report the conflict, identify timestamps and scope, and resolve at the authoritative source. Do not ask another agent to vote on the truth.

## Evidence requirements

For any material claim, capture:

- source and query or pathway;
- org/brand/entity scope;
- observation time and the source's own update time when available;
- denominator and time window for metrics;
- whether the result is fact, reported claim, inference, or unresolved gap;
- known sync lag, exclusions, and data-quality limits.

“Current,” “today,” “just now,” and other freshness-sensitive requests require a live read. Memory and prior chat are not current evidence.

Search before reporting no result: try stable identifiers, approved synonyms, related canonical objects, pagination, and full threads where applicable. Stop when the documented path is exhausted; do not wander through broad schemas or unrelated tools.

## StaydOS platform rules

StaydOS is a multi-brand operating system and `orgId` is its scope spine.

1. Brand identity must carry through every feature. Read identity from the canonical org registry; never hardcode brand names, ids, colors, or fonts into features.
2. Theme comes from design tokens.
3. Product UI is mobile-first, works at 375px, and lives in one registered shell reachable from desktop and mobile navigation.
4. Choose deliberately among the existing data patterns: mock warehouse, My Tasks work store, live Supabase, or hybrid CRM. Do not add another warehouse.
5. Register new modules and document their data mode.
6. New live tables use `org_id` with RLS. Existing CRM keeps `company_id` or `brand_id`. Never create a third tenant key.
7. Live actions authorize the exact leaf scope server-side. Service-role credentials never go to browsers or agents.
8. The provider remains source of record for external integrations; secrets stay in runtime secret stores.

## StaydOS agent APIs

- Treat agent API credentials as holdco-wide service credentials even when an endpoint is narrow.
- Use a dedicated env variable for each API class.
- Begin with discovery or overview, then resolve exact leaf scope and entity.
- Use bounded reads and writes. Apply pagination and result limits.
- Deduplicate before creates or batch writes.
- Require explicit approval for consequential writes unless a reviewed standing rail covers them.
- Read back every write from the authoritative endpoint or provider.
- Do not add or simulate delete behavior by default.

## Build evidence

A StaydOS change is not verified by a local happy path alone. The normal gate includes:

- source architecture and current-state documents;
- module registry and data-mode update;
- targeted tests and lint;
- production build;
- at least two org scopes plus holdco;
- mobile and desktop behavior;
- exact write authorization and read-back when live actions change.

These are class-level rules. Feature-specific contracts and current-state documents remain authoritative for their domains.
