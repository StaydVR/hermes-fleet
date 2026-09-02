---
name: staydos-platform-architecture
description: "Use when designing, reviewing, or changing StaydOS modules, data models, integrations, organization scope, theming, navigation, or responsive UI."
version: 1.0.0
author: Stayd Fleet
license: MIT
metadata:
  hermes:
    tags: [staydos, architecture, org-scope, data, security]
---

# StaydOS platform architecture

Apply this skill before proposing or implementing a StaydOS feature. It is a class-level guardrail; the current StaydOS architecture, module registry, integration guide, and feature contract remain authoritative.

## Start with the source set

1. Read the repository `AGENTS.md` and architecture document.
2. Read the dated current-state document so shipped and planned work are not confused.
3. Read the module registry before creating a route, table, or integration.
4. Read the integration guide when a provider or credential is involved.
5. Read the feature contract and recent migration history for the affected module.

If the documents conflict, prefer the binding architecture for rules and the newest verified current-state record for what is live. Surface the conflict instead of inventing a reconciliation.

## Three product contracts

### Brand identity carries through

- `orgId` is the application scope spine.
- Resolve identity from the canonical org registry. Never hardcode a brand list, name, color, font, or logo in feature code.
- Holdco rolls up descendants; a leaf sees itself.
- A brand switch must change both scope and theme.
- Filter visible org choices through the authenticated grant surface. Client filtering is user experience; server authorization and RLS remain enforcement.

### Theme comes from tokens

- Use the established semantic design tokens and font system.
- Do not add brand-specific colors or font values inside a component.
- Verify the same component under multiple org themes.

### Mobile-first, one shell

- Design at 375px first and layer larger layouts upward.
- Keep wide data inside local horizontal overflow.
- Register app routes in the existing shell and both desktop and mobile navigation.
- Portal fixed overlays to the document body when shell effects can create a containing block.

## Choose an existing data pattern

Do not create another warehouse. Choose and register one of:

- mock warehouse for local vision and layout work;
- the existing browser work store for My Tasks only;
- live Supabase for operational modules;
- hybrid CRM for secured live reads with an explicit fallback mode.

Identity and data mode are separate. A mock page and a live page still use the same `orgId` registry. Never mix mock rows into a response presented as live.

## Tenant and database rules

- New live tables use `org_id` and row-level security with the approved recursive org-access helpers.
- Grandfathered CRM tables keep `company_id` or `brand_id`; do not rename them and do not invent a third tenant key.
- Derive write scope from the target row when possible. Do not trust only a client-claimed org.
- Service-role credentials remain server-side and never reach a browser or an agent.
- Empty states must distinguish no data from filtered or unauthorized data. Filters and grouping must not silently drop known rows.

## Integrations

- The external provider remains source of record.
- Store credentials in runtime secret stores or the approved encrypted credential registry.
- For per-account credentials, stamp `org_id` from the credential used to fetch the data.
- For a holdco credential returning mixed subsidiaries, map the provider's subsidiary field through a reviewed source map.
- Register the integration scope and data mode before wiring a module.

## Definition of done

Before calling the feature complete:

1. update the source docs and module registry;
2. run targeted tests and lint;
3. run the production build;
4. verify holdco plus at least two org scopes;
5. verify mobile and desktop layouts;
6. verify exact authorization and RLS for reads and writes;
7. verify provider or database results from the authoritative source;
8. state any remaining mock, hybrid, lag, or rollout limitation.
