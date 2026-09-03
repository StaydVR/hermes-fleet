# New-agent launch manifest

## Charter

- [ ] Durable role and non-goals are explicit.
- [ ] Tier, audience, department owner role, security owner role, requester, and reviewer are named by role.
- [ ] An existing agent or skill cannot serve the need more simply.
- [ ] Every job maps to a source, tool, freshness rule, write boundary, and acceptance prompt.

## Profile

- [ ] Every angle-bracket placeholder in this directory is replaced.
- [ ] The slug is stable, lowercase, and matches the intended live profile.
- [ ] No peer credentials, memories, sessions, scheduled jobs, or identity text were copied.
- [ ] Runtime config contains the complete Slack exact-mention, one-final-reply, and working-status contract.
- [ ] `SLACK_REACTIONS=true` is present in non-secret defaults.

## Access

- [ ] Required credentials are dedicated or have a documented scope rationale.
- [ ] Secret values exist only in protected runtime stores.
- [ ] Required tools work from the profile's real backend.
- [ ] Prohibited tools and delete capability are absent or structurally blocked.
- [ ] Positive and negative access tests pass.

## Slack

- [ ] Dedicated app created from the reviewed manifest.
- [ ] Installed OAuth grant includes the intended minimum scopes, `reactions:write`, and `assistant:write`.
- [ ] Bot and app tokens belong to the intended app and workspace.
- [ ] Approved rooms and access model are documented.
- [ ] DM, exact-message channel/thread/group-DM mention, unmentioned follow-up, reaction, footer, failure, and one-receipt tests pass.

## Apply and acceptance

- [ ] Repository validator and unit tests pass.
- [ ] Shell, Python, YAML, and diff checks pass.
- [ ] Shared and local skill dry-run composition passes without collisions.
- [ ] Exact reviewed commit is applied.
- [ ] Only the target gateway is restarted.
- [ ] Every applicable item in `docs/ACCEPTANCE.md` has evidence.
- [ ] Rollback revision and command are ready.
